#Run these in terminal
#pip install google-genai python-dotenv
#Done by Chong Li Heng 2603072

from google import genai
from dotenv import load_dotenv
from google.genai import types
from pathlib import Path
import os
import json

class GeminiAPI: 
    #initialise variables for the prompt
    #initialise prompt message and meal plan data
    def __init__(self, pax, total_grocery_cost, country, exclusion):
          self.__pax = pax
          self.__total_grocery_cost = total_grocery_cost
          self.__country = country
          self.__exclusion = exclusion
          self.__meal_plan_data = None
          self.__prompt = None
          self.__feedbackprompt = None
          self.__env = Path(__file__).resolve().parent / ".env"     #initialise __env which will be checked at call_api()
    
    #crafts prompt and saves it to __prompt
    def craft_prompt(self):
        self.__prompt = f"""
        Generate a grocery list and meals for:
        Country: {self.__country} | Budget: {self.__total_grocery_cost} | Pax: {self.__pax} | Exclusion: {self.__exclusion}

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
    
    #call API using __prompt
    def call_api(self,prompt_type):
        if prompt_type == "feedback":
            __content = self.__feedbackprompt
        else:
            __content = self.__prompt

        if (self.__env.exists() and load_dotenv() != False):                        #check if env file missing and "load_dotenv()" loads the env file while checking if its empty
            client = genai.Client(http_options=types.HttpOptions(timeout=150000))   #A timer incase the AI takes too long to return an object
            try:
                #API Call to gemini 3.8 flash
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=__content,
                    config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                    )
                )     

                #Response generated
                if response:
                    self.__meal_plan_data = response.text                           #save json object into the __meal_plan_data
                    if self.__meal_plan_data != None:
                        print("\nRecommended Meals Generated !!!")
                        return True
                    else:
                        print("\nNo Meals Generated")
                        return False                
                  
            #Error Handling from API    
            except (ValueError, AttributeError, Exception) as e:
                error_msg = getattr(e, "message", str(e))    
                print(f"{error_msg}\n")
                return False
        else:
            print("Error: ENV file not found!!!")
            return False

    #craft the API prompt to analyse history of meals
    def craft_feedback_prompt(self, prexisting_mealplans):
        self.__feedbackprompt = f'''Analyze existing meals: {prexisting_mealplans}. Identify and state the specific vitamins and nutrients that are missing along with their recommended amounts. Then, generate an optimized diet/grocery list addressing them for:
Country: {self.__country} | Budget: {self.__total_grocery_cost} | Pax: {self.__pax} | Exclusion: {self.__exclusion}

Return JSON matching this schema exactly:
{{
"pax": 1,
"observation": "string",
"Error": "string or 'budget is too low to craft a meal'",
"Total_grocery_cost": 0.0,
"Grocery_list": [{{"ingredient_name": "string", "Price_per_ingredient": 0.0, "Quantity": "string"}}],
"Dishes": [{{
    "dish_name": "string",
    "cuisine": "Chinese|Malay|Indian|Japanese|Thai|Korean|Vietnamese|Italian|Mexican|Western",
    "recipe": "string",
    "calorie_count_per_meal_output": "string",
    "protein_count_per_meal_output": "string",
    "fats_count_per_meal": "string",
    "price_per_meal": 0.0,
    "ingredients": "string"
}}]
}}'''
    #return generated meal plan
    def generate_meal_plan(self):
        return self.__meal_plan_data

    def hardcode_normal_meal_plan(self):
     #check if sampleoutput exists and has contents
        if Path("sampleoutput.json").exists():
                try:
                    with open("sampleoutput.json", "r") as file:
                        data = json.load(file)

                    if not data:
                        print("\nSample output is missing!")
                    else:
                        #returns the sampleoutput
                        self.__meal_plan_data = data
                except json.JSONDecodeError:
                    print("\nSample output is missing!")
        else:
            return ("\nUnable to generate response!")

    
    def hardcode_feedback_meal_plan(self):
     #check if sample feedback output exists and has contents
        if Path("samplefeedbackoutput.json").exists():
                try:
                    with open("samplefeedbackoutput.json", "r") as file:
                        data = json.load(file)

                    if not data:
                        print("\nSample feedback output is missing!")
                    else:
                        #returns the sample feedback output
                        self.__meal_plan_data = data
                except json.JSONDecodeError:
                    print("\nSample feedback output is missing!")
        else:
            return ("\nUnable to generate response!")






# #checks for env file
# def checkENV():
#     return env_path.exists()

# #craft the prompt to be fed into the Gemini API Call
# def craftprompt(pax, total_grocery_cost, country,exclusion):
#         return f"""
#         Generate a grocery list and meals for:
#         Country: {country} | Budget: {total_grocery_cost} | Pax: {pax} | Exclusion: {exclusion}

#         Return JSON matching this schema:
#         {{
#         "pax": 1,
#         "Error": "string or 'budget is too low to craft a meal' if insufficient",
#         "Total_grocery_cost": 0.0,
#         "Grocery_list": [
#             {{"ingredient_name": "string", "Price_per_ingredient": 0.0, "Quantity": "string"}}
#         ],
#         "Dishes": [
#             {{
#                 "dish_name": "string",
#                 "cuisine": "Chinese|Malay|Indian|Japanese|Thai|Korean|Vietnamese|Italian|Mexican|Western",
#                 "recipe": "string",
#                 "calorie_count_per_meal_output": "string",
#                 "protein_count_per_meal_output": "string",
#                 "fats_count_per_meal": "string",
#                 "price_per_meal": 0.0,
#                 "ingredients": "string"
#             }}
#         ]
#         }}
#         """


# #Gemini API Call
# def GeminiAPI(prompt):
#     isENV = checkENV()
#     if (isENV == True):
#         load_dotenv()
#         # Initialize the client (reads GEMINI_API_KEY automatically from environment)
#         # Also adds a timer incase the AI takes too long to return an object
#         client = genai.Client(
#             http_options=types.HttpOptions(timeout=15000)
#         )
#         try:
#             #API Call to gemini 3.8 flash
#             response = client.models.generate_content(
#                 model="gemini-3.8-flash",
#                 contents=prompt,
#                 config=types.GenerateContentConfig(
#                     response_mime_type="application/json"
#                 )
#             )
            
#             #Response generated
#             if response:
#                 return response.text

#         #Error Handling from API    
#         except (ValueError, AttributeError, Exception) as e:
#             error_msg = getattr(e, "message", str(e))    
#             return f"{error_msg}\n"
#     else:
#         return "\nenv file is missing !"


# #Hardcoded Sample API Call Output
# def HCodeGeminiAPI(prompt):
#     #check if sampleoutput exists and has contents
#     if Path("sampleoutput.json").exists():
#             try:
#                 with open("sampleoutput.json", "r") as file:
#                     data = json.load(file)

#                 if not data:
#                     return "\nSample output is missing!"
#                 else:
#                     #returns the sampleoutput
#                     return data
#             except json.JSONDecodeError:
#                 return "\nSample output is missing!"
#     else:
#         return "\nUnable to generate response!"

    

