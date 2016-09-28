#!/usr/bin/env python3
"""
Simple Tornado web example
"""

import time

import tornado.web
from tornado import gen
from tornado.ioloop import IOLoop, PeriodicCallback


# pylint: disable = abstract-method
class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        print("Request received sleep 0.5 sec...")
        yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.5)
        self.write("Hello from Tornado web server: {0:s}".format(
            time.strftime('%Y-%m-%d-%H:%M:%S')))
        self.finish()
        # Or use "self.render()" that calls "self.finish()" as well
# pylint: enable = abstract-method


def heartbeat():
    print('heartbeat:', time.strftime('%Y-%m-%d-%H:%M:%S'))


@gen.engine
def shutdown(delay):
    yield gen.Task(IOLoop.instance().add_timeout, time.time() + delay)
    print("Shutting down web server...")
    IOLoop.instance().stop()


if __name__ == '__main__':
    print("Web server on port 8888...")
    app = tornado.web.Application([("/", MainHandler), ])
    app.listen(8888)

    print("PeriodicCallback for heartbeat every 5 seconds")
    PeriodicCallback(heartbeat, 5000).start()

    print("Callback for delayed IOLoop stop after 60 seconds...")
    IOLoop.instance().add_callback(shutdown, 60)

    print("Starting IOLoop:", time.strftime('%Y-%m-%d-%H:%M:%S'))
    IOLoop.instance().start()
