#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bottle Web Application for Generating Example X-Y Plots.

This script implements a web application using the Bottle framework to create
simple X-Y line plots. Users can input paired X and Y numerical data,
specify axis labels and line color, and then visualize the generated plot
directly on the web page or download it as an SVG or PNG image.

The application utilizes:
-   Bottle: As the micro web-framework for routing and request handling.
-   WTForms: For creating and validating the web form used for data input.
-   Matplotlib & Seaborn: For generating the plots.
-   form_valid: A custom module (presumably `plots.form_valid`) for custom
    form field validation.

Key functionalities include:
-   Displaying a form to input X and Y data series, axis labels, and line color.
-   Validating user input, including ensuring X and Y data have equal length.
-   Generating line plots based on valid input.
-   Displaying the plot as a base64 encoded PNG image on the web page.
-   Allowing users to download the plot as an SVG or PNG file.
-   A "Clear" functionality to reset the form fields.

The main route is `/example`, which handles both GET (displaying the form) and
POST (processing data and generating the plot) requests.
"""
# Original creation details:
# Created on Fri Aug  5 11:34:19 2016
# @author: bcolsen

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

from .. import form_valid as fv # Custom form validators

# Default data for the X and Y data form fields
example_data = '0.0\n1.0\n2.0\n3.0\n4.0\n5.0\n6.0\n7.0\n8.0\n9.0\n10.0'

plt.rcParams['svg.fonttype'] = 'none' # Ensure fonts are not rasterized in SVG

# Setup template path for Bottle
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


def eprint(*args, **kwargs):
    """
    Prints the given arguments to the standard error stream (sys.stderr).

    This function is a simple wrapper around the built-in `print()` function,
    redirecting its output to stderr. This can be useful for logging errors
    or debug messages separately from standard output, especially in web
    server environments.

    Parameters
    ----------
    *args :
        Variable length argument list, passed directly to `print()`.
    **kwargs :
        Arbitrary keyword arguments, passed directly to `print()`.
        Common examples include `sep` or `end`.
    """
    print(*args, file=sys.stderr, **kwargs)


@route("/example", method=['POST', 'GET'])
def plot_app():
    """
    Handles requests for the example plot generation page (`/example`).

    For GET requests, it displays a web form (`DataForm`) allowing users to
    input X and Y data, axis labels, and line color.
    For POST requests, it processes the submitted form data. Based on the
    actions (generate plot, download SVG/PNG, or clear form):
    -   If form data is valid:
        -   'Download SVG/PNG': Calls `make_plot()` to generate the plot in the
            requested format and returns it as a file download. The filenames
            for download are currently hardcoded as 'ce_plot.svg'/'ce_plot.png',
            which might be a leftover from copying code and could be generalized.
        -   'Generate Plot' (default): Calls `make_plot()` to generate a PNG,
            encodes it in base64, and re-renders the page displaying the
            image and the populated form.
    -   'Clear': Resets the form fields to their default or empty values.
    -   If form data is invalid, it re-renders the page with validation errors.

    Returns
    -------
    bottle.HTTPResponse or str
        An HTTP response for file downloads, or an HTML string (rendered
        template) for displaying the page.
    """
    form = DataForm(request.forms)
    filled = request.forms.get('filled', '').strip() # Hidden field for submission state
    svg = request.forms.get('svg_download', '').strip() # SVG download button
    png = request.forms.get('png_download', '').strip() # PNG download button
    clear = request.forms.get('clear', '').strip() # Clear button

    img = '' # To store base64 encoded image for display

    if clear:
        filled = None # Mark form as not "filled"
        # Reset form fields
        form.x_data.data = form.x_data.default # Reset to default example_data
        form.y_data.data = form.y_data.default # Reset to default example_data
        form.x_label.data = form.x_label.default
        form.y_label.data = form.y_label.default # Corrected: y_label instead of x_label
        form.color.data = form.color.default
        # form.color.data = form.color.default # Duplicate line removed
    elif filled and form.validate(): # If form submitted and valid
        x_data_list = fv.data_split(form.x_data.data)
        y_data_list = fv.data_split(form.y_data.data)
        x_label = form.x_label.data
        y_label = form.y_label.data
        color = form.color.data
        if svg:
            chart_type = 'svg'
            response.content_type = 'image/svg+xml' # Correct MIME for SVG
            # TODO: Filename for download should be generic (e.g., 'example_plot.svg')
            response.set_header("Content-Disposition",
                                "attachment; filename=example_plot.svg") # Corrected filename
            return make_plot(x_data_list, y_data_list, x_label, y_label,
                             chart_type, color)
        elif png:
            chart_type = 'pngat' # High-DPI PNG for download
            response.content_type = 'image/png'
            # TODO: Filename for download should be generic
            response.set_header("Content-Disposition",
                                "attachment; filename=example_plot.png") # Corrected filename
            return make_plot(x_data_list, y_data_list, x_label, y_label,
                             chart_type, color)
        else: # Default action: display plot on page
            chart_type = 'png' # Standard DPI PNG for web display
            img_bytes = make_plot(x_data_list, y_data_list, x_label,
                                  y_label, chart_type, color)
            img = base64.b64encode(img_bytes).decode('ascii') # Encode for HTML
    else: # Form not submitted yet, or submitted but invalid
        filled = None # Ensures validation errors are shown if form was submitted and invalid

    # Render the template
    return template('example_app', filled=filled, form=form, img=img)


class DataForm(Form):
    """
    Defines the web form for collecting X-Y data and plot configuration.

    This WTForms class specifies fields for user input, including X data,
    Y data, axis labels, and line color for a simple X-Y plot. It includes
    validators to ensure data integrity, correct formatting, and that X and Y
    data series have the same number of points.

    Fields
    ------
    x_data : TextAreaField
        Input for X-axis numerical data. Validated for being required, data
        length (2 to 100,000 points), and float convertibility. Defaults to
        `example_data`.
    y_data : TextAreaField
        Input for Y-axis numerical data. Validated for being required, data
        length, matching length with `x_data`, and float convertibility.
        Defaults to `example_data`.
    x_label : StringField
        Optional label for the X-axis. Validated for length (max 50 chars).
        Defaults to an empty string.
    y_label : StringField
        Optional label for the Y-axis. Validated for length (max 50 chars).
        Defaults to an empty string.
    color : StringField
        Hex color code for the plot line. Validated for being required and
        matching hex color pattern (e.g., #RRGGBB). Defaults to '#4C72B0'.
    """
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
    """
    Generates a simple X-Y line plot image from the provided data.

    This function takes X and Y data series, optional axis labels, a line color,
    and a chart type, then creates a line plot using Matplotlib and Seaborn.
    The plot is rendered to an in-memory buffer and returned as bytes.

    Parameters
    ----------
    x_data : list of float
        The numerical data for the X-axis.
    y_data : list of float
        The numerical data for the Y-axis. Must be of the same length as `x_data`.
    x_label : str, optional
        Label for the X-axis. If None or empty, no label is set. Default is None.
    y_label : str, optional
        Label for the Y-axis. If None or empty, no label is set. Default is None.
    chart_type : str, optional
        The desired output format of the plot. Accepted values:
        -   'png': Standard resolution PNG (100 DPI).
        -   'svg': SVG format (300 DPI).
        -   'pdf': PDF format (300 DPI).
        -   'pngat': High resolution PNG (300 DPI, for attachment/download).
        Default is "png".
    color : str, optional
        Hexadecimal color code for the plot line. Default is '#4C72B0'.

    Returns
    -------
    bytes
        The plot image rendered as bytes in the specified `chart_type` format.
    """
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 5.5))
    fig.clf() # Clear the figure
    ax = plt.subplot(111) # Add subplot

    # Convert data to NumPy arrays of floats
    x_data_arr = np.array(x_data, dtype=float)
    y_data_arr = np.array(y_data, dtype=float)
    
    plt.plot(x_data_arr, y_data_arr, color=color) # Create the line plot

    ax.yaxis.set_ticks_position('left') # Ticks on the left y-axis
    ax.xaxis.set_ticks_position('bottom') # Ticks on the bottom x-axis
    ax.tick_params(direction='out') # Ticks pointing outwards

    if y_label:
        plt.ylabel(y_label)
    if x_label:
        plt.xlabel(x_label)

    plt.tight_layout() # Adjust plot to fit labels etc.

    outs = BytesIO() # In-memory buffer for the image
    
    # Determine format and DPI based on chart_type
    if chart_type == 'pdf':
        type_form = 'pdf'
        dpi = 300
    elif chart_type == 'svg':
        type_form = 'svg'
        dpi = 300
    elif chart_type == 'pngat': # High-DPI PNG for attachments
        type_form = 'png'
        dpi = 300
    else: # Default to standard web PNG
        type_form = 'png'
        dpi = 100
        
    fig.savefig(outs, dpi=dpi, format=type_form, transparent=True) # Save to buffer
    img_bytes = outs.getvalue()
    outs.close()
    plt.close(fig) # Close the figure to free memory
    return img_bytes
