import os
from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain how the U.S. legal system works."}
    ],
    temperature=0.7,
    max_tokens=500
)

