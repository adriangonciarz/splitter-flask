FROM python:3.7.3-slim-stretch

RUN mkdir /srv

WORKDIR /srv
RUN mkdir uploads && mkdir output

ADD templates/ .
ADD requirements.txt .
ADD splitter.py .

RUN pip install -r requirements.txt

CMD python splitter.py
