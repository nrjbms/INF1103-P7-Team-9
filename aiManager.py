# name: string,
# budget: float,
# pax: int,
# Diet_restriction: string,
# Calorie_count: int,
# Protein: int,
# Fats: int,
# Country: string,
# Error: string,
# Recipe: multiline_string ,
# Cuisine: string,
# Total 

from google import genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="hello AI"
)

print(interaction.output_text)