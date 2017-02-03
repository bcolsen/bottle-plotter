#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
from __future__ import division, print_function

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from io import BytesIO
import base64
import os
import sys

import bottle
from bottle import route, response, template, request
from wtforms import (Form, StringField, TextAreaField, validators)

from .. import form_valid as fv

example_data = '0.0\n1.0\n2.0\n3.0\n4.0\n5.0\n6.0\n7.0\n8.0\n9.0\n10.0'

plt.rcParams['svg.fonttype'] = 'none'

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@route("/example", method=['POST', 'GET'])
def plot_app():
    form = DataForm(request.forms)
    filled = request.forms.get('filled', '').strip()
    svg = request.forms.get('svg_download', '').strip()
    png = request.forms.get('png_download', '').strip()
    clear = request.forms.get('clear', '').strip()

    img = ''

    if clear:
        filled = None
        form.x_data.data = ''
        form.y_data.data = ''
        form.x_label.data = ''
        form.x_label.data = ''
        form.color.data = form.color.default
        form.color.data = form.color.default
    elif filled and form.validate():
        x_data_list = fv.data_split(form.x_data.data)
        y_data_list = fv.data_split(form.y_data.data)
        x_label = form.x_label.data
        y_label = form.y_label.data
        color = form.color.data
        if svg:
            chart_type = 'svg'
            response.content_type = 'image/svg'
            response.set_header("Content-disposition",
                                "attachment; filename=ce_plot.svg")
            return make_plot(x_data_list, y_data_list, x_label, y_label,
                             chart_type, color)
        elif png:
            chart_type = 'pngat'
            response.content_type = 'image/png'
            response.set_header("Content-disposition",
                                "attachment; filename=ce_plot.png")
            return make_plot(x_data_list, y_data_list, x_label, y_label,
                             chart_type, color)
        else:
            chart_type = 'png'
            img = base64.b64encode(make_plot(x_data_list, y_data_list, x_label,
                                             y_label, chart_type, color))
    else:
        filled = None
    return template('example_app', filled=filled, form=form, img=img)


class DataForm(Form):
    x_data = TextAreaField('X Data:',
                           [validators.InputRequired(),
                            fv.DataLength(min=2, max=100000,
                                          message='Data must be comma or ' +
                                          'line separated and have 2 to ' +
                                          '100000 values'),
                            fv.DataFloat()],
                           default=example_data)
    y_data = TextAreaField('Y Data:',
                           [validators.InputRequired(),
                            fv.DataLength(min=2, max=100000,
                                          message='Data must be comma or ' +
                                          'line separated and have 2 to ' +
                                          '100000 values'),
                            fv.DataLengthEqual('x_data',
                                               message='Y data must be the ' +
                                               'same length as X data'),
                            fv.DataFloat()],
                           default=example_data)
    x_label = StringField('X-axis Label:',
                          [validators.Optional(),
                           validators.Length(min=0, max=50,
                                             message='Longer than 50 ' +
                                             'characters')],
                          default='')
    y_label = StringField('Y-axis Label:',
                          [validators.Optional(),
                           validators.Length(min=0, max=50,
                                             message='Longer than 50 ' +
                                             'characters')],
                          default='')
    color = StringField('Line Color:',
                        [validators.InputRequired(),
                         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", 
                                           message='Not valid HTML rgb hex ' +
                                           'color (eg. #4C72B0)')],
                        default='#4C72B0')


def make_plot(x_data, y_data, x_label=None, y_label=None,
              chart_type="png", color='#4C72B0'):
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 5.5))
    fig.clf()
    ax = plt.subplot(111)

    x_data = np.array(x_data, dtype=float)
    y_data = np.array(y_data, dtype=float)
    plt.plot(x_data, y_data, color=color)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out')

    if y_label:
        plt.ylabel(y_label)
    if x_label:
        plt.xlabel(x_label)

    plt.tight_layout()

    outs = BytesIO()
    fig.canvas.draw()

    if chart_type == 'pdf':
        type_form = 'pdf'
        dpi = 300
    elif chart_type == 'svg':
        type_form = 'svg'
        dpi = 300
    elif chart_type == 'pngat':
        type_form = 'png'
        dpi = 300
    else:
        type_form = 'png'
        dpi = 100
    fig.savefig(outs, dpi=dpi, format=type_form)
    img = outs.getvalue()
    outs.close()
    return img
