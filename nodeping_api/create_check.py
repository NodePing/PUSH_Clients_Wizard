#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL

defaults = {
    'interval': 15,
    'enabled': False,
    'public': False,
    'runlocations': None,
    'homeloc': False,
    'ipv6': False,
    'threshold': 5,
    'sens': 2
}


def _create_url(token, customerid):
    """ Creates the url for sending data to NodePing

    Formats the url based on whether or not the
    customerid is None
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}checks?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}checks?token={1}".format(API_URL, token)

    return url


def _package_variables(variables, check_type):
    """ Removes token and customer id and adds check type to dict data

    Removes the token from the dictionary that will be sent to NodePing
    in JSON format as well as the customer id since these aren't a part
    of the check data. Also adds the check type.
    """
    variables.update({'type': check_type})
    variables.pop('token')
    variables.pop('customerid')

    return variables


def audio_check(
        token,
        target,
        customerid=None,
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing AUDIO check

    Expects a token and target variable. The rest are optional
    and are configured to match the NodePing defaults as described
    in the documentation.
    """

    check_variables = _package_variables(locals(), 'AUDIO')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def cluster_check(
        token,
        data,
        customerid="",
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing Cluster check. Allows you to have a
    check pass/fail based on the status of other checks. Data is
    expected to be a dictionary with a key "data" and values being
    the ID of checks for the cluster with values of 1 or 0 for pass
    or fail.

    Example dictionary:
    checks = {
        "data": {
            "201205050153W2Q4C-0J2HSIRF": "1",
            "201205050153W2Q4C-4RZT8MLN": "1",
            "201205050153W2Q4C-IOPPFQOT": "1"
        }
    }
    """

    check_variables = _package_variables(locals(), 'CLUSTER')
    data = check_variables['data']['data']
    check_variables['data'] = data

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def dns_check(
        token,
        target="",
        customerid="",
        port=53,
        transport='udp',
        dnstype='A',
        dnsrd=1,
        contentstring="",
        dnstoresolve="",
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing DNS check

    target - the FQDN/IP of the DNS server you want to query
    contentstring - what you expect the response to be when resolving
    dnstoresolve - FQDN/IP you want to resolve
    dnsrd - Recursion Desired [1=true, 0=false]
    """

    check_variables = _package_variables(locals(), 'DNS')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ftp_check(
        token,
        target,
        customerid="",
        label="",
        port=21,
        username="",
        password="",
        invert="",
        contentstring="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing FTP check

    Username/password:
    Optional. Many FTP sites can be checked using the username
    "anonymous" with the password set to any valid email address.
    If the username and password are left blank, the check will
    attempt to login anonymously. If you do supply login credentials
    for the check, please note the Terms Of Service paragraph on
    confidential information such as logins.

    invert - whether you expect a file to exist or not.
    1 == you expect it to exist

    contentstring - the name of the file on he ftp server
    """

    check_variables = _package_variables(locals(), 'FTP')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def http_check(
        token,
        target,
        customerid="",
        label="",
        ipv6=False,
        follow=False,
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing HTTP check

    Expects a token and a target variable.

    ipv6: If you want to resolve via IPv6
    follow: If you want to follow redirects or not
    """

    check_variables = _package_variables(locals(), 'HTTP')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def httpadv_check(
        token,
        target,
        label="",
        customerid="",
        invert=False,
        contentstring="",
        data="",
        method="",
        postdata="",
        receiveheaders="",
        sendheaders="",
        statuscode=200,
        ipv6=False,
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing HTTPADV check

    Expects a token and a target variable.

    contentstring - check to see if the content contains this string
    data/postdata - key/value pairs for POST fields
    sendheaders - key/value pairs for request headers
    receiveheaders - key/value pairs for response headers
    statuscode - HTTP status code expected in return
    """

    check_variables = _package_variables(locals(), 'HTTPADV')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def httpcontent_check(
        token,
        target,
        customerid="",
        label="",
        invert=False,
        contentstring="",
        ipv6=False,
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing HTTPCONTENT check

    Expects a token and target variable.

    ipv6 - If you want to resolve to IPv6 or not
    invert - True if you expect content in the string, False if you
    don't expect the string
    contentstring - the string to check for in the body of the web page
    """

    check_variables = _package_variables(locals(), 'HTTPCONTENT')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def httpparse_check(
        token,
        target,
        customerid="",
        label="",
        fields="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing HTTPPARSE check.

    Expects a token and a target. Expects a keyed
    list of fields, with an arbitrary string as the key.
    Each object should have a name, min, and max

    Example dictionary:
    fields = {
        "fields": {
            "processmem": {
                "name": "processmem",
                "min": 1000,
                "max": 5000
            },
            "cpuload": {
                "name": "cpuload",
                "min": 1,
                "max": 5
            }
        }
    }
    """

    check_variables = _package_variables(locals(), 'HTTPPARSE')
    fields = check_variables['fields']['fields']
    check_variables['fields'] = fields

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def imap4_check(
        token,
        target,
        customerid="",
        label="",
        port="",
        verify=True,
        email="",
        password="",
        secure=False,
        username="",
        warningdays="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing IMAP4 check
    """

    check_variables = _package_variables(locals(), 'IMAP4')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def mysql_check(
        token,
        target,
        customerid=None,
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing MYSQL check.

    Expects a token and target variable.
    """

    check_variables = _package_variables(locals(), 'IMAP4')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ntp_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        port=123,
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing NTP check.

    Expects a token and target variable. An optional port
    value can be passed as well as "invert", where True is
    to pass if it responds, and False is to pass if it fails.
    """

    check_variables = _package_variables(locals(), 'NTP')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ping_check(
        token,
        target,
        customerid=None,
        label="",
        ipv6=defaults['ipv6'],
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing PING check

    Expects a token and target variable. The rest are optional
    and are configured to match the NodePing defaults as described
    in the documentation.
    """

    check_variables = _package_variables(locals(), 'PING')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def pop3_check(
        token,
        target,
        customerid=None,
        label="",
        port="",
        verify=True,
        email="",
        username="",
        password="",
        secure=False,
        warningdays="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """
    """

    check_variables = _package_variables(locals(), 'POP3')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def port_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        port="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """
    """

    check_variables = _package_variables(locals(), 'PORT')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def push_check(
        token,
        checktoken="reset",
        customerid=None,
        label="",
        fields="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        oldresultfail=False,
        dep="",
        notifications=""
):
    """ Creates a NodePing PUSH check

    Field variable will look like this:

    fields = {
        "apcupsd": {
            "name": "apcupsd",
            "min": 1,
            "max": 1
        },
        "load1min": {
            "name": "load.1min",
            "min": "0",
            "max": "4"
        },
        "load5min": {
            "name": "load.5min",
            "min": "0",
            "max": "2"
        },
        "memavail": {
            "name": "memavail",
            "min": "100",
            "max": "10000"
        }
    }
    """

    check_variables = _package_variables(locals(), 'PUSH')
    fields = check_variables['fields']
    check_variables['fields'] = fields

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def rbl_check(
        token,
        target,
        customerid=None,
        label="",
        ignore="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing RBL check

    Set to ignore to be a list of RBLs to ignore at
    https://nodeping.com/rbl_check.html

    Example: ignore=["zen.spamhaus.org", "dnsbl.sorbs.net"]
    """

    check_variables = _package_variables(locals(), 'RBL')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def rdp_check(
        token,
        target,
        customerid=None,
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing RDP check
    """

    check_variables = _package_variables(locals(), 'RDP')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def sip_check(
        token,
        target,
        customerid=None,
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing SIP check
    """

    check_variables = _package_variables(locals(), 'SIP')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def smtp_check(
        token,
        target,
        customerid=None,
        invert=False,
        port=25,
        verify=True,
        email="",
        password="",
        secure=False,
        username="",
        warningdays="",
        label="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing SMTP check
    """

    check_variables = _package_variables(locals(), 'SMTP')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def snmp_check(
        token,
        target,
        customerid=None,
        label="",
        port=161,
        fields="",
        snmpv=1,
        snmpcom="public",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing SNMP check

    Field variable will look like this:

    fields = {
        "name1": {
            "name": "name1",
            "min": 1,
            "max": 5
        },
        "name2": {
            "name": "name2",
            "min": "0",
            "max": "4"
        },
        "name3": {
            "name": "name3",
            "min": "0",
            "max": "2"
        }
    }

    fields - values will be your OIDs
    port - default is 161
    snmpv - default is SNMPv1, also available is 2c for SNMPv2c
    snmpcom - SNMP community indicator
    """

    check_variables = _package_variables(locals(), 'SNMP')
    fields = check_variables['fields']
    check_variables['fields'] = fields

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ssh_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        contentstring="",
        port=22,
        username="",
        password="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing SSH check

    contentstring - a string to look for in the response received after the login
    invert - If the contentstring should exist or shouldn't exist
    port - port that the sshd service is running on
    """

    check_variables = _package_variables(locals(), 'SSH')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ssl_check(
        token,
        target,
        customerid=None,
        label="",
        warningdays="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing SSL check

    warningdays - how soon you want a warning of an expiring cert
    """

    check_variables = _package_variables(locals(), 'SSL')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def websocket_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        contentstring="",
        data="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing WebSocket check

    contentstring - text to check for in the response
    invert - False = check if the contentstring exists
    """

    check_variables = _package_variables(locals(), 'WEBSOCKET')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)


def whois_check(
        token,
        target,
        customerid=None,
        label="",
        whoisserver="",
        ipv6=False,
        invert=False,
        contentstring="",
        warningdays="",
        interval=defaults['interval'],
        enabled=defaults['enabled'],
        public=defaults['public'],
        runlocations=defaults['runlocations'],
        homeloc=defaults['homeloc'],
        threshold=defaults['threshold'],
        sens=defaults['sens'],
        dep="",
        notifications=""
):
    """ Creates a NodePing whois check

    whoisserver - Server to query for whois entry
    warningdays - How many days before to warn for domain name expiry
    contentstring - string that you expect in the response
    invert - False = you expect the contentstring to be there
    """

    check_variables = _package_variables(locals(), 'WHOIS')

    url = _create_url(token, customerid)

    return _query_nodeping_api.post(url, check_variables)
