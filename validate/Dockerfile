FROM python:pika
ADD . /src
EXPOSE 5672
CMD python /src/validate.py $RABBIT_ADDR