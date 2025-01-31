import requests
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Define the API endpoints and keys from environment variables
url = os.getenv("API_URL")
key = os.getenv("API_KEY")
llm_url = os.getenv("API_LLM_URL")
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
local_path = os.getenv("LOCAL_PATH")

# Send POST request to LLM API for processing
def send_to_llm(llm_url, headers, data):
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
    file_path = local_path + 'curriculum-be-golang/100-ticketing/app/controllers/controllers.go'  # Replace with the path to your code file
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
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    llm_response = send_to_llm(llm_url, headers, data_llm)
    # print (llm_response)

    response_data = llm_response

    # Extract the content from the first choice's message
    content_string = response_data['choices'][0]['message']['content']

    # The content string contains a JSON object embedded in a larger text. We need to extract this JSON object.
    # We can use a regex to find the JSON object within the content string.
    import re

    # Find the JSON object within the content string
    json_object_str = re.search(r'```json\n(.*?)\n```', content_string, re.DOTALL).group(1)

    # Parse the JSON object
    json_object = json.loads(json_object_str)

    # Extract file_content and commit_message
    file_content = json_object.get('code')
    commit_message = json_object.get('commit_message')

    # Print the extracted information
    print("Fixed Code:\n", file_content, "\n")
    print("Commit Message:\n", commit_message)

    file_path = ''
    with open(file_path, 'w') as file:
        file.write(file_content)

if __name__ == "__main__":
    main()