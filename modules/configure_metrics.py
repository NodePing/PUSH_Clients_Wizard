#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from importlib.machinery import SourceFileLoader
from PyInquirer import prompt
from os.path import expanduser, isfile

field_options = {}


def _get_names_and_status(key_name, message):
    """ Gets file paths until the user asks to stop
    """

    get_names = True
    names = {}
    i = 1

    while get_names:

        questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': message
            },
            {
                'type': 'list',
                'name': 'state',
                'message': 'Should it be absent or present?',
                'choices': [
                    'Present',
                    'Absent'
                ]
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Add another to the check?'
            }
        ]

        answers = prompt(questions)

        name = "{0}.{1}".format(key_name, answers['name'])
        key = "{0}{1}".format(key_name, i)

        if answers['state'] == 'Present':
            names.update({key: {'name': name, 'min': 1, 'max': 1}})
        elif answers['state'] == 'Absent':
            names.update({key: {'name': name, 'min': 0, 'max': 0}})

        if answers['get_another']:
            i += 1
        else:
            break

    return names


def _get_disk_quotas(key_name, message):
    """ Collects drive names/mountpoints and a min/max capacity
    """

    get_names = True
    names = {}
    i = 1

    while get_names:

        # Min/max are output in an opposite day sort of fashion due to
        # free disk space being sort of opposite
        questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': message
            },
            {
                'type': 'input',
                'name': 'min',
                'message': 'Max disk free space percentage (E.g 20 for 20%)?',
            },
            {
                'type': 'input',
                'name': 'max',
                'message': 'Min disk free space percentage (E.g 80 for 80%)?',
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Add another to the check?'
            }
        ]

        answers = prompt(questions)

        _min = int(answers['min']) / 100
        _max = int(answers['max']) / 100

        name = "{0}.{1}".format(key_name, answers['name'])
        key = "{0}{1}".format(key_name, i)

        names.update({key: {'name': name, 'min': _min, 'max': _max}})

        if answers['get_another']:
            i += 1
        else:
            break

    return names


def apcupsd_metric(key_name):
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


def cassandra_metric(key_name):
    """ Sets Cassandra metric to monitor Cassandra cluster

    Asks user for IPs of Cassandra databases to monitor
    """

    cassandra_ips = []

    adding_ips = True

    while adding_ips:
        check_questions = [
            {
                'type': 'input',
                'name': 'ip',
                'message': 'Cassandra IP address'
            },
            {
                'type': 'confirm',
                'name': 'adding_ips',
                'message': 'Add another IP address'
            }
        ]

        check_answers = prompt(check_questions)

        cassandra_ips.append(check_answers['ip'])
        adding_ips = check_answers['adding_ips']

    cassandra_fields = {}
    i = 1

    for ip in cassandra_ips:
        name = "{0}.{1}".format(key_name, ip)
        key = "{0}{1}".format(key_name, i)
        i += 1

        cassandra_fields.update(
            {key: {'name': name, 'min': 1, 'max': 1}})

    return cassandra_fields


def checkiptables_metric(key_name):
    """
    """

    check_questions = [
        {
            'type': 'input',
            'name': 'ip4_count',
            'message': 'Expected IPv4 rule count:'
        },
        {
            'type': 'input',
            'name': 'ip6_count',
            'message': 'Expected IPv6 rule count:'
        }
    ]

    check_answers = prompt(check_questions)

    ip4 = check_answers['ip4_count']
    ip6 = check_answers['ip6_count']

    metrics = {
        "{0}_ipv4".format(key_name): {
            'name': "{0}.ipv4".format(key_name),
            'min': ip4,
            'max': ip4
        },
        "{0}_ipv6".format(key_name): {
            'name': "{0}.ipv6".format(key_name),
            'min': ip6,
            'max': ip6
        }

    }

    return metrics


