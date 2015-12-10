# loan-eval-rabbit
Loan Eval microservices with RabbitMQ Integration

This repo contains a prototype application built as microservices. The services collaborate to evaluate a loan application.
The services are written in Python (2.7) and use the pika library to support integration via RabbittMQ. The purpose of the prototype
is to validate the CQRS pattern and identify performance issues.

## HIGH-LEVEL ARCHITECTURE

The high-level architecture is based on the CQRS pattern. The existing components just implement the "command" side of the pattern.

[graphic to be provided]

The current components and their roles in the non-prototype version:

1. Web Client--Feeds json loan application data to the API gateway
2. API Gateway--Facade for the application. Will include user auth in the future
3. Loan Eval Policy--Front controller for the app. Runs the main workflow--loan validation followed by scatter-gather for the assessment services
4. Loan Data Validation--Checks the json loan data for correctness and completeness
5. Purchase Eligibility Assessment--Checks the loan data for compliance with purchase rules
6. Credit Risk Assessment--Assesses the riskiness of the loan
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

  python async_logger.py

7. In the first terminal, run

  curl -i -X POST http://dockerhost:6080/loaneval/api/v1.0/sendl/2

8. Watch the messages flow in the async_logger.py terminal

## STRUCTURE OF A LOAN EVAL MICROSERVICE

As of December 2015, the Loan Eval microservices are written in python 2.7 and integrated with RabbitMQ--an AMQP message broker.
The microservices use the Pika library to access RabbitMQ. The [RabbitMQ tutorial] [rabbit] has good examples.

[rabbit] http://www.rabbitmq.com/getstarted.html

Each of the loan eval microservices has the same structure:

* Hashbang for python
* Imports
* Message Gateway code (an abstraction the rabbit API that should allow replacement. Duplicate code in each, needs to be "inherited")
* Template methods (implement the core logic)
* Main method (connects to rabbit and blocks, listening for incoming messages)

## KEY METHODS

The key methods are the first two template methods--on_message and processMessage.

Note: Python programmers tend to use underscore_case and I started that way, but quickly reverted to old habits e.g. camelCase.

### on_message

on_message is a callback from the Pika library setup when you register the channel & queue.

It is called with several args including the message body. Every instance has the same steps:

  message = getTypedMessageBody(method.routing_key,body)        # Convert the message body to a python dictionary
  logReceive(method.routing_key,message)                        # Print the message on stdout

  processMessage(channel,exchange,method.routing_key,message)   # process the message

### processMessage

Each processMessage is basically a "switch" statement that has a case for each of the event message/ routing key handled by the microservice.

The "eval" service handles three routing keys

* pml.eval.request
* loan.validation.reply
* pml.eval-services.reply

For each key, the required actions are taken

  if routing_key == "pml.eval.request":
    start_time[id] = message["timestamp"]
    reply_key = 'loan.validation.request'
    sendReplyAndControl(channel,exchange,reply_key,message)

  elif routing_key == "loan.validation.reply":
    reply_key = 'contract.purchase-eligible.request'
    sendReplyAndControl(channel,exchange,reply_key,message)
    reply_key = 'borrower.credit-assessment.request'
    sendReplyAndControl(channel,exchange,reply_key,message)

  elif routing_key == "pml.eval-services.reply":
    logAndSendResponseTime(id)
    reply_key = 'pml.eval.reply'
    sendReplyAndControl(channel,exchange,reply_key,message)

### sendReplyAndControl

The sendReplyAndControl method provides a response on the app's pub-sub channel as well as on a "control" channel for logging.