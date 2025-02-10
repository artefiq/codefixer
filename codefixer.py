import os
from dotenv import load_dotenv
import sonar, llm, git

# Load environment variables
load_dotenv()

project_name = "project_test"

# Define the variables from .env file
API_URL = os.getenv("API_URL")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
API_KEY = os.getenv("API_KEY")
API_LLM_URL = os.getenv("API_LLM_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
NEW_REPO_NAME = project_name
LOCAL_PATH = os.getenv("LOCAL_PATH")
LOCAL_REPO_PATH = LOCAL_PATH + project_name
CLONE_REPO_URL = os.getenv("CLONE_REPO_URL")
SONAR_PROJECT_PATH = os.path.abspath(project_name)

''' FUNCTIONS '''

# Prepare headers for the API requests
def api_create_headers(auth=None):
    headers = {
        "Authorization": f"Basic {auth}" if auth else f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    return headers

# Fungsi untuk menulis perubahan pada file
def file_modify(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

''' MAIN '''

def main():

# 1. Clone Repository
    
    # git.git_run_command(["git", "clone", CLONE_REPO_URL], LOCAL_REPO_PATH)

# 2. Authenticate with sonarqube, and create a new project, then generate a token

    # Get authentication token
    auth = sonar.auth_encode_basic(LOGIN, PASSWORD)

    # Create headers
    headers = api_create_headers(auth)

    # # Define project name

    # # Create project
    # project_response = sonar.sonar_create_project(API_URL, headers, project_name)
    
    # if project_response:
    #     # Generate project analysis token if project creation was successful
    #     token_response = sonar.sonar_generate_token(API_URL, headers, project_name)
    #     if token_response:
    #         print("Generated Token Info:", token_response)


# 3. Generate unit test for the code
    
    # Open the file in read mode
    file_path = LOCAL_PATH + f'codefixer/{project_name}/server.js'  # Replace with the path to your code file
    with open(file_path, 'r') as file:
        # Read the contents of the file
        file_contents = file.read()

    # Prepare data for LLM request
    data_llm = {
        "messages": [
            {"role": "system", "content": "give test unit for this code to be used in sonar-scanner, only give the test code as 'code', and 'commit_message' in a json with no extra data, path to my app file is ../server "},
            {"role": "user", "content": f"make it so i can get 100 percent code coverage in sonarqube " + f"{file_contents}"}
        ],

        "stream" : True
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
        ""
    }

    llm.llm_process_response(API_LLM_URL, headers, data_llm, "test_unit")

# 4. Scan the code with sonar-scanner

    print(f"1. Menjalankan unit test dengan coverage di '{SONAR_PROJECT_PATH}'...")
    sonar.sonar_run_command("npm run test -- --coverage", cwd=SONAR_PROJECT_PATH)

    # Pastikan file coverage/lcov.info ada
    coverage_file = os.path.join(SONAR_PROJECT_PATH, "coverage/lcov.info")
    if not os.path.exists(coverage_file):
        print("ERROR: File 'coverage/lcov.info' tidak ditemukan. Pastikan Jest dikonfigurasi dengan benar.")
        return

    print(f"\n2. Menjalankan SonarScanner di folder '{project_name}/'...")
    sonar.sonar_run_command("sonar-scanner", cwd=SONAR_PROJECT_PATH)

    print("\nScan selesai! Cek hasilnya di SonarQube.")

# 5. Search for issues in SonarQube using API

    # Get the issues from the API
    issues_data = sonar.sonar_get_issues(API_URL, headers, "CODE_SMELL", project_name)

# 6. Process issues and get responses from LLM API

    if issues_data:
        issues = issues_data.get('issues', [])
        if issues:
            for i, issue in enumerate(issues, start=1):
                # Extract issue details
                issue_key = issue['key']
                rule = issue['rule']
                component = issue['component']
                severity = issue['severity']
                project = issue['project']
                line = issue.get('line', 'N/A')
                text_range = issue.get('textRange', {})
                message = issue['message']
                
                # Extract file path and line number
                file_name = component.split(':')[1] if ':' in component else component
                file_path_line = f"{file_name}:{text_range.get('startLine', 'Unknown')}"

                # Print issue details
                print(f"Processing issue: {i}")
                print(f"Issue Key: {issue_key}")
                print(f"Rule: {rule}")
                print(f"Component: {component}")
                print(f"Severity: {severity}")
                print(f"Project: {project}")
                print(f"Line: {line}")
                print(f"Message: {message}")
                print(f"File Path: {file_path_line}\n")

                # Open the file in read mode
                file_path = LOCAL_PATH + 'codefixer/test_index'  # Replace with the path to your code file
                with open(file_path+".js", 'r') as file:
                    # Read the contents of the file
                    file_contents = file.read()

                # Prepare data for LLM request
                data_llm = {
                    "messages": [
                        {"role": "system", "content": "Help fix the code and give it in a json format as code (just give the fixed code, and keep it's functionallity), with commit message to github as commit_message. Follow the instruction and do not use any markdown"},
                        {"role": "user", "content": f"{issues} + {file_contents}"}
                    ],

                    "stream" : True
                }

                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                    ""
                }

                llm.llm_process_response(API_LLM_URL, headers, data_llm, "code_fix")

                # Save the fixed code
                # with open(file_path + "_fixed.js", 'w') as file:
                #     file.write(file_contents)

                print("\n")
        else:
            print("No issues found.")
    else:
        print("Failed to fetch issues.")

# 7. Create a new repository on GitHub

    # new_repo_ssh_url = github_create_repo(NEW_REPO_NAME)
    # print(f"New repository SSH URL: {new_repo_ssh_url}")

# 8. Clone the new repository

    # git_run_command(["git", "clone", CLONE_REPO_URL], LOCAL_REPO_PATH)
    # print(f"Cloned repository to {LOCAL_REPO_PATH}")

# 9. Modify the cloned repository with the generated issues

    # repo_dir = os.path.join(LOCAL_REPO_PATH, NEW_REPO_NAME)

    # component = issues['component']
    # file_name = component.split(':')[1] if ':' in component else component

    # file_modify(os.path.join(repo_dir, file_name), file_content)
    # print("Modified README.md")

# 10. Commit the changes to the repository



# 11. Push the changes to the remote repository



# 12. Delete the local repository

    

# 13. Delete the remote repository

    # github_delete_repo(NEW_REPO_NAME)
    # print(f"Repository {NEW_REPO_NAME} deleted successfully.")

if __name__ == "__main__":
    main()