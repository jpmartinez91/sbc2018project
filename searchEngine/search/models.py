# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Resource(object):
    """docstring for Resource."""
    def __init__(self, arg):
        super(Resource, self).__init__()
        self.arg = arg
