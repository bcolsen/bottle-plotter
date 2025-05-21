#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
"""
Main Bottle application for serving plot applications.

This module handles routing and serves static files and dynamic plot
visualizations.
"""


import matplotlib
from bottle import route, run, template, static_file, error
import plots.ash_plot
import plots.example_plot
import plots.ce_plot
matplotlib.use('Agg')


@route("/")
def home():
    return template('home')


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@error(404)
def error404(error):
    return "Error 404: Page not found."


if __name__ == '__main__':
    import os
    app_host = os.environ.get('APP_HOST', '0.0.0.0')
    app_port = int(os.environ.get('APP_PORT', 8080))
    app_debug = os.environ.get(
        'APP_DEBUG',
        'False').lower() in (
        'true',
        '1',
        't')
    run(host=app_host, port=app_port, debug=app_debug, reload=True)
