#!/usr/bin/python
#
# Test known bugs to prevent regressions. Run from 'module_utils' with
#
#   python3 -m unittest
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html

from tests import params
import parsers
import unittest

# Add regression testing when a bug is found.