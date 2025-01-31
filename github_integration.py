import subprocess
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
NEW_REPO_NAME = "curriculum-be-golang"
LOCAL_PATH = os.getenv("LOCAL_PATH")
LOCAL_REPO_PATH = LOCAL_PATH + "github-api-test"
CLONE_REPO_URL = os.getenv("CLONE_REPO_URL")

# Fungsi untuk menjalankan perintah Git
def run_git_command(command, repo_path):
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(f"Success: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

# Fungsi untuk membuat repositori baru di GitHub
def create_github_repo(repo_name):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": False
    }
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully.")
        return response.json()["ssh_url"]
    else:
        raise Exception(f"Failed to create repository: {response.status_code} {response.text}")

def delete_github_repo(repo_name):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Repository '{repo_name}' deleted successfully.")
    else:
        raise Exception(f"Failed to delete repository: {response.status_code} {response.text}")

# Fungsi untuk menulis perubahan pada file
def modify_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

# Main function
def main():
    try:
        # 1. Clone repository
        run_git_command(["git", "clone", CLONE_REPO_URL], LOCAL_REPO_PATH)
        print(f"Cloned repository to {LOCAL_REPO_PATH}")

        # 2. Create new repository on GitHub
        new_repo_ssh_url = create_github_repo(NEW_REPO_NAME)
        print(f"New repository SSH URL: {new_repo_ssh_url}")

        # 3. Change repository origin
        run_git_command(["git", "remote", "remove", "origin"], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)
        run_git_command(["git", "remote", "add", "origin", f"https://github.com/{GITHUB_USERNAME}/{NEW_REPO_NAME}"], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)

        # 4. Push to the new repo
        run_git_command(["git", "push", "origin", "main"], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)
        print("Pushed changes to new repository")

        # 5. Make a new branch named "other_branch_test"
        new_branch_name = "other_branch_test"
        run_git_command(["git", "checkout", "-b", new_branch_name], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)

        # 6. Modify file in the cloned repository
        modify_file(os.path.join(LOCAL_REPO_PATH + "/" + NEW_REPO_NAME, "README.md"), "# New Change")
        print("Modified README.md")

        # 7. Add modified file to staging and commit
        run_git_command(["git", "add", "."], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)
        run_git_command(["git", "commit", "-m", "Initial commit for new branch"], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)

        # 7. Push the changes to new branch
        run_git_command(["git", "push", "-u", "origin", new_branch_name], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)

        # 6. Try pull request
        run_git_command(["git", "pull", "origin", new_branch_name], LOCAL_REPO_PATH + "/" + NEW_REPO_NAME)

        # 8. Delete the repo
        delete_github_repo(NEW_REPO_NAME)
        print(f"Repository {NEW_REPO_NAME} deleted succesfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
