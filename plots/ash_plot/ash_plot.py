#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
from __future__ import division, print_function

import pylab as plt
import numpy as np
import seaborn as sns

from io import BytesIO
import os
import base64

import bottle
from bottle import route, response, template, request
from wtforms import (Form, StringField, TextAreaField, validators)

from .ASH.ash import ash

from .. import form_valid as fv

paper_data = '-0.38763\n0.80928\n1.5736\n-0.19156\n-1.2762\n0.012471\n' + \
             '2.7392\n-0.14373\n1.5309\n-0.71012\n2.6883\n-0.97024\n' + \
             '-0.18379\n0.39052\n0.89383\n-0.28856\n-0.82227\n-1.2461\n' + \
             '2.8595\n0.50082'

plt.rcParams['svg.fonttype'] = 'none'

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


@route("/ash", method=['POST', 'GET'])
def plot():
    form = DataForm(request.forms)
    filled = request.forms.get('filled', '').strip()
    svg = request.forms.get('svg_download', '').strip()
    png = request.forms.get('png_download', '').strip()
    clear = request.forms.get('clear', '').strip()

    img = ''

    if clear:
        filled = None
        form.xlabel.data = ''
        form.data.data = ''
        form.color.data = form.color.default
        form.fill_color.data = form.fill_color.default
    elif filled and form.validate():
        data_list = fv.data_split(form.data.data)
        xlabel = form.xlabel.data
        color = form.color.data
        fill_color = form.fill_color.data
        if svg:
            chart_type = 'svg'
            response.content_type = 'image/svg'
            response.set_header("Content-disposition",
                                "attachment; filename=ash_plot.svg")
            return ash_png(data_list, xlabel, chart_type, color, fill_color)
        elif png:
            chart_type = 'pngat'
            response.content_type = 'image/png'
            response.set_header("Content-disposition",
                                "attachment; filename=ash_plot.png")
            return ash_png(data_list, xlabel, chart_type, color, fill_color)
        else:
            chart_type = 'png'
            img = base64.b64encode(ash_png(data_list, xlabel, chart_type,
                                           color, fill_color))
    else:
        filled = None

    return template('ash_app', filled=filled, form=form, img=img)


class DataForm(Form):
    data = TextAreaField('Data copied from a table or ' +
                         'separated by commas (5 to 100000 points)',
                         [validators.InputRequired(),
                          fv.DataLength(min=5, max=100000,
                                    message='Data must be comma or line ' +
                                    'separated and have 5 to 100000 values'),
                          fv.DataFloat()],
                         default=paper_data)
    xlabel = StringField('X-axis Label',
                         [validators.Optional(),
                          validators.Length(min=0, max=50,
                                            message='Longer than 50 ' +
                                                    'characters')],
                         default='')
    color = StringField('Line Color',
                        [validators.InputRequired(),
                         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                                           message="Not valid HTML rgb hex color (eg. #4C72B0)")],
                        default='#4C72B0')
    fill_color = StringField('Fill Color',
                             [validators.InputRequired(),
                              validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                                                message="Not valid HTML rgb hex color (eg. #4C72B0)")],
                             default='#92B2E7')


def ash_png(data, xlabel=None, chart_type="png",
            color='#4C72B0', fill_color='#92B2E7'):
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 6))
    fig.clf()

    a = np.array(data, dtype=float)
    bins = None

    ash_obj_a = ash(a, bin_num=bins, force_scott=True)

    ax = plt.subplot(111)
    ax.plot(ash_obj_a.ash_mesh, ash_obj_a.ash_den, lw=2, color=color)

    # plot the solid ASH
    ash_obj_a.plot_ash_infill(ax, color=fill_color, alpha=1)

    # barcode like data representation
    ash_obj_a.plot_rug(ax, alpha=1, color=color)

    # put statistics on the graph
    ash_obj_a.plot_stats(ax, color=color)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out')
    ax.set_yticks([])

    if xlabel:
        plt.xlabel(xlabel)
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)

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
