FROM python:pika
ADD . /src
EXPOSE 5672
CMD python /src/credit.py $RABBIT_ADDR