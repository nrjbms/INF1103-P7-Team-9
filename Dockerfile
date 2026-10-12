FROM python:3.14.7-slim

WORKDIR /app

RUN pip install --no-cache-dir google-genai python-dotenv pycountry pydantic reportlab

COPY .env .
COPY  aiManager.py . 
COPY  dataManager.py . 
COPY  inputManager.py . 
COPY  logicManager.py . 
COPY pdfmaker.py .
COPY meal_history.json .
COPY sampleoutput.json .
COPY dietaryRules.json .
COPY main.py .
COPY automated_test_case.py .
COPY test_logicManager.py .
COPY test.py .
COPY testcase.json .
COPY /icons .

CMD ["python","main.py"]