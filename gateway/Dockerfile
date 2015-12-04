FROM python:pika
RUN pip install flask
ADD . /src
EXPOSE 5672 6080
CMD python /src/rest_gateway.py $RABBIT_ADDR