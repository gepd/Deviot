# !/usr/bin/env python
# -*- coding: utf-8 -*-

from .errors import error


def print_error(code_error):
    print("=== MESSAGE ===")
    print(error[code_error])
