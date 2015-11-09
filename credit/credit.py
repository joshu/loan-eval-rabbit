#!/usr/bin/env python
import pika
import sys
import json
import time
import random
import uuid

def createChannelOnTopicExchange(conection, exchange):
  channel = connection.channel()
  channel.exchange_declare(exchange=exchange, type='topic')
  return channel

def createExclusiveQueue(channel):
  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue
  return queue_name

def bindQueuesToExchange(exchange,queue_name,binding_keys):
  for binding_key in binding_keys:
    channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key=binding_key)

def handleEvents(ch, method, properties, body):
  message_dict = unpackMessage(method.routing_key,body)

  sleepRandom(1,2)  # here is whwre the work would be done

  message_dict["purchase_result"] = "pass"
  message_dict["timestamp"] = time.time()
  rk = 'borrower.credit-assessment.complete'
  publishEvent(ch, exchange, rk, message_dict)

def unpackMessage(rk,body):
  d = json.loads(body)
  id = d["request_id"]
  uid = uuid.UUID(id)
  timestamp = d["timestamp"]
  print " [credit] Received %r:%r:%r" % (str(uid),timestamp,rk)
  return d

def publishEvent(channel, exchange, routing_key, message_dict):
  newBody = json.dumps(message_dict)
  channel.basic_publish(exchange=exchange,
                       routing_key=routing_key,
                       body=newBody)
  print " [credit] Sent     %r:%r:%r" % (message_dict["request_id"],
                                          message_dict["timestamp"],routing_key)

def sleepRandom(low, high):
  rn = random.randint(0,1)
  if rn == 1:
    time.sleep(low)
  else:
    time.sleep(high)

def consumeEvents(chan, qn):
  chan.basic_consume(handleEvents,
                    queue=qn,
                    no_ack=True)
  chan.start_consuming()

#
# Main
#
host = sys.argv[1] or 'localhost'
exchange = 'topic_loan_eval'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = createChannelOnTopicExchange(connection,exchange)
queue_name = createExclusiveQueue(channel)

binding_keys = ['borrower.credit-assessment.request']
bindQueuesToExchange(exchange,queue_name,binding_keys)

print ' [credit] Waiting for events. To exit press CTRL+C'

consumeEvents(channel, queue_name)
