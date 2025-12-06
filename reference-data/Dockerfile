# add slim python base image to install dependencies from requirements.txt then execute the mock server
FROM python:3.11-slim   
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "reference_data_api:app", "--host", "0.0.0.0", "--port", "8000"]