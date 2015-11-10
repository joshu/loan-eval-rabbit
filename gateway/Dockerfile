FROM python:pika
ADD . /src
EXPOSE 5672
CMD python /src/gateway.py $RABBIT_ADDR