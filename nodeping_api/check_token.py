#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import _query_nodeping_api

API_URL = 'https://api.nodeping.com/api/1/'


def main(token):

    url = "{0}accounts?token={1}".format(API_URL, token)

    valid_token = _query_nodeping_api.get(url)

    try:
        valid_token['error']
    except KeyError:
        return True
    else:
        raise Exception("You have supplied an invalid API key")


if __name__ == '__main__':
    main()
