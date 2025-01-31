import requests
import base64
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the API endpoints and keys from environment variables
url = os.getenv("API_URL")
key = os.getenv("API_KEY")
llm_url = os.getenv("API_LLM_URL")
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")

# Encode login credentials for Basic Authentication
def encode_authentication(login, password):
    auth = base64.b64encode(f"{login}:{password}".encode()).decode()
    return auth

# Prepare headers for the API requests
def create_headers(auth=None):
    headers = {
        "Authorization": f"Basic {auth}" if auth else f"Bearer {key}",
        "Content-Type": "application/json"
    }
    return headers

# Send GET request to search for issues
def get_issues(url, headers, params):
    response = requests.get(url + "api/issues/search", headers=headers, params=params)
    if response.status_code == 200:
        print("Issues searched successfully!")
        return response.json()
    else:
        print(f"Failed to search issues. Status code: {response.status_code}")
        print(response.text)  # For debugging
        return None

# Send POST request to LLM API for processing
def send_to_llm(llm_url, headers, data):
    response = requests.post(llm_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get response from LLM. Status code: {response.status_code}")
        print(response.text)  # For debugging
        return None

# Main function to process issues and get responses
def process_issues(issues):
    i = 1
    for issue in issues:
        print(f"Processing issue: {i}")
        i += 1

        # Extract issue details
        issue_key = issue['key']
        rule = issue['rule']
        component = issue['component']
        severity = issue['severity']
        project = issue['project']
        line = issue['line']
        text_range = issue['textRange']
        message = issue['message']

        # Print issue details
        print(f"Issue Key: {issue_key}")
        print(f"Rule: {rule}")
        print(f"Component: {component}")
        print(f"Project: {project}")
        print(f"Line: {line}")
        print(f"Message: {message}")

        # Extract file path and line number
        file_name = component.split(':')[1]
        file_path_line = f"{file_name}:{text_range['startLine']}"
        print(f"File Path: {file_path_line}")

        # Prepare data for LLM request
        data_llm = {
            "messages": [
                {"role": "system", "content": "Help fix the code."},
                {"role": "user", "content": f"{issue}"}
            ],
        }

        # Send request to LLM API
        llm_response = send_to_llm(llm_url, create_headers(), data_llm)

        if llm_response:
            assistant_message = llm_response["choices"][0]["message"]["content"]
            print("\nResponse from Assistant:")
            print(assistant_message)
        print("\n")

# Main execution
def main():
    # Get authentication token
    auth = encode_authentication(login, password)

    # Create headers
    headers = create_headers(auth)

    # Define parameters for issue search
    payload_issues = {
        "types": "BUG",
        'componentKeys': "reactnative"
    }

    # Get the issues from the API
    issues_data = get_issues(url, headers, payload_issues)

    if issues_data:
        issues = issues_data.get('issues', [])
        if issues:
            process_issues(issues)
        else:
            print("No issues found.")
    else:
        print("Failed to fetch issues.")

if __name__ == "__main__":
    main()