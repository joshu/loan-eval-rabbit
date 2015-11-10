FROM python:pika
ADD . /src
EXPOSE 5672
CMD python /src/purchase.py $RABBIT_ADDR