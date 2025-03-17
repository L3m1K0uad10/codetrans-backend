import requests
import json

# File path (you can dynamically fetch the path of the opened file in your code editor)
file_path = "/Users/apple/Documents/projects/codetrans-backend/ide/code2.py"

# Read the content of the program file
with open(file_path, 'r') as file:
    file_content = file.read()

# Backend URL (change to your backend endpoint)
endpoint = "http://127.0.0.1:8000/processing/translate/"

# Send the program file content as JSON
data = {
    "file_name": "code.py",  # You can send metadata, like the file name
    "language": "python",  # If you want to send the programming language or other info
    "file_content": file_content,
    "level": "Partial"
}

# Send POST request with the content as JSON
response = requests.post(endpoint, json = data)

# Handle the response
if response.status_code == 200:
    print("File content sent successfully!")
    #print(json.dumps(response.json(), indent = 4))
    data = response.json()
    print(data["translated_code"])
else:
    print("Failed to send content. Status code: ", response.status_code)