def checkpf_firewall_metric(key_name):
    """
    """

    check_questions = [
        {
            'type': 'input',
            'name': 'count',
            'message': 'Expected rule count:'
        }
    ]

    check_answers = prompt(check_questions)

    count = check_answers['count']

    metrics = {
        key_name: {
            'name': key_name,
            'min': count,
            'max': count
        }
    }

    return metrics


def checkpid_metric(key_name):
    """
    """

    message = "What is the /path/to/pidfile.pid?"

    return _get_names_and_status(key_name, message)


def checksum_metric(key_name, client=None):
    """
    """

    check_questions = [
        {
            'type': 'confirm',
            'name': 'has_file',
            'message': 'Do you have an existing checksum config file to read from?'
        },
        {
            'type': 'input',
            'name': 'filename',
            'message': 'What is the path to the file:',
            'when': lambda check_answers: check_answers['has_file']
        },
        {
            'type': 'input',
            'name': 'hash_algo',
            'message': 'What is the hashing algorithm used (SHA1, SHA256, etc.)?',
            'when': lambda check_answers: check_answers['has_file']
        }
    ]

    check_answers = prompt(check_questions)

    if check_answers['has_file']:
        filename = check_answers['filename']

    # Gather from file if user chose to provide one
    # TODO: CREATE FUNCTION TO EXPAND FUNCTIONALITY TO JSON/POSIX
    if check_answers['has_file']:
        fields = {}
        i = 1

        algorithm = check_answers['hash_algo']

        # Parse checksum config files for values
        # Don't need to return the checksum since the file already exists
        if isfile(expanduser(filename)):
            if client == "Python" or client == "Python3":
                checksum_conf = SourceFileLoader(
                    'configfile', filename).load_module()

                files = checksum_conf.files

                for name, checksum in files.items():
                    name = "{0}.{1}".format(key_name, name)
                    key = "{0}{1}".format(key_name, i)
                    i += 1

                    fields.update(
                        {key: {'name': name, 'min': 1, 'max': 1, 'checksum': checksum, 'hash_algorithm': algorithm}})

            elif client == "PowerShell":
                with open(filename, 'r') as f:
                    data = json.load(f)

                for content in data:
                    name = "{0}.{1}".format(key_name, content['FileName'])
                    key = "{0}{1}".format(key_name, i)
                    checksum = content['Hash']
                    algorithm = content['HashAlgorithm']

                    i += 1

                    fields.update({key: {'name': name, 'min': 1, 'max': 1,
                                         'checksum': checksum, 'hash_algorithm': algorithm}})

            elif client == "POSIX":
                with open(filename, 'r') as f:
                    data = f.readlines()

                for content in data:
                    content = content.strip('\n').split()

                    # i[0] == filename and i[1] == the checksum
                    name = "{0}.{1}".format(key_name, content[0])
                    key = "{0}{1}".format(key_name, i)
                    i += 1

                    fields.update(
                        {key: {'name': name, 'min': 1, 'max': 1, 'checksum': content[1], 'hash_algorithm': algorithm}})

            return fields

        # The file doesn't exist if
        else:
            print("Invalid file. Please specify a valid file")

    # Gather file names and its hash directly from user at prompt
    else:
        get_files = True
        files = {}
        i = 1

        while get_files:

            file_questions = [
                {
                    'type': 'input',
                    'name': 'name',
                    'message': 'What is the name and full path of the file:'
                },
                {
                    'type': 'input',
                    'name': 'checksum',
                    'message': 'What is the checksum for this file:'
                },
                {
                    'type': 'input',
                    'name': 'hash_algo',
                    'message': 'What is the hashing algorithm used (SHA1, SHA256, etc.)?',
                },
                {
                    'type': 'confirm',
                    'name': 'get_files',
                    'message': 'Add another file to check?'
                }
            ]

            file_answers = prompt(file_questions)

            name = "{0}.{1}".format(key_name, file_answers['name'])
            key = "{0}{1}".format(key_name, i)

            files.update(
                {key: {'name': name,
                       'checksum': file_answers['checksum'], 'min': 1, 'max': 1, 'hash_algorithm': file_answers['hash_algo']}})

            if file_answers['get_files']:
                i += 1
            else:
                break

        return files


