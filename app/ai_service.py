import os
from openai import OpenAI
from dotenv import load_dotenv
import ollama
from constants import SCHEMA_PROMPT, DETECT_INTENT_PROMPT, TABLE_SELECTION_PROMPT

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )

    def detect_intent(
            self,
            user_input: str, 
            system_prompt: str = DETECT_INTENT_PROMPT
            ) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
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
                    "GRAPHIC_GENERATIONS": ""
                }
            }
    
    def _table_selections(
            self, 
            nl_sql_prompt: str,
            table_selection_prompt: str = TABLE_SELECTION_PROMPT,
            full_schema: str = SCHEMA_PROMPT) -> list:
        """
        Given a natural language SQL prompt and the full DB schema, return relevant tables and their DDL statements.
        Uses OpenAI GPT model for inference.
        """
        system_prompt = table_selection_prompt + full_schema

        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": nl_sql_prompt}
                ],
                temperature=0.2
            )
            print(response, "#!@#!@#!@#!")
            content = response.choices[0].message.content
            return eval(content)  # or use json.loads() if strict JSON is enforced
        except Exception as e:
            print(f"Table extraction error: {e}")
            return []


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
                        'content': 'You are a SQL expert who writes syntactically correct SQL queries for sqlite.'+
                        f'Use following Schema for reference: {self._table_selections(nl_sql_prompt=natural_language_prompt)}'
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
    
    def generate_audio (self, user_input) -> dict:
        pass

    def generate_graphics (self, user_input) -> dict:
        pass

    def orchestrator(self, user_input: str) -> dict:
        """
        Orchestrates the intent detection and appropriate response generation.
        """
        try:
            # Step 1: Detect user intent
            intent_result = self.detect_intent(user_input)
            intent_data = intent_result.get("intent", {})

            # Step 2: Initialize response
            response = {"intent": intent_data, "output": None}

            # Step 3: Route to appropriate generation method
            if intent_data.get("SQL_QUERY", [False])[0]:
                sql_output = self.generate_sql_query(user_input)
                response["output"] = {"type": "sql", "content": sql_output}
            elif intent_data.get("AUDIO_GENERATION", False):
                audio_output = self.generate_audio(user_input)
                response["output"] = {"type": "audio", "content": audio_output}
            elif intent_data.get("GRAPHIC_GENERATIONS", False):
                graphics_output = self.generate_graphics(user_input)
                response["output"] = {"type": "graphic", "content": graphics_output}
            else:
                response["output"] = {"type": "text", "content": "⚠️ Could not determine a valid intent."}

            return response

        except Exception as e:
            print(f"Orchestration error: {e}")
            return {
                "intent": {},
                "output": {"type": "error", "content": f"❌ Error: {str(e)}"}
            }

