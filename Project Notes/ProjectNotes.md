5-Member Functional Work Distribution

Member 1: 
## User Profile & Dietary Restrictions Module (io_manager Lead)
Functional Scope: User onboarding, basic identity, and allergy safety filters.
Key Responsibilities:
Build the terminal input and validation functions for user Name, Country, and Pax per meal.   
Implement the dropdown menu and tuple formatting parser for the 9 Dietary Restrictions (e.g., No Seafood, No Nuts, Halal Only).   
Ensure all print() statements and user-facing views for this module live strictly inside io_manager.   

Member 2: 
## Financial & Budget Enforcement Module (logic_manager & io_manager)
Functional Scope: Cost tracking, currency validation, and budget constraint logic.
Key Responsibilities:Write validation functions for the Budget input (ensuring real-world float values with a minimum threshold of $10).   
Implement the multi-condition Budget Caps business rule in logic_manager to ensure total meal costs never exceed the user’s specified limit.   
Build summary views in io_manager to display budget changes and financial breakdowns.   

Member 3: 
## Nutritional Goals & Macro Customization Module (logic_manager & io_manager)
Functional Scope: Health targets, calorie counting, and nutritional gap analysis.
Key Responsibilities:Build the Meal Goal selection dropdown (Recommended, Low Calorie, High Protein, Macros) with strict integer and minimum-amount validation for calories, protein, and fats.   
Code the business logic in logic_manager that analyzes AI outputs against nutritional gaps and recommends adjustments.   
Implement reasonability check logic to catch unrealistic user inputs and trigger error messages. 

Member 4: 
## AI Prompt Engineering & API Core Module (ai_manager Lead)
Functional Scope: Core AI communication, schema validation, and error resilience.
Key Responsibilities:Own the ai_manager module to ensure every record passes through the AI API as required.   
Design robust prompt templates that convert structured inputs into recipes, cuisines, and dish arrays (Dishes, Recipe, Total).  
Implement JSON schema validation, malformed output retry logic, and graceful API failure handling so the application never crashes.  

Member 5: 
## Persistence, Regeneration Loop & DevOps Lead (data_manager & DevOps)
Functional Scope: Data storage, feedback loops, and deployment packaging.
Key Responsibilities:Own the data_manager module to load and save processed records to CSV/JSON files across runs, including post-generation filtering functions.   
Implement the algorithm tracking and regeneration system (handling user rejections, scoring disliked styles, ratings, and enforcing the 5-try limit).   
Lead DevOps integration: set up Docker containerization, verify that docker run works seamlessly across all laptops, and manage the Git branching/PR workflow.   