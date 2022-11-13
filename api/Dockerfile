### Build and install packages
FROM python:3.8.13 as base-image

LABEL name="app-api"

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install 'pipenv==2022.11.11'

COPY ./Pipfile  /Pipfile
COPY ./Pipfile.lock  /Pipfile.lock
RUN pipenv install --system --ignore-pipfile --deploy

### Final image
FROM python:3.8.13-slim-buster

LABEL name="app-api"

# set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create entrypoints
COPY ./start-uvicorn.sh /

RUN groupadd -r app && \
    useradd -r -g app app && \
    sed -i 's/\r$//g' /start-uvicorn.sh && \
    chmod +x /start-uvicorn.sh && \
    chown app:app /start-uvicorn.sh

RUN apt-get update && \
    apt-get install -y \
            libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=base-image /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=base-image /usr/local/bin/ /usr/local/bin/

# Now copy the real contents of the app
COPY ./ /app

WORKDIR /app

RUN chown -R app:app /app/

# Switch to app user
USER app
EXPOSE 8000
ENTRYPOINT [ "/start-uvicorn.sh" ]
