#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
from __future__ import division, print_function

from bottle import route, run, template, static_file

import matplotlib
matplotlib.use('Agg')

import plots.ash_plot
import plots.ce_plot
import plots.example_plot

"""
Plotting form data in bottle
"""
static_dir = "/var/www/plot/static/"


@route("/")
def home():
    return template('home')


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reload=True)
