#!/usr/bin/env python
import pika
import sys
import json
import time
import random
import uuid
import os

#
# Message Gateway abstraction
#
def createChannelOnDefaultExchange(connection, queue):
  channel = connection.channel()
  channel.queue_declare(queue=queue)
  return channel

def createQueueOnTopicExchange(connection, exchange):
  channel = connection.channel()
  channel.exchange_declare(exchange=exchange, type='topic')
  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue
  return channel, queue_name

def bindQueuesToExchange(channel,exchange,queue_name,binding_keys):
  for binding_key in binding_keys:
    channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key=binding_key)

def getTypedMessageBody(rk,body):
  d = json.loads(body)
  return d

def sendReply(channel, exchange, routing_key, message_dict):
  newBody = json.dumps(message_dict)
  channel.basic_publish(exchange=exchange,
                       routing_key=routing_key,
                       body=newBody)

def register(chan,callback,qn):
	chan.basic_consume(callback,
                    queue=qn,
                    no_ack=True)

def run(chan):
   chan.start_consuming()

def serviceName():
	file_name = (os.path.basename(__file__))
	return file_name.split('.')[0]

def logReceive(routing_key, message):
  uid = uuid.UUID(message["request_id"])
  print " [%s] Received %r:%r:%r" % (serviceName(),
  	str(uid),message["timestamp"],routing_key)

def logSend(routing_key, message):
  uid = uuid.UUID(message["request_id"])
  print " [%s] Sent     %r:%r:%r" % (serviceName(),
  	str(uid),message["timestamp"],routing_key)

def sleepRandom(min,max):
  rn = random.randint(0,1)
  if rn == 1:
    time.sleep(min)
  else:
    time.sleep(max)

def sendMessageToControl(routing_key,message):
   sendReply(control_channel,control_exchange,routing_key,message)

#
# Method overrides
#

def on_client_message(ch, method, properties, body):
  message = getTypedMessageBody(method.routing_key,body)
  logReceive(method.routing_key,message)
  sendMessageToControl(method.routing_key,message)

  message["timestamp"] = time.time()

  publish_key = 'pml.eval.request'
  sendReplyAndControl(reply_channel, reply_exchange, publish_key, message)

def on_eval_message(ch, method, properties, body):
  message = getTypedMessageBody(method.routing_key,body)
  logReceive(method.routing_key,message)
  sendMessageToControl(method.routing_key,message)

  message["timestamp"] = time.time()

  publish_key = 'pml.eval.reply'
  sendReplyAndControl(reply_channel, reply_exchange, publish_key, message)

def sendReplyAndControl(channel, exchange, routing_key, message):
  sendReply(channel,exchange,routing_key,message)
  logSend(routing_key,message)
  sendMessageToControl(routing_key,message)

#
# Main
#
try:
    host = sys.argv[1]
except IndexError:
    host = 'localhost'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

client_request_queue = 'eval.request'
request_channel = createChannelOnDefaultExchange(connection, client_request_queue)

client_reply_queue = 'eval.reply'
client_reply_channel = createChannelOnDefaultExchange(connection, client_reply_queue)

eval_request_queue = 'pml.eval.request'
eval_request_channel = createChannelOnDefaultExchange(connection, eval_request_queue)

reply_exchange = 'topic_loan_eval'
reply_channel, queue_out = createQueueOnTopicExchange(connection,reply_exchange)

binding_keys = ['pml.eval.request']
bindQueuesToExchange(reply_channel,reply_exchange,queue_out,binding_keys)

control_exchange = 'fre.eval.control'
control_channel, control_queue = createQueueOnTopicExchange(connection,control_exchange)

register(request_channel, on_client_message, client_request_queue)
register(request_channel, on_eval_message, eval_request_queue)

print ' [%s] Waiting for events. To exit press CTRL+C' % (serviceName())

run(request_channel)

# callbacks runs here