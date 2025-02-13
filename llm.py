import os
import json
import re
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the API endpoints and keys from environment variables
API_KEY = os.getenv("API_KEY")
API_LLM_URL = os.getenv("API_LLM_URL")
LOCAL_PATH = os.getenv("LOCAL_PATH")

# Common headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_js_files(directory):
    return [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.js')]

def llm_send_request(llm_url, data):
    data["stream"] = True
    try:
        with requests.post(llm_url, json=data, headers=HEADERS, stream=True, timeout=100) as response:
            if response.status_code == 200:
                result, start_time = "", time.time()
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        try:
                            chunk_json = chunk.decode().strip()
                            if chunk_json.startswith('data:'):
                                chunk_json = chunk_json[5:].strip()
                            chunk_data = json.loads(chunk_json)
                            result += chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        except (json.JSONDecodeError, Exception) as e:
                            print(f"Error processing chunk: {e}")
                print(f"Execution Time: {time.time() - start_time:.6f} seconds")
                return result
            print(f"Failed LLM response. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    return None

def llm_process_response(data_llm, mode, result_path):
    response = llm_send_request(API_LLM_URL, data_llm)
    if not response:
        print("No valid response from LLM API.")
        return
    try:
        cleaned_json = json.loads(response.replace('```json', '').replace('```', '').strip())
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return
    json_object = extract_json_object(cleaned_json)
    if not json_object:
        print("Unexpected response format.")
        return
    process_response(json_object, mode, result_path)

def extract_json_object(cleaned_json):
    if isinstance(cleaned_json, dict):
        if "choices" in cleaned_json:
            content = cleaned_json["choices"][0].get("delta", {}).get("content", "").strip()
            match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            return json.loads(match.group(1).strip() if match else content)
        elif "code" in cleaned_json and "commit_message" in cleaned_json:
            return cleaned_json
    return None

def process_response(json_object, mode, result_path):
    if mode == "codefix":
        print("\nFixed Code:\n", json_object.get('code', ''))
        print("Commit Message:\n", json_object.get('commit_message', ''))
    elif mode == "test_unit":
        code = json_object.get("code", "")
        if code:
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            with open(result_path, "w", encoding="utf-8") as file:
                file.write(code)
            print(f"Code saved to {result_path}")
        else:
            print("No code found in JSON.")

def generate_test_unit(project_name):
    js_files = get_js_files(os.path.join(LOCAL_PATH, f'codefixer/{project_name}/app'))
    js_files.append(os.path.join(LOCAL_PATH, f'codefixer/{project_name}/server.js'))
    for file_path in js_files:
        relative_path = os.path.relpath(file_path, '/home/Artefiq/code/telkom/codefixer/project_test')
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        result_path = os.path.join(LOCAL_PATH, f'codefixer/{project_name}/__tests__/{file_name}.test.js')
        with open(file_path, 'r') as file:
            file_contents = file.read()
        data_llm = {
            "messages": [
                {"role": "system", "content": f"Generate unit tests for {file_name} using Jest & Supertest for SonarQube."},
                {"role": "user", "content": f"Ensure 100% coverage: {file_contents}"}
            ],
            "model": "deepseek",
            "stream": True
        }
        llm_process_response(data_llm, "test_unit", result_path)
