FROM python:3.12-slim as build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"

# railway env vars
ARG DEBUG
ENV DEBUG=$DEBUG
ARG PORT
ENV PORT=${PORT:-8000}

WORKDIR /code
COPY . /code

RUN echo "Build-time PORT value: $PORT"

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE $PORT

COPY ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

ENTRYPOINT [ "/code/entrypoint.sh" ]