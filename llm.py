import requests
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables
load_dotenv()

# Define the API endpoints and keys from environment variables
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
API_LLM_URL = os.getenv("API_LLM_URL")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
LOCAL_PATH = os.getenv("LOCAL_PATH")

# Send POST request to LLM API for processing
def llm_send_request(llm_url, headers, data):
    response = requests.post(llm_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get response from LLM. Status code: {response.status_code}")
        print(response.text)  # For debugging
        return None
    
# Main execution
def main():
    # Open the file in read mode
    file_path = LOCAL_PATH + 'curriculum-be-golang/100-ticketing/app/controllers/root.go'  # Replace with the path to your code file
    with open(file_path, 'r') as file:
        # Read the contents of the file
        file_contents = file.read()

    # Prepare data for LLM request
    data_llm = {
        "messages": [
            {"role": "system", "content": "Help fix the code and give it in a json format as code, with commit message to github as commit_message."},
            {"role": "user", "content": f"{file_contents}"}
        ],
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    llm_response = llm_send_request(API_LLM_URL, headers, data_llm)

    if not llm_response:
        print("No valid response from LLM API.")
        return

    # Extract the content from the first choice's message
    content_string = llm_response['choices'][0]['message']['content']

    # Find the JSON object within the content string
    json_match = re.search(r'```json\n(.*?)\n```', content_string, re.DOTALL)
    
    if not json_match:
        print("Failed to extract JSON object from response.")
        return

    json_object_str = json_match.group(1)

    # Parse the JSON object
    json_object = json.loads(json_object_str)

    # Extract file_content and commit_message
    file_content = json_object.get('code')
    commit_message = json_object.get('commit_message')

    # Print the extracted information
    print("Fixed Code:\n", file_content, "\n")
    print("Commit Message:\n", commit_message)

    # Save the fixed code
    with open(file_path, 'w') as file:
        file.write(file_content)

if __name__ == "__main__":
    main()