def drives_metric(key_name):
    """ Collects drive names/mountpoints and a min/max capacity
    """

    message = "What is the drive name/mount point?"

    return _get_disk_quotas(key_name, message)


def fileage_metric(key_name):
    """
    """

    get_names = True
    names = {}
    i = 1

    while get_names:

        questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': 'What is the full /path/to/file?'
            },
            {
                'type': 'input',
                'name': 'days',
                'message': 'How many days old max should the file be?'
            },
            {
                'type': 'input',
                'name': 'hours',
                'message': 'How many hours old max should the file be?'
            },
            {
                'type': 'input',
                'name': 'minutes',
                'message': 'How many minutes old max should the file be?'
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Add another to the check?'
            }
        ]

        answers = prompt(questions)

        name = "{0}.{1}".format(key_name, answers['name'])
        key = "{0}{1}".format(key_name, i)
        days = answers['days']
        hours = answers['hours']
        minutes = answers['minutes']

        names.update(
            {key: {'name': name, 'days': days, 'hours': hours, 'minutes': minutes, 'min': 1, 'max': 1}})

        if answers['get_another']:
            i += 1
        else:
            break

    return names


def iocage_metric(key_name):
    """ Set names of iocage jails and the state you expect them to be in
    """

    message = "What is the name of the iocage jail?"

    return _get_names_and_status(key_name, message)


def memory_metric(key_name):
    """ Set the minimum and maximum amount of free memory available on a system
    """

    # Min/max are output in an opposite day sort of fashion due to free memory space being sort of opposite
    questions = [
        {
            'type': 'input',
            'name': 'min',
            'message': 'What is the max memory free you want it to reach (E.g 350)?',
        },
        {
            'type': 'input',
            'name': 'max',
            'message': 'What is the minimum memory free you want it to reach (E.g 8192)?',
        }
    ]

    answers = prompt(questions)

    _min = int(answers['min'])
    _max = int(answers['max'])

    return {key_name: {'name': key_name, 'min': _min, 'max': _max}}


def sqlstat_metric(key_name, client=None):
    """ Set the expected output of a MySQL/MariaDB database
    """

    if client != 'POSIX':
        message = 'What value do you expect to get when running a query? (Default: database count)'

        questions = [
            {
                'type': 'input',
                'name': 'output',
                'message': message,
            }
        ]

        answers = prompt(questions)
        output = int(answers['output'])
    else:
        output = 1

    return {key_name: {'name': key_name, 'min': output, 'max': output}}


