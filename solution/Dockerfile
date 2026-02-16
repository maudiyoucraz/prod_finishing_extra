FROM python:3.12.1-alpine3.19

RUN apk update && \
    apk add dos2unix postgresql-client postgresql-dev postgresql-libs gcc libpq-dev musl-dev && \
    rm -rf /var/cache/apk/*
 
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN ls -la /app/

ENV SERVER_ADDRESS=0.0.0.0:8080 \
    SERVER_PORT=8080 \
    POSTGRES_CONN=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB \
    POSTGRES_JDBC_URL=jdbc:postgresql://your_postgresql_container_name:5432/dbname \
    POSTGRES_USERNAME=$POSTGRES_USER \
    POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    POSTGRES_HOST=$POSTGRES_HOST \
    POSTGRES_PORT=$POSTGRES_PORT \
    POSTGRES_DATABASE=$POSTGRES_DB \
    RANDOM_SECRET=your_random_secret_key
CMD ["sh", "-c", "exec python3 -m flask run --host=0.0.0.0 --port=$SERVER_PORT 2>&1 || python3 -c 'import traceback; traceback.print_exc()'"]

# CMD ["sh", "-c", "exec python3 -m flask run --host=0.0.0.0 --port=$SERVER_PORT"]

