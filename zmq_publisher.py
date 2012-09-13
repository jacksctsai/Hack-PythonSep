# -*- coding: utf-8 -*-
import zmq


class ZmqPublisher(object):
    def __init__(self, publish_endpoint, publish_id):
        self._publish_id = publish_id

        context = zmq.Context()

        self._publisher = context.socket(zmq.PUB)
        self._publisher.bind(publish_endpoint)

    def publish(self, msg):
        self._publisher.send('%s %s' % (self._publish_id, msg))
