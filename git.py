import os
import subprocess
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the variables from .env file
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
LOCAL_PATH = os.getenv("LOCAL_PATH")
CLONE_REPO_URL = os.getenv("CLONE_REPO_URL")

NEW_REPO_NAME = "curriculum-be-golang"
LOCAL_REPO_PATH = os.path.join(LOCAL_PATH, "github-api-test")

# Common headers for GitHub API requests
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Helper function to run Git commands
def git_run_command(command, repo_path):
    try:
        result = subprocess.run(
            command, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            text=True, check=True
        )
        print(f"Success: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}")

# Function to create a new GitHub repository
def github_create_repo(repo_name):
    response = requests.post("https://api.github.com/user/repos", headers=HEADERS, json={"name": repo_name, "private": False})
    
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully.")
        return response.json().get("ssh_url")
    
    raise Exception(f"Failed to create repository: {response.status_code} {response.text}")

# Function to delete a GitHub repository
def github_delete_repo(repo_name):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    response = requests.delete(url, headers=HEADERS)
    
    if response.status_code == 204:
        print(f"Repository '{repo_name}' deleted successfully.")
    else:
        raise Exception(f"Failed to delete repository: {response.status_code} {response.text}")
