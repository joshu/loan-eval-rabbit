class MessageGateway(object):
  def __init__(self, exchange, host):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.channel = createChannelOnTopicExchange(self.connection,exchange)
		self.queue_name = createExclusiveQueue(self.channel)

  def createChannelOnTopicExchange(conection, exchange):
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, type='topic')
    return channel

  def createExclusiveQueue(self, channel):
	  self.result = channel.queue_declare(exclusive=True)
	  self.queue_name = self.result.method.queue
	  return self.queue_name

	def bindQueuesToExchange(self,exchange,queue_name,binding_keys):
	  for binding_key in binding_keys:
	    self.channel.queue_bind(exchange=exchange,
	                       queue=queue_name,
	                       routing_key=binding_key)

	def publishEvent(self, channel, exchange, routing_key, message_dict):
	  self.newBody = json.dumps(message_dict)
	  self.channel.basic_publish(exchange=exchange,
	                       routing_key=routing_key,
	                       body=self.newBody)

	def consumeEvents(self, chan, qn):
	  self.chan.basic_consume(handleEvents,
	                    queue=qn,
	                    no_ack=True)
	  self.chan.start_consuming()
