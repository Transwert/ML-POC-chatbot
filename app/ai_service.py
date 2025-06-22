import os
from openai import OpenAI
from dotenv import load_dotenv
import ollama  # make sure you have this installed

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )

    def detect_intent(self, user_input: str) -> dict:
        system_prompt = """
You are an AI assistant that classifies user input into one or more of the following intents:
1. AUDIO_GENERATION: When the user wants to convert text or content to audio.
2. SQL_QUERY: When the user wants to run a SQL query or asks for a database-related operation.
3. DATA_GENERATION: When the user wants to generate charts, visuals, or insights from data.

Return result in JSON with this schema:
{
  "intent": {
    "AUDIO_GENERATION": Boolean,
    "SQL_QUERY": [Boolean, "Optional SQL string"],
    "DATA_GENERATION": "Optional string describing chart or data insight"
  }
}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3
            )
            return eval(response.choices[0].message.content)
        except Exception as e:
            print(f"Intent detection error: {e}")
            return {
                "intent": {
                    "AUDIO_GENERATION": False,
                    "SQL_QUERY": [False, ""],
                    "DATA_GENERATION": ""
                }
            }
    def generate_sql_query(self, natural_language_prompt: str) -> str:
        """
        Uses local OLLAMA model (sqlcoder2) to convert a natural language question into SQL.
        """
        try:
            response = ollama.chat(
                model='pxlksr/defog_sqlcoder-7b-2:F16',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a SQL expert who writes syntactically correct SQL queries for sqlite.'
                    },
                    {
                        'role': 'user',
                        'content': natural_language_prompt
                    }
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"SQL generation error: {e}")
            return "ERROR: Failed to generate SQL."
