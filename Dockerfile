# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye

WORKDIR /python-docker

COPY requirements.txt requirements.txt
COPY model_files model_files
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "5001"]
