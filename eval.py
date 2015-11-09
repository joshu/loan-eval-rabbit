#!/usr/bin/env python
import pika
import sys
import json
import time
import uuid
 
def createChannelOnTopicExchange(connection,exchange):
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,type='topic')
    return channel
 
def getExclusiveQueue(channel):
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    return queue_name
 
def bindQueuesToExchange(exchange, queue_name, bindingKeys):
    for binding_key in  bindingKeys:
      channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=binding_key)
 
def handleEvents(ch, method, properties, body):
    exchange = 'topic_loan_eval'
    event = json.loads(body)
    id = event["request_id"]
    uid = uuid.UUID(id)
    timestamp = event["timestamp"]
#    print " [eval] Received %r:%r:%r" % (id,timestamp,method.routing_key)
 
    if method.routing_key == "pml.eval.request":
#      print " [eval] Start time for %r = %r" % (str(uid),timestamp)
      start_time[id] = timestamp
      rk = 'loan.validation.request'
      publishEvent(ch,exchange,rk,time.time(),id,event)
 
    elif method.routing_key == "loan.validation.complete":
      rk = 'contract.purchase-eligible.request'
      publishEvent(ch,exchange,rk,time.time(),id,event)
      rk = 'borrower.credit-assessment.request'
      publishEvent(ch,exchange,rk,time.time(),id,event)
 
    elif method.routing_key == "pml.eval-services.complete":
      complete_time = time.time()
      response_time = complete_time - start_time[id]
      print " [eval] Response time: %r:%r" % (str(uid),response_time)
      rk = 'pml.loan-eval.complete'
      publishEvent(ch,exchange,rk,complete_time,id,event)
 
def publishEvent(channel,exchange,routing_key,timestamp,id,event):
      event["timestamp"] = timestamp
      eventJSON = json.dumps(event)
      channel.basic_publish(exchange=exchange,
                           routing_key=routing_key,
                           body=eventJSON)
#      print " [eval] Sent     %r:%r:%r" % (id,timestamp,routing_key)
 
#
# Main
#

start_time = {}
exchange = 'topic_loan_eval'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = createChannelOnTopicExchange(connection,exchange)
 
queue_name = getExclusiveQueue(channel)
 
binding_keys = ['pml.eval.request', 'loan.validation.complete', 'pml.eval-services.complete']
bindQueuesToExchange(exchange, queue_name, binding_keys)
 
print ' [eval] Waiting for events. To exit press CTRL+C'
 
channel.basic_consume(handleEvents,
                      queue=queue_name,
                      no_ack=True)
 
channel.start_consuming()