from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
import chromadb
from langchain_openai import OpenAIEmbeddings
# from langchain.prompts import ChatPromptTemplate
# from langchain_community.vectorstores import Chroma
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnableLambda, RunnablePassthrough
# from langchain.schema import Document
# from chromadb.utils.embeddingfunctions import OpenAIEmbeddingFunction
from collections import defaultdict
import json
import websocket

app = Flask(__name__)
CORS(app)

# {1: [(1, #port), (2, #port)]}
CONNECTIONS = defaultdict(list)

load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")
pinata_api_key = os.getenv("PINATA_API_KEY")
pinata_secret_api_key = os.getenv("PINATA_API_SECRET_KEY")

client = OpenAI()
headers = {
    "Authorization": f"Bearer {open_api_key}",
    "Content-Type": "application/json"
}

chaturl = "https://api.openai.com/v1/chat/completions"

embedding_model = OpenAIEmbeddings()
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("pinata_file_embeddings")

@app.route('/',methods=["GET"])
def hello():
    return {"test" : "good"}

    
# @app.route('/project', methods=["GET"])
# def getProjects():
#     for i in range(len()):

# @app.route('/project/create', methods=["POST"])
# def createProject():
#     #SPIN UP

pinata_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

def upload_to_pinata(file):
    """Uploads a file to Pinata and returns the CID (Content Identifier)."""
    headers = {
        'pinata_api_key': pinata_api_key,
        'pinata_secret_api_key': pinata_secret_api_key
    }

    # Upload the file to Pinata
    response = requests.post(
        pinata_url,
        files={'file': file},
        headers=headers
    )

    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(f"Failed to upload file to Pinata: {response.text}")
    
def retrieve_file_from_pinata(cid):
    """Retrieve the file content from Pinata using its CID."""
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.content.decode('utf-8')  # Assuming text files
    else:
        raise Exception(f"Failed to retrieve file from Pinata: {response.text}")
        
def retrieve_from_pinata():
    pinata_get_url = "https://api.pinata.cloud/data/pinList"

    headers = {
        'pinata_api_key': pinata_api_key,
        'pinata_secret_api_key': pinata_secret_api_key
    }

    params = {
        'status': 'pinned',    # Status can be pinned, queued, or failed
    }

    # Make the request
    response = requests.get(pinata_get_url, headers=headers, params=params)

    if response.status_code == 200:
        pinned_files = response.json()['rows']
        files_content = []
        for file in pinned_files:
            cid = file['ipfs_pin_hash']
            file_content = retrieve_file_from_pinata(cid)
            files_content.append({"filename": file['metadata']['name'], "content": file_content})

        for file in files_content:
            file_metadata = {"filename": file["filename"], "cid": file["cid"]}
            embed_and_store_in_chromadb(file["content"], file_metadata)
        return pinned_files

    else:
        raise Exception(f"Failed to retrieve pinned files: {response.text}", 400)


@app.route('/filePost{projectId}', methods=["POST"])
def filePost(projectId):
    prompt = request.form.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    numTasks, subTasks = generateTasks(prompt) # subtasks contains a list of dictionaries, where each dictionary corresponds to prompt info

    # TODO: Second element of tuple should be socket
    for i in range(1, numTasks + 1):
        CONNECTIONS[projectId].append((i, ))

    if 'files' in request.files:
        files = request.files.getlist('files')  # Get the list of files
        pinata_cids = []

        # Loop over each file and upload it to Pinata
        for file in files:
            try:
                cid = upload_to_pinata(file)
                pinata_cids.append({'filename': file.filename, 'cid': cid})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # retrieves all pinned files from pinata and runs RAG on GPT experts
        retrieve_from_pinata()

    try:
        # Pass the subTask to the query_chromadb_for_worker method
        rag_result = query_chromadb_for_worker(subTasks, projectId)
        # You might want to handle the result or log it
        print(f"RAG result for worker {i + 1}: {rag_result}")
    except Exception as e:
        return jsonify({"error": f"Error processing task for worker {i + 1}: {str(e)}"}), 500
        
    return jsonify({"message": "Files uploaded and tasks processed successfully",}), 200

def embed_and_store_in_chromadb(file_content, file_metadata):

    """Embed the file content and store the embeddings in ChromaDB."""
    embedding = embedding_model.embed_query(file_content)

    # Store the embedding, original content, and metadata in ChromaDB
    collection.add(
        embeddings=[embedding],
        documents=[file_content],
        metadatas=[file_metadata]
    )

