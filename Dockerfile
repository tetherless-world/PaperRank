FROM python:3.7

ADD . /app

RUN pip install -r app/requirements.txt

CMD [ "python", "app/scripts/test.py" ]
