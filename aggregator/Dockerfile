FROM python:pika
ADD . /src
EXPOSE 5672
CMD python /src/aggregator.py $RABBIT_ADDR