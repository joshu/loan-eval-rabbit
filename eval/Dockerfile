FROM python:pika
ADD . /src
EXPOSE 5672
CMD python /src/eval.py $RABBIT_ADDR