def processor_metric(key_name):
    """ Set the minimum and maximum load averages expected for a system
    """

    questions = [
        {
            'type': 'confirm',
            'name': 'is_windows',
            'message': 'Are you getting load metrics for Windows?',
            'default': False
        },
        {
            'type': 'input',
            'name': 'cpumin',
            'message': "What's the min CPU load (load average) you expect?",
            'when': lambda answers: answers['is_windows']
        },
        {
            'type': 'input',
            'name': 'cpumax',
            'message': "What's the max CPU load (or load average) you expect?",
            'when': lambda answers: answers['is_windows']
        },
        {
            'type': 'input',
            'name': '1min_min',
            'message': "What's the 1 minute load min (Blank if ignoring)?",
            'when': lambda answers: not answers['is_windows']
        },
        {
            'type': 'input',
            'name': '1min_max',
            'message': "What's the 1 minute load max (Blank if ignoring)?",
            'when': lambda answers: not answers['is_windows']
        },
        {
            'type': 'input',
            'name': '5min_min',
            'message': "What's the 5 minute load min (Blank if ignoring)?",
            'when': lambda answers: not answers['is_windows']
        },
        {
            'type': 'input',
            'name': '5min_max',
            'message': "What's the 5 minute load max (Blank if ignoring)?",
            'when': lambda answers: not answers['is_windows']
        },
        {
            'type': 'input',
            'name': '15min_min',
            'message': "What's the 15 minute load min (Blank if ignoring)?",
            'when': lambda answers: not answers['is_windows']
        },
        {
            'type': 'input',
            'name': '15min_max',
            'message': "What's the 15 minute load max (Blank if ignoring)?",
            'when': lambda answers: not answers['is_windows']
        }
    ]

    answers = prompt(questions)

    if answers['is_windows']:
        if not answers['cpumin']:
            _min = 0
        else:
            _min = answers['cpumin']

        _max = answers['cpumax']

        return {key_name: {'name': key_name, 'min': _min, 'max': _max}}
    else:
        loads = {}

        if answers['1min_max'] != '':
            key = "{0}{1}".format(key_name, "1min")
            name = "{0}.{1}".format(key_name, "1min")

            if not answers['1min_min']:
                _min = 0
            else:
                _min = answers['1min_min']
            loads.update(
                {key: {'name': name, 'min': _min, 'max': answers['1min_max']}})

        if answers['5min_max'] != '':
            key = "{0}{1}".format(key_name, "5min")
            name = "{0}.{1}".format(key_name, "5min")

            if not answers['5min_min']:
                _min = 0
            else:
                _min = answers['5min_min']
            loads.update(
                {key: {'name': name, 'min': _min, 'max': answers['5min_max']}})

        if answers['15min_max'] != '':
            key = "{0}{1}".format(key_name, "15min")
            name = "{0}.{1}".format(key_name, "15min")

            if not answers['15min_min']:
                _min = 0
            else:
                _min = answers['15min_min']

            loads.update(
                {key: {'name': name, 'min': _min, 'max': answers['15min_max']}})

        return loads


def redismaster_metric(key_name):
    """ Sets redismaster to be always passing
    """

    return {key_name: {'name': key_name, 'min': 1, 'max': 1}}


def memavail_metric(key_name):
    """
    """

    # Min/max are output in an opposite day sort of fashion due to free memory space being sort of opposite
    questions = [
        {
            'type': 'input',
            'name': 'min',
            'message': 'What is the max memory available you want it to reach (E.g 350)?',
        },
        {
            'type': 'input',
            'name': 'max',
            'message': 'What is the minimum memory available you want it to reach (E.g 8192)?',
        }
    ]

    answers = prompt(questions)

    _min = int(answers['min'])
    _max = int(answers['max'])

    name = "{0}".format(key_name)

    return {name: {'name': name, 'min': _min, 'max': _max}}


def pingstatus_metric(key_name):
    """ Sets pingstatus IP addresses and whether they should be pass or fail
    """

    get_hosts = True
    hosts = {}
    i = 1

    while get_hosts:
        questions = [
            {
                'type': 'input',
                'name': 'host',
                'message': 'What is the fqdn or IP of the host you want to ping?'
            },
            {
                'type': 'confirm',
                'name': 'online',
                'message': 'Do you expect this address to be pingable?'
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Do you wish to add another host to ping?'
            }
        ]

        answers = prompt(questions)

        name = "{0}.{1}".format(key_name, answers['host'])
        key = "{0}{1}".format(key_name, i)

        if answers['online']:
            pingable = 1
        else:
            pingable = 0

        hosts.update(
            {key: {'name': name, 'min': pingable, 'max': pingable}})

        if not answers['get_another']:
            break

        i += 1

    return hosts


def zfs_metric(key_name):
    """ Set min/max values on free space for zfs datasets
    """

    message = "Which ZFS dataset do you want to monitor?"

    return _get_disk_quotas(key_name, message)


def start_metric(name):
    """ Print blocks to make metric creation easier to read
    """

    print("===== Configuring {0} =====".format(name))


def end_metric(name):
    """ Print blocks to make metric creation easier to read
    """

    print("===== {0} configuration complete =====\n".format(name))


