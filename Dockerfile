FROM python:buster

COPY ./ /app
WORKDIR /app

RUN pip install -U pip
RUN pip install -r requirements-dev.txt

CMD gunicorn -b :${PORT-5000} app:app 