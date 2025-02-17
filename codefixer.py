import os
from dotenv import load_dotenv
import sonar, llm, git, sys, jest

# Load environment variables
load_dotenv()

# Project configuration
project_name = "project_test"

# Load credentials and API URLs from .env file
API_URL = os.getenv("API_URL")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
NEW_REPO_NAME = project_name
LOCAL_PATH = os.getenv("LOCAL_PATH")
LOCAL_REPO_PATH = os.path.join(LOCAL_PATH, project_name)
CLONE_REPO_URL = os.getenv("CLONE_REPO_URL")
SONAR_PROJECT_PATH = os.path.abspath(project_name)

# Nilai default
DEFAULTS = {
    "unit_test": 0,
    "jest": 0,
    "jest_retest": 0,
    "sonar_create": 0,
    "sonar_scan": 0,
    "sonar_hotspot": 0,
    "sonar_issue": 0,
    "log": 0,
    "llm_model": "dev",
}

def help_message(args):
    if (args == DEFAULTS):
        print("Penggunaan: python codefixer.py [options]")
        print("Opsi yang dapat diterapkan:")
        for key, value in DEFAULTS.items():
            if (key != "llm_model"):
                print(f"    {key}=0/1 (default={value})")
            else:
                print(f"    {key}=dev/openai (default={value})")

def parse_args():
    args = DEFAULTS.copy()
    
    for arg in sys.argv[1:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
            if key in args:
                if key in ["unit_test", "jest", "jest_retest", "sonar_create", "sonar_scan", "sonar_hotspot", "sonar_issue", "log"]:
                    try:
                        args[key] = int(value)
                    except ValueError:
                        print(f"Peringatan: '{key}' harus berupa angka! Menggunakan default {args[key]}.")
                else:
                    args[key] = value

    return args

# Function to prepare headers for API requests
def api_create_headers(auth=None):
    return {
        "Authorization": f"Basic {auth}" if auth else f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

# Function to modify file content
def file_modify(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)

# Main execution function
def main():
    args = parse_args() # Initiallize arguments key=value variable

    help_message(args) # Print help message if no options is chosen

    # Change LLM URL if necessary
    if (args['llm_model'] == "openai"):
        API_LLM_URL = os.getenv("API_LLM_URL_2")
        API_KEY = os.getenv("API_KEY_2")
    elif (args['llm_model'] == "dev"):
        API_LLM_URL = os.getenv("API_LLM_URL")
        API_KEY = os.getenv("API_KEY")

    # # Step 1: Clone Repository
    # git.git_run_command(["git", "clone", CLONE_REPO_URL], LOCAL_REPO_PATH)
    
    # Step 2: Authenticate with SonarQube and create a new project
    auth = sonar.auth_encode_basic(LOGIN, PASSWORD)
    headers = api_create_headers(auth)
    
    if (args['sonar_create'] == 1):
        # Create SonarQube project
        project_response = sonar.sonar_create_project(API_URL, headers, project_name)
        
        if project_response:
            # Generate project analysis token if project creation was successful
            token_response = sonar.sonar_generate_token(API_URL, headers, project_name)
            if token_response:
                print("Generated Token Info:", token_response)
    
    # Step 3: Generate unit tests for the project
    if (args['unit_test'] == 1): llm.generate_test_unit(API_LLM_URL, API_KEY, args['llm_model'], project_name)

    # Step 4: Scan the project code with SonarQube
    jest_result = None
    if (args['jest'] == 1 or args['jest_retest'] == 1): 
        jest_result = sonar.sonar_run_command("npm run test -- --coverage", cwd=SONAR_PROJECT_PATH)
        
        if (jest_result and args['jest_retest'] == 1): 
            jest.re_test(API_LLM_URL, API_KEY, args['llm_model'], jest_result)
            jest_result = sonar.sonar_run_command("npm run test -- --coverage", cwd=SONAR_PROJECT_PATH)

    if (args['sonar_scan'] == 1): sonar.sonar_run_command("sonar-scanner", cwd=SONAR_PROJECT_PATH)

    # Step 5: Retrieve and process issues and hotspots from SonarQube, then fix it using LLM API
    if (args['sonar_hotspot'] == 1):
        hotspots_data = sonar.sonar_get_hotspots(API_URL, headers, "", project_name)
        sonar.process_issues(API_LLM_URL, API_KEY, args['llm_model'], hotspots_data, "hotspot", os.path.join(LOCAL_PATH, 'codefixer/project_test/server'), result_path=os.path.join(LOCAL_PATH, f"codefixer/{project_name}"))
    
    if (args['sonar_issue'] == 1):
        issues_data = sonar.sonar_get_issues(API_URL, headers, "BUG", "reactnative")
        sonar.process_issues(API_LLM_URL, API_KEY, args['llm_model'], issues_data, "issue", os.path.join(LOCAL_PATH, 'codefixer/test_index'), result_path=os.path.join(LOCAL_PATH, "codefixer/"))
    
    # # Step 7: Create a new repository on GitHub
    # new_repo_ssh_url = git.github_create_repo(NEW_REPO_NAME)
    # print(f"New repository SSH URL: {new_repo_ssh_url}")
    
    # # Step 8: Clone the new repository
    # git.git_run_command(["git", "clone", CLONE_REPO_URL], LOCAL_REPO_PATH)
    # print(f"Cloned repository to {LOCAL_REPO_PATH}")

    # # Step 9. Commit the changes to the repository


    # # Step 10. Push the changes to the remote repository


    # # Step 11. Delete the local repository

if __name__ == "__main__":
    main()

'''
    [17/02/25]
    [v] 1. output jest diambil sebagai array string, dikirim hanya baris yang dilaporkan jest (belum tercover unit test)

    [14/02/25]
    [v] 1. output jest diambil sebagai array string, dikirim hanya baris yang dilaporkan jest (belum tercover unit test)
    [v] 2. help untuk args saat run kode
    [v] 3. implement api model llm baru, agar dapat memilih llm

    [13/02/25]
    [v] 1. bersihkan komen kode dari codefixer (dicopy dulu ke file backup)
    [v] 2. pakai env di depan python agar tidak banyak mengubah kode saat testing
            contoh saat running:  
                llm=0 sonar=0 log=0 llm_model=dev/openai python codefixer.py
    [v] 3. log output dibuat minimal (yang penting aja)
                contoh log default -> nama_file take n.second
    [v] 4. .env ditambahkan untuk support beberapa llm
    [v] 5. bisa pilih llm apa yang dipake (no 2)    
'''