FROM python:3.14.7-slim

WORKDIR /app

RUN pip install --no-cache-dir google-genai python-dotenv pycountry pydantic reportlab

COPY .env .
COPY  aiManager.py . 
COPY  dataManager.py . 
COPY  inputManager.py . 
COPY logic/ ./logic/
COPY pdfmaker.py .
COPY meal_history.json .
COPY sampleoutput.json .
COPY dietaryRules.json .
COPY main.py .
COPY automated_test_case.py .
COPY test.py .
COPY testcase.json .
COPY /icons .
COPY db_config.py .
COPY justeat.py .
COPY mysql_storage.py .
COPY samplefeedbackoutput.json .
COPY Saved_MealPlans.py .
COPY Test_dataManager.py .

CMD ["python","main.py"]