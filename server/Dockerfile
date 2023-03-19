# syntax=docker/dockerfile:1
FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
