FROM python:3.11-slim-buster
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

ADD . .
