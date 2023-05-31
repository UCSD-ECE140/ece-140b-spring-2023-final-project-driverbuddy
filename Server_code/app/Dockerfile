FROM python:3.10.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install libev-dev -y

COPY ./src/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

WORKDIR /app

EXPOSE 80

CMD python main.py