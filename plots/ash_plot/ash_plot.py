#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bottle Web Application for Average Shifted Histogram (ASH) Plotting.

This script implements a web application using the Bottle framework to generate
Average Shifted Histograms (ASH). Users can input numerical data, specify plot
parameters like labels and colors, and then visualize the generated ASH plot
directly on the web page or download it as an SVG or PNG image.

The application utilizes:
-   Bottle: As the micro web-framework for routing and request handling.
-   WTForms: For creating and validating the web form used for data input.
-   Matplotlib & Seaborn: For generating the actual ASH plots.
-   ASH.ash: A custom module (presumably `plots.ash_plot.ASH.ash`) that provides
    the `ash` class for ASH computation.
-   form_valid: A custom module (presumably `plots.form_valid`) for custom
    form field validation.

Key functionalities include:
-   Displaying a form to input data and plot configurations.
-   Validating user input.
-   Generating ASH plots based on valid input.
-   Displaying the plot as a base64 encoded PNG image on the web page.
-   Allowing users to download the plot as an SVG or PNG file.
-   A "Clear" functionality to reset the form fields.

The main route is `/ash`, which handles both GET (displaying the form) and
POST (processing data and generating the plot) requests.
"""
# Original creation details:
# Created on Fri Aug  5 11:34:19 2016
# @author: bcolsen

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

from .ASH.ash import ash # Custom ASH calculation class
from .. import form_valid as fv # Custom form validators

# Default data for the form, appears to be from a paper or example
paper_data = '-0.38763\n0.80928\n1.5736\n-0.19156\n-1.2762\n0.012471\n' + \
             '2.7392\n-0.14373\n1.5309\n-0.71012\n2.6883\n-0.97024\n' + \
             '-0.18379\n0.39052\n0.89383\n-0.28856\n-0.82227\n-1.2461\n' + \
             '2.8595\n0.50082'

plt.rcParams['svg.fonttype'] = 'none' # Ensure fonts are not rasterized in SVG

# Setup template path for Bottle
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


@route("/ash", method=['POST', 'GET'])
def plot():
    """
    Handles requests for the ASH plot generation page (`/ash`).

    For GET requests, it displays a web form (`DataForm`) allowing users to
    input data and plot parameters.
    For POST requests, it processes the submitted form data. Based on the
    actions (generate plot, download SVG/PNG, or clear form):
    -   If form data is valid:
        -   'Download SVG/PNG': Calls `ash_png()` to generate the plot in the
            requested format and returns it as a file download.
        -   'Generate Plot' (default): Calls `ash_png()` to generate a PNG,
            encodes it in base64, and re-renders the page displaying the
            image and the populated form.
    -   'Clear': Resets the form fields to their default values.
    -   If form data is invalid, it re-renders the page with validation errors.

    Returns
    -------
    bottle.HTTPResponse or str
        An HTTP response for file downloads, or an HTML string (rendered
        template) for displaying the page.
    """
    form = DataForm(request.forms)
    filled = request.forms.get('filled', '').strip() # Hidden field to track if form was submitted
    svg = request.forms.get('svg_download', '').strip() # SVG download button
    png = request.forms.get('png_download', '').strip() # PNG download button
    clear = request.forms.get('clear', '').strip() # Clear button

    img = '' # To store base64 encoded image for display

    if clear:
        filled = None # Mark form as not "filled" to avoid re-validation
        # Reset form fields to default or empty
        form.xlabel.data = ''
        form.data.data = form.data.default # Reset to default paper_data
        form.color.data = form.color.default
        form.fill_color.data = form.fill_color.default
    elif filled and form.validate(): # If form submitted and valid
        data_list = fv.data_split(form.data.data) # Process input data string
        xlabel = form.xlabel.data
        color = form.color.data
        fill_color = form.fill_color.data
        
        if svg:
            chart_type = 'svg'
            response.content_type = 'image/svg+xml' # Correct MIME type for SVG
            response.set_header("Content-Disposition", # Note: Content-Disposition, not Content-disposition
                                "attachment; filename=ash_plot.svg")
            return ash_png(data_list, xlabel, chart_type, color, fill_color)
        elif png:
            chart_type = 'pngat' # High-DPI PNG for download
            response.content_type = 'image/png'
            response.set_header("Content-Disposition",
                                "attachment; filename=ash_plot.png")
            return ash_png(data_list, xlabel, chart_type, color, fill_color)
        else: # Default action: display plot on page
            chart_type = 'png' # Standard DPI PNG for web display
            img_bytes = ash_png(data_list, xlabel, chart_type, color, fill_color)
            img = base64.b64encode(img_bytes).decode('ascii') # Encode for HTML embedding
    else: # Form not submitted yet, or submitted but invalid
        filled = None # Ensures validation errors are shown if form was submitted and invalid

    # Render the template
    return template('ash_app', filled=filled, form=form, img=img)


class DataForm(Form):
    """
    Defines the web form for collecting ASH plot data and configuration.

    This class uses WTForms to define fields and their validation rules.
    The form allows users to input numerical data, specify an X-axis label,
    and choose colors for the plot line and fill.

    Fields
    ------
    data : TextAreaField
        For multi-line input of numerical data. Data points can be separated
        by newlines or commas. Validated for being required, having a certain
        number of points (5 to 100,000), and being convertible to floats.
        Defaults to `paper_data`.
    xlabel : StringField
        Optional label for the X-axis of the plot. Validated for length
        (max 50 characters). Defaults to an empty string.
    color : StringField
        Hexadecimal color code for the ASH plot line. Validated for being
        a required field and matching a hex color pattern (e.g., #RRGGBB).
        Defaults to '#4C72B0'.
    fill_color : StringField
        Hexadecimal color code for the ASH plot fill. Validated for being
        a required field and matching a hex color pattern.
        Defaults to '#92B2E7'.
    """
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
    """
    Generates an Average Shifted Histogram (ASH) plot image.

    This function takes numerical data and several plotting parameters,
    creates an ASH plot using Matplotlib and Seaborn, and returns the
    rendered image as bytes. It utilizes the `ash` class from the
    local `ASH` module for the core ASH computation.

    The plot includes:
    -   The ASH density line.
    -   A filled representation of the ASH.
    -   A rug plot showing individual data points.
    -   Summary statistics displayed on the graph.

    Parameters
    ----------
    data : list of float
        The numerical data to be plotted.
    xlabel : str, optional
        Label for the X-axis. If None or empty, no label is set.
        Default is None.
    chart_type : str, optional
        The desired output format of the plot. Accepted values:
        -   'png': Standard resolution PNG (100 DPI).
        -   'svg': SVG format (300 DPI).
        -   'pdf': PDF format (300 DPI).
        -   'pngat': High resolution PNG (300 DPI, typically for attachment/download).
        Default is "png".
    color : str, optional
        Hexadecimal color code for the ASH line, rug plot, and statistics text.
        Default is '#4C72B0'.
    fill_color : str, optional
        Hexadecimal color code for the filled area under the ASH curve.
        Default is '#92B2E7'.

    Returns
    -------
    bytes
        The plot image rendered as bytes in the specified `chart_type` format.
    """
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 6))
    fig.clf() # Clear the figure explicitly

    a = np.array(data, dtype=float) # Ensure data is a NumPy array of floats
    bins = None # Let the ash object determine binning

    ash_obj_a = ash(a, bin_num=bins, force_scott=True) # Create ASH object

    ax = plt.subplot(111) # Add subplot to the figure
    ax.plot(ash_obj_a.ash_mesh, ash_obj_a.ash_den, lw=2, color=color)

    # plot the solid ASH
    ash_obj_a.plot_ash_infill(ax, color=fill_color, alpha=1) # Using alpha=1 for solid fill

    # barcode like data representation (rug plot)
    ash_obj_a.plot_rug(ax, alpha=1, color=color)

    # put statistics on the graph
    ash_obj_a.plot_stats(ax, color=color)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out') # Ticks pointing out
    ax.set_yticks([]) # Remove y-axis ticks and labels

    if xlabel:
        plt.xlabel(xlabel)
    
    plt.tight_layout() # Adjust plot to ensure everything fits without overlapping
    plt.subplots_adjust(top=0.95) # Adjust top to make space for potential titles (though none here)

    outs = BytesIO() # In-memory buffer for image
    # fig.canvas.draw() # Not strictly necessary before savefig for most backends
    
    # Determine format and DPI based on chart_type
    if chart_type == 'pdf':
        type_form = 'pdf'
        dpi = 300
    elif chart_type == 'svg':
        type_form = 'svg'
        dpi = 300
    elif chart_type == 'pngat': # High-DPI PNG
        type_form = 'png'
        dpi = 300
    else: # Default to standard web PNG
        type_form = 'png'
        dpi = 100
        
    fig.savefig(outs, dpi=dpi, format=type_form, transparent=True) # Save to buffer, transparent background
    img_bytes = outs.getvalue()
    outs.close()
    plt.close(fig) # Close the figure to free memory
    return img_bytes
