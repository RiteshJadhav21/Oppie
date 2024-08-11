from flask import Flask, render_template, request, jsonify
import subprocess
import json
import logging

# Load AWS commands data
with open('aws_commands.json', 'r') as f:
    AWS_COMMANDS = json.load(f)

API_KEY = "XYZ"
AZURE_ENDPOINT = "https://chat-model.openai.azure.com/"
API_VERSION = "2024-02-01"
MODEL = "gpt-35-turbo-0613"

SYSTEM_MSG = (
    "Act as an AWS Engineer who is expert in creating AWS CLI Commands. "
    "Cross-reference your response with the provided AWS command list."
)

client = AzureOpenAI(api_key=API_KEY, azure_endpoint=AZURE_ENDPOINT, api_version=API_VERSION)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get", methods=["POST"])
def chat():
    user_message = request.form.get("msg")
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    logging.info(f"User message: {user_message}")
    response = get_chat_response(user_message)
    return jsonify({"response": response})

def get_chat_response(user_input):
    try:
        command = search_command_in_reference(user_input)
        if not command:
            command = generate_command_with_openai(user_input)

        output = execute_aws_command(command)
        human_readable_output = convert_output_to_human_readable(output)

        return human_readable_output

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return f"Error: {str(e)}"

def search_command_in_reference(user_input):
    for service, commands in AWS_COMMANDS.items():
        for command in commands:
            if service.lower() in user_input.lower():
                return command['command']
    return None

def generate_command_with_openai(user_input):
    result = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": user_input}
        ],
        model=MODEL
    )
    return result.choices[0].message.content.strip()

def execute_aws_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}, Error: {e.output.decode('utf-8')}")
        raise Exception(f"Command execution failed: {e.output.decode('utf-8')}")

def convert_output_to_human_readable(output):
    result = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"Convert this CLI output data into a human-readable format: {output}"}
        ],
        model=MODEL
    )
    return result.choices[0].message.content.strip()

if __name__ == '__main__':
    app.run(debug=True)