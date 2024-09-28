import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}



url = "https://api.openai.com/v1/chat/completions"

def test(prompt):

    prompts = [
        "I would like to explain a concept involving multiple ChatGPT agents working together to complete complex tasks. The main idea is to create a system where one central ChatGPT (Task Manager) breaks down a complex task into smaller subtasks and assigns them to specialized ChatGPT \"workers.\" Each worker will handle a specific part of the task independently. Can you summarize what I mean by this?",
        "Explain the structure of a system where a central ChatGPT (Task Manager) delegates tasks to other ChatGPT agents (workers). The central ChatGPT should be able to:\n"
 + "1. Analyze and decompose a complex task into manageable subtasks.\n"
 + "2. Generate specific prompts for each worker to guide them in their subtasks.\n"
 + "3. Collect and integrate the results from each worker to complete the original task.",
        "Provide examples of tasks that could be effectively managed by this system of multiple ChatGPT agents. Consider both simple tasks (like developing a library inventory system) and more complex projects (like building a ridesharing app). Detail how the task would be broken down and assigned to different agents.",
        "Now, consider yourself as the central ChatGPT in this scenario. I would like you to respond to the prompt I give you in the same manner as a central ChatGPT. These tasks involve: coming up with subtasks small enough such that you are confident that a GPT worker" +
        "can handle it, generate examples such that each individual GPT worker can fully understand what is meant by your system prompt and returns to you an appropriate response," + 
        "as well as passing on information to these GPT workers any information such as files and their appropriate description. What I mean by that last part is, for example, if I give you a CSV file, I will give you the details of all the column names and what they contain, and you need to pass on to the appropriate workers the information should it be relevant, so they can complete their task in full."
    ]

    messages = []

    # Loop through each prompt
    for i, prompt in enumerate(prompts):
        # Add the user prompt to the conversation history
        messages.append({"role": "user", "content": prompt})

        # Define the payload for the request
        data = {
            "model": "gpt-4",  # or gpt-4
            "messages": messages,
        }

        # Send the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            assistant_response = result['choices'][0]['message']['content']
            print(f"Prompt {i + 1}: '{prompt}'\nAssistant Response:\n", assistant_response)

            # Add the assistant's response to the conversation history
            messages.append({"role": "assistant", "content": assistant_response})
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            break  # Exit the loop on failure
    print(messages)