def main(metrics, client):

    field_values = {}

    for metric in metrics:
        start_metric(metric)

        complete = False

        # metrics with prompts to accept user input are put here to
        # validate if the user input was correct. If not, the while loop
        # repeats and asks the user for the data for that metric again
        while not complete:
            # if metric == 'cassandra':
            #     data = cassandra_metric('cassandra')
            # elif metric == 'checkiptables':
            #     data = checkiptables_metric('checkiptables')
            # elif metric == 'checkpf_firewall':
            #     data = checkpf_firewall_metric('checkpf_firewall')
            # elif metric == 'checksum':
            #     data = checksum_metric('checksum', client)
            # elif metric == 'checkpid':
            #     data = checkpid_metric('checkpid')
            # elif metric == 'drives':
            #     data = drives_metric('drives')
            # elif metric == 'fileage':
            #     data = fileage_metric('fileage')
            # elif metric == 'iocage':
            #     data = iocage_metric('iocage')
            # elif metric == 'memory':
            #     data = memory_metric('memory')
            # elif metric == 'mysqlstat':
            #     data = sqlstat_metric('mysqlstat', client=client)
            # elif metric == 'pgsqlstat':
            #     data = sqlstat_metric('pgsqlstat')
            # elif metric == 'processor':
            #     data = processor_metric('processor')
            # elif metric == 'zfs':
            #     data = zfs_metric('zfs')
            # elif metric == 'diskfree':
            #     data = drives_metric('diskfree')
            # elif metric == 'load':
            #     data = processor_metric('load')
            # elif metric == 'memavail':
            #     data = memavail_metric('memavail')
            # elif metric == 'memfree':
            #     data = memory_metric('memfree')
            # elif metric == 'pingstatus':
            #     data = pingstatus_metric('pingstatus')
            # else:
            #     break

            if 'cassandra' in metric:
                data = cassandra_metric('cassandra')
            elif 'checkiptables' in metric:
                data = checkiptables_metric('checkiptables')
            elif 'checkpf_firewall' in metric:
                data = checkpf_firewall_metric('checkpf_firewall')
            elif 'checksum' in metric:
                data = checksum_metric('checksum', client)
            elif 'checkpid' in metric:
                data = checkpid_metric('checkpid')
            elif 'drives' in metric:
                data = drives_metric('drives')
            elif 'fileage' in metric:
                data = fileage_metric('fileage')
            elif 'iocage' in metric:
                data = iocage_metric('iocage')
            elif 'memory' in metric:
                data = memory_metric('memory')
            elif 'mysqlstat' in metric:
                data = sqlstat_metric('mysqlstat', client=client)
            elif 'pgsqlstat' in metric:
                data = sqlstat_metric('pgsqlstat')
            elif 'processor' in metric:
                data = processor_metric('processor')
            elif 'zfs' in metric:
                data = zfs_metric('zfs')
            elif 'diskfree' in metric:
                data = drives_metric('diskfree')
            elif 'load' in metric:
                data = processor_metric('load')
            elif 'memavail' in metric:
                data = memavail_metric('memavail')
            elif 'memfree' in metric:
                data = memory_metric('memfree')
            elif 'pingstatus' in metric:
                data = pingstatus_metric('pingstatus')
            else:
                break

            complete_questions = [
                {
                    'type': 'confirm',
                    'name': 'complete',
                    'message': 'Does this information look correct'
                }
            ]

            header = "{0:<50}{1:<10}{2:<10}".format("Name", "Min", "Max")
            print("{0}\n{1}".format(header, ("-" * len(header))))

            for key, value in data.items():
                print("{0:<50}{1:<10}{2:<10}".format(
                    value['name'], value['min'], value['max']))

            print("\n")

            complete_answers = prompt(complete_questions)

            if complete_answers['complete']:
                complete = True

        # Metrics here expect no user input and don't need to be
        # prompted for user confirmation for the data being correct
        if 'apcupsd' in metric:
            data = apcupsd_metric('apcupsd')
        elif 'redismaster' in metric:
            data = redismaster_metric('redismaster')

        end_metric(metric)

        field_values.update(data)

    return field_values
