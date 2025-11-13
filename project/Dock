FROM python:3.10-bullseye

RUN apt-get update -y  && apt-get install -y default-jdk

COPY . /neksio

WORKDIR /neksio

RUN python3 -m  venv /opt/venv

RUN pip install pip  --upgrade
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/

RUN java --version
RUN apt-get update && apt-get install -y postgresql-client

RUN   /opt/venv/bin/pip3 install -r requirements.txt


RUN chmod +x /neksio/entrypoint.sh

CMD ["/neksio/entrypoint.sh"]