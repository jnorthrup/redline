# If necessary, install the openai Python library by running
# pip install openai

import os
from openai import OpenAI

# Retrieve the API key and base URL from environment variables
api_key = os.environ.get("HUGGINGFACE_API_KEY")
base_url = "https://rajr8mu889ikx6zh.us-east-1.aws.endpoints.huggingface.cloud/v1/"

# Check if the environment variable is set
if not api_key:
    raise ValueError(
        "Please set the HUGGINGFACE_API_KEY environment variable."
    )

client = OpenAI(base_url=base_url, api_key=api_key)

chat_completion = client.chat.completions.create(
    model="tgi",
    messages=[{"role": "user", "content": "I like you. I love you"}],
    stream=True,
)
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[{"role": "user", "content": user_input}],
        stream=True,
    )
    for message in chat_completion:
        print(message.choices[0].delta.content, end="", flush=True)
    print()

for message in chat_completion:
    print(message.choices[0].delta.content, end="", flush=True)
print()
