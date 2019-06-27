FROM python:3.7.3-slim-stretch

RUN mkdir /app

WORKDIR /app
RUN mkdir uploads && mkdir output

ADD templates/ ./templates/
ADD static/ ./static/
ADD requirements.txt .
ADD splitter.py .

RUN pip install -r requirements.txt

EXPOSE 8080

RUN export FLASK_APP=app.py
CMD flask run --host=0.0.0.0 --port=8080