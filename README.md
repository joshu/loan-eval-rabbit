# loan-eval-rabbit
Loan Eval microservices with RabbitMQ Integration

This repo contains a prototype application built as microservices. The services collaborate to evaluate a mortage loan.
The services are written in Python (2.7) and use the pika library to support integration via RabbittMQ. The purpose of the prototype
is to validate the CQRS pattern and identify performance issues.

## HIGH-LEVEL ARCHITECTURE

The high-level architecture is based on the CQRS pattern. The existing components just implement the "command" side of the pattern.

[graphic to be provided]

The current components and their roles in the non-prototype version:

1. Mock Client--Feeds json loan application data to the API gateway
2. API Gateway--Facade for the application. Will include user auth in the future
3. Loan Eval Policy--Front controller for the app. Runs the main workflow--loan validation followed by scatter-gather for the assessment services
4. Loan Data Validation--Checks the json loan data for correctness and completeness
5. Purchase Eligibility Assessment--Checks the loan data for purchase eligibility
6. Credit Risk Assessment--Assesses the riskyness of the loan
7. Aggregator--Aggregates the purchase and credit assessments for the for the front controller.
8. Event Store--Will contain all of the events produced by the application.

## DEPENDENCIES

* Docker
* Python
* Pika
* RabbitMQ

## INSTALLATION

Assumes you are using docker

1. Download the repo
2. Build the python image with pika

  docker build -t python:pika .

2. Run the build_images.sh script to make the docker images
3. Start RabbitMQ in the docker server

  docker run -d -p 5672:5672 -p 15672:15672  --name rabbitmq rabbitmq

4. Get the RabbitMQ container address using

  docker inspect --format '{{ .NetworkSettings.IPAddress }}' ${CID}

5. Edit the run_services.sh script with the RabbitMQ address (for now :--)
6. Start another terminal and run

  python receive_control.py "#"

7. In the first terminal, run

  python mock_client.py 1

8. Watch the messages flow in the receive_control.py terminal
