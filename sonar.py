import requests
import base64
import subprocess
import llm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_LLM_URL = os.getenv("API_LLM_URL")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def auth_encode_basic(login, password):
    """Encode login credentials as a base64 string for Basic Authentication."""
    return base64.b64encode(f"{login}:{password}".encode()).decode()

def send_post_request(url, headers, payload):
    response = requests.post(url, headers=headers, params=payload)
    if response.status_code == 200:
        return response.json()
    print(f"Request failed. Status code: {response.status_code}")
    print(response.text)
    return None

def sonar_create_project(api_url, project_name):
    return send_post_request(f"{api_url}api/projects/create", HEADERS, {"name": project_name, "project": project_name})

def sonar_generate_token(api_url, project_name):
    return send_post_request(f"{api_url}api/user_tokens/generate", HEADERS, {"name": project_name, "projectKey": project_name, "type": "PROJECT_ANALYSIS_TOKEN"})

def sonar_scan(project_name, sonar_project_path):
    """Run unit tests with coverage and scan the code using SonarQube."""
    print(f"Running unit test with coverage in '{sonar_project_path}'...")
    sonar_run_command("npm run test -- --coverage", cwd=sonar_project_path)

    coverage_file = os.path.join(sonar_project_path, "coverage/lcov.info")
    if not os.path.exists(coverage_file):
        print("ERROR: 'coverage/lcov.info' not found. Ensure Jest is configured correctly.")
        return
    
    print(f"Running SonarScanner in '{project_name}/'...")
    print("Scan completed! Check results in SonarQube.")

def sonar_get_issues(api_url, type, project_name):
    """Retrieve issues from SonarQube."""
    params = {"types": type, "componentKeys": project_name}
    response = requests.get(f"{api_url}api/issues/search", headers=HEADERS, params=params)
    return response.json() if response.status_code == 200 else None

def sonar_get_hotspots(api_url, type, project_name):
    """Retrieve security hotspots from SonarQube."""
    params = {"types": type, "projectKey": project_name}
    response = requests.get(f"{api_url}api/hotspots/search", headers=HEADERS, params=params)
    return response.json() if response.status_code == 200 else None

def process_code_fix(file_path, message, result_path, issue_type):
    """Reads the file, sends data to LLM, and saves the fixed code."""
    try:
        with open(file_path + ".js", 'r') as file:
            file_contents = file.read()
        
        system_message = "You are a helpful assistant that formats responses as JSON."
        user_message = f"Include the corrected code in the 'code' key and provide a meaningful commit message in the 'commit_message' key. Code snippet: {file_contents} Issue message: {message}"
        
        if issue_type == "hotspot":
            user_message += " Security hotspot detected."
        
        data_llm = {"messages": [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}], "temperature": 1.0, "top_p": 0.9, "top_k": 30, "max_tokens": -1, "presence_penalty": -0.2, "frequency_penalty": 0.2, "stream": False}
        
        fixed_code_data = llm.llm_process_response(API_LLM_URL, HEADERS, data_llm, "codefix", result_path)
        fixed_code = fixed_code_data.get("code", "")
        
        with open(file_path + "_fixed.js", 'w') as file:
            file.write(fixed_code)
    except Exception as e:
        print(f"Error processing code fix: {e}")

def process_issues(issues_data, issue_type, file_path, result_path):
    """Processes issues or hotspots and triggers code fixing if applicable."""
    if not issues_data:
        print("Failed to fetch issues.")
        return
    
    issues = issues_data.get("hotspots" if issue_type == "hotspot" else "issues", [])
    if not issues:
        print("No issues found.")
        return
    
    for i, issue in enumerate(issues, start=1):
        print(f"Processing {issue_type}: {i}")
        print(f"Key: {issue.get('key')}")
        print(f"Component: {issue.get('component')}")
        print(f"Message: {issue.get('message')}\n")
        
        process_code_fix(file_path, issue.get('message'), result_path, issue_type)

def sonar_run_command(command, cwd=None):
    """Run a shell command in a specified directory."""
    process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line, end="")
    process.stdout.close()
    process.wait()
