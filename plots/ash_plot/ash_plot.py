#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
"""
Handles the Average Shifted Histogram (ASH) plot generation and its
web interface using Bottle.

This module defines the route for the ASH plot, handles form submissions
for customizing the plot, and generates the ASH plot image.
"""
import numpy as np
import pylab as plt
import seaborn as sns
from io import BytesIO
import os
import base64
import bottle
from bottle import route, response, template, request
from wtforms import (Form, StringField, TextAreaField, validators)
from .. import form_valid as fv
from .ASH.ash import ash


# Read default data from file
default_data = ""
try:
    with open(os.path.join(os.path.dirname(__file__),
                           'ash_default_data.txt'), 'r') as f:
        default_data = f.read()
except FileNotFoundError:
    # Fallback or error logging if needed, for now, using an empty string
    # or a predefined string as in the original paper_data.
    # For this task, we assume the file is present.
    pass

plt.rcParams['svg.fonttype'] = 'none'

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


@route("/ash", method=['POST', 'GET'])
def plot():
    """
    Handles GET and POST requests for the ASH plot page.

    On GET, displays the form with default values.
    On POST, validates form data, generates the ASH plot, and either
    returns the plot as a downloadable file or embeds it in the page.
    """
    form = DataForm(request.forms)
    img = ''
    action = request.forms.get('action', '').strip()

    if request.method == 'POST' and action == 'clear':
        form.xlabel.data = ''
        form.data.data = default_data  # Reset to default on clear
        form.color.data = form.color.default
        form.fill_color.data = form.fill_color.default
        filled_flag = False
    elif request.method == 'POST' and form.validate():
        data_list = fv.data_split(form.data.data)
        xlabel = form.xlabel.data
        color = form.color.data
        fill_color = form.fill_color.data
        filled_flag = True

        if action == 'svg_download':
            response.content_type = 'image/svg+xml'  # Corrected MIME type
            response.set_header(
                "Content-disposition",
                "attachment; filename=ash_plot.svg")
            return generate_ash_plot_image(
                data_list,
                xlabel,
                chart_type='svg',
                color=color,
                fill_color=fill_color)
        elif action == 'png_download':
            response.content_type = 'image/png'
            response.set_header(
                "Content-disposition",
                "attachment; filename=ash_plot.png")
            return generate_ash_plot_image(
                data_list,
                xlabel,
                chart_type='pngat',
                color=color,
                fill_color=fill_color)
        else:  # Display plot on page
            img_data = generate_ash_plot_image(
                data_list,
                xlabel,
                chart_type='png',
                color=color,
                fill_color=fill_color)
            img = base64.b64encode(img_data).decode(
                'utf-8')  # Ensure string for template
    else:
        # Initial GET request or validation failed
        if not form.is_submitted():  # For initial GET
            form.data.data = default_data
            form.color.data = form.color.default
            form.fill_color.data = form.fill_color.default
        filled_flag = False
        # If form.errors exist, they will be available in the template.
        # A good follow-up would be to explicitly display form.errors in
        # ash_app.tpl.

    return template('ash_app', filled=filled_flag, form=form, img=img)


class DataForm(Form):
    """
    WTForm for collecting ASH plot parameters from the user.
    Includes fields for data, x-axis label, line color, and fill color.
    """
    data = TextAreaField(
        'Data copied from a table or ' +
        'separated by commas (5 to 100000 points)',
        [validators.InputRequired(),
         fv.DataLength(min=5, max=100000,
                       message='Data must be comma or line separated and ' +
                               'have 5 to 100000 values'),
         fv.DataFloat()],
        default=default_data)
    xlabel = StringField(
        'X-axis Label',
        [validators.Optional(),
         validators.Length(min=0, max=50, message='Longer than 50 characters')],
        default='')
    color = StringField(
        'Line Color',  # Default is set here
        [validators.InputRequired(),
         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                           message="Not valid HTML rgb hex color "
                                   "(eg. #4C72B0)")],
        default='#4C72B0')
    fill_color = StringField(
        'Fill Color',  # Default is set here
        [validators.InputRequired(),
         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                           message="Not valid HTML rgb hex color "
                                   "(eg. #4C72B0)")],
        default='#92B2E7')


def generate_ash_plot_image(data, xlabel=None, chart_type="png",
                            color=None, fill_color=None):
    """
    Generates an Average Shifted Histogram (ASH) plot image.

    Args:
        data (list): A list of numerical data points.
        xlabel (str, optional): Label for the x-axis. Defaults to None.
        chart_type (str, optional): Type of chart to generate ('png', 'svg',
                                    'pngat'). 'pngat' is for high-res PNG.
                                    Defaults to "png".
        color (str, optional): Hex color string for the plot line and markers.
                               Defaults to '#4C72B0' if None.
        fill_color (str, optional): Hex color string for the area under the
                                    ASH curve. Defaults to '#92B2E7' if None.

    Returns:
        bytes: The generated plot image in the specified format.
    """
    # Default colors if not provided
    final_color = color if color is not None else '#4C72B0'
    final_fill_color = fill_color if fill_color is not None else '#92B2E7'

    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 6))
    fig.clf()

    a = np.array(data, dtype=float)
    bins = None  # Let ASH determine bins

    # force_scott for consistency
    ash_obj_a = ash(a, bin_num=bins, force_scott=True)

    ax = plt.subplot(111)
    ax.plot(ash_obj_a.ash_mesh, ash_obj_a.ash_den, lw=2, color=final_color)

    # plot the solid ASH
    ash_obj_a.plot_ash_infill(ax, color=final_fill_color, alpha=1)

    # barcode like data representation
    ash_obj_a.plot_rug(ax, alpha=1, color=final_color)

    # put statistics on the graph
    ash_obj_a.plot_stats(ax, color=final_color)

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
    # Determine DPI and format based on chart_type
    if chart_type == 'svg':
        type_form = 'svg'
        # DPI for SVG might not be strictly necessary but good for consistency
        dpi = 300
    elif chart_type == 'pngat':  # High-res PNG
        type_form = 'png'
        dpi = 300
    else:  # Standard 'png' for web display
        type_form = 'png'
        dpi = 100

    fig.savefig(outs, dpi=dpi, format=type_form)
    img_bytes = outs.getvalue()
    outs.close()
    plt.close(fig)  # Close the figure to free memory
    return img_bytes
