#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
from wtforms import validators
import numpy as np
import re


class DataLength():
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        if not message:
            message = u'Data must be between %i and %i values long.' % (min, max)
        self.message = message

    def __call__(self, form, field):
        data_list = data_split(field.data)
        l = data_list and len(data_list) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise validators.ValidationError(self.message)


class DataLengthEqual():
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        if not message:
            message = u'Data must be the same length.'
        self.message = message

    def __call__(self, form, field):
        data_list = data_split(field.data)
        other_list = data_split(getattr(form, self.fieldname).data)
        l = data_list and len(data_list) or 0
        o = other_list and len(other_list) or 0
        if l != o:
            raise validators.ValidationError(self.message)


class DataFloat():
    def __init__(self, message=None):
        if not message:
            message = u'Number cannot be converted to float.'
        self.message = message

    def __call__(self, form, field):
        try:
            data_list = data_split(field.data)
            np.array(data_list, dtype=float)
        except ValueError as err:
            raise validators.ValidationError(err)


def data_split(data):
    data_list = re.split(r'[\s,]+', data.strip())
    try:
        if not data_list[0]:
            del data_list[0]
        if not data_list[-1]:
            del data_list[-1]
    except IndexError:
        return None
    else:
        return data_list
