#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
"""
Handles an example plot generation and its web interface using Bottle.

This module defines the route for an example plot, handles form submissions
for customizing the plot (data, labels, colors), and generates the
plot image. It serves as a basic template for creating new plot types.
"""
import base64
import os
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import bottle
from bottle import route, response, template, request
from wtforms import (Form, StringField, TextAreaField, validators)

from .. import form_valid as fv
# import sys  # Unused


# Load default data from file
module_dir = os.path.dirname(__file__)
try:
    with open(os.path.join(module_dir, 'example_default_data.txt'), 'r') as f:
        default_data = f.read()
except FileNotFoundError:
    default_data = "0\n1\n2\n3\n4\n5"  # Fallback data

plt.rcParams['svg.fonttype'] = 'none'

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


@route("/example", method=['POST', 'GET'])
def plot_app():
    """
    Handles GET and POST requests for the example plot page.

    On GET, displays the form with default values.
    On POST, validates form data, generates the example plot, and either
    returns the plot as a downloadable file or embeds it in the page.
    """
    form = DataForm(request.forms)
    img = ''
    action = request.forms.get('action', '').strip()

    if request.method == 'POST' and action == 'clear':
        form.x_data.data = default_data
        form.y_data.data = default_data
        form.x_label.data = form.x_label.default  # Reset to WTForms default
        form.y_label.data = form.y_label.default  # Reset to WTForms default
        form.color.data = form.color.default
        filled_flag = False
    elif request.method == 'POST' and form.validate():
        x_data_list = fv.data_split(form.x_data.data)
        y_data_list = fv.data_split(form.y_data.data)
        x_label = form.x_label.data
        y_label = form.y_label.data
        line_color = form.color.data  # Use submitted color
        filled_flag = True

        if action == 'svg_download':
            response.content_type = 'image/svg+xml'  # Corrected MIME type
            response.set_header(
                "Content-disposition",
                "attachment; filename=example_plot.svg")  # Corrected filename
            return generate_example_plot_image(
                x_data_list,
                y_data_list,
                x_label,
                y_label,
                chart_type='svg',
                color=line_color)
        elif action == 'png_download':
            response.content_type = 'image/png'
            response.set_header(
                "Content-disposition",
                "attachment; filename=example_plot.png")  # Corrected filename
            return generate_example_plot_image(
                x_data_list,
                y_data_list,
                x_label,
                y_label,
                chart_type='pngat',
                color=line_color)
        else:  # Display plot on page
            img_data = generate_example_plot_image(
                x_data_list,
                y_data_list,
                x_label,
                y_label,
                chart_type='png',
                color=line_color)
            img = base64.b64encode(img_data).decode(
                'utf-8')  # Ensure string for template
    else:
        # Initial GET request or validation failed
        if not form.is_submitted():  # For initial GET
            form.x_data.data = default_data
            form.y_data.data = default_data
            # Labels and color will use WTForms defaults defined in the class
        filled_flag = False
        # form.errors will be available in the template if validation failed

    return template('example_app', filled=filled_flag, form=form, img=img)


class DataForm(Form):
    """
    WTForm for collecting example plot parameters from the user.
    Includes fields for X and Y data, X and Y axis labels, and line color.
    Default data for X and Y is loaded from an external file.
    """
    x_data = TextAreaField(
        'X Data:',
        [validators.InputRequired(),
         fv.DataLength(min=2, max=100000,
                       message='Data must be comma or line separated and '
                               'have 2 to 100000 values'),
         fv.DataFloat()],
        default=default_data)  # Default loaded from file
    y_data = TextAreaField(
        'Y Data:',
        [validators.InputRequired(),
         fv.DataLength(min=2, max=100000,
                       message='Data must be comma or line separated and '
                               'have 2 to 100000 values'),
         fv.DataLengthEqual('x_data',
                            message='Y data must be the same length as X data'),
         fv.DataFloat()],
        default=default_data)  # Default loaded from file
    x_label = StringField(
        'X-axis Label:',
        [validators.Optional(),
         validators.Length(min=0, max=50, message='Longer than 50 characters')],
        default='')  # Default set here (empty string)
    y_label = StringField(
        'Y-axis Label:',
        [validators.Optional(),
         validators.Length(min=0, max=50, message='Longer than 50 characters')],
        default='')  # Default set here (empty string)
    color = StringField(
        'Line Color:',
        [validators.InputRequired(),
         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                           message='Not valid HTML rgb hex color '
                                   '(eg. #4C72B0)')],
        default='#4C72B0')  # Default set here


def generate_example_plot_image(x_data, y_data, x_label=None, y_label=None,
                                chart_type="png", color=None):
    """
    Generates an example plot image.

    Args:
        x_data (list): X-axis data.
        y_data (list): Y-axis data.
        x_label (str, optional): Label for the x-axis. Defaults to None.
        y_label (str, optional): Label for the y-axis. Defaults to None.
        chart_type (str, optional): Type of chart ('png', 'svg', 'pngat').
                                    Defaults to "png".
        color (str, optional): Hex color for the plot line. Defaults to
                               '#4C72B0' if None.

    Returns:
        bytes: The generated plot image in the specified format.
    """
    final_color = color if color is not None else '#4C72B0'
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 5.5))
    # fig.clf() # Not strictly necessary as figure is new
    ax = fig.add_subplot(111)

    x_data_np = np.array(x_data, dtype=float)
    y_data_np = np.array(y_data, dtype=float)
    ax.plot(x_data_np, y_data_np, color=final_color)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out')

    if y_label:
        ax.set_ylabel(y_label)
    if x_label:
        ax.set_xlabel(x_label)

    plt.tight_layout()

    outs = BytesIO()
    # Determine DPI and format based on chart_type
    if chart_type == 'svg':
        img_format = 'svg'
        dpi = 300
    elif chart_type == 'pngat':  # High-res PNG
        img_format = 'png'
        dpi = 300
    else:  # Standard 'png' for web display
        img_format = 'png'
        dpi = 100

    fig.savefig(outs, dpi=dpi, format=img_format)
    img_bytes = outs.getvalue()
    outs.close()
    plt.close(fig)  # Free memory
    return img_bytes
