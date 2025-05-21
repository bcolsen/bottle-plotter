#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bottle Web Application for Coulombic Efficiency (CE) Plotting.

This script implements a web application using the Bottle framework to generate
plots of Coulombic Efficiency (CE) typically found in battery cycle life data.
Users can input cycle numbers and corresponding CE values, specify plot labels
and colors, and then visualize the generated CE plot directly on the web page
or download it as an SVG or PNG image.

The application features:
-   Bottle: For web routing and request handling.
-   WTForms: For form creation and input validation.
-   Matplotlib & Seaborn: For generating the plots.
-   A custom `MinorSymLogLocator` for Matplotlib to enhance tick placement on
    'symlog' scaled axes, particularly for CE data that approaches 100%.
-   Custom form validation utilities (presumably from `plots.form_valid`).

Key functionalities include:
-   Displaying a form for CE data (cycle numbers, CE values) and plot parameters.
-   Validating user input for data integrity and format.
-   Generating CE plots with a 'symlog' y-axis to effectively display values
    very close to 100%.
-   Displaying the plot as a base64 encoded PNG on the web page.
-   Allowing download of the plot as SVG or PNG.
-   A "Clear" function to reset form fields.

The main route is `/ce`, handling GET (display form) and POST (process data,
generate plot) requests. The `ce_plot` function handles the core Matplotlib
plotting logic, while `ce_png` wraps this to produce image bytes.
"""
# Original creation details:
# Created on Fri Aug  5 11:34:19 2016
# @author: bcolsen

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

from .. import form_valid as fv # Custom form validators

# Default data for the form fields
battery_data = '87.29\n98.65\n99.25\n99.49\n99.63\n99.70\n99.76\n99.81\n' + \
               '99.85\n99.87\n99.89\n99.91\n99.93\n99.94\n99.96'
cycle_data = '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15'

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
        A common example is `sep` or `end`.
    """
    print(*args, file=sys.stderr, **kwargs)


@route("/ce", method=['POST', 'GET'])
def plot_ce():
    """
    Handles requests for the Coulombic Efficiency (CE) plot page (`/ce`).

    For GET requests, it displays a web form (`DataForm_CE`) for user input.
    For POST requests, it processes submitted form data. Actions include:
    -   If form data is valid:
        -   'Download SVG/PNG': Calls `ce_png()` to generate the plot in the
            requested format and returns it as a file download.
        -   'Generate Plot' (default): Calls `ce_png()` for a PNG, base64 encodes
            it, and re-renders the page with the image and populated form.
    -   'Clear': Resets form fields to defaults.
    -   If form data is invalid, re-renders with validation errors.

    Returns
    -------
    bottle.HTTPResponse or str
        HTTP response for file downloads, or HTML string (rendered template).
    """
    form = DataForm_CE(request.forms)
    filled = request.forms.get('filled', '').strip()
    svg = request.forms.get('svg_download', '').strip()
    png = request.forms.get('png_download', '').strip()
    clear = request.forms.get('clear', '').strip()

    img = '' # Base64 encoded image for display

    if clear:
        filled = None
        form.x_label.data = form.x_label.default
        form.x_data.data = form.x_data.default
        form.y_label.data = form.y_label.default
        form.y_data.data = form.y_data.default
        form.color.data = form.color.default
    elif filled and form.validate():
        x_data_list = fv.data_split(form.x_data.data)
        y_data_list = fv.data_split(form.y_data.data)
        x_label = form.x_label.data
        y_label = form.y_label.data
        color = form.color.data
        if svg:
            chart_type = 'svg'
            response.content_type = 'image/svg+xml' # Correct MIME for SVG
            response.set_header("Content-Disposition",
                                "attachment; filename=ce_plot.svg")
            return ce_png(x_data_list, y_data_list,
                          x_label, y_label, chart_type, color)
        elif png:
            chart_type = 'pngat' # High-DPI PNG
            response.content_type = 'image/png'
            response.set_header("Content-Disposition",
                                "attachment; filename=ce_plot.png")
            return ce_png(x_data_list, y_data_list, x_label,
                          y_label, chart_type, color)
        else: # Default: display plot on page
            chart_type = 'png' # Standard DPI PNG for web
            img_bytes = ce_png(x_data_list, y_data_list,
                               x_label, y_label, chart_type, color) # Corrected order of x_label, y_label
            img = base64.b64encode(img_bytes).decode('ascii')
    else:
        filled = None # Show validation errors if any

    return template('ce_app', filled=filled, form=form, img=img)


