#!/usr/bin/env python
import pika
import sys
import json
import uuid
import time
 
def ULADDictionary():
    d = {
      "request_id": 12345678901234567890,
      "ulad": {},
      "events": {},
      "feedback": {}
    }
    return d
 
def createTopicExchangeOnChannel(host,exchange):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
 
    channel.exchange_declare(exchange=exchange, type='topic')
    return (connection, channel)
 
def createDefaultExchangeOnChannel(host, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
 
    channel.queue_declare(queue=queue)
    return (connection, channel)
 
def createMessage(d,id,timestamp):
  d["request_id"]=id.hex
  d["timestamp"]=timestamp
  message=json.dumps(d)
  return message
 
#
# Main
#
 
ulad = ULADDictionary()
 
# exchange = 'topic_loan_eval'
queue = 'eval.request'
# results = createTopicExchangeOnChannel('localhost',exchange)
results = createDefaultExchangeOnChannel('localhost',queue)
connection = results[0]
channel = results[1]
 
# routing_key = 'pml.eval.request'
 
countTxt = sys.argv[1] or '1'
 
for i in range(int(countTxt)):
  id = uuid.uuid4()
  start = time.time()
  message=createMessage(ulad,id,start)
 
  channel.basic_publish(exchange='',
         routing_key=queue,
         body=message)
  print " [mock_client] Sent %r:%r:%r" % (str(id),start,queue)
 
connection.close()