import requests
import base64
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the API endpoint
API_URL = os.getenv("API_URL")

# Define login credentials for basic authentication
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

# Encode login credentials as a base64 string for Basic Authentication
def auth_encode_basic(login, password):
    return base64.b64encode(f"{login}:{password}".encode()).decode()

# Prepare headers for API requests
def api_create_headers(auth):
    return {
        "Authorization": f"Basic {auth}",
    }

# Create a new project in SonarQube
def sonar_create_project(api_url, headers, project_name):
    payload = {
        "name": project_name,
        "project": project_name,
        # "mainBranch": "develop",  # Optional: Uncomment if needed
        # "visibility": "private"  # Optional: Uncomment if needed
    }

    response = requests.post(api_url + "api/projects/create", headers=headers, params=payload)
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

    response = requests.post(api_url + "api/user_tokens/generate", headers=headers, params=payload)
    if response.status_code == 200:
        print("Token generated successfully!")
        response_json = response.json()
        response_parsed = {key: value for key, value in response_json.items() if key != 'token'}
        return response_parsed
    else:
        print(f"Failed to generate token. Status code: {response.status_code}")
        print(response.text)  # Debugging info
        return None

# Main execution function
def main():
    # Get authentication token
    auth = auth_encode_basic(LOGIN, PASSWORD)

    # Create headers
    headers = api_create_headers(auth)

    # Define project name
    project_name = "project_test"

    # Create project
    project_response = sonar_create_project(API_URL, headers, project_name)
    
    if project_response:
        # Generate project analysis token if project creation was successful
        token_response = sonar_generate_token(API_URL, headers, project_name)
        if token_response:
            print("Generated Token Info:", token_response)

if __name__ == "__main__":
    main()