class DataForm_CE(Form):
    """
    Defines the web form for Coulombic Efficiency (CE) plot generation.

    This WTForms class specifies fields for user input, including cycle numbers
    (X-data), CE values (Y-data), axis labels, and marker color. It includes
    validators to ensure data integrity and correct formatting.

    Fields
    ------
    x_data : TextAreaField
        Input for cycle numbers. Validated for being required, data length,
        and float convertibility. Defaults to `cycle_data`.
    y_data : TextAreaField
        Input for CE percentage values. Validated for being required, data length,
        matching length with `x_data`, and float convertibility. Defaults to
        `battery_data`.
    x_label : StringField
        Optional label for the X-axis. Validated for length. Defaults to
        'Cycle Number'.
    y_label : StringField
        Optional label for the Y-axis. Validated for length. Defaults to
        'Coulombic Efficiency (%)'.
    color : StringField
        Hex color code for plot markers. Validated for being required and
        matching hex color pattern. Defaults to '#4C72B0'.
    """
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
    Dynamically find minor tick positions for a 'symlog' scaled axis.

    This Matplotlib `Locator` is designed to place minor ticks appropriately
    on an axis that uses symmetrical logarithmic scaling (`symlog`). It aims
    to place ticks linearly within the defined linear threshold region around
    zero and logarithmically outside this region. The number of minor ticks
    (subdivisions) adapts based on whether the interval is within the linear
    or logarithmic part of the scale.
    """
    def __init__(self, linthresh):
        """
        Initialize the locator with the linear threshold of the symlog scale.

        Parameters
        ----------
        linthresh : float
            The `linthresh` value of the symlog scale. This defines the range
            `(-linthresh, linthresh)` around zero where the scale is linear.
        """
        self.linthresh = linthresh

    def __call__(self):
        """
        Return the locations of the minor ticks.

        This method is called by Matplotlib to get the minor tick positions.
        It retrieves the major tick locations from the axis and calculates
        minor tick positions between them. The number of subdivisions between
        major ticks is 10 if the interval is within the linear region
        (`+/- linthresh`), and 9 (for logarithmic spacing) otherwise.

        Returns
        -------
        numpy.ndarray
            An array of minor tick locations.
        """
        majorlocs = self.axis.get_majorticklocs()
        minorlocs = []

        for i in range(1, len(majorlocs)):
            majorstep = majorlocs[i] - majorlocs[i-1]
            # Determine number of subdivisions based on whether the midpoint
            # of the interval between major ticks falls into the linear region.
            if abs(majorlocs[i-1] + majorstep/2) < self.linthresh:
                ndivs = 10 # Linear behavior
            else:
                ndivs = 9  # Logarithmic behavior (typically 9 intervals for log)
            
            if ndivs <= 0: continue # Avoid division by zero or negative
            
            minorstep = majorstep / ndivs
            # Generate minor ticks, excluding the first one (which is a major tick)
            locs = np.arange(majorlocs[i-1], majorlocs[i], minorstep)[1:]
            minorlocs.extend(locs)

        return self.raise_if_exceeds(np.array(minorlocs))

    def tick_values(self, vmin, vmax):
        """
        Return the values of the located ticks.

        Note: This method is part of the `Locator` interface but is typically
        not implemented for minor tick locators that depend on major ticks,
        as the minor ticks are calculated dynamically in `__call__`.
        Raising `NotImplementedError` is standard practice in such cases.

        Parameters
        ----------
        vmin : float
            The minimum value of the view range.
        vmax : float
            The maximum value of the view range.

        Raises
        ------
        NotImplementedError
            Always, as this method is not used for this locator type.
        """
        raise NotImplementedError('Cannot get tick locations for a '
                                  '%s type.' % type(self))


def ce_plot(x_data, y_data, ax=None, linthresh=0.1, **kwargs):
    """
    Plots Coulombic Efficiency (CE) data with a symmetrical log (symlog) y-axis.

    This function processes CE data (typically percentages) and plots it against
    cycle numbers or another x-axis quantity. The y-axis is scaled using
    'symlog' to effectively visualize CE values that are often very close to
    100%. Data is transformed (y_data - 100) before plotting on the symlog scale.
    It also applies custom minor ticks using `MinorSymLogLocator` and styles
    the grid.

    Parameters
    ----------
    x_data : array_like
        The data for the x-axis (e.g., cycle numbers).
    y_data : array_like
        The Coulombic Efficiency data for the y-axis (e.g., percentages).
        If values are < 2 (e.g., 0.99), they are multiplied by 100.
    ax : matplotlib.axes.Axes, optional
        The Matplotlib Axes object to plot on. If None, a new plot is created
        using `plt.plot()`. Default is None.
    linthresh : float, optional
        The linear threshold parameter for the symlog y-axis scale. This defines
        the range `(-linthresh, linthresh)` around the transformed zero point
        (i.e., 100% CE) where the scale is linear. Default is 0.1.
    **kwargs :
        Additional keyword arguments passed directly to `ax.plot()` or `plt.plot()`.
        Common examples include `marker`, `mfc` (markerfacecolor), `lw` (linewidth).
    """
    y_data_arr = np.array(y_data, dtype=float)
    # If CE values are like 0.99, convert to percentage; otherwise, assume already percentage.
    y_data_arr = y_data_arr*100 if y_data_arr.max() < 2 else y_data_arr
    
    # Transform y_data for symlog plotting: (CE % - 100)
    # This centers the "ideal" 100% CE at 0 on the transformed scale.
    y_transformed = y_data_arr - 100
    
    if ax is None:
        plt.plot(x_data, y_transformed, **kwargs)
        current_ax = plt.gca()
    else:
        ax.plot(x_data, y_transformed, **kwargs)
        current_ax = ax
        
    current_ax.set_yscale('symlog', linthreshy=linthresh)
    current_ax.get_yaxis().set_minor_locator(MinorSymLogLocator(linthresh))
    current_ax.tick_params(axis='y', which='minor') # Ensure minor ticks are drawn
    
    # Adjust y-tick labels to show original CE % values instead of transformed values
    locs, _ = plt.yticks() # Get current tick locations (which are on the transformed scale)
    plt.yticks(locs, ["{:.{prec}f}".format(l + 100, prec=max(0, 2-int(np.log10(abs(l))) if l !=0 else 2)) if abs(l) < 1 else str(int(l+100)) for l in locs])


    current_ax.grid(b=True, which='major', axis='y', color=(0.9, 0.9, 0.9),
                    linestyle='-')
    current_ax.grid(b=True, which='minor', axis='y', color=(0.9, 0.9, 0.9), 
                    linestyle='-', linewidth=0.5)
    
    current_ax.get_xaxis().set_major_locator(MaxNLocator(integer=True)) # Ensure integer x-axis ticks
    plt.tight_layout() # Adjust layout


def ce_png(x_data, y_data, x_label, y_label, chart_type="png",
           fill_color='#4C72B0'):
    """
    Generates a Coulombic Efficiency (CE) plot image and returns it as bytes.

    This function sets up the plot style, creates a figure and axes, calls
    `ce_plot` to draw the CE data, applies labels, and then saves the plot
    to an in-memory buffer in the specified image format.

    Parameters
    ----------
    x_data : list of float
        Data for the x-axis (e.g., cycle numbers).
    y_data : list of float
        Data for the y-axis (Coulombic Efficiency values).
    x_label : str
        Label for the X-axis.
    y_label : str
        Label for the Y-axis.
    chart_type : str, optional
        The desired output format. Options: 'png' (100 DPI), 'svg' (300 DPI),
        'pdf' (300 DPI), 'pngat' (300 DPI PNG). Default is "png".
    fill_color : str, optional
        Hex color code for the plot markers' face color. Default is '#4C72B0'.

    Returns
    -------
    bytes
        The plot image rendered as bytes in the specified `chart_type` format.
    """
    sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)

    fig = plt.figure(figsize=(6, 5.5))
    fig.clf() # Clear figure
    ax = plt.subplot(111)
    
    # Plotting CE data with markers, no line (lw=0)
    ce_plot(x_data, y_data, ax=ax, marker='o', mfc=fill_color, mec=fill_color, ms=8, lw=0) # mec for marker edge color

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(direction='out') # Ticks point outwards
    
    if y_label:
        plt.ylabel(y_label)
    if x_label:
        plt.xlabel(x_label)

    plt.tight_layout()
    plt.subplots_adjust(top=0.95) # Adjust top margin

    outs = BytesIO() # In-memory buffer
    
    # Determine format and DPI
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
        
    fig.savefig(outs, dpi=dpi, format=type_form, transparent=True)
    img_bytes = outs.getvalue()
    outs.close()
    plt.close(fig) # Close figure to free memory
    return img_bytes
