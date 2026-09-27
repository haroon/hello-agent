from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain what an AI agent is in one paragraph"
)

print(response.text)

