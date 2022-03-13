FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY /backend/requirements.txt /code/
RUN pip install -r requirements.txt
COPY /backend/. /code/
