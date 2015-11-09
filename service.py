#!/usr/bin/env python
import pika
import sys
import json
import time
import random
 
def createTopicExchangeOnChannel(host, exchange):
  connection = pika.BlockingConnection(pika.ConnectionParameters( host=host))
  channel = connection.channel()
  channel.exchange_declare(exchange=exchange, type='topic')
  return channel
 
def createExclusiveQueue(channel):
  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue
  return queue_name
 
def bindQueuesToExchange(exchange,queue_name,binding_keys):
  channel.queue_bind(exchange=exchange,
                     queue=queue_name,
                     routing_key='contract.purchase-eligible.request')
 
def handleEvents(ch, method, properties, body):
    d = json.loads(body)
    id = d["request_id"]
    timestamp = d["timestamp"]
    print " [purchase] Received %r:%r:%r" % (id,timestamp,method.routing_key)
 
 
    sleepOneOrTwo()  # here is whwre the work would be done
 
    d["purchase_result"] = "pass"
    d["timestamp"] = time.time()
    newBody = json.dumps(d)
    rk = 'contract.purchase-eligible.complete'
    channel.basic_publish(exchange='topic_loan_eval',
                         routing_key=rk,
                         body=newBody)
    print " [purchase] Sent     %r:%r:%r" % (id,d["timestamp"],rk)
 
def sleepOneOrTwo():
  rn = random.randint(0,1)
  if rn == 1:
    time.sleep(1)
  else:
    time.sleep(2)
 
#
# Main
#
 
exchange = 'topic_loan_eval'
channel = createTopicExchangeOnChannel('127.0.0.1',exchange)
 
queue_name = createExclusiveQueue(channel)
 
bindQueuesToExchange(exchange,queue_name,'')
 
print ' [purchase] Waiting for events. To exit press CTRL+C'
 
channel.basic_consume(handleEvents,
                      queue=queue_name,
                      no_ack=True)
 
channel.start_consuming()