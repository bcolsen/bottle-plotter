#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
"""
Custom WTForms validators used for plot data input forms.

This module provides validators for checking data length, equality of data
lengths between two fields, and whether data can be converted to floats.
It also includes a helper function to split input strings into a list of
data points.
"""
import re
from wtforms import validators
import numpy as np


class DataLength():
    """
    Validates that the number of data points in a field is within a
    specified range.
    """

    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        if not message:
            message = 'Data must have between %i and %i values.' % (min, max)
        self.message = message

    def __call__(self, form, field):
        data_list = data_split(field.data)
        length = len(data_list) if data_list else 0
        if length < self.min or (self.max != -1 and length > self.max):
            raise validators.ValidationError(self.message)


class DataLengthEqual():
    """
    Validates that the number of data points in the current field is equal
    to the number of data points in another specified field.
    """

    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        if not message:
            message = ('Data must be the same length as the "%s" field.'
                       % fieldname.replace('_', ' ').title())
        self.message = message

    def __call__(self, form, field):
        data_list = data_split(field.data)
        try:
            other_field = getattr(form, self.fieldname)
        except AttributeError:
            raise validators.ValidationError(
                f"Invalid field name '{self.fieldname}' provided to "
                "DataLengthEqual validator.")
        other_list = data_split(other_field.data)

        current_length = len(data_list) if data_list else 0
        other_length = len(other_list) if other_list else 0
        if current_length != other_length:
            raise validators.ValidationError(self.message)


class DataFloat():
    """
    Validates that all data points in a field can be converted to float
    numbers. Empty data is considered valid by this validator.
    """

    def __init__(self, message=None):
        if not message:
            message = ('All data points must be numbers (e.g., 3.14 or -42).')
        self.message = message

    def __call__(self, form, field):
        data_list = data_split(field.data)
        if not data_list:  # If no data, it's valid from this validator's perspective
            return
        try:
            np.array(data_list, dtype=float)
        except ValueError:  # Catch NumPy's more specific error
            raise validators.ValidationError(self.message)


def data_split(data_string):
    """
    Splits a string of data points into a list of strings.

    Args:
        data_string (str): A string containing data points separated by
                           commas and/or whitespace.

    Returns:
        list[str]: A list of strings, where each string is a potential
                   data point. Returns an empty list if the input
                   string is empty or contains only separators.

    Handles:
    - Multiple separators (e.g., "1, 2  3 ,, 4").
    - Leading/trailing separators/whitespace.
    - Empty input string or string with only separators (returns []).
    - Strips whitespace from each resulting item.
    """
    if not data_string or data_string.isspace():
        return []
    # Split by one or more occurrences of comma or whitespace
    # Then filter out any empty strings that result from multiple separators
    # or leading/trailing separators.
    data_list = [s for s in re.split(r'[\s,]+', data_string.strip()) if s]
    return data_list
