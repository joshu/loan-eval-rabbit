#!/usr/bin/env python
import pika
import sys
import json
import uuid
 
def createTopicExchangeOnChannel(host, exchange):
  connection = pika.BlockingConnection(pika.ConnectionParameters( host=host))
  channel = connection.channel()
  channel.exchange_declare(exchange=exchange, type='topic')
  return channel

def createExclusiveQueue(channel):
  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue
  return queue_name

def getBindingKeysFromArgs():
  bks = sys.argv[1:]
  if not bks:
      print >> sys.stderr, "Usage: %s [binding_key]..." % (sys.argv[0],)
      sys.exit(1)
  return bks

def bindQueuesToExchange(exchange,queue_name,binding_keys):
  for binding_key in binding_keys:
    channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key=binding_key)

def handleEvents(ch, method, properties, body):
  d = json.loads(body)
  id =d["request_id"]
  uid = uuid.UUID(id)
  timestamp = d["timestamp"] or 'None'
  print " [x] %r:%r:%r" % (str(uid),timestamp,method.routing_key)

def consumeEvents(chan, qn):
  chan.basic_consume(handleEvents,
                    queue=qn,
                    no_ack=True)
  chan.start_consuming()
 
 #
 # Main
 #

exchange   = "topic_loan_eval"
channel    = createTopicExchangeOnChannel('localhost',exchange)
queue_name = createExclusiveQueue(channel)
 
binding_keys = getBindingKeysFromArgs()
 
bindQueuesToExchange(exchange, queue_name, binding_keys)
 
print ' [receive_events] Waiting for events. To exit press CTRL+C'
 
consumeEvents(channel, queue_name)