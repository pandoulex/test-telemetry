# syntax=docker/dockerfile:1
FROM python:2.7-alpine
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt
COPY lib /app/lib
COPY main.py /app/main.py
WORKDIR /app
CMD ["python", "main.py"]
