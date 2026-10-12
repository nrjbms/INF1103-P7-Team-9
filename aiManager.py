#Run these in terminal
#pip install google-genai python-dotenv
#Done by Chong Li Heng 2603072

from google import genai
from dotenv import load_dotenv
from google.genai import types
from pathlib import Path
import os
import json


env_path = Path(__file__).resolve().parent / ".env"

#checks for env file
def checkENV():
    return env_path.exists()

#craft the prompt to be fed into the Gemini API Call
def craftprompt(pax, total_grocery_cost, country,exclusion):
        return f"""
        Generate a grocery list and meals for:
        Country: {country} | Budget: {total_grocery_cost} | Pax: {pax} | Exclusion: {exclusion}

        Return JSON matching this schema:
        {{
        "pax": 1,
        "Error": "string or 'budget is too low to craft a meal' if insufficient",
        "Total_grocery_cost": 0.0,
        "Grocery_list": [
            {{"ingredient_name": "string", "Price_per_ingredient": 0.0, "Quantity": "string"}}
        ],
        "Dishes": [
            {{
                "dish_name": "string",
                "cuisine": "Chinese|Malay|Indian|Japanese|Thai|Korean|Vietnamese|Italian|Mexican|Western",
                "recipe": "string",
                "calorie_count_per_meal_output": "string",
                "protein_count_per_meal_output": "string",
                "fats_count_per_meal": "string",
                "price_per_meal": 0.0,
                "ingredients": "string"
            }}
        ]
        }}
        """


#Gemini API Call
def GeminiAPI(prompt):
    isENV = checkENV()
    if (isENV == True):
        load_dotenv()
        # Initialize the client (reads GEMINI_API_KEY automatically from environment)
        # Also adds a timer incase the AI takes too long to return an object
        client = genai.Client(
            http_options=types.HttpOptions(timeout=15000)
        )
        try:
            #API Call to gemini 3.8 flash
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            #Response generated
            if response:
                return response.text

        #Error Handling from API    
        except (ValueError, AttributeError, Exception) as e:
            error_msg = getattr(e, "message", str(e))    
            return f"{error_msg}\n"
    else:
        return "\nenv file is missing !"


#Hardcoded Sample API Call Output
def HCodeGeminiAPI(prompt):
    #check if sampleoutput exists and has contents
    if Path("sampleoutput.json").exists():
            try:
                with open("sampleoutput.json", "r") as file:
                    data = json.load(file)

                if not data:
                    return "\nSample output is missing!"
                else:
                    #returns the sampleoutput
                    return data
            except json.JSONDecodeError:
                return "\nSample output is missing!"
    else:
        return "\nUnable to generate response!"

    

    
