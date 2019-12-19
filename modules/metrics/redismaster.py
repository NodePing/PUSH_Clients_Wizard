#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
from modules import _utils


def redismaster_metric(key_name):
    """ Sets redismaster to be always passing
    """

    return {key_name: {'name': key_name, 'min': 1, 'max': 1}}


def configure_redismaster(archive_dir, client):
    """ Sets up the client configuration for redismaster metric

    Asks the user for information to connect to their Redis database
    via a Redis Sentinel. Places the connection information in the config file
    """

    _utils.seperator()
    print("\n=====Configuring the redismaster metric=====")

    questions = [
        {
            'type': 'input',
            'name': 'redis_master',
            'message': 'What is the master-group-name that is monitored'
        },
        {
            'type': 'input',
            'name': 'redis_master_ip',
            'message': 'What is the IP address of the Redis master server'
        },
        {
            'type': 'input',
            'name': 'sentinel_ip',
            'message': 'What is the IP address of the sentinel to connect to'
        },
        {
            'type': 'input',
            'name': 'port',
            'message': 'What is the IP address of the sentinel port'
        }
    ]

    answers = _utils.confirm_choice(questions)

    redis_master = answers['redis_master']
    redis_master_ip = answers['redis_master_ip']
    sentinel_ip = answers['sentinel_ip']
    port = answers['port']

    if client == 'POSIX':
        redismaster_dir = "{0}/POSIX/NodePingPUSHClient/modules/redismaster".format(
            archive_dir)
        vars_file = join(redismaster_dir, "variables.sh")

        with open(vars_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace(
            'redis_master=""', 'redis_master="%s"' % redis_master)
        filedata = filedata.replace('redis_master_ip=""',
                                    'redis_master_ip="%s"' % redis_master_ip)
        filedata = filedata.replace(
            'sentinel_ip=""', 'sentinel_ip="%s"' % sentinel_ip)
        filedata = filedata.replace('port=""', 'port="%s"' % port)

        with open(vars_file, 'w', newline='\n') as f:
            f.write(filedata)

    elif client == 'Python' or client == 'Python3':
        redismaster_dir = "{0}/{1}/NodePing{1}PUSH/metrics/redismaster".format(
            archive_dir, client)

        redismaster_file = join(redismaster_dir, "config.py")

        with open(redismaster_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace('REDIS_MASTER = ""',
                                    'REDIS_MASTER = "%s"' % redis_master)

        filedata = filedata.replace('REDIS_MASTER_IP = ""',
                                    'REDIS_MASTER_IP = "%s"' % redis_master_ip)

        filedata = filedata.replace('SENTINEL_IP = ""',
                                    'SENTINEL_IP = "%s"' % sentinel_ip)

        filedata = filedata.replace('PORT = ""', 'PORT = "%s"' % port)

        with open(redismaster_file, 'w', newline='\n') as f:
            f.write(filedata)
