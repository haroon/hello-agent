from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Explain what an AI agent is in one paragraph."
)

print(response.output_text)

