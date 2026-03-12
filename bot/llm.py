from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY_LLM = os.getenv("API_KEY_LLM")
BASE_URL_LLM = os.getenv("BASE_URL_LLM", "https://api.artemox.com/v1")

client = OpenAI(
    api_key=API_KEY_LLM,
    base_url=BASE_URL_LLM
)


def extract_filters(query: str):

    tools = [{
        "type": "function",
        "function": {
            "name": "search_cars",
            "description": "Extract structured car search filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand": {"type": "string"},
                    "color": {"type": "string"},
                    "price_max": {"type": "integer"},
                    "year_min": {"type": "integer"}
                }
            }
        }
    }]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                    You extract car search filters.

                    The user may write in Russian or English.

                    Rules:
                    - Translate brands to English (e.g. "хонду" -> "Honda", "ниссан" -> "Nissan").
                    - Translate colors to English ("красную" -> "Red", "черную" -> "Black").
                    - Convert prices like "2 млн", "2000000", "2 million yen" to integer.
                    - Return ONLY valid filters for the function.
                    - If a filter is not present, omit it.

                    Examples:

                    "Найди хонду"
                    → brand: Honda

                    "Красную BMW до 2 млн"
                    → brand: BMW
                    → color: Red
                    → price_max: 2000000

                    "дешевую мазду поновее"
                    → brand: Mazda
                    """
            },
            {
                "role": "user",
                "content": query
            }
        ],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if not message.tool_calls:
        return {}

    args = message.tool_calls[0].function.arguments

    return json.loads(args)