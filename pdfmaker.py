#Done by Chong Li Heng 2603072
#Install these before starting
#pip install reportlab

from abc import ABC, abstractmethod
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table,Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import re




class PDF:

    def __init__(self,selected_meal_plan,filename):
        #set selected_meal_plan and filename
        self.__selected_meal_plan = selected_meal_plan
        self.__filename = f"{filename}.pdf"
        
        #set constant variables that are used in the other methods
        self.__story = []                                               #__story is the list of elements that would make up the format of the PDF
        self.__foodIcon = os.path.join("icons", "foodIcon.png")

        # Initialize stylesheet and define reusable custom paragraph styles
        self.__styles = getSampleStyleSheet()        
        self.__header_style = ParagraphStyle(
            "HeaderTitle",
            fontName="Times-Roman",
            fontSize=30,
            textColor=colors.HexColor("#444444"),
            alignment=1
        )
        self.__heading2 = self.__styles["Heading2"]
        self.__align_right = ParagraphStyle(
            'Right', 
            parent=ParagraphStyle('LargerNormal',parent=self.__styles['Normal'],fontSize=11), 
            alignment=2
        )
        self.__dish_title_style = ParagraphStyle(
            'DishTitleStyle',
            parent=self.__styles['Heading1'],
            fontSize=22,         
            leading=26,          
            alignment=1          
        )
        self.__standard_font = ParagraphStyle(
            'LargerNormal',
            parent=self.__styles['Normal'],
            fontSize=11
        )
        self.__standard_space = self.__story.append(Spacer(1,10))


        #self.__invalid_filename = r'[<>:"/\\|?*]'          >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # creates the front page header
    def __styling(self,canvas, doc):
        canvas.saveState()

        #set page width and page height as a reference when doing styling
        self.__page_w,self.__page_h = doc.pagesize
        canvas.setFillColor(colors.HexColor("#F5F3ED")) #background color fill
        canvas.setStrokeColor(colors.white)
        canvas.rect(0,self.__page_h - 130, self.__page_w, 130, fill = 1, stroke = 1) #header container size
        
        #Ensure that if Logo does not exist, no error will pop up
        if os.path.exists(self.__foodIcon):
            canvas.drawImage(self.__foodIcon, 40,self.__page_h - 110,width=70,height=70,mask="auto")

        #set title name
        self.__p = Paragraph("Meal Planner", self.__header_style)
        self.__p.wrapOn(canvas,250,50)
        self.__p.drawOn(canvas,180,self.__page_h-85)

        canvas.restoreState()



    #This function will create the PDF
    def makepdf(self):
        self.__doc = SimpleDocTemplate(self.__filename,pagesize=A4)

        #creates a space after the header
        self.__story.append(Spacer(1,80))


        #breaking down the budget json object into its individual parts
        self.__total_cost = self.__selected_meal_plan['Total_grocery_cost']
        self.__grocery_list = self.__selected_meal_plan['Grocery_list']
        self.__name = self.__selected_meal_plan['name']
        self.__pax = self.__selected_meal_plan['pax']
        self.__date = self.__selected_meal_plan['date']
        self.__dishes = self.__selected_meal_plan['Dishes']

        
        #header information including name of user, grocery list price, planned servings and date of budget plan generation
        self.__groccery_list_information = [
            [
                Paragraph(f"<b>Budget Plan for </b> <u>{self.__name}</u>",self.__heading2),
                Paragraph(f"<b>Date:</b> {self.__date} ", self.__align_right)
            ],
            [
                Paragraph(f"Servings (Pax): {self.__pax}", self.__standard_font),
                Paragraph(f"Total Grocery Cost: ${self.__total_cost}",self.__align_right)
            ]
        ]
        self.__story.append(Table(self.__groccery_list_information,colWidths=[200,250]))
        self.__story.append(Spacer(1, 50))


        #lists out the dishes by name and cuisine
        self.__story.append(Paragraph("Dishes", self.__heading2))
        for self.__dish in self.__dishes:
                self.__dish_name = self.__dish["dish_name"]
                self.__cuisine = self.__dish["cuisine"]
                self.__story.append(Paragraph(f"• {self.__dish_name} ({self.__cuisine})",self.__standard_font))
                self.__standard_space
        self.__story.append(Spacer(1, 35))


        #list out the total grocery list
        self.__story.append(Paragraph("Grocery List", self.__heading2))
        for self.__item in self.__grocery_list:
            self.__ingredient_name = self.__item["ingredient_name"]
            self.__price = self.__item["Price_per_ingredient"]
            self.__quantity = self.__item["Quantity"]
            self.__story.append(Paragraph(f"• {self.__quantity} of <b>{self.__ingredient_name}</b> (${self.__price})",self.__standard_font))
            self.__standard_space

        for self.__dish in self.__dishes:    
            #next page
            self.__story.append(PageBreak())

            #breaking down the individual dish information
            self.__dish_name = self.__dish["dish_name"]
            self.__cuisine = self.__dish["cuisine"]
            self.__calorie_count = self.__dish["calorie_count_per_meal_output"]
            self.__protein_count = self.__dish["protein_count_per_meal_output"]
            self.__fat_count = self.__dish["fats_count_per_meal"]
            self.__dishprice = self.__dish["price_per_meal"]
            self.__ingredients = self.__dish["ingredients"]
            self.__recipe = self.__dish["recipe"]


            #dish name
            self.__story.append(Paragraph(f"<b>{self.__dish_name}</b>", self.__dish_title_style))        
            self.__story.append(Spacer(1,30))

            #dish price
            self.__story.append(Paragraph(f"Price per pax : ${self.__dishprice}",self.__standard_font))
            self.__story.append(Spacer(1,20))

            #dish nutritional information
            self.__story.append(Paragraph("Nutritional Information per serving", self.__heading2))
            self.__story.append(Paragraph(f"Calorie count : {self.__calorie_count}",self.__standard_font))
            self.__standard_space
            self.__story.append(Paragraph(f"Protein count : {self.__protein_count}",self.__standard_font))
            self.__standard_space
            self.__story.append(Paragraph(f"Fat count : {self.__fat_count}",self.__standard_font))
            self.__story.append(Spacer(1,20))

            #list out the list of ingredients for individual dish
            self.__story.append(Paragraph("Ingredients", self.__heading2))
            self.__ingredients = [s.strip() for s in self.__ingredients.split(",") if s.strip()]
            for i, self.__ingredient in enumerate(self.__ingredients, start=1):
                self.__story.append(Paragraph(f"{i}. {self.__ingredient}.", self.__standard_font))
                self.__standard_space
            self.__story.append(Spacer(1,20))

            #list out the list of recipe instructions for individual dish
            self.__story.append(Paragraph("Instructions", self.__heading2))
            self.__instructions = re.split(r"(?=\d+\.\s)", self.__recipe)
            for self.__instruction in self.__instructions:
                if self.__instruction.strip():
                    self.__story.append(Paragraph(self.__instruction.strip(), self.__standard_font))
                    self.__story.append(self.__standard_space)

        #builds the pdf "onFirstPage" creates the header "Budget Planner"
        self.__doc.build(self.__story, onFirstPage=self.__styling)
        if os.path.exists(self.__filename):
            print("\nPDF File has been made !")
            # return False  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>





