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
def git_run_command(command, repo_path):
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
def github_create_repo(repo_name):
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

def github_delete_repo(repo_name):
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
def file_modify(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

# Main function
def main():
    try:
        # 1. Clone repository
        git_run_command(["git", "clone", CLONE_REPO_URL], LOCAL_REPO_PATH)
        print(f"Cloned repository to {LOCAL_REPO_PATH}")

        # 2. Create new repository on GitHub
        new_repo_ssh_url = github_create_repo(NEW_REPO_NAME)
        print(f"New repository SSH URL: {new_repo_ssh_url}")

        # 3. Change repository origin
        repo_dir = os.path.join(LOCAL_REPO_PATH, NEW_REPO_NAME)
        git_run_command(["git", "remote", "remove", "origin"], repo_dir)
        git_run_command(["git", "remote", "add", "origin", f"https://github.com/{GITHUB_USERNAME}/{NEW_REPO_NAME}"], repo_dir)

        # 4. Push to the new repo
        git_run_command(["git", "push", "origin", "main"], repo_dir)
        print("Pushed changes to new repository")

        # 5. Make a new branch named "other_branch_test"
        new_branch_name = "other_branch_test"
        git_run_command(["git", "checkout", "-b", new_branch_name], repo_dir)

        # 6. Modify file in the cloned repository
        file_modify(os.path.join(repo_dir, "README.md"), "# New Change")
        print("Modified README.md")

        # 7. Add modified file to staging and commit
        git_run_command(["git", "add", "."], repo_dir)
        git_run_command(["git", "commit", "-m", "Initial commit for new branch"], repo_dir)

        # 8. Push the changes to new branch
        git_run_command(["git", "push", "-u", "origin", new_branch_name], repo_dir)

        # 9. Try pull request
        git_run_command(["git", "pull", "origin", new_branch_name], repo_dir)

        # 10. Delete the repo
        github_delete_repo(NEW_REPO_NAME)
        print(f"Repository {NEW_REPO_NAME} deleted successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
