FROM python:latest

ENV API_TOKEN=sk-demo-1234567890abcdef

ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y curl vim iputils-ping
RUN pip install -r requirements.txt

EXPOSE 5000 22

CMD python app.py
