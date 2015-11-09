#!/usr/bin/env python
import pika
import sys
import json
import time
import random
 
def createChannelOnTopicExchange(connection, exchange):
  channel = connection.channel()
  channel.exchange_declare(exchange=exchange, type='topic')
  return channel
 
def createChannelOnDefaultExchange(connection, queue):
  channel = connection.channel()
  channel.queue_declare(queue=queue)
  return channel

def createExclusiveQueue(channel):
  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue
  return queue_name
 
def bindQueuesToExchange(channel,exchange,queue_name,binding_keys):
  for binding_key in binding_keys:
    channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key=binding_key)
 
def handleEvents(ch, method, properties, body): 
  message_dict = unpackMessage(method.routing_key,body)

  sleepOneOrTwo()  # here is where the work would be done
  message_dict["purchase_result"] = "pass"
  message_dict["timestamp"] = time.time()

  publishEvent(channel_out,exchange,'pml.eval.request',message_dict)

def unpackMessage(rk,body):
  d = json.loads(body)
  id = d["request_id"]
  timestamp = d["timestamp"]
  print " [gateway] Received %r:%r:%r" % (id,timestamp,rk)
  return d

def publishEvent(channel, exchange, routing_key, message_dict):
  newBody = json.dumps(message_dict)
  channel.basic_publish(exchange=exchange,
                       routing_key=routing_key,
                       body=newBody)
  print " [gateway] Sent     %r:%r:%r" % (message_dict["request_id"],
                                          message_dict["timestamp"],routing_key)

def sleepOneOrTwo():
  rn = random.randint(0,1)
  if rn == 1:
    time.sleep(1)
  else:
    time.sleep(2)

def consumeEvents(chan, qn):
  chan.basic_consume(handleEvents,
                    queue=qn,
                    no_ack=True)
  chan.start_consuming()
 
#
# Main
#

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

queue = 'eval.request'
channel_in = createChannelOnDefaultExchange(connection, queue)

exchange = 'topic_loan_eval'
channel_out = createChannelOnTopicExchange(connection, exchange)
queue_out = createExclusiveQueue(channel_out)

binding_keys = ['pml.eval.request']
bindQueuesToExchange(channel_out,exchange,queue_out,binding_keys)
 
print ' [gateway] Waiting for events. To exit press CTRL+C'
 
consumeEvents(channel_in, queue)

# handleEvents runs here