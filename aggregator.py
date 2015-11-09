#!/usr/bin/env python
import pika
import sys
import json
import time
 
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
    event = unpackMessage(method.routing_key,body)

    correlation_id = event["request_id"]
    if correlation_id not in wip:
      wip[correlation_id] = {"purchase":False, "credit":False, "finished":False}
  
    if method.routing_key == "contract.purchase-eligible.complete":
      wip[correlation_id]["purchase"] = True
 
    if method.routing_key == "borrower.credit-assessment.complete":
      wip[correlation_id]["credit"] = True
 
    if wip[correlation_id]["credit"] and wip[correlation_id]["purchase"] and not wip[correlation_id]["finished"]:
      wip[correlation_id]["finished"] = True
      rk = 'pml.eval-services.complete'
      publishEvent(ch,exchange,rk,time.time(),correlation_id,event)

def unpackMessage(rk,body):
  d = json.loads(body)
  id = d["request_id"]
  timestamp = d["timestamp"]
  print " [aggregator] Received %r:%r:%r" % (id,timestamp,rk)
  return d
 
def publishEvent(channel,exchange,routing_key,timestamp,id,event):
      event["timestamp"] = timestamp
      eventJSON = json.dumps(event)
      channel.basic_publish(exchange=exchange,
                           routing_key=routing_key,
                           body=eventJSON)
      print " [aggregator] Sent     %r:%r:%r" % (id,timestamp,routing_key)
 
def consumeEvents(chan, qn):
  chan.basic_consume(handleEvents,
                    queue=qn,
                    no_ack=True)
  chan.start_consuming()

#
# Main
#
 
wip = {}
exchange = 'topic_loan_eval'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = createChannelOnTopicExchange(connection,exchange)
 
queue_name = getExclusiveQueue(channel)
 
binding_keys = ['contract.purchase-eligible.complete', 'borrower.credit-assessment.complete']
bindQueuesToExchange(exchange, queue_name, binding_keys)
 
print ' [aggregator] Waiting for events. To exit press CTRL+C'
 
consumeEvents(channel, queue_name)
