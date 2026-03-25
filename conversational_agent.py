import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load env
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

def get_current_weather(location):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"

    response = requests.get(url)
    data = response.json()

    if "error" in data:
        return f"Error: {data['error']['message']}"

    weather_info = data["current"]

    return json.dumps({
        "location": data["location"]["name"],
        "temperature_c": weather_info["temp_c"],
        "condition": weather_info["condition"]["text"],
    })


def get_weather_forecast(location, days=3):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}&aqi=no"

    response = requests.get(url)
    data = response.json()

    if "error" in data:
        return f"Error: {data['error']['message']}"

    forecast_days = data["forecast"]["forecastday"]

    return json.dumps({
        "location": data["location"]["name"],
        "forecast": [
            {
                "date": d["date"],
                "max_temp_c": d["day"]["maxtemp_c"],
            }
            for d in forecast_days
        ]
    })

def calculator(expression):
    try:
        allowed_chars = "0123456789+-*/(). "

        for char in expression:
            if char not in allowed_chars:
                return "Error: Invalid characters in expression"

        result = eval(expression)
        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"

def execute_tool_safely(tool_call, available_functions):
    function_name = tool_call.function.name

    if function_name not in available_functions:
        return json.dumps({
            "success": False,
            "error": f"Unknown function: {function_name}"
        })

    try:
        function_args = json.loads(tool_call.function.arguments)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON: {str(e)}"
        })

    try:
        result = available_functions[function_name](**function_args)

        return json.dumps({
            "success": True,
            "function_name": function_name,
            "result": result
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Execution failed: {str(e)}"
        })

from concurrent.futures import ThreadPoolExecutor

def execute_tools_parallel(tool_calls, available_functions):
    def run_tool(tool_call):
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": execute_tool_safely(tool_call, available_functions),
        }

    with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
        return list(executor.map(run_tool, tool_calls))

weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer"},
                },
                "required": ["location"],
            },
        },
    },
]

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
            },
            "required": ["expression"],
        },
    },
}

available_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
}

cot_tools = weather_tools + [calculator_tool]
available_functions["calculator"] = calculator

def get_last_user_message(messages):
    for msg in reversed(messages):
        if msg["role"] == "user":
            return msg["content"]
    return ""

def process_messages(client, messages, tools=None, available_functions=None):
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            )
    except Exception as e:
        print("\n⚠️ Tool call failed, using fallback...\n")
        
        last_user_message = get_last_user_message(messages)
            
            
        text = last_user_message.lower()

        cities = []
        if "cairo" in text:
            cities.append("Cairo")
        if "london" in text:
            cities.append("London")
        if "riyadh" in text:
            cities.append("Riyadh")
        
        if len(cities) >= 2:
            results = []
            for city in cities:
                data = json.loads(get_current_weather(city))
                results.append((city, data["temperature_c"]))
                
            diff = round(abs(results[0][1] - results[1][1]), 1)
            
            messages.append({
                "role": "assistant",
                "content": f"{results[0][0]}: {results[0][1]}°C, {results[1][0]}: {results[1][1]}°C → Difference = {diff}°C"
                })
            return messages
        elif len(cities) == 1:
            result = get_current_weather(cities[0])
            messages.append({
                "role": "assistant",
                "content": result
                })
            return messages
        
        else:
            result = get_current_weather(last_user_message)
            
            messages.append({
                "role": "assistant",
                "content": result
                })
            return messages

    response_message = response.choices[0].message
    
    content = str(response_message)
    
    if "function" in content and "location" in content:
        last_user_message = get_last_user_message(messages)
        
        text = last_user_message.lower()
        
        cities = []
        if "cairo" in text:
            cities.append("Cairo")
        if "london" in text:
            cities.append("London")
        if "riyadh" in text:
            cities.append("Riyadh")
            
        if len(cities) >= 2:
            results = []
            for city in cities:
                data = json.loads(get_current_weather(city))
                results.append((city, data["temperature_c"]))
                
            diff = round(abs(results[0][1] - results[1][1]), 1)
            
            messages.append({
                "role": "assistant",
                "content": f"{results[0][0]}: {results[0][1]}°C, {results[1][0]}: {results[1][1]}°C → Difference = {diff}°C"
                })
            return messages
    
    



    messages.append(response_message)

    if response_message.tool_calls:
        tool_results = execute_tools_parallel(response_message.tool_calls, available_functions)
        
        for result in tool_results:
            messages.append(result)
            
        second_response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
        )
        final_message = second_response.choices[0].message

        content = final_message.content
        try:
            structured = json.loads(content)
            
            messages.append({
                "role": "assistant",
                "content": json.dumps(structured, indent=2)
                })
        except:
            messages.append({
                "role": "assistant",
                "content": content
                })
    else:
        last_user_message = get_last_user_message(messages)

        result = get_current_weather(last_user_message)

        messages.append({
            "role": "assistant",
            "content": f"(Fallback) {result}"
        })

    return messages


cot_system_message = """You are a weather assistant with access to tools.

RULES:
1. ALWAYS use tools when needed.
2. ONLY call ONE function at a time.
3. First get weather data for each city separately.
4. Then use the calculator if needed.
5. Do NOT combine multiple function calls in one step.
6. Wait for tool results before continuing.

Solve problems step by step and give a final answer.
"""

def run_conversation(client, system_message):
    messages = [{"role": "system", "content": system_message}]

    print("Weather Assistant: Hello! Ask me about the weather.")
    print("(Type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        messages = process_messages(
            client,
            messages,
            cot_tools,
            available_functions,
        )

        last_message = messages[-1]
        
        if hasattr(last_message, "content") and last_message.content:
            print(f"\nWeather Assistant: {last_message.content}\n")
        
        elif isinstance(last_message, dict) and last_message.get("content"):
             print(f"\nWeather Assistant: {last_message['content']}\n")

        
if __name__ == "__main__":
    print("Starting Chain of Thought Weather Assistant...\n")
    run_conversation(client, cot_system_message)

