import requests
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the API endpoints and keys from environment variables
API_KEY = os.getenv("API_KEY")
API_LLM_URL = os.getenv("API_LLM_URL")
LOCAL_PATH = os.getenv("LOCAL_PATH")

def llm_send_request(llm_url, headers, data):
    data["stream"] = True  # Enable streaming if required by API

    try:
        with requests.post(llm_url, json=data, headers=headers, stream=True, timeout=100) as response:
            if response.status_code == 200:
                result = ""
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        try:
                            chunk_json = chunk.decode().strip()
                            if chunk_json:
                                if chunk_json.startswith('data:'):
                                    chunk_json = chunk_json[5:].strip()

                                try:
                                    chunk_data = json.loads(chunk_json)
                                    content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    print(content, end="", flush=True)
                                    result += content
                                except json.JSONDecodeError:
                                    print(f"Error: Received non-JSON chunk. Raw data: {chunk_json}")
                        except Exception as e:
                            print(f"Unexpected error while processing chunk: {e}")
                return result
            else:
                print(f"Failed to get response from LLM. Status code: {response.status_code}")
                print(response.text)
                return None
    except requests.exceptions.Timeout:
        print("Request timed out. Try increasing the timeout or optimizing the request.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return None

def llm_process_response(API_LLM_URL, headers, data_llm, mode):
    llm_response = llm_send_request(API_LLM_URL, headers, data_llm)

    if not llm_response:
        print("No valid response from LLM API.")
        return

    cleaned_response = llm_response.replace('```json', '').replace('```', '').strip()
    print("\nCleaned LLM response:\n", cleaned_response)

    try:
        cleaned_json = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        return

    json_object = extract_json_object(cleaned_json)
    if not json_object:
        print("Unexpected response format from LLM.")
        return

    if mode == "codefix":
        process_codefix(json_object)
    elif mode == "test_unit":
        process_test_unit(json_object)

def extract_json_object(cleaned_json):
    if isinstance(cleaned_json, dict) and "choices" in cleaned_json:
        choices = cleaned_json.get("choices", [])
        if choices and isinstance(choices[0], dict):
            content_string = choices[0].get("delta", {}).get("content", "").strip()
            json_match = re.search(r'```json\n(.*?)\n```', content_string, re.DOTALL)
            json_object_str = json_match.group(1).strip() if json_match else content_string

            try:
                return json.loads(json_object_str)
            except json.JSONDecodeError:
                print("Failed to parse extracted JSON.")
                return None
    elif isinstance(cleaned_json, dict) and "code" in cleaned_json and "commit_message" in cleaned_json:
        return cleaned_json
    
    return None

def process_codefix(json_object):
    file_data = json_object.get('code', '')
    commit_message = json_object.get('commit_message', '')

    print("\nFixed Code:\n", file_data)
    print("Commit Message:\n", commit_message)

def process_test_unit(json_object):
    filename = "project_test/__tests__/server.test.js"
    code = json_object.get("code", "")

    if code:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            file.write(code)
        print(f"Code saved to {filename}")
    else:
        print("No code found in JSON.")
