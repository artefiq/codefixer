import requests
import base64
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Encode login credentials as a base64 string for Basic Authentication
def auth_encode_basic(login, password):
    credentials = f"{login}:{password}"
    return base64.b64encode(credentials.encode()).decode()

# Create a new project in SonarQube
def sonar_create_project(api_url, headers, project_name):
    payload = {"name": project_name, "project": project_name}

    response = requests.post(f"{api_url}api/projects/create", headers=headers, params=payload)
    if response.status_code == 200:
        print("Project created successfully!")
        return response.json()
    else:
        print(f"Failed to create project. Status code: {response.status_code}")
        print(response.text)  # Debugging info
    return None

# Generate an analysis token for the project
def sonar_generate_token(api_url, headers, project_name):
    payload = {
        "name": project_name,
        "projectKey": project_name,
        "type": "PROJECT_ANALYSIS_TOKEN",
    }

    response = requests.post(f"{api_url}api/user_tokens/generate", headers=headers, params=payload)
    if response.status_code == 200:
        print("Token generated successfully!")
        response_json = response.json()
        return {key: value for key, value in response_json.items() if key != 'token'}
    else:
        print(f"Failed to generate token. Status code: {response.status_code}")
        print(response.text)  # Debugging info
    return None

# Send GET request to search for issues
def sonar_get_issues(api_url, headers, type, project_name):
    params = {
        "types": f"{type}", # change the issue type
        'componentKeys': f"{project_name}" # change with project name
    }

    response = requests.get(f"{api_url}api/issues/search", headers=headers, params=params)
    if response.status_code == 200:
        print("Issues searched successfully!\n")
        return response.json()
    else:
        print(f"Failed to search issues. Status code: {response.status_code}")
        print(response.text)  # For debugging info
    return None

# Process issues and get responses
def sonar_process_issues(issues):
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
        print(f"Severity: {severity}")
        print(f"Project: {project}")
        print(f"Line: {line}")
        print(f"Message: {message}")

        # Extract file path and line number
        file_name = component.split(':')[1] if ':' in component else component
        file_path_line = f"{file_name}:{text_range.get('startLine', 'Unknown')}"
        print(f"File Path: {file_path_line}\n")

def sonar_run_command(command, cwd=None):
    """Jalankan perintah shell dalam folder tertentu."""
    process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        print(line, end="")

    process.stdout.close()
    process.wait()