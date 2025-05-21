#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom WTForms Validators and Data Processing Utilities.

This module provides a collection of custom validator classes intended for use
with WTForms (or similar form handling libraries). These validators are tailored
for common data validation tasks encountered in web forms that accept numerical
or structured textual input, such as lists of numbers. Additionally, it includes
utility functions for pre-processing form data before validation or use.

The validators include checks for:
-   The number of data points in a field (DataLength).
-   Equality of data points count between two fields (DataLengthEqual).
-   Convertibility of all data points in a field to float (DataFloat).

A helper function `data_split` is provided to parse string input (e.g., from
a TextAreaField) into a list of individual data entries based on common
delimiters like commas or whitespace.

These utilities are designed to be used in conjunction with web applications
that require robust input validation for data-driven plotting or analysis tools.
"""
# Original creation details:
# Created on Fri Aug  5 11:34:19 2016
# @author: bcolsen

from wtforms import validators
import numpy as np
import re


class DataLength():
    """
    WTForms validator to check if the number of data points in a field
    falls within a specified range [min, max].

    The input field's data is first split into a list of potential data points
    using the `data_split` utility function. The length of this list is then
    compared against the `min` and `max` thresholds.
    """
    def __init__(self, min=-1, max=-1, message=None):
        """
        Initialize the validator.

        Parameters
        ----------
        min : int, optional
            The minimum allowed number of data points. If -1, no minimum limit
            is enforced. Default is -1.
        max : int, optional
            The maximum allowed number of data points. If -1, no maximum limit
            is enforced. Default is -1.
        message : str, optional
            Error message to raise in case of a validation error. If None, a
            default message is generated.
        """
        self.min = min
        self.max = max
        if not message:
            message = u'Data must be between %i and %i values long.' % (min, max)
        self.message = message

    def __call__(self, form, field):
        """
        Perform the validation.

        This method is called by WTForms during form validation.

        Parameters
        ----------
        form : wtforms.form.Form
            The form instance that this validator is part of.
        field : wtforms.fields.Field
            The field instance that this validator is validating.

        Raises
        ------
        wtforms.validators.ValidationError
            If the number of data points is less than `min` or greater than `max`
            (and `max` is not -1).
        """
        data_list = data_split(field.data)
        l = data_list and len(data_list) or 0 # Length is 0 if data_list is None or empty
        if l < self.min or (self.max != -1 and l > self.max):
            raise validators.ValidationError(self.message)


class DataLengthEqual():
    """
    WTForms validator to check if the number of data points in the current
    field is equal to the number of data points in another specified field.

    Both fields' data are split using `data_split`, and their lengths are compared.
    """
    def __init__(self, fieldname, message=None):
        """
        Initialize the validator.

        Parameters
        ----------
        fieldname : str
            The name of the other field in the form whose data length should
            be compared with the current field's data length.
        message : str, optional
            Error message to raise in case of a validation error (lengths differ).
            If None, a default message is used.
        """
        self.fieldname = fieldname
        if not message:
            message = u'Data must be the same length.'
        self.message = message

    def __call__(self, form, field):
        """
        Perform the validation.

        Compares the length of processed data in the current field with the
        length of processed data in the field specified by `self.fieldname`.

        Parameters
        ----------
        form : wtforms.form.Form
            The form instance.
        field : wtforms.fields.Field
            The field being validated.

        Raises
        ------
        wtforms.validators.ValidationError
            If the number of data points in the two fields is not equal.
        AttributeError
            If the `fieldname` specified during initialization does not exist
            in the form.
        """
        try:
            other_field = getattr(form, self.fieldname)
        except AttributeError:
            raise AttributeError(u'Invalid field name "%s" for DataLengthEqual validator.' % self.fieldname)
        
        data_list_current = data_split(field.data)
        data_list_other = data_split(other_field.data)
        
        len_current = data_list_current and len(data_list_current) or 0
        len_other = data_list_other and len(data_list_other) or 0
        
        if len_current != len_other:
            raise validators.ValidationError(self.message)


class DataFloat():
    """
    WTForms validator to check if all data points in a field can be
    converted to floating-point numbers.

    The field's data is split using `data_split`, and then an attempt is made
    to convert the resulting list of strings into a NumPy array of floats.
    """
    def __init__(self, message=None):
        """
        Initialize the validator.

        Parameters
        ----------
        message : str, optional
            Error message to raise if any data point cannot be converted to float.
            If None, a default message is used.
        """
        if not message:
            message = u'Number cannot be converted to float.' # Note: Original message implies single number.
                                                             # Actual check is on all numbers in list.
        self.message = message

    def __call__(self, form, field):
        """
        Perform the validation.

        Attempts to convert all processed data points from the field to floats.

        Parameters
        ----------
        form : wtforms.form.Form
            The form instance.
        field : wtforms.fields.Field
            The field being validated.

        Raises
        ------
        wtforms.validators.ValidationError
            If any data point in the field cannot be converted to a float.
            The error message from the underlying `ValueError` during conversion
            is typically used.
        """
        data_list = data_split(field.data)
        if data_list is None or len(data_list) == 0:
            # No data to validate, or data_split returned None (e.g. empty input)
            # Depending on requirements, this might be acceptable or require DataRequired.
            # This validator only checks convertibility if data points exist.
            return

        try:
            np.array(data_list, dtype=float)
        except ValueError as err:
            # Use a more specific message or the original field-level message
            # The `err` from numpy can be informative, e.g., "could not convert string to float: 'abc'"
            raise validators.ValidationError(f"{self.message} Details: {err}")


def data_split(data_string):
    """
    Splits a string of data by whitespace or commas and cleans up empty entries.

    This utility function is designed to parse a string, typically from a form
    field, that contains multiple data points separated by commas, spaces,
    tabs, or newlines. It removes leading/trailing whitespace from the overall
    string and then splits it. It also filters out any empty strings that might
    arise from multiple delimiters (e.g., "1,,2" or "1  2").

    Parameters
    ----------
    data_string : str
        The input string containing data points.

    Returns
    -------
    list of str or None
        A list of non-empty strings, where each string is an individual
        data point extracted from the input.
        Returns `None` if the input `data_string` is None, empty, or contains
        only whitespace and delimiters that result in no actual data points.
    """
    if data_string is None:
        return None
        
    # Strip leading/trailing whitespace from the whole string first
    processed_string = data_string.strip()
    if not processed_string: # If string is empty or only whitespace
        return None

    # Split by one or more occurrences of whitespace or comma
    data_list = re.split(r'[\s,]+', processed_string)
    
    # Filter out any empty strings that might still be present
    # (e.g. if original string was just "," or " , ")
    # Although re.split with `+` should handle most cases of multiple delimiters,
    # an initial or final delimiter on a non-empty string might leave an empty string.
    # Example: ",1,2" -> ["", "1", "2"] by some splitters.
    # The original code had try-except for deleting first/last if empty.
    # A list comprehension is cleaner for filtering all empty strings.
    
    cleaned_list = [item for item in data_list if item] # Keeps only non-empty strings

    if not cleaned_list: # If list is empty after cleaning
        return None
    
    return cleaned_list
