#!/usr/bin/env python
import pika
import sys
import json
import uuid
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

def on_message(ch, method, properties, body):
  message = getTypedMessageBody(method.routing_key,body)
  logReceive(method.routing_key,message)

def getBindingKeysFromArgs():
  bks = sys.argv[1:]
  if not bks:
      print >> sys.stderr, "Usage: %s [binding_key]..." % (sys.argv[0],)
      sys.exit(1)
  return bks

#
# Main
#

host = 'localhost'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

exchange   = "fre.eval.control"
channel, queue_name = createQueueOnTopicExchange(connection,exchange)

binding_keys = getBindingKeysFromArgs()

bindQueuesToExchange(channel, exchange, queue_name, binding_keys)

print ' [%s] Waiting for events. To exit press CTRL+C' %(serviceName())

register(channel, on_message, queue_name)
run(channel)