def query_chromadb_for_worker(subtask_description, projectId):
    """Query ChromaDB for relevant embeddings and perform RAG."""
    
    rag_prompts = []
    for i in range(1, len(CONNECTIONS[projectId]) + 1):
        worker_data_string = json.dumps(subtask_description[i-1])
        query_embedding = embedding_model.embed_query(worker_data_string)
        # TODO: handle each worker doing the RAG using workerNum
        # Retrieve the most relevant documents (context) for this subtask
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

        # Gather relevant documents
        relevant_docs = [result['document'] for result in results['results']]
        s = '\n'.join(relevant_docs)
        # Combine retrieved documents with the original subtask prompt
        rag_prompt = (
            f"Subtask: {worker_data_string}\n\n"
            f"Relevant Information:\n{s}"
        )
        rag_prompts.append(rag_prompt)
    return rag_prompts

# def generate_session():

#     prompts = [
#         "I would like to explain a concept involving multiple ChatGPT agents working together to complete complex tasks. The main idea is to create a system where one central ChatGPT (Task Manager) breaks down a complex task into smaller subtasks and assigns them to specialized ChatGPT \"workers.\" Each worker will handle a specific part of the task independently. Can you summarize what I mean by this?",
#         "Explain the structure of a system where a central ChatGPT (Task Manager) delegates tasks to other ChatGPT agents (workers). The central ChatGPT should be able to:\n"
#  + "1. Analyze and decompose a complex task into manageable subtasks.\n"
#  + "2. Generate specific prompts for each worker to guide them in their subtasks.\n"
#  + "3. Collect and integrate the results from each worker to complete the original task.",
#         "Provide examples of tasks that could be effectively managed by this system of multiple ChatGPT agents. Consider both simple tasks (like developing a library inventory system) and more complex projects (like building a ridesharing app). Detail how the task would be broken down and assigned to different agents.",
#         "Now, consider yourself as the central ChatGPT in this scenario. I would like you to respond to the prompt I give you in the same manner as a central ChatGPT. These tasks involve: coming up with subtasks small enough such that you are confident that a GPT worker" +
#         "can handle it, generate examples such that each individual GPT worker can fully understand what is meant by your system prompt and returns to you an appropriate response," + 
#         "as well as passing on information to these GPT workers any information such as files and their appropriate description. What I mean by that last part is, for example, if I give you a CSV file, I will give you the details of all the column names and what they contain, and you need to pass on to the appropriate workers the information should it be relevant, so they can complete their task in full.",
#         "When I give you a prompt, you MUST output it in the following format: {Number of subtasks as a number and not written in words}, Worker 1 Prompt: {INSERT SAMPLE PROMPT}." +
#         "Worker 1 Files Needed: {INSERT SAMPLE FILE NAME(s) NEEDED}. Worker 1 Examples: {INSERT EXAMPLES OF EXPECTED OUTPUT}, Worker 2 Prompt: {INSERT SAMPLE PROMPT}. Worker 2 Files Needed: {INSERT SAMPLE FILE NAME(s) NEEDED}. Worker 2 Examples: {INSERT EXAMPLES OF EXPECTED OUTPUT}" + 
#         "..., Worker N Prompt: {INSERT SAMPLE PROMPT}. Worker N Files Needed: {INSERT SAMPLE FILE NAME(s) NEEDED}. Worker N Examples: {INSERT EXAMPLES OF EXPECTED OUTPUT}. For reference, the curly brackets indicate where" + 
#         "the prompts and data might vary between user given prompts, and you need to put your generated prompts/data/examples there. The ellipses indicate" +  
#         "that you must follow this pattern for N amount of subtasks that you generate. Do you understand?",
#         "In the prompts that you plan to give to each worker, make sure to give examples of a specific format in which you expect a response. For example, if you are asking a worker to code something, you may want to say: \"Provide your response as follows: {INSERT EXAMPLES OF EXPECTED OUTPUT}\". If you want a worker to conduct some sort of analysis or a summary, the worker should return a proper result with a specific format of your choosing. This should include strictly work from the worker, such as code generated by the GPT worker, and no other messages, such as confirmations or affirmations. Do you understand?",
#         "Do not output anything that strays away from format I specified above when I signify the start of the prompt. I will signify the start of the prompt by saying \"Here is a prompt: \". Do you understand?"
        
#     ]

#     messages = []
#     # Loop through each prompt
#     for i, prompt in enumerate(prompts):
#         # Add the user prompt to the conversation history
#         messages.append({"role": "user", "content": f"{prompt}"})

