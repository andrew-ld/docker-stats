FROM python:3

WORKDIR /srv/docker_stats

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY __main__.py .

COPY ./docker_stats /srv/docker_stats/docker_stats

RUN python3 -OO -m compileall .

CMD python3 .
