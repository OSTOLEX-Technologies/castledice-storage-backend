ARG IMAGE_VERSION=python:3.10.13-alpine
ARG PLATFORM

###########
# BUILDER #
###########

# pull official base image
FROM --platform=${PLATFORM} ${IMAGE_VERSION} as builder

# create the appropriate directories
ENV APP_HOME=/app/web
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements.txt
ADD ./requirements.txt .

# install psycopg2 dependencies
RUN set -ex \
    && apk update \
    && apk add --no-cache --virtual .build-deps postgresql-dev gcc python3-dev \
    musl-dev zlib-dev jpeg-dev build-base libwebp-dev linux-headers curl-dev curl \
    && curl –proto ‘=https’ –tlsv1.2 -sSf https://sh.rustup.rs | sh \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

EXPOSE 8000

#ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

ENTRYPOINT ["./entrypoint.sh"]
