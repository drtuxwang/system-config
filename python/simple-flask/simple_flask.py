#!/usr/bin/env python3
"""
Simple Flask test
"""

import sys

import flask

# pylint: disable = invalid-name
app = flask.Flask(__name__)
# pylint: enable = invalid-name


@app.route('/')
def default():
    """
    Default
    """
    return 'I am simple Flask demo!'


@app.route('/healthcheck')
def health_check():
    """
    Perform health check
    """
    return 'I am healthy!'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    """
    Uses jinja2 template generate greeting
    """
    return flask.render_template('hello.html', name=name)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        app.run()
