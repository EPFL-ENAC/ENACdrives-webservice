# build the Django static content
FROM python:3.10-alpine as django-static
WORKDIR /app
RUN apk add --no-cache \
    gcc \
    curl \
    musl-dev \
    mariadb-connector-c-dev
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./pyproject.toml ./poetry.lock /app/
RUN /root/.local/bin/poetry install

COPY ./enacdrivesweb /app/enacdrivesweb
COPY ./upload /app/upload
COPY ./private /app/private
COPY .secrets.env .secrets.json /app/
COPY Makefile /app/

RUN apk add bash make

CMD [ "make", "container_entrypoint" ]
