FROM python:3.7.3-slim-stretch

RUN mkdir /app

WORKDIR /app
RUN mkdir uploads && mkdir output

ADD templates/ ./templates/
ADD requirements.txt .
ADD app.py .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD python splitter.py
