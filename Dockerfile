FROM python:latest

WORKDIR ./voiplocker_stats

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY __main__.py .

COPY ./voiplocker_stats ./voiplocker_stats

RUN python3 -m compileall .

CMD python3 .
