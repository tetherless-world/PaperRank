FROM python:3.7

ADD . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app/scripts

CMD [ "python", "full_scrape.py" ]
