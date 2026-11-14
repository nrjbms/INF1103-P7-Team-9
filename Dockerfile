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
COPY /main_test_cases .
COPY . .

CMD ["python","justeat.py"]


#steps to run container:
# 1) docker compose down -v
# 2) docker compose up -d db
# 3) docker compose logs -f fb
# 4) docker --rm -it app python justeat.py
# or alternatively to run hardcoded test.py:
# 4) docker --rm -it app python test.py