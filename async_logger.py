from pika.adapters.twisted_connection import TwistedProtocolConnection
from pika.connection import ConnectionParameters
from twisted.internet import protocol, reactor, task
from twisted.python import log
import uuid
import json
import os


class Consumer(object):
    def on_connected(self, connection):
        d = connection.channel()
        d.addCallback(self.got_channel)
        d.addCallback(self.queue_declared)
        d.addCallback(self.queue_bound)
        d.addCallback(self.handle_deliveries)
        d.addErrback(log.err)

    def got_channel(self, channel):
        self.channel = channel

        return self.channel.queue_declare(exclusive=True)

    def queue_declared(self, queue):
        self._queue_name = queue.method.queue

        self.channel.queue_bind(queue=self._queue_name,
                                exchange="topic_loan_eval",
                                routing_key="*.*.*")

    def queue_bound(self, ignored):
        return self.channel.basic_consume(queue=self._queue_name)

    def handle_deliveries(self, queue_and_consumer_tag):
        queue, consumer_tag = queue_and_consumer_tag
        self.looping_call = task.LoopingCall(self.consume_from_queue, queue)

        return self.looping_call.start(0)

    def consume_from_queue(self, queue):
        d = queue.get()

        return d.addCallback(lambda result: self.handle_payload(*result))

    def handle_payload(self, channel, method, properties, body):
        self.logReceive(method.routing_key,body)

    def serviceName(self):
			file_name = (os.path.basename(__file__))
			return file_name.split('.')[0]

    def logReceive(self, routing_key, message):
      eval_request = json.loads(message)
      print(message)
      uid = uuid.UUID(eval_request["request_id"])
      print " [%s] Received %r:%r:%r" % (self.serviceName(),
        str(uid),eval_request["timestamp"],routing_key)


if __name__ == "__main__":
    consumer1 = Consumer()
    # consumer2 = Consumer()

    parameters = ConnectionParameters()
    cc = protocol.ClientCreator(reactor,
                                TwistedProtocolConnection,
                                parameters)
    d1 = cc.connectTCP("localhost", 5672)
    d1.addCallback(lambda protocol: protocol.ready)
    d1.addCallback(consumer1.on_connected)
    d1.addErrback(log.err)

    # d2 = cc.connectTCP("localhost", 5672)
    # d2.addCallback(lambda protocol: protocol.ready)
    # d2.addCallback(consumer2.on_connected)
    # d2.addErrback(log.err)

    reactor.run()
