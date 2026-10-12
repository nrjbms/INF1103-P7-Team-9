#Done by Chong Li Heng 2603072
#Install these before starting
#pip install reportlab

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table,Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import re

#definitions    
#contents of the PDF will be stored in this array
story = []
foodIcon = os.path.join("icons", "foodIcon.png")
styles = getSampleStyleSheet()
heading2 = styles["Heading2"]
align_right = ParagraphStyle(
    'Right', 
    parent=ParagraphStyle('LargerNormal',parent=styles['Normal'],fontSize=11), 
    alignment=2
)
dish_title_style = ParagraphStyle(
    'DishTitleStyle',
    parent=styles['Heading1'],
    fontSize=22,         
    leading=26,          
    alignment=1          
)
standard_font = ParagraphStyle(
    'LargerNormal',
    parent=styles['Normal'],
    fontSize=11
)
standard_space = story.append(Spacer(1,10))
invalid_filename = r'[<>:"/\\|?*]'
story = []

# creates the front page header
def styling(canvas, doc):
    canvas.saveState()

    page_w,page_h = doc.pagesize
    canvas.setFillColor(colors.HexColor("#F5F3ED")) #background color fill
    canvas.setStrokeColor(colors.white)
    
    canvas.rect(0,page_h - 130, page_w, 130, fill = 1, stroke = 1) #header container size
    
    #Ensure that if Logo does not exist, no error will pop up
    if os.path.exists(foodIcon):
        canvas.drawImage(foodIcon, 40,page_h - 110,width=70,height=70,mask="auto")

    #Header styling
    header_style = ParagraphStyle(
        "HeaderTitle",
        fontName="Times-Roman",
        fontSize=30,
        textColor=colors.HexColor("#444444"),
        alignment=1
    )

    #set title name
    p = Paragraph("Meal Planner", header_style)
    p.wrapOn(canvas,250,50)
    p.drawOn(canvas,180,page_h-85)

    canvas.restoreState()



#This function will create the PDF
def makepdf(plan):
    #sets the file name
    fileName = input("What would you like to name the file: ")

    #check if file name is valid
    validName = False
    while(validName == False):
        if re.search(invalid_filename, fileName):
            print("\nInvalid file name !")
            fileName = input("What would you like to name the file: ")
        else:
            validName = True
            fileName = f"{fileName}.pdf"    
            doc = SimpleDocTemplate(fileName,pagesize=A4)


    #creates a space after the header
    story.append(Spacer(1,80))


    #breaking down the budget json object into its individual parts
    total_cost = plan['Total_grocery_cost']
    grocery_list = plan['Grocery_list']
    name = plan['name']
    pax = plan['pax']
    date = plan['date']
    dishes = plan['Dishes']

    
    #header information including name of user, grocery list price, planned servings and date of budget plan generation
    groccery_list_information = [
        [
            Paragraph(f"<b>Budget Plan for </b> <u>{name}</u>",heading2),
            Paragraph(f"<b>Date:</b> {date} ", align_right)
        ],
        [
            Paragraph(f"Servings (Pax): {pax}", standard_font),
            Paragraph(f"Total Grocery Cost: ${total_cost}",align_right)
        ]
    ]
    story.append(Table(groccery_list_information,colWidths=[200,250]))
    story.append(Spacer(1, 50))


    #lists out the dishes by name and cuisine
    story.append(Paragraph("Dishes", heading2))
    for dish in dishes:
            dish_name = dish["dish_name"]
            cuisine = dish ["cuisine"]
            story.append(Paragraph(f"• {dish_name} ({cuisine})",standard_font))
            standard_space
    story.append(Spacer(1, 35))


    #list out the total grocery list
    story.append(Paragraph("Grocery List", heading2))
    for item in grocery_list:
        ingredient_name = item["ingredient_name"]
        price = item["Price_per_ingredient"]
        quantity = item["Quantity"]
        story.append(Paragraph(f"• {quantity} of <b>{ingredient_name}</b> (${price})",standard_font))
        standard_space




    for dish in dishes:    
        #next page
        story.append(PageBreak())

        #breaking down the individual dish information
        dish_name = dish["dish_name"]
        cuisine = dish["cuisine"]
        calorie_count = dish["calorie_count_per_meal_output"]
        protein_count = dish["protein_count_per_meal_output"]
        fat_count = dish["fats_count_per_meal"]
        dishprice = dish["price_per_meal"]
        ingredients = dish["ingredients"]
        recipe = dish["recipe"]


        #dish name
        story.append(Paragraph(f"<b>{dish_name}</b>", dish_title_style))        
        story.append(Spacer(1,30))

        #dish price
        story.append(Paragraph(f"Price per pax : ${dishprice}",standard_font))
        story.append(Spacer(1,20))

        #dish nutritional information
        story.append(Paragraph("Nutritional Information per serving", heading2))
        story.append(Paragraph(f"Calorie count : {calorie_count}",standard_font))
        standard_space
        story.append(Paragraph(f"Protein count : {protein_count}",standard_font))
        standard_space
        story.append(Paragraph(f"Fat count : {fat_count}",standard_font))
        story.append(Spacer(1,20))

        #list out the list of ingredients for individual dish
        story.append(Paragraph("Ingredients", heading2))
        ingredients = [s.strip() for s in ingredients.split(",") if s.strip()]
        for i, ingredient in enumerate(ingredients, start=1):
            story.append(Paragraph(f"{i}. {ingredient}.", standard_font))
            standard_space
        story.append(Spacer(1,20))

        #list out the list of recipe instructions for individual dish
        story.append(Paragraph("Instructions", heading2))
        instructions = re.split(r"(?=\d+\.\s)", recipe)
        for instruction in instructions:
            if instruction.strip():
                story.append(Paragraph(instruction.strip(), standard_font))
                story.append(standard_space)

    #builds the pdf "onFirstPage" creates the header "Budget Planner"
    doc.build(story, onFirstPage=styling)
    if os.path.exists(fileName):
        print("\nPDF File has been made !")
        return False