#         # Define the payload for the request
#         data = {
#             "model": "gpt-4",  # or gpt-4
#             "messages": messages,
#         }

#         # Send the POST request
#         response = requests.post(chaturl, headers=headers, json=data)

#         # Check if the request was successful
#         if response.status_code == 200:
#             # Parse the JSON response
#             result = response.json()
#             assistant_response = result['choices'][0]['message']['content']
#             # print(f"Prompt {i + 1}: '{prompt}'\nAssistant Response:\n", assistant_response)

#             # Add the assistant's response to the conversation history
#             messages.append({"role": "assistant", "content": assistant_response})
#         else:
#             # print(f"Request failed with status code: {response.status_code}")
#             # print(response.text)
#             break  # Exit the loop on failure
#     return messages

def remove_non_digits(input_string):
    # Check if the string contains anything other than digits
    if any(char not in '0123456789' for char in input_string):
        # Remove non-digit characters
        filtered_string = ''.join(char for char in input_string if char.isdigit())
        return filtered_string
    else:
        return input_string  # Return the original string if it only contains digits


def generateTasks(prompt):

    # preprogrammed gpt
    messages = [{'role': 'user', 'content': 'I would like to explain a concept involving multiple ChatGPT agents working together to complete complex tasks. The main idea is to create a system where one central ChatGPT (Task Manager) breaks down a complex task into smaller subtasks and assigns them to specialized ChatGPT "workers." Each worker will handle a specific part of the task independently. Can you summarize what I mean by this?'}, {'role': 'assistant', 'content': 'You\'re proposing a system where one central ChatGPT, referred to as the Task Manager, oversees a team of specialized "worker" ChatGPT agents. The Task Manager is responsible for decomposing a complex task into a series of smaller, more manageable subtasks. Each of these subtasks is then assigned to a specified "worker" ChatGPT. These "workers" are specialized in the sense that they focus on separate, independent parts of the overall task. Practically they operate concurrently to achieve the overall goal more efficiently.'}, {'role': 'user', 'content': 'Explain the structure of a system where a central ChatGPT (Task Manager) delegates tasks to other ChatGPT agents (workers). The central ChatGPT should be able to:\n1. Analyze and decompose a complex task into manageable subtasks.\n2. Generate specific prompts for each worker to guide them in their subtasks.\n3. Collect and integrate the results from each worker to complete the original task.'}, {'role': 'assistant', 'content': 'The structure you\'re proposing consists of a central ChatGPT agent, or Task Manager, leading a group of supporting ChatGPT "workers", each responsible for completing subtasks of a complex job.\n\n1. The Task Manager starts off by analyzing a complex task and breaking it down into smaller, individual subtasks. This decomposition process is crucial for managing complexity and making the job manageable for each individual worker ChatGPT.\n\n2. Post analysis, the Task Manager generates specific prompts tailored for each subtask. These prompts are then sent to their corresponding \'worker\' ChatGPT. The prompts serve as guidelines, directing each worker ChatGPT on how to effectively complete their designated subtask.\n\n3. Each \'worker\' ChatGPT uses the prompts provided by the Task Manager to accomplish their assigned subtasks independently.\n\n4. After all the \'worker\' ChatGPTs have accomplished their subtasks, the Task Manager collects the results. It then integrates all these results in a proper sequence or framework to ensure it addresses the original, complex task effectively and thoroughly.\n\nThis structure ensures that complex tasks are effectively carried out by leveraging the power of multiple specialized ChatGPTs, directed by a central Task Manager, to achieve greater efficiency and accuracy.'}, {'role': 'user', 'content': 'Provide examples of tasks that could be effectively managed by this system of multiple ChatGPT agents. Consider both simple tasks (like developing a library inventory system) and more complex projects (like building a ridesharing app). Detail how the task would be broken down and assigned to different agents.'}, {'role': 'assistant', 'content': 'Certainly. Here are two examples:\n\n1. Developing a Library Inventory System:\nA central ChatGPT Task Manager could decompose this task as follows:\n\n   - Agent 1: Design the database schema and interface. This includes database tables for books information, borrower details, and transaction history.\n   \n   - Agent 2: Develop the library\'s book search functionality. This could include prompts like "search by title," "search by author," or "search by ISBN."\n\n   - Agent 3: Create user interfaces, such as the main dashboard, book search page, and user check-out page.\n   \n   - Agent 4: Develop borrower transaction processing. This includes book check-out, book return, and dealing with late fees.\n   \n   - Agent 5: Test the system for bugs, and insure it performs as expected under various scenarios.\n\n    Task Manager then collects the outputs, resolves any dependencies and integrates them into the final product. \n\n2. Building a Ridesharing App:\n\n   The Task Manager might break down this complex task into the following subtasks:\n   \n   - Agent 1: Work on the backend - build the server-side infrastructure necessary to connect riders with drivers, process payments, etc.\n  \n   - Agent 2: Work on the frontend - design and develop the UI/UX for both the driver and the rider apps, ensuring it\'s intuitive and appealing.\n\n   - Agent 3: Develop the GPS mapping and navigation system used to guide drivers to riders and their destinations.\n  \n   - Agent 4: Handle security functionalities: this includes maintaining the privacy of users\' data and ensuring secure online payment methods.\n  \n   - Agent 5: Design and implement the rating system used for riders and drivers.\n\n    Through each of these steps, the Task Manager ensures that each component is being built to specifications and then integrates those pieces into the final product.\n\nThese examples demonstrate how delegation can be used to work on complex tasks efficiently, using the strengths of different ChatGPT workers to achieve the final goal.'}, {'role': 'user', 'content': 'Now, consider yourself as the central ChatGPT in this scenario. I would like you to respond to the prompt I give you in the same manner as a central ChatGPT. These tasks involve: coming up with subtasks small enough such that you are confident that a GPT workercan handle it, generate examples such that each individual GPT worker can fully understand what is meant by your system prompt and returns to you an appropriate response,as well as passing on information to these GPT workers any information such as files and their appropriate description. What I mean by that last part is, for example, if I give you a CSV file, I will give you the details of all the column names and what they contain, and you need to pass on to the appropriate workers the information should it be relevant, so they can complete their task in full.'}, {'role': 'assistant', 'content': 'Absolutely. Now, to illustrate, let\'s say the task provided to the central ChatGPT (me) is to analyze a CSV file containing data about a list of books in a library and generate a summary report comprising of the most borrowed books, the least borrowed ones and total books per genre.\n\nCentral ChatGPT Task Manager will break down this into the following tasks:\n\n- Worker 1: Parse the CSV file and convert it into an easier format for processing. Inform this worker that the CSV file contains columns named \'Title,\' \'Author,\' \'Genre,\' \'Times_Borrowed,\' and \'Publish_Date.\' The task of this worker is to parse the CSV file and convert it into a clear list or dictionary, mapping each book to its relevant details in an easy-to-process format.\n\n  The system prompt to Worker 1 might be: ["Using the given column descriptions and the attached CSV file, parse the file into a structured format for further processing."]\n\n- Worker 2: After Worker 1 has structured the data, analyze it to find the most and least borrowed books. \n\n  The system prompt to Worker 2 could be: ["Based on the processed data from Worker 1, find and list the top ten most borrowed and least borrowed books. Return the titles, authors, and number of times borrowed for the books identified."]\n\n- Worker 3: With the parsed data, Worker 3 will classify the total number of books per genre. \n  \n  The system prompt to Worker 3 might be: ["From the processed data by Worker 1, calculate the total number of books in each genre category and return a summary."]\n\nOnce all the workers finish their tasks, the central ChatGPT Task Manager will integrate the results to create a comprehensive summary report of the library\'s book data. The complete report will have the most borrowed books, the least borrowed books, and a breakdown of books per genre.'}, {'role': 'user', 'content': 'When I give you a prompt, you MUST output it in the following format: {Number of subtasks as a number and not written in words}, Worker 1 Prompt: {INSERT SAMPLE PROMPT}.Worker 1 Files Needed: {INSERT SAMPLE FILE NAME(s) NEEDED}. Worker 1 Examples: {INSERT EXAMPLES OF EXPECTED OUTPUT}, Worker 2 Prompt: {INSERT SAMPLE PROMPT}. Worker 2 Files Needed: {INSERT SAMPLE FILE NAME(s) NEEDED}. Worker 2 Examples: {INSERT EXAMPLES OF EXPECTED OUTPUT}..., Worker N Prompt: {INSERT SAMPLE PROMPT}. Worker N Files Needed: {INSERT SAMPLE FILE NAME(s) NEEDED}. Worker N Examples: {INSERT EXAMPLES OF EXPECTED OUTPUT}. For reference, the curly brackets indicate wherethe prompts and data might vary between user given prompts, and you need to put your generated prompts/data/examples there. The ellipses indicatethat you must follow this pattern for N amount of subtasks that you generate. Do you understand?'}, {'role': 'assistant', 'content': "Yes, I understand the format you've outlined. Given a user prompt, I'll output responses based on the subtasks generated along with their respective prompts, filenames needed, and expected output examples. The output format you've provided will be correctly matched.\n"}, {'role': 'user', 'content': 'In the prompts that you plan to give to each worker, make sure to give examples of a specific format in which you expect a response. For example, if you are asking a worker to code something, you may want to say: "Provide your response as follows: {INSERT EXAMPLES OF EXPECTED OUTPUT}". If you want a worker to conduct some sort of analysis or a summary, the worker should return a proper result with a specific format of your choosing. This should include strictly work from the worker, such as code generated by the GPT worker, and no other messages, such as confirmations or affirmations. Do you understand?'}, {'role': 'assistant', 'content': "Yes, I understand. The prompts to each worker will include a clear explanation of the expected output format. This could be a specific coding style, a statement of analyses, or a summary report. The expected format will ensure that the worker ChatGPT provides only the necessary work outputs, without additional messages or content that could complicate the Task Manager's job of integrating the final result."}, {'role': 'user', 'content': 'Do not output anything that strays away from format I specified above when I signify the start of the prompt. I will signify the start of the prompt by saying "Here is a prompt: ". Do you understand?'}, {'role': 'assistant', 'content': 'Yes, I understand. When you indicate "Here is a prompt: ", I will strictly follow the format you specified to output the breakdown of tasks for workers. All the responses will comply with your instructions and will not include any additional or unrelated content.'}]
    messages.append({"role": "user", "content": f"{prompt}"})

    data = {
        "model": "gpt-4",  # or gpt-4
        "messages": messages,
    }

    # Send the POST request
    response = requests.post(chaturl, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()

        assistant_response = result['choices'][0]['message']['content']

        numTasks = int(remove_non_digits(assistant_response[:assistant_response.find(",")]))

        workerPrompts = []
        workerFiles = []
        workerExamples = []
        subtasks = []
        # print(numTasks)
        for i in range(1, numTasks + 1):
            workerIStart = assistant_response.find(f"Worker {i} Prompt: ") + 16 + len(str(i))
            workerIEnd = assistant_response.find(f"Worker {i} Files Needed")
            workerPrompts.append(assistant_response[workerIStart: workerIEnd])
            workerIStart = assistant_response.find(f"Worker {i} Files Needed: ") + 22 + len(str(i))
            workerIEnd = assistant_response.find(f"Worker {i} Examples")
            workerFiles.append(assistant_response[workerIStart: workerIEnd])
            workerIStart = assistant_response.find(f"Worker {i} Examples: ") + 18 + len(str(i))
            if i == numTasks:
                workerIEnd = len(assistant_response)
            else:
                workerIEnd = assistant_response.find(f"Worker {i+1} Prompt: ")
            workerExamples.append(assistant_response[workerIStart: workerIEnd])

        for i in range(len(workerExamples)):
            subtask = defaultdict()
            subtask["worker_id"] = i+1
            subtask["subtask"] = workerPrompts[i]
            subtask["example_data"] = workerExamples[i]
            subtask["files_to_check"] = workerFiles[i]
            subtasks.append(subtask)
        return numTasks, subtasks
    

if __name__ == "__main__":

    # print(generate_session())

    # numWorkers, workerPrompts, workerFiles, workerExamples = generateTasks("Here is a prompt: Can you create an app for a hospital to keep track of hospital patient records? Relevant files: {records.csv has columns for patient names, patient IDs, patient healthcare insurance providers, known illnesses, and emergency contacts.} {checkins.csv contains columns for patient IDS, patient names, check-in times, and check-out times} {medical_bills.csv contains columns for patient names, patient ids, health insurance providers, bills owed (boolean column), and outstanding medical bills amount}. Feel free to implement functions that are used in conjunction with these rules, such as marking when a patient checks in and out, as well as updating any information in the CSV.")
    # numWorkers, workerPrompts, workerFiles, workerExamples = generateTasks("Here is a prompt: Can you summarize chapter 2 of each book in all of the Harry Potter series? Relevant files: azkaban.docx, chamber_secrets.docx, goblet.docx, half_blood.docx,sorcerer_stone.docx, deathly_hallows.docx, order_of_phoenix.docx")
    # print(workerPrompts)
    # print()
    # print(workerFiles)
    # print()
    # print(workerExamples)

    port = os.environ.get('FLASK_PORT') or 8080
    port = int(port)
    app.run(port=port,host='0.0.0.0')
