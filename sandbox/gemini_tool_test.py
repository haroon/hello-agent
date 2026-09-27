from datetime import datetime
from google import genai
from google.genai import types

def get_prompt():
    prompts = ["What time is it?", "How is the weather in Lahore, Pakistan?", "What is 60 + 7?"]

    print("Please choose a prompt:")
    for i, prompt in enumerate(prompts, start=1):
        print(f"{i}. {prompt}")

    selection = "What is the meaning of life?"
    while True:
        choice = input("Enter 1, 2, 3 or (q)uit ")

        if choice in ("1", "2", "3"):
            selection = prompts[int(choice) - 1]
            break
        elif choice.toLower() == 'q':
            break
        print("Invalid choice. Please enter 1, 2, 3 or (q)uit")
    return selection

def get_system_time():
    return datetime.now().astimezone().isoformat()

def get_weather(city: str):
    return f"Weather for {city}: Sunny"

def calculate_sum(a: int, b: int):
    return a + b

functions = {
    "get_system_time": get_system_time,
    "get_weather": get_weather,
    "calculate_sum": calculate_sum,
}

client = genai.Client()

tool = types.Tool(
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
    ]
)

config = types.GenerateContentConfig(
    tools=[tool],
)

prompt = get_prompt()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt,
    config=config,
)

for part in response.candidates[0].content.parts:
    if part.function_call:
        f_call = part.function_call
        f_name = f_call.name
        f_args = f_call.args

        print(f'calling {f_name} with args {f_args}...')

        function = functions.get(f_name)
        if function is None:
            raise ValueError(f"Unknown function: {f_name}")

        result = function(**f_args)

        f_response = types.Part.from_function_response(
            name=f_name,
            response={"result": result},
        )

        contents = [
            prompt,
            response.candidates[0].content,
            types.Content(
                role="user",
                parts=[f_response],
            ),
        ]

        final_response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,
            config=config,
        )

        print(final_response.text)
        break
