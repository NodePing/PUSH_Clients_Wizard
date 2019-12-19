#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def apcupsd_metric():
    """ Sets APCUPSD metrics to fail when APC isn't ONLINE
    """

    apc_fields = {
        'apcupsd': {
            'name': 'apcupsd',
            'min': 1,
            'max': 1
        }
    }

    return apc_fields
