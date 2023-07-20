FROM python:3.10-alpine
WORKDIR /app
RUN apk add --no-cache \
    gcc \
    curl \
    musl-dev \
    mariadb-dev \
    mariadb-connector-c-dev \
    samba-client
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./pyproject.toml ./poetry.lock /app/
RUN /root/.local/bin/poetry install

COPY ./enacdrivesweb /app/enacdrivesweb
COPY ./upload /app/upload
COPY .secrets.env .secrets.json /app/
COPY enacmoni.cred /app/
COPY Makefile /app/

RUN apk add bash make

CMD [ "make", "container_entrypoint" ]
