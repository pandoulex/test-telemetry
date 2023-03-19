#!/usr/bin/python
from __future__ import unicode_literals

import logging
import random
import socket
import time

import prometheus_client
from prometheus_client import CollectorRegistry

from lib.metric import GraphiteBridge
from lib.log import CustomLogger

registry = CollectorRegistry()

counter = prometheus_client.Counter(
    name='counter_1',
    namespace='test',
    subsystem='counter',
    documentation='a counter',
    registry=registry
)

gauge = prometheus_client.Gauge(
    name='gauge_1',
    namespace='test',
    subsystem='gauge',
    documentation='a gauge',
    registry=registry
)

summary = prometheus_client.Summary(
    name='summary_1',
    namespace='test',
    subsystem='summary',
    documentation='a summary',
    registry=registry
)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8000)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)

    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.INFO)
    ch = CustomLogger(sock)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    bridge = GraphiteBridge(sock, registry=registry, tags=True)
    metric_thread = bridge.start()

    try:
        loop = 0
        while True:
            loop += 1
            time.sleep(5)
            counter.inc()
            gauge.set(random.randint(0, 100))
            summary.observe(random.random())
            if loop % 6 == 0:
                try:
                    raise AttributeError('test exception')
                except Exception as err:
                    logger.exception("an error occured:")
            else:
                logger.info("an info log with random value: %s", random.random())
    finally:
        sock.close()


if __name__ == '__main__':
    main()
