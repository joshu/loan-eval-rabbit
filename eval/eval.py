#!/usr/bin/env python
import pika
import sys
import json
import time
import random
import uuid
import os
import socket

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

  processMessage(channel,exchange,method.routing_key,message)

def processMessage(channel,exchange,routing_key,message):
  sleepRandom(1,2)  # here is where the work would be done
  message["purchase_result"] = "pass"
  message["timestamp"] = time.time()
  id = uuid.UUID(message["request_id"])

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

def sendReplyAndControl(channel, exchange, reply_key, message):
  sendReply(channel,exchange,reply_key,message)
  logSend(reply_key,message)
  sendMessageToControl(reply_key,message)

def logAndSendResponseTime(id):
  complete_time = time.time()
  response_time = complete_time - start_time[id]
  rt_message = { "request_id" : id, "response_time" : response_time }
  print " [%s] Response %r:%r" % (serviceName(),str(id),response_time)
  rt_message = {}
  rt_message["request_id"] = str(id)
  rt_message["timestamp"]  = response_time
  reply_key = 'pml.eval.response-time'
  sendMessageToControl(reply_key,rt_message)
  sendResponseTimeAsUDP(response_time)

def sendResponseTimeAsUDP(rt):
  MESSAGE = "loan_eval_api.amqp.eval.request.response_time:%d|ms" % (rt)
  print "UDP target IP:", UDP_IP
  print "UDP target port:", UDP_PORT
  print "message:", MESSAGE

  sock = socket.socket(socket.AF_INET,     # Internet
                       socket.SOCK_DGRAM)  # UDP
  sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

#
# Main
#
try:
    host = sys.argv[1]
except IndexError:
    host = 'localhost'

UDP_IP = host
UDP_PORT = 8125    # StatsD

start_time = {}
exchange = 'topic_loan_eval'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel, queue_name = createQueueOnTopicExchange(connection,exchange)

binding_keys = ['pml.eval.request', 'loan.validation.reply', 'pml.eval-services.reply']
bindQueuesToExchange(channel, exchange, queue_name, binding_keys)

control_exchange = 'fre.eval.control'
control_channel, control_queue = createQueueOnTopicExchange(connection,control_exchange)

print ' [%s] Waiting for events. To exit press CTRL+C' % (serviceName())

register(channel, on_message, queue_name)
run(channel)

# on_message runs here