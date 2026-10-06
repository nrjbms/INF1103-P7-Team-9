from google import genai
from dotenv import load_dotenv
import threading

load_dotenv()

# Initialize the client (reads GEMINI_API_KEY automatically from environment)
client = genai.Client()

#timer function
def time_out():
    return True

#checks if data is valid
def validatedata(pax, total_grocery_cost, country,exclusion):
    try:
        float(total_grocery_cost.strip())
        valid_grocery = True
    except:
        valid_grocery = False
    valid_pax = pax.isdigit()
    valid_country = isinstance(country,str)    
    valid_exclusion = isinstance(exclusion,str)
    errormsg = ""
    if valid_pax == False:
        errormsg = errormsg + "!! Please key in Pax as a valid number \n"
    if valid_grocery == False:
        errormsg = errormsg +"!! Please key in Total grocery Cost as a valid number \n"
    if valid_country == False:
        errormsg = errormsg +"!! Please key in a valid Country"
    if valid_exclusion == False:
        errormsg = errormsg + "!! Please key in a valid exclusion"
    #return prompt if data is correct
    if valid_pax == True and valid_grocery == True and valid_country == True:
        return (True,"")
    else:
        return (False,errormsg)

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
    #Timer incase response taking too long to load
    timer= threading.Timer(1, time_out)
    timer.start()

    try:
        #API Call to gemini 3.8 flash
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
        }
        )

        #If prompt takes too long to load, automatically stop
        if timer == True:
            return "Prompt took too long"
        
        #Response generated
        if response:
            timer.cancel()
            return response.text

    #Error Handling from API    
    except (ValueError, AttributeError, Exception) as e:
        timer.cancel()            
        return f"An error has occurred: \n\n{str(e)}"


#Hardcoded Sample API Call Output
# def GeminiAPI(prompt):
    response = {
            "pax": 1,
            "Error": "",
            "Total_grocery_cost": 42.2,
            "Grocery_list": [
                {
                "ingredient_name": "Jasmine Rice",
                "Price_per_ingredient": 4.5,
                "Quantity": "2 kg"
                },
                {
                "ingredient_name": "Chicken Breast",
                "Price_per_ingredient": 7.5,
                "Quantity": "800 g"
                },
                {
                "ingredient_name": "Fresh Eggs",
                "Price_per_ingredient": 3.4,
                "Quantity": "10 pcs"
                },
                {
                "ingredient_name": "Minced Pork",
                "Price_per_ingredient": 3.8,
                "Quantity": "300 g"
                },
                {
                "ingredient_name": "Firm Tofu",
                "Price_per_ingredient": 1.8,
                "Quantity": "600 g (2 blocks)"
                },
                {
                "ingredient_name": "Bok Choy",
                "Price_per_ingredient": 2.4,
                "Quantity": "500 g"
                },
                {
                "ingredient_name": "Carrots",
                "Price_per_ingredient": 1.2,
                "Quantity": "500 g"
                },
                {
                "ingredient_name": "Potatoes",
                "Price_per_ingredient": 2.2,
                "Quantity": "800 g"
                },
                {
                "ingredient_name": "Garlic and Onion Pack",
                "Price_per_ingredient": 3.0,
                "Quantity": "1 pack"
                },
                {
                "ingredient_name": "Cooking Oil",
                "Price_per_ingredient": 2.5,
                "Quantity": "500 ml"
                },
                {
                "ingredient_name": "Light Soy Sauce",
                "Price_per_ingredient": 2.2,
                "Quantity": "500 ml"
                },
                {
                "ingredient_name": "Spaghetti Pasta",
                "Price_per_ingredient": 1.9,
                "Quantity": "500 g"
                },
                {
                "ingredient_name": "Canned Chopped Tomatoes",
                "Price_per_ingredient": 1.8,
                "Quantity": "400 g"
                },
                {
                "ingredient_name": "Curry Powder",
                "Price_per_ingredient": 2.0,
                "Quantity": "100 g"
                },
                {
                "ingredient_name": "Spring Onions",
                "Price_per_ingredient": 1.0,
                "Quantity": "1 bunch"
                },
                {
                "ingredient_name": "Cabbage",
                "Price_per_ingredient": 3.0,
                "Quantity": "1 small head (600 g)"
                }
            ],
            "Dishes": [
                {
                "dish_name": "Chicken and Bok Choy Stir-Fry with Rice",
                "cuisine": "Chinese",
                "recipe": "1. Dice 200g chicken breast and slice 1 clove garlic. 2. Heat 1 tbsp oil in a pan, fry garlic until fragrant, then cook chicken until lightly browned. 3. Add 125g chopped bok choy and 1 tbsp soy sauce. Stir-fry for 3-4 minutes until cooked through. 4. Serve hot with 1 cup cooked jasmine rice.",
                "calorie_count_per_meal_output": "540 kcal",
                "protein_count_per_meal_output": "42g",
                "fats_count_per_meal": "14g",
                "price_per_meal": 3.1,
                "ingredients": "Chicken Breast, Bok Choy, Garlic, Light Soy Sauce, Cooking Oil, Jasmine Rice"
                },
                {
                "dish_name": "Minced Pork Bolognese Spaghetti",
                "cuisine": "Italian",
                "recipe": "1. Boil 100g spaghetti in salted water until al dente. 2. In a skillet, sauté diced onion and garlic in 1 tbsp oil. 3. Add 150g minced pork and cook until browned. 4. Pour in 200g canned chopped tomatoes, simmer for 10 minutes until sauce thickens, then toss with the spaghetti.",
                "calorie_count_per_meal_output": "620 kcal",
                "protein_count_per_meal_output": "34g",
                "fats_count_per_meal": "18g",
                "price_per_meal": 3.3,
                "ingredients": "Spaghetti Pasta, Minced Pork, Canned Chopped Tomatoes, Onion, Garlic, Cooking Oil"
                },
                {
                "dish_name": "Braised Chicken and Potato Curry",
                "cuisine": "Malay",
                "recipe": "1. Dice 200g chicken breast, 1 potato, and 1/2 carrot. 2. Sauté chopped onion and garlic in 1 tbsp oil, then stir in 1.5 tbsp curry powder with a splash of water to form a paste. 3. Add chicken, potatoes, carrots, and 1.5 cups water. Simmer covered for 20 minutes until potatoes are tender. 4. Serve over steamed jasmine rice.",
                "calorie_count_per_meal_output": "580 kcal",
                "protein_count_per_meal_output": "40g",
                "fats_count_per_meal": "15g",
                "price_per_meal": 3.4,
                "ingredients": "Chicken Breast, Potatoes, Carrots, Curry Powder, Onion, Garlic, Cooking Oil, Jasmine Rice"
                },
                {
                "dish_name": "Tofu and Egg Donburi Bowl",
                "cuisine": "Japanese",
                "recipe": "1. Slice 300g firm tofu and 1/2 onion. 2. In a skillet, simmer sliced onions in 1/2 cup water, 1 tbsp soy sauce, and a pinch of sugar. 3. Add tofu slices and cook for 3 minutes. 4. Beat 2 eggs and pour over the simmering mixture. Cover and cook on low heat until eggs are softly set. 5. Slide over a warm bowl of rice and garnish with spring onions.",
                "calorie_count_per_meal_output": "510 kcal",
                "protein_count_per_meal_output": "28g",
                "fats_count_per_meal": "16g",
                "price_per_meal": 2.2,
                "ingredients": "Firm Tofu, Fresh Eggs, Onion, Spring Onions, Light Soy Sauce, Jasmine Rice"
                },
                {
                "dish_name": "Classic Egg and Vegetable Fried Rice",
                "cuisine": "Chinese",
                "recipe": "1. Heat 1 tbsp oil in a wok. Beat 2 eggs and scramble lightly, then set aside. 2. Sauté minced garlic, 1 diced carrot, and 100g shredded cabbage until crisp-tender. 3. Add 1.5 cups cooled cooked jasmine rice and stir-fry on high heat. 4. Return eggs to wok, season with 1.5 tbsp soy sauce, toss well, and top with chopped spring onions.",
                "calorie_count_per_meal_output": "490 kcal",
                "protein_count_per_meal_output": "18g",
                "fats_count_per_meal": "15g",
                "price_per_meal": 1.9,
                "ingredients": "Jasmine Rice, Fresh Eggs, Carrots, Cabbage, Garlic, Light Soy Sauce, Spring Onions, Cooking Oil"
                }
            ]
    }
    
    return response