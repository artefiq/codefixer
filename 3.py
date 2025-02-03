import requests
import base64
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the API endpoints and keys from environment variables
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
API_LLM_URL = os.getenv("API_LLM_URL")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

# Encode login credentials for Basic Authentication
def auth_encode_basic(login, password):
    auth = base64.b64encode(f"{login}:{password}".encode()).decode()
    return auth

# Prepare headers for the API requests
def api_create_headers(auth=None):
    headers = {
        "Authorization": f"Basic {auth}" if auth else f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    return headers

# Send GET request to search for issues
def sonar_get_issues(api_url, headers, params):
    response = requests.get(api_url + "api/issues/search", headers=headers, params=params)
    if response.status_code == 200:
        print("Issues searched successfully!")
        return response.json()
    else:
        print(f"Failed to search issues. Status code: {response.status_code}")
        print(response.text)  # For debugging
        return None

# Send POST request to LLM API for processing
def llm_send_request(llm_url, headers, data):
    response = requests.post(llm_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get response from LLM. Status code: {response.status_code}")
        print(response.text)  # For debugging
        return None

# Process issues and get responses
def process_sonar_issues(issues):
    for i, issue in enumerate(issues, start=1):
        print(f"Processing issue: {i}")

        # Extract issue details
        issue_key = issue['key']
        rule = issue['rule']
        component = issue['component']
        severity = issue['severity']
        project = issue['project']
        line = issue.get('line', 'N/A')
        text_range = issue.get('textRange', {})
        message = issue['message']

        # Print issue details
        print(f"Issue Key: {issue_key}")
        print(f"Rule: {rule}")
        print(f"Component: {component}")
        print(f"Project: {project}")
        print(f"Line: {line}")
        print(f"Message: {message}")

        # Extract file path and line number
        file_name = component.split(':')[1] if ':' in component else component
        file_path_line = f"{file_name}:{text_range.get('startLine', 'Unknown')}"
        print(f"File Path: {file_path_line}")

        # Prepare data for LLM request
        data_llm = {
            "messages": [
                {"role": "system", "content": "Help fix the code."},
                {"role": "user", "content": f"{issue}"}
            ],
        }

        # Send request to LLM API
        llm_response = llm_send_request(API_LLM_URL, api_create_headers(), data_llm)

        if llm_response:
            assistant_message = llm_response["choices"][0]["message"]["content"]
            print("\nResponse from Assistant:")
            print(assistant_message)
        print("\n")

# Main execution
def main():
    # Get authentication token
    auth = auth_encode_basic(LOGIN, PASSWORD)

    # Create headers
    headers = api_create_headers(auth)

    # Define parameters for issue search
    payload_issues = {
        "types": "BUG",
        'componentKeys': "reactnative"
    }

    # Get the issues from the API
    issues_data = sonar_get_issues(API_URL, headers, payload_issues)

    if issues_data:
        issues = issues_data.get('issues', [])
        if issues:
            process_sonar_issues(issues)
        else:
            print("No issues found.")
    else:
        print("Failed to fetch issues.")

if __name__ == "__main__":
    main()
