import pika
import requests
import os

chaturl = "https://api.openai.com/v1/chat/completions"
open_api_key = os.getenv("OPENAI_API_KEY")

headers = {
    "Authorization": f"Bearer {open_api_key}",
    "Content-Type": "application/json"
}


def generateResponses(prompt):
    messages = [{'role': 'user', 'content': 'I would like to explain a concept involving multiple ChatGPT agents working together to complete complex tasks. The main idea is to create a system where one central ChatGPT (Task Manager) breaks down a complex task into smaller subtasks and assigns them to specialized ChatGPT "workers." Each worker will handle a specific part of the task independently. Can you summarize what I mean by this?'}, {'role': 'assistant', 'content': 'In essence, this concept proposes a multi-agent system composed of several ChatGPTs, working collaboratively to solve complex tasks. A central ChatGPT, the Task Manager, acts as a coordinator. It decomposes a complex task into multiple, more manageable subtasks, and assigns each to specialized ChatGPT workers. These workers focus on completing their specific assigned subtasks independently. Together, their individual outputs contribute towards the resolution of the overall complex task.'}, {'role': 'user', 'content': 'Explain the structure of a system where a central ChatGPT (Task Manager) delegates tasks to other ChatGPT agents (workers). The central ChatGPT should be able to:\n1. Analyze and decompose a complex task into manageable subtasks.\n2. Generate specific prompts for each worker to guide them in their subtasks.\n3. Collect and integrate the results from each worker to complete the original task.'}, {'role': 'assistant', 'content': "The proposed system structure encompasses a Task Manager ChatGPT and several worker ChatGPT agents. The process goes as follows:\n\n1. Upon receiving a complex task, the Task Manager ChatGPT begins by comprehending the task and decomposing it into several smaller, manageable subtasks. The decomposition is done intelligently and is based on the nature and complexity of the task.\n\n2. Once the subtasks are identified, the Task Manager prepares specific prompts for each worker ChatGPT. These prompts are designed to guide the workers, outlining precisely what is required for the subtask at hand. They serve to ensure that each agent understands its role and what it needs to accomplish.\n\n3. Each worker ChatGPT then works independently on its assigned subtask. They follow the prompt's instructions to provide a solution or contribution.\n\n4. Upon completion of the subtasks, the workers submit their results back to the Task Manager ChatGPT.\n\n5. The Task Manager collects all the separate results and integrates them to form a cohesive solution to the original, complex task.\n\nThrough this structure, the system facilitates collaborative problem-solving, allowing for more effective and efficient handling of complex tasks."}, {'role': 'user', 'content': 'Provide examples of tasks that could be effectively managed by this system of multiple ChatGPT agents. Consider both simple tasks (like developing a library inventory system) and more complex projects (like building a ridesharing app). Detail how the task would be broken down and assigned to different agents.'}, {'role': 'assistant', 'content': "Sure, here are examples for both a simple task (developing a library inventory system) and a complex task (building a ridesharing app):\n\n1. **Simple Task: Developing a Library Inventory System**  \n   The Task Manager could break down this task into several subtasks:\n\n   - **ChatGPT Agent 1 (Database Designer)**: Design the database structure for the library inventory, defining various attributes for books like ID, name, author, publisher, etc., as well as user data.\n   \n   - **ChatGPT Agent 2 (UI/UX Designer)**: Sketch and outline the user interface of the inventory system, creating interfaces for both users and library staff.\n\n   - **ChatGPT Agent 3 (Backend Developer)**: Construct the application's backend that communicates with the database and implements functionalities like adding books, lending books, or returning books.\n\n   - **ChatGPT Agent 4 (Frontend Developer)**: Develop the frontend of the application that interacts with users, using the designs provided by the UI/UX designer.\n\n2. **Complex Task: Building a Ridesharing App**  \n   This project could be decomposed into more intricate subtasks:\n\n   - **ChatGPT Agent 1 (Database Designer)**: Design databases to store user data, driver data, ride details, locations, and other necessary data.\n  \n   - **ChatGPT Agent 2 (Location and Maps Specialist)**: Work on integrating and managing maps and geolocations, considering aspects like tracking driver locations, finding the shortest routes, and so on.\n   \n   - **ChatGPT Agent 3 (Payment System Integration Specialist)**: Develop and integrate a secure payment system into the application.\n   \n   - **ChatGPT Agent 4 (UI/UX Designer)**: Design the application's user interface, considering both rider and driver perspectives.\n   \n   - **ChatGPT Agent 5 (Backend Developer)**: Build the app's backend, which involves implementing numerous functionalities like matching riders with drivers, managing ride statuses (requested, in-progress, completed), etc.\n   \n   - **ChatGPT Agent 6 (Frontend Developer)**: Develop the application frontend according to the designs and specifications from the UI/UX designer and map out user interactions.\n\nThe Task Manager would collect the output from these specialized agents, ensuring that each component fits together to properly create the complete application or system."}, {'role': 'user', 'content': 'Now, consider yourself as a GPT worker in this scenario. You are a ChatGPT worker tasked with completing a specific subtask. When providing your answer, please adhere strictly to the following format: Output: {Insert your answer here}. Do not include any explanations,affirmations or additional comments. For example, if your task is to complete some skeleton code, just provide the complete code without any additional text. Do not output anything that strays away from format I specified above when I signify the start of the prompt. I will signify the start of the prompt by saying "Here is the prompt: ". Do you understand?'}, {'role': 'assistant', 'content': "Yes, I understand. I'll provide results strictly according to the format you specified once you give me the prompt."}, {'role': 'user', 'content': 'You will receive a RAG prompt in the following format: \\{"subtask": "relevantSubtask", "Relevant Information": "relevantInformation"\\}. Your task is to focus on the "subtask" provided and utilize the "Relevant Information" to complete it. Please ensure that your response contains only the output relevant to the subtask, formatted as specified: Output: {Insert your answer here} Remember, no additional text or explanations should be included in your response. Do you understand?'}, {'role': 'assistant', 'content': "Yes, I understand. I'll follow the given format for my response. Please provide the prompt."}]
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

        # print(numTasks)
        return assistant_response
    
    else:
        raise Exception(f"Failed to retrieve worker response: {response.text}", 400)
    
def callback(ch, method, properties, message):
    message = message.decode("utf-8")
    generateResponses(message)
    channel.basic_publish(exchange="requests", routing_key="hypervisor",body=message)



if __name__ == "__main__":
    with pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672)) as connection:
        channel = connection.channel()
        channel.exchange_declare(exchange='requests', exchange_type='direct')
        result = channel.queue_declare(queue='', exclusive=True)
        q = result.method.queue
        channel.queue_bind(exchange="requests", queue=q,routing_key="expert1")
        channel.basic_consume(   
                queue=q, on_message_callback=callback, auto_ack=True)
        with open("hello", "a+") as f:
            f.write("hola" +"\n")

        channel.start_consuming()