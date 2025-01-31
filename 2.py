import requests
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# Define the API endpoint
url = os.getenv("API_URL")

# Define your login credentials for basic authentication
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")

# Encode the login credentials as a base64 string
auth = base64.b64encode(f"{login}:{password}".encode()).decode()

# Define the headers with basic authentication
headers = {
    "Authorization": f"Basic {auth}",
    # "Content-Type": "application/json"
}

# Define the payload with the required parameters
payload_create_project = {
    "name": "project_test",
    "project": "project_test",
    # "mainBranch": "develop",  # Optional: Uncomment and set if needed
    # "visibility": "private"  # Optional: Uncomment and set if needed
}

payload_generate_token = {
    "name": "project_test",
    "projectKey": "project_test",
    "type": "PROJECT_ANALYSIS_TOKEN",
}

# Send the POST request
response_create_project = requests.post(url + "api/projects/create", headers=headers, params=payload_create_project)

# Check the response status code
if response_create_project.status_code == 200:
    print("Project created successfully!")
    print(response_create_project.json())  # Print the response JSON if needed

    response_generate_token = requests.post(url + "api/user_tokens/generate", headers=headers, params=payload_generate_token)
    if response_generate_token.status_code == 200:
        print("Token generated successfully!")
        response_json = response_generate_token.json()
        response_parsed = {key: value for key, value in response_json.items() if key != 'token'}
        print(response_parsed)  # Print the response JSON if needed
    else:
        print(f"Failed to generate token. Status code: {response_generate_token.status_code}")
        print(response_generate_token.text)  # Print the response text for debugging

else:
    print(f"Failed to create project. Status code: {response_create_project.status_code}")
    print(response_create_project.text)  # Print the response text for debugging
