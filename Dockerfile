FROM python:3.14.7-slim

WORKDIR /app

# RUN pip install --no-cache-dir google-genai python-dotenv pycountry pydantic reportlab 
RUN pip install --no-cache-dir google-genai python-dotenv pycountry pydantic reportlab mysql-connector-python
COPY .env .
COPY  aiManager.py . 
COPY  inputManager.py . 
COPY logic/ ./logic/
COPY pdfmaker.py .
COPY sampleoutput.json .
COPY dietaryRules.json .
COPY main.py .
COPY test.py .
COPY /icons .
COPY db_config.py .
COPY justeat.py .
COPY mysql_storage.py .
COPY samplefeedbackoutput.json .
COPY Saved_MealPlans.py .
COPY . .

CMD ["python","justeat.py"]
