from datetime import datetime
from google import genai

def get_system_time():
    return datetime.now().astimezone().isoformat()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="What time is it?",
    config={
        "tools": [get_system_time],
    },
)
print(response.text)
