FROM docker.pkg.github.com/dturnbu/python3-base/python38-base:latest

ENV PONTOON_HOST=0.0.0.0
ENV PONTOON_PORT=5000

EXPOSE ${PONTOON_PORT}

ADD --chown=python:python ./plugins ./plugins
ADD --chown=python:python ./utils ./utils
ADD --chown=python:python ./pontoon.py ./pontoon.py
ADD --chown=python:python ./requirements.txt ./requirements.txt
ADD --chown=python:python ./start.sh ./start.sh

CMD ["/bin/bash", "-c", "./start.sh"]