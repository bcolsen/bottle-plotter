#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
"""
Handles the Coulombic Efficiency (CE) plot generation and its
web interface using Bottle.

This module defines the route for the CE plot, handles form submissions
for customizing the plot (data, labels, colors), and generates the
CE plot image. It includes a specialized plot function for CE data
that uses a symmetric logarithmic scale for the y-axis.
"""
import base64
import os
from io import BytesIO

import numpy as np
import pylab as plt
import seaborn as sns
# import sys # Unused
import bottle
from bottle import route, response, template, request
from wtforms import (Form, StringField, TextAreaField, validators)
from matplotlib.ticker import MaxNLocator, Locator

from .. import form_valid as fv


# Load default data from files
module_dir = os.path.dirname(__file__)
try:
    with open(os.path.join(module_dir, 'ce_default_x_data.txt'), 'r') as f:
        default_x_data = f.read()
except FileNotFoundError:
    default_x_data = "1\n2\n3\n4\n5"  # Fallback
try:
    with open(os.path.join(module_dir, 'ce_default_y_data.txt'), 'r') as f:
        default_y_data = f.read()
except FileNotFoundError:
    default_y_data = "99\n99.5\n99.7\n99.8\n99.9"  # Fallback


plt.rcParams['svg.fonttype'] = 'none'

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
bottle.TEMPLATE_PATH.insert(0, dir_path)


@route("/ce", method=['POST', 'GET'])
def plot_ce():
    """
    Handles GET and POST requests for the CE plot page.

    On GET, displays the form with default values.
    On POST, validates form data, generates the CE plot, and either
    returns the plot as a downloadable file or embeds it in the page.
    """
    form = DataForm_CE(request.forms)
    img = ''
    # Handles different submit buttons
    action = request.forms.get('action', '').strip()

    if request.method == 'POST' and action == 'clear':
        form.x_data.data = default_x_data
        form.y_data.data = default_y_data
        form.x_label.data = form.x_label.default
        form.y_label.data = form.y_label.default
        form.color.data = form.color.default
        filled_flag = False
    elif request.method == 'POST' and form.validate():
        x_data_list = fv.data_split(form.x_data.data)
        y_data_list = fv.data_split(form.y_data.data)
        x_label = form.x_label.data
        y_label = form.y_label.data
        marker_color_val = form.color.data
        filled_flag = True

        if action == 'svg_download':
            response.content_type = 'image/svg+xml'
            response.set_header(
                "Content-disposition",
                "attachment; filename=ce_plot.svg")
            return generate_ce_plot_image(
                x_data_list,
                y_data_list,
                x_label,
                y_label,
                chart_type='svg',
                marker_color=marker_color_val)
        elif action == 'png_download':
            response.content_type = 'image/png'
            response.set_header(
                "Content-disposition",
                "attachment; filename=ce_plot.png")
            return generate_ce_plot_image(
                x_data_list,
                y_data_list,
                x_label,
                y_label,
                chart_type='pngat',
                marker_color=marker_color_val)
        else:  # Display plot on page
            img_data = generate_ce_plot_image(
                x_data_list,
                y_data_list,
                x_label,
                y_label,
                chart_type='png',
                marker_color=marker_color_val)
            img = base64.b64encode(img_data).decode('utf-8')
    else:
        # Initial GET request or validation failed
        if not form.is_submitted():  # For initial GET
            form.x_data.data = default_x_data
            form.y_data.data = default_y_data
            form.x_label.data = form.x_label.default
            form.y_label.data = form.y_label.default
            form.color.data = form.color.default
        filled_flag = False
        # form.errors will be available in the template if validation failed

    return template('ce_app', filled=filled_flag, form=form, img=img)


class DataForm_CE(Form):
    """
    WTForm for collecting CE plot parameters from the user.
    Includes fields for X and Y data, X and Y axis labels, and marker color.
    Default values for data are loaded from external files.
    """
    x_data = TextAreaField(
        'Cycle Number',
        [validators.InputRequired(),
         fv.DataLength(min=2, max=100000,
                       message='Data must be comma or line separated and '
                               'have 2 to 100000 values'),
         fv.DataFloat()],
        default=default_x_data)
    y_data = TextAreaField(
        'Battery CE',
        [validators.InputRequired(),
         fv.DataLength(min=2, max=100000,
                       message='Data must be comma or line separated and '
                               'have 2 to 100000 values'),
         fv.DataLengthEqual('x_data',
                            message='CE must have the same number of point '
                                    'as cycles'),
         fv.DataFloat()],
        default=default_y_data)
    x_label = StringField(
        'X-axis Label',
        [validators.Optional(),
         validators.Length(min=0, max=50, message='Longer than 50 characters')],
        default='Cycle Number')  # Default set here
    y_label = StringField(
        'Y-axis Label',
        [validators.Optional(),
         validators.Length(min=0, max=50, message='Longer than 50 characters')],
        default='Coulombic Efficiency (%)')  # Default set here
    color = StringField(
        'Marker Color',
        [validators.InputRequired(),
         validators.Regexp("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                           message='Not valid HTML rgb hex color '
                                   '(eg. #4C72B0)')],
        default='#4C72B0')  # Default set here


class MinorSymLogLocator(Locator):
    """
    Dynamically find minor tick positions based on the positions of
    major ticks for a symlog scaling.
    """

    def __init__(self, linthresh):
        """
        Ticks will be placed between the major ticks.
        The placement is linear for x between -linthresh and linthresh,
        otherwise its logarithmically.
        """
        self.linthresh = linthresh

    def __call__(self):
        'Return the locations of the ticks'
        majorlocs = self.axis.get_majorticklocs()
        minorlocs = []
        for i in range(1, len(majorlocs)):
            majorstep = majorlocs[i] - majorlocs[i - 1]
            if abs(majorlocs[i - 1] + majorstep / 2) < self.linthresh:
                ndivs = 10
            else:
                ndivs = 9
            minorstep = majorstep / ndivs
            locs = np.arange(majorlocs[i - 1], majorlocs[i], minorstep)[1:]
            minorlocs.extend(locs)
        return self.raise_if_exceeds(np.array(minorlocs))

    def tick_values(self, vmin, vmax):
        raise NotImplementedError(
            'Cannot get tick locations for a %s type.' %
            type(self))


def ce_plot(
        x_data,
        y_data,
        ax=None,
        linthresh=0.1,
        marker_color='#4C72B0',
        **kwargs):
    """
    Core plotting function for CE data. Plots y_data vs x_data using a
    symmetric log scale for the y-axis (transformed by y-100).

    Args:
        x_data (list/array): X-axis data (e.g., cycle number).
        y_data (list/array): Y-axis data (e.g., Coulombic Efficiency).
                             Values < 2 are assumed to be fractions and
                             multiplied by 100.
        ax (matplotlib.axes.Axes, optional): Axes to plot on. If None,
                                             creates new.
        linthresh (float, optional): The range within which the plot is linear
                                     before transitioning to log scale
                                     (-linthresh to +linthresh).
        marker_color (str, optional): Color for the markers.
        **kwargs: Additional keyword arguments passed to `ax.plot()`.
    """
    y_data_arr = np.array(y_data, dtype=float)
    # Adjust y_data: if max is < 2, assume it's efficiency like 0.99 -> 99
    y_data_transformed = (y_data_arr * 100
                          if y_data_arr.max() < 2 else y_data_arr)
    y_plot_data = y_data_transformed - 100

    current_ax = ax if ax is not None else plt.gca()
    current_ax.plot(
        x_data,
        y_plot_data,
        marker='o',
        mfc=marker_color,
        lw=0,
        **kwargs)  # mfc is markerfacecolor

    current_ax.set_yscale('symlog', linthreshy=linthresh)
    current_ax.get_yaxis().set_minor_locator(MinorSymLogLocator(linthresh))
    current_ax.tick_params(axis='y', which='minor')

    locs, _ = plt.yticks()  # Use current_ax.get_yticks() if issues
    # Format labels to avoid excessive precision
    current_ax.set_yticks(locs,
                          [f"{loc_val + 100:.{8}g}" for loc_val in locs])

    current_ax.grid(
        b=True,
        which='major',
        axis='y',
        color=(
            0.9,
            0.9,
            0.9),
        linestyle='-')
    current_ax.grid(
        b=True,
        which='minor',
        color=(
            0.9,
            0.9,
            0.9),
        linestyle='-',
        linewidth=0.5)
    current_ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
    # plt.tight_layout() # Call this in the calling function
    # (generate_ce_plot_image)


def generate_ce_plot_image(
        x_data,
        y_data,
        x_label,
        y_label,
        chart_type="png",
        marker_color=None):
    """
    Generates a Coulombic Efficiency (CE) plot image.

    Args:
        x_data (list): X-axis data (e.g., cycle numbers).
        y_data (list): Y-axis data (e.g., CE values).
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        chart_type (str, optional): Type of chart ('png', 'svg', 'pngat').
                                    Defaults to "png".
        marker_color (str, optional): Hex color for markers. Defaults to
                                      '#4C72B0'.

    Returns:
        bytes: The generated plot image in the specified format.
    """
    final_marker_color = marker_color if marker_color is not None else '#4C72B0'
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 5.5))
    # fig.clf() # Not strictly necessary as figure is new
    ax = fig.add_subplot(111)  # Use add_subplot for clarity

    # Pass final_marker_color
    ce_plot(x_data, y_data, ax=ax, marker_color=final_marker_color)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out')

    if y_label:
        ax.set_ylabel(y_label)
    if x_label:
        ax.set_xlabel(x_label)

    plt.tight_layout()
    fig.subplots_adjust(top=0.95)  # Keep or remove based on visual output

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
