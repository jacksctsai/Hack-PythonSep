# -*- coding: utf-8 -*-
import zmq


class ZmqSubscriber(object):
    def __init__(self, publish_endpoint, publish_id):
        context = zmq.Context()

        # connect to tetris server
        self._subscriber = context.socket(zmq.SUB)
        self._subscriber.connect(publish_endpoint)
        self._subscriber.setsockopt(zmq.SUBSCRIBE, publish_id)

        # initialize poll set
        self._poller = zmq.Poller()
        self._poller.register(self._subscriber, zmq.POLLIN)


    def poll(self):
        socks = dict(self._poller.poll(0))
        if self._subscriber not in socks:
            return ''
        if socks[self._subscriber] != zmq.POLLIN:
            return ''

        recv_str = self._subscriber.recv()
        (_, code_str) = recv_str.split(None, 1) # strip publish_id
        return code_str
