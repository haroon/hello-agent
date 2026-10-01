import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
model = os.getenv("GEMINI_MODEL")

def get_prompt():
    return input("Hello. How can I help you? ")

def get_system_time():
    return datetime.now().astimezone().isoformat()

def get_weather(city: str):
    return f"Weather for {city}: Sunny"

def calculate_sum(a: int, b: int):
    return a + b

def stop_running():
    return False

functions = {
    "get_system_time": get_system_time,
    "get_weather": get_weather,
    "calculate_sum": calculate_sum,
    "stop_running": stop_running,
}


def process_prompt(parts):
    f_responses = []
    for part in parts:
        if not part.function_call:
            continue

        f_call = part.function_call
        f_name = f_call.name
        f_args = f_call.args

        print(f'calling {f_name} with args {f_args}...')

        if f_name == "stop_running":
            return False, f_responses

        function = functions.get(f_name)
        if function is None:
            raise ValueError(f"Unknown function: {f_name}")

        result = function(**f_args)

        f_responses.append(types.Part.from_function_response(
            name=f_name,
            response={"result": result}
        ))
    return True, f_responses

def main():

    client = genai.Client()

    tools = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_system_time",
                description="Get the current date and time of the computer running this program.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                ),
            ),
            types.FunctionDeclaration(
                name="get_weather",
                description="Get the weather for a city.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "city": types.Schema(type="STRING"),
                    },
                    required=["city"],
                ),
            ),
            types.FunctionDeclaration(
                name="calculate_sum",
                description="Calculate the sum of two numbers.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "a": types.Schema(type="INTEGER"),
                        "b": types.Schema(type="INTEGER"),
                    },
                    required=["a", "b"],
                ),
            ),
            types.FunctionDeclaration(
                name="stop_running",
                description="Stops the execution of the program.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                ),
            )
        ]
    )

    config = types.GenerateContentConfig(
        tools=[tools],
    )


    while True:
        prompt = get_prompt()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        should_continue, responses = process_prompt(response.candidates[0].content.parts)

        if not should_continue:
            break

        contents = [
            prompt,
            response.candidates[0].content,
            types.Content(
                role="user",
                parts=responses,
            ),
        ]

        final_response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        print(final_response.text)

if __name__ == "__main__":
    main()