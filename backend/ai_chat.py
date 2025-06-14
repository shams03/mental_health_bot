import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from functools import partial
from openai import AsyncOpenAI
import json

load_dotenv()

# Configure OpenAI
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Gemini model
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

class AIChat:
    @staticmethod
    async def get_openai_response(message: str) -> dict:
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a mental health support chatbot. 
                    Your responses should be empathetic, supportive, and helpful.
                    After each response, analyze the user's message and provide their mood in a single word.
                    Format your response as JSON with 'response' and 'mood' fields.
                    The mood should be one of: happy, sad, anxious, angry, neutral, excited, confused, or stressed."""},
                    {"role": "user", "content": message}
                ],
                response_format={ "type": "json_object" }
            )
            # print(response)
            result = response.choices[0].message.content
            result = json.loads(result)
            # print(result ,"FHEIFHEOHFOWHWOHFOWEFHWO")
            return {
                'response': result['response'],
                'mood': result['mood']
            }
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return {
                'response': "I apologize, but I'm having trouble processing your message right now. Please try again later.",
                'mood': "unknown"
            }

    @staticmethod
    async def get_gemini_response(message: str) -> dict:
        try:
            prompt = f"""You are a mental health support chatbot. 
            Your responses should be empathetic, supportive, and helpful.
            After each response, analyze the user's message and provide their mood in a single word.
            Format your response as JSON with 'response' and 'mood' fields.
            The mood should be one of: happy, sad, anxious, angry, neutral, excited, confused, or stressed.
            
            User message: {message}"""
            
            response = gemini_model.generate_content(prompt)
            result = response.text
            print(result,"FHEIFHEOHFOWHWOHFOWEFHWO")
            # Parse the JSON response
            result = json.loads(result)
            print(result,"iiiiiiiiiiiiiHWOHFOWEFHWO")
            
            return {
                'response': result['response'],
                'mood': result['mood']
            }
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return {
                'response': "I apologize, but I'm having trouble processing your message right now. Please try again later.",
                'mood': "unknown"
            } 