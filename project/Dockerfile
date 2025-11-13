FROM python:3.10-slim

RUN apt-get update -y && apt-get install -y \
    default-jdk \
    iputils-ping \
    postgresql-client

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN java --version

WORKDIR /neksio

COPY requirements.txt .

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

COPY . .

RUN chmod +x /neksio/entrypoint.sh

CMD ["/neksio/entrypoint.sh"]
