#!/usr/bin/env python3
"""
Tornado web client example (solves C10k problem)
"""

import time

import tornado.httpclient
from tornado import gen
from tornado.ioloop import IOLoop


def handle_request(response):
    """
    Callback example
    """
    if response.error:
        print("Error:", response.error)
    else:
        print("handle_request: {0:d} characters".format(len(response.body)))


@gen.coroutine
def async_request(url):
    """
    Coroutine example
    """
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(url)
    if response.error:
        print("Error:", response.error)
    # Use for Python 2:
    # raise tornado.gen.Return(response.body)
    return response.body
    # Return Future that needs yield


@gen.engine
def get_request(url):
    """
    Get request
    """
    text = yield async_request(url)
    print("get_request: {0:d} characters".format(len(text)))
    print(text[:1024])


def main():
    """
    Start client to fetch "http://google.com"
    """
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch('http://google.com', handle_request)

    IOLoop.instance().add_callback(get_request, 'http://google.com')

    print("Starting IOLoop:", time.strftime('%Y-%m-%d-%H:%M:%S'))
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
