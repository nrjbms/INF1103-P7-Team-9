#Done by Chong Li Heng 2603072
#Install these before starting
#pip install reportlab

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table,Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


import dataManager
import inputManager

foodIcon = os.path.join("icons", "foodIcon.png")

def styling(canvas, doc):
    # creates the header
    canvas.saveState()
    page_w,page_h = doc.pagesize
    canvas.setFillColor(colors.HexColor("#F5F3ED")) #background color fill
    canvas.setStrokeColor(colors.white)
    
    canvas.rect(0,page_h - 130, page_w, 130, fill = 1, stroke = 1) #header container size
    

    #Ensure that if Logo does not exist, no error will pop up
    if os.path.exists(foodIcon):
        canvas.drawImage(foodIcon, 40,page_h - 110,width=70,height=70,mask="auto")
    else:
        print("No Icon")

    #Header styling
    header_style = ParagraphStyle(
        "HeaderTitle",
        fontName="Times-Roman",
        fontSize=30,
        textColor=colors.HexColor("#444444"),
        alignment=1
    )


    p = Paragraph("Meal Planner", header_style)
    p.wrapOn(canvas,250,50)
    p.drawOn(canvas,180,page_h-85)

    canvas.restoreState()




def makepdf(fileName, plan):
    fileName = f"{fileName}.pdf"    
    doc = SimpleDocTemplate("test1.pdf",pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []

    story.append(Spacer(1,80))
    total_cost = plan['Total_grocery_cost']
    grocery_list = plan['Grocery_list']
    name = plan['name']
    pax = plan['pax']
    date = plan['date']
    dishes = plan['Dishes']

    

    budget_data = [
        [
            Paragraph(f"<b>Budget Plan for </b> <u>{name}</u>",styles["Heading2"]),
            Paragraph(f"<b>Date:</b> {date} ", ParagraphStyle('Right', parent=ParagraphStyle('LargerNormal',parent=styles['Normal'],fontSize=14), alignment=2))
        ],
        [
            Paragraph(f"Servings (Pax): {pax}", ParagraphStyle('LargerNormal',parent=styles['Normal'],fontSize=11)),
            Paragraph(f"Total Grocery Cost: ${total_cost}",ParagraphStyle('Right', parent=ParagraphStyle('LargerNormal',parent=styles['Normal'],fontSize=14), alignment=2))
        ]
    ]

    story.append(Table(budget_data,colWidths=[200,250]))
    story.append(Spacer(1, 50))
    story.append(Paragraph("Dishes", styles['Heading2']))
    for dish in dishes:
            dish_name = dish["dish_name"]
            cuisine = dish ["cuisine"]
            story.append(Paragraph(f"• {dish_name} ({cuisine})",ParagraphStyle(   'LargerNormal',parent=styles['Normal'],fontSize=14)))
            story.append(Spacer(1,10))
    story.append(Spacer(1, 35))



    story.append(Paragraph("Grocery List", styles['Heading2']))

    for item in grocery_list:
        ingredient_name = item["ingredient_name"]
        price = item["Price_per_ingredient"]
        quantity = item["Quantity"]
        story.append(Paragraph(f"• {quantity} of <b>{ingredient_name}</b> (${price})",ParagraphStyle(   'LargerNormal',parent=styles['Normal'],fontSize=14)))
        story.append(Spacer(1,10))

    
    doc.build(story, onFirstPage=styling)


# records = get_all_records()
# for record in records:
#     total_cost = record['Total_grocery_cost']
#     groccery_list = record['Grocery_list']
#     name = record['name']
#     pax = record['pax']
#     date = record['date']
#     print(total_cost,"\n",groccery_list,"\n\n")


records = inputManager.get_selected_plan("meal_history.json")
makepdf("test1",records)