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
import base64
import os
import sys

from matplotlib.ticker import MaxNLocator, Locator

import bottle
from bottle import route, response, template, request
from wtforms import (Form, StringField, TextAreaField, validators)

from .. import form_valid as fv

battery_data = '87.29\n98.65\n99.25\n99.49\n99.63\n99.70\n99.76\n99.81\n' + \
               '99.85\n99.87\n99.89\n99.91\n99.93\n99.94\n99.96'
cycle_data = '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15'

plt.rcParams['svg.fonttype'] = 'none'

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@route("/ce", method=['POST', 'GET'])
def plot_ce():
    form = DataForm_CE(request.forms)
    filled = request.forms.get('filled', '').strip()
    svg = request.forms.get('svg_download', '').strip()
    png = request.forms.get('png_download', '').strip()
    clear = request.forms.get('clear', '').strip()

    img = ''

    if clear:
        filled = None
        form.x_label.data = ''
        form.x_data.data = ''
        form.y_label.data = ''
        form.y_data.data = ''
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
            return ce_png(x_data_list, y_data_list,
                          x_label, y_label, chart_type, color)
        elif png:
            chart_type = 'pngat'
            response.content_type = 'image/png'
            response.set_header("Content-disposition",
                                "attachment; filename=ce_plot.png")
            return ce_png(x_data_list, y_data_list, x_label,
                          y_label, chart_type, color)
        else:
            chart_type = 'png'
            img = base64.b64encode(ce_png(x_data_list, y_data_list,
                                          y_label, x_label, chart_type, color))
    else:
        filled = None
    return template('ce_app', filled=filled, form=form, img=img)


class DataForm_CE(Form):
    x_data = TextAreaField('Cycle Number',
                           [validators.InputRequired(),
                            fv.DataLength(min=2, max=100000,
                                          message='Data must be comma or ' +
                                          'line separated and have 2 to ' +
                                          '100000 values'),
                            fv.DataFloat()],
                           default=cycle_data)
    y_data = TextAreaField('Battery CE',
                           [validators.InputRequired(),
                            fv.DataLength(min=2, max=100000,
                                          message='Data must be comma or ' +
                                          'line separated and have 2 to ' +
                                          '100000 values'),
                            fv.DataLengthEqual('x_data',
                                               message='CE must have the ' +
                                               'same number of point as ' +
                                               'cycles'),
                            fv.DataFloat()],
                           default=battery_data)
    x_label = StringField('X-axis Label',
                          [validators.Optional(),
                           validators.Length(min=0, max=50,
                                             message='Longer than 50 ' +
                                             'characters')],
                          default='Cycle Number')
    y_label = StringField('Y-axis Label',
                          [validators.Optional(),
                           validators.Length(min=0, max=50,
                                             message='Longer than 50 ' +
                                             'characters')],
                          default='Coulombic Efficiency (%)')
    color = StringField('Marker Color',
                        [validators.InputRequired(),
                         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", 
                                           message='Not valid HTML rgb hex ' +
                                           'color (eg. #4C72B0)')],
                        default='#4C72B0')


class MinorSymLogLocator(Locator):
    """
    Dynamically find minor tick positions based on the positions of
    major ticks for a symlog scaling.
    """
    def __init__(self, linthresh):
        """
        Ticks will be placed between the major ticks.
        The placement is linear for x between -linthresh and linthresh,
        otherwise its logarithmically
        """
        self.linthresh = linthresh

    def __call__(self):
        'Return the locations of the ticks'
        majorlocs = self.axis.get_majorticklocs()

        # iterate through minor locs
        minorlocs = []

        # handle the lowest part
        for i in range(1, len(majorlocs)):
            majorstep = majorlocs[i] - majorlocs[i-1]
            if abs(majorlocs[i-1] + majorstep/2) < self.linthresh:
                ndivs = 10
            else:
                ndivs = 9
            minorstep = majorstep / ndivs
            locs = np.arange(majorlocs[i-1], majorlocs[i], minorstep)[1:]
            minorlocs.extend(locs)

        return self.raise_if_exceeds(np.array(minorlocs))

    def tick_values(self, vmin, vmax):
        raise NotImplementedError('Cannot get tick locations for a '
                                  '%s type.' % type(self))


def ce_plot(x_data, y_data, ax=None, linthresh=0.1, **kwargs):
    y_data = np.array(y_data, dtype=float)
    y_data = y_data*100 if y_data.max() < 2 else y_data
    if ax is None:
        plt.plot(x_data, y_data-100, **kwargs)
    else:
        ax.plot(x_data, y_data-100, **kwargs)
    plt.yscale('symlog', linthreshy=linthresh)
    plt.gca().get_yaxis().set_minor_locator(MinorSymLogLocator(linthresh))
    plt.tick_params(axis='y', which='minor')
    loc, labels = plt.yticks()
    plt.yticks(loc, (loc + 100))
    plt.grid(b=True, which='major', axis='y', color=(0.9, 0.9, 0.9),
             linestyle='-')
    plt.grid(b=True, which='minor', color=(0.9, 0.9, 0.9), linestyle='-',
             linewidth=0.5)
    plt.gca().get_xaxis().set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()


def ce_png(x_data, y_data, x_label, y_label, chart_type="png",
           fill_color='#4C72B0'):
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 5.5))
    fig.clf()
    ax = plt.subplot(111)
    ce_plot(x_data, y_data, ax=ax, marker='o', mfc=fill_color, lw=0)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out')
    if y_label:
        plt.ylabel(y_label)
    if x_label:
        plt.xlabel(x_label)

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
