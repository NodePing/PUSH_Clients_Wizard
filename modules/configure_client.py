#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import distutils.errors
import json
import os
import stat
import sys
import zipfile
from distutils.dir_util import copy_tree
from os.path import expanduser, isfile, join
from os.path import split as path_split
from pprint import pprint
import paramiko
from PyInquirer import prompt

from . import _utils

CLIENT_UNZIPPED_DIR = 'PUSH_Clients-master'


def _add_metric(archive_dir, client_path, name, client):
    """ Adds the metric to the enabled metrics file

    Works with the POSIX, Python/3, and PowerShell clients.
    Removes all default metrics from the metrics file for the specified
    client. Adds the metric that is enabled by the user in manage_checks.py
    """

    if '@' in client_path:
        client_path = client_path.split(':')[-1]

    if client == 'POSIX':
        filename = join(archive_dir, "POSIX/NodePingPUSHClient/moduleconfig")
        metric_path = join(
            client_path, 'NodePingPUSHClient/modules/{0}/{0}.sh\n'.format(name))

        string = "{0}={1}".format(name, metric_path)

        string = _utils.win_to_other_path(string)

        # Append the location of the module to the moduleconfig file
        with open(filename, 'a', newline='\n') as f:
            f.write(string)

        # Make the module executable
        sh_script = join(
            archive_dir, "POSIX/NodePingPUSHClient/modules/{0}/{0}.sh".format(name))

        st = os.stat(sh_script)
        os.chmod(sh_script, st.st_mode | stat.S_IEXEC)

    # Use configparser to add the metric to the [modules] section
    elif client == 'Python' or client == 'Python3':
        filename = join(
            archive_dir, "{0}/NodePing{0}PUSH/config.ini".format(client))

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(filename)

        config.set('modules', name, value='yes')
        _utils.write_config(config, filename)
    elif client == 'PowerShell':
        filename = join(
            archive_dir, "PowerShell/NodePingPowerShellPUSH/moduleconfig.json")

        module = "modules\\{0}\\{0}.ps1".format(name)

        # Data for the new module that will go in the moduleconfig file for PS
        array = {
            "name": name,
            "FileName": "powershell.exe",
            "Arguments": module
        }

        with open(filename, 'r') as f:
            json_data = json.load(f)

        # Append the new module info to the config dictionary
        json_data.append(array)

        # Dump the modules dictionary over the file in JSON format
        with open(filename, 'w') as f:
            f.write(json.dumps(json_data, indent=8, sort_keys=True))


def _empty_config_file(path, client):
    """ Clears all the contents in a config file

    Clears the contents so the defaults do not conflict with the user
    specified checks they want to enable
    """

    if client == 'POSIX':
        filename = join(path, "POSIX/NodePingPUSHClient/moduleconfig")

        open(filename, 'w').close()

    elif client == 'Python' or client == 'Python3':
        filename = join(path, "{0}/NodePing{0}PUSH/config.ini".format(client))

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(filename)

        config.remove_option('modules', 'diskfree')
        config.remove_option('modules', 'load')
        config.remove_option('modules', 'memfree')

        _utils.write_config(config, filename)
    elif client == 'PowerShell':
        filename = join(
            path, "PowerShell/NodePingPowerShellPUSH/moduleconfig.json")

        with open(filename, 'w') as f:
            f.write("[]\n")


def _get_save_directory(check_id):
    """ Asks the user the path where the client will be stored

    This is primarily necessary for POSIX, as the other clients are
    able to operate from any relative path
    """

    check_questions = [
        {
            'type': 'confirm',
            'name': 'run_remote',
            'message': 'Will the client run on a remote machine?'
        },
        {
            'type': 'input',
            'name': 'remote_user',
            'message': 'What remote user you will use for remote copy?',
            'when': lambda answers: answers.get('run_remote', True)
        },
        {
            'type': 'input',
            'name': 'remote_host',
            'message': 'What is the IP/FQDN of the remote server?',
            'when': lambda answers: answers.get('run_remote', True)
        },
        {
            'type': 'input',
            'name': 'save_destionation',
            'message': 'What directory do you want the client stored in?'
        }
    ]

    answers = _utils.confirm_choice(check_questions)

    if not answers['run_remote']:
        save_destionation = expanduser(answers['save_destionation'])
        return "{0}/{1}".format(save_destionation, check_id)
    else:
        user = answers['remote_user']
        server = answers['remote_host']
        save_dir = expanduser(answers['save_destionation'])
        path = "{0}@{1}:{2}/{3}".format(user, server, save_dir, check_id)

        return path


def _place_client(src, dest, client, _id):
    """ Copies the client to its destination

    Accepts a src, destination dir, and the client type. Determines if the dest
    is local or remote and places the client in the necessary directory with
    the permissions of the current user locally, or the user that is being used
    for ssh
    """

    _utils.seperator()

    if client == 'POSIX':
        client_dir = join(src, "POSIX/NodePingPUSHClient")
    else:
        client_dir = join(src, "{0}/NodePing{0}PUSH".format(client))

    if "@" in dest:
        username = dest.split('@')[0]
        host = dest.split('@')[1].split(':')[0]
        # Destination dir being copied to
        dirname = dest.split('@')[1].split(':')[1]

        connected = False

        print("Gathering SSH information")

        while not connected:

            ssh_questions = [
                {
                    'type': 'list',
                    'name': 'use_password',
                    'message': 'Will you use ssh keys or a password',
                    'choices': ['keys', 'password']
                },
                {
                    'type': 'password',
                    'name': 'password',
                    'message': 'Enter the remote user\'s password',
                    'when': lambda answers: answers['use_password'] is 'password'
                },
                {
                    'type': 'input',
                    'name': 'ssh_key',
                    'message': 'Specify the path to the ssh keys to use',
                    'when': lambda answers: answers['use_password'] is 'keys'
                },
                {
                    'type': 'password',
                    'name': 'ssh_key_pass',
                    'message': 'Password for ssh key (if one exists)',
                    'when': lambda answers: answers['use_password'] is 'keys'
                },
                {
                    'type': 'input',
                    'name': 'ssh_port',
                    'message': 'Specify the ssh port (Default 22)',
                    'default': '22'
                },
                {
                    'type': 'list',
                    'name': 'remote_os',
                    'message': 'What is the OS the client will be copied to',
                    'choices': ['Windows', 'Other']
                }
            ]

            answers = _utils.confirm_choice(ssh_questions)

            if not answers['ssh_port']:
                port = 22
            else:
                port = int(answers['ssh_port'])

            try:
                transport = paramiko.Transport((host, port))
            except paramiko.ssh_exception.SSHException:
                input("Unable to connect. Press enter to continue")

                # TODO: ask user if they want to reconnect on fail
                # reconnect = [
                #     {
                #         'type': 'confirm',
                #         'name': 'reconnect',
                #         'message': 'Do you want to try to reconnect?'
                #     }
                # ]

                # connect_answer = _utils.inquirer_confirm(reconnect)

                # if not connect_answer['reconnect']:
                #     return answers['remote_os']
                return answers['remote_os']

            if answers['use_password'] == 'password':
                try:
                    transport.connect(username=username,
                                      password=answers['password'])

                except paramiko.ssh_exception.AuthenticationException:
                    print("SSH authentication failed. Not copying files. Continuing")
                except paramiko.ssh_exception.SSHException:
                    print("SSH Authentication issue. No acceptable MACs")
                else:
                    connected = True

            else:
                key = _utils.get_sshkey(expanduser(
                    answers['ssh_key']), answers['ssh_key_pass'])

                if not key:
                    print("\nInvalid ssh key\n")
                    continue

                try:
                    transport.connect(username=username, pkey=key)

                except paramiko.ssh_exception.AuthenticationException:
                    print("SSH authentication failed. Not copying files. Continuing")
                else:
                    connected = True

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Make nonexistent paths on remote computer
        _utils.make_missing_dirs(sftp, dirname, answers['remote_os'])

        os.chdir(path_split(client_dir)[0])
        parent = path_split(client_dir)[1]

        for item in os.walk(parent):
            local_subdir = item[0]
            files = item[2]

            make_dir = join(dirname, local_subdir)

            if answers['remote_os'] == 'Windows':
                make_dir = _utils.nix_to_win_path(make_dir)
            else:
                make_dir = _utils.win_to_other_path(make_dir)

            sftp.mkdir(make_dir)

            for i in files:
                src_file = join(local_subdir, i)
                dest_file = join(dirname, src_file)

                if answers['remote_os'] == 'Windows':
                    dest_file = _utils.nix_to_win_path(dest_file)
                else:
                    dest_file = _utils.win_to_other_path(dest_file)

                sftp.put(src_file, dest_file)

                # Make remote shell scripts executable
                if ".sh" in dest_file or ".py" in dest_file:
                    sftp.chmod(dest_file, 0o750)

        sftp.close()
        transport.close()

        return answers['remote_os']

    else:
        if os.name == 'nt':
            os_name = 'Windows'
        else:
            os_name = 'Other'

        if client == 'POSIX':
            dest = join(
                dest, "NodePingPUSHClient")
        else:
            dest = join(
                dest, "NodePing{0}PUSH".format(client))

        try:
            os.makedirs(dest)
        except PermissionError:
            print("You do not have permissions to create this directory")
            print(
                "You can find the configured client in {0}\n".format(client_dir))
            input("Press enter to continue: ")

            return os_name

        try:
            copy_tree(client_dir, dest)
        except distutils.errors.DistutilsFileError:
            print("You do not have permissions to copy files to this directory")
            print(
                "You can find the configured client in {0}\n".format(client_dir))
            input("Press enter to continue: ")

        return os_name


def _unzip(zip_archive, dest_dir):
    """ Unzips a .zip archive
    """

    with zipfile.ZipFile(zip_archive, 'r') as master_zip:
        master_zip.extractall(dest_dir)


def configure_checksum(keys, all_metrics, archive_dir, client):
    """ Puts the checksum metric info in its necessary config file

    Accepts the keys that are generated in the configure_metrics py file
    and the whole output from that. Sorts through the keys and grabs the data
    and stores variables in a format that the language reads.
    """

    print("\n=====Configuring the checksum metric=====")

    hash_dict = {}
    hash_list_ps = []

    for key in keys:
        checksum_data = all_metrics[key]

        filename = '.'.join(checksum_data['name'].split('.')[1:])
        checksum = checksum_data['checksum']
        algorithm = checksum_data['hash_algorithm']

        if client == 'POSIX':
            hash_dict.update(
                {filename: {'checksum': checksum, 'algorithm': algorithm}})
        elif client == 'Python' or client == 'Python3':
            hash_dict.update({filename: checksum})

        elif client == 'PowerShell':
            _dict = {"FileName": filename, "Hash": checksum.upper(),
                     "HashAlgorithm": algorithm.upper()}

            hash_list_ps.append(_dict)

    if client == 'POSIX':
        checksum_dir = "{0}/POSIX/NodePingPUSHClient/modules/checksum".format(
            archive_dir)
        checksum_file = join(checksum_dir, "checksum.txt")
        checksum_type_file = join(checksum_dir, "checksum_type.txt")

        # Clear contents of checksum.txt file
        open(checksum_file, 'w').close()
        # Clear contents of checksum_type.txt file
        open(checksum_type_file, 'w').close()

        with open(checksum_file, 'a', newline='\n') as f:
            for key, value in hash_dict.items():
                line = "{0} {1}\n".format(key, value['checksum'])
                f.write(line)

        # Write the hashing algorithm type to file
        with open(checksum_type_file, 'w', newline='\n') as f:
            f.write(hash_dict[filename]['algorithm'].lower())

    elif client == 'Python' or client == 'Python3':
        checksum_dir = "{0}/{1}/NodePing{1}PUSH/metrics/checksum".format(
            archive_dir, client)

        checksum_file = join(checksum_dir, "config.py")

        # Clear contents of config.py file
        open(checksum_file, 'w').close()

        with open(checksum_file, 'a', newline='\n') as f:
            f.write("files = ")
            pprint(hash_dict, stream=f)
            f.write("\nhash_algorithm = \"{0}\"".format(algorithm.lower()))

    elif client == "PowerShell":
        checksum_dir = "{0}/{1}/NodePing{1}PUSH/modules/checksum".format(
            archive_dir, client)

        checksum_file = join(checksum_dir, "checksum.json")

        # Clear contents of the config.json file
        open(checksum_file, 'w').close()

        with open(checksum_file, 'w') as f:
            f.write(json.dumps(hash_list_ps, indent=8, sort_keys=True))


def configure_checkpid(keys, all_metrics, archive_dir, client):
    """ Puts the checkpid metric info in its necessary config file

    Accepts the keys that are generated in the configure_metrics py file
    and the whole output from that. Sorts through the keys and grabs the data
    and stores variables in a format that the language reads.
    """

    print("\n=====Configuring the checkpid metric=====")

    filenames = []

    for key in keys:
        data = all_metrics[key]
        filename = '.'.join(data['name'].split('.')[1:])

        filenames.append(filename)

    if client == "POSIX":
        checkpid_dir = "{0}/POSIX/NodePingPUSHClient/modules/checkpid".format(
            archive_dir)
        checkpid_file = join(checkpid_dir, "checkpid.txt")

        # Clear contents of checkpid.txt file
        open(checkpid_file, 'w').close()

        with open(checkpid_file, 'a', newline='\n') as f:
            for pidfile in filenames:
                f.write("%s\n" % pidfile)

    elif client == "Python" or client == "Python3":
        checkpid_dir = "{0}/{1}/NodePing{1}PUSH/metrics/checkpid".format(
            archive_dir, client)

        checkpid_file = join(checkpid_dir, "config.py")

        # Clear contents of config.py file
        open(checkpid_file, 'w').close()

        with open(checkpid_file, 'w', newline='\n') as f:
            f.write("PIDFILES = ")
            f.write(str(filenames))

    elif client == "PowerShell":
        pass


def configure_fileage(keys, all_metrics, archive_dir, client):
    """ Puts the fileage metric info in its necessary config file

    Sets up the fileage metrics in the appropriate client config files
    """

    print("\n=====Configuring the fileage metric=====")

    if client == 'POSIX':
        fileage_dir = "{0}/POSIX/NodePingPUSHClient/modules/fileage".format(
            archive_dir)
        fileage_file = join(fileage_dir, "fileage.txt")

        lines = []

        for key in keys:
            data = all_metrics[key]
            filename = '.'.join(data['name'].split('.')[1:])
            days = data['days']
            hours = data['hours']
            minutes = data['minutes']

            lines.append("{0} {1} {2} {3}".format(
                filename, days, hours, minutes))

        # Clear contents of fileage.txt file
        open(fileage_file, 'w').close()

        with open(fileage_file, 'a', newline='\n') as f:
            for line in lines:
                f.write("{0}\n".format(line))

    elif client == 'Python' or client == 'Python3':
        fileage_dir = "{0}/{1}/NodePing{1}PUSH/metrics/fileage".format(
            archive_dir, client)
        fileage_file = join(fileage_dir, "config.py")

        files = {}

        for key in keys:
            data = all_metrics[key]
            filename = '.'.join(data['name'].split('.')[1:])
            days = data['days']
            hours = data['hours']
            minutes = data['minutes']
            files.update(
                {filename: {"days": days, "hours": hours, "minutes": minutes}})

        # Clear contents of the config.py file
        open(fileage_file, 'w').close()

        with open(fileage_file, 'a', newline='\n') as f:
            f.write("filenames = ")
            pprint(files, stream=f)

    elif client == 'PowerShell':
        fileage_dir = "{0}/{1}/NodePing{1}PUSH/modules/fileage".format(
            archive_dir, client)

        fileage_file = join(fileage_dir, "fileage.json")

        files = []

        # Clear contents of the fileage.json file
        open(fileage_file, 'w').close()

        for key in keys:
            data = all_metrics[key]
            filename = '.'.join(data['name'].split('.')[1:])
            days = data['days']
            hours = data['hours']
            minutes = data['minutes']

            data = {"FileName": filename, "Age": {
                "days": days, "hours": hours, "minutes": minutes}}

            files.append(data)

        with open(fileage_file, 'w') as f:
            f.write(json.dumps(files, indent=8, sort_keys=True))


def configure_mysqlstat(archive_dir, client):
    """ Sets up the client configuration for mysqlstat metric

    Asks the user for information to connect to their MySQL database
    Places the connection information in the config file
    """

    _utils.seperator()
    print("\n=====Configuring the mysqlstat metric=====")

    questions = [
        {
            'type': 'input',
            'name': 'username',
            'message': 'What is the database username for authentication'
        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'What is the user\'s password? (Will not echo)'
        },
        {
            'type': 'input',
            'name': 'hostname',
            'message': 'What host will you be connecting on (e.g. 127.0.0.1)'
        },
        {
            'type': 'input',
            'name': 'querystring',
            'message': 'Query to run (empty for default of getting db count)'
        }
    ]

    answers = _utils.confirm_choice(questions)

    username = answers['username']
    password = answers['password']
    host = answers['hostname']
    querystring = answers['querystring']

    if client == 'POSIX':
        mysqlstat_dir = "{0}/POSIX/NodePingPUSHClient/modules/mysqlstat".format(
            archive_dir)
        vars_file = join(mysqlstat_dir, "variables.sh")

        if not querystring:
            with open(vars_file, 'r', newline='\n') as f:
                for line in f:
                    if "querystring" in line:
                        querystring = line.split('=')[1]

        with open(vars_file, 'w', newline='\n') as f:
            f.write("username=\"%s\"\n" % username)
            f.write("password=\"%s\"\n" % password)
            f.write("host=\"%s\"\n" % host)
            f.write("querystring=%s" % querystring)

    elif client == 'Python' or client == 'Python3':
        py_questions = [
            {
                'type': 'input',
                'name': 'unix_socket',
                'message': 'Path to the mysql.sock socket (required if not Windows, usually in /tmp)'
            }
        ]

        py_answers = prompt(py_questions)
        unix_socket = py_answers['unix_socket']

        mysqlstat_dir = "{0}/{1}/NodePing{1}PUSH/metrics/mysqlstat".format(
            archive_dir, client)

        mysqlstat_file = join(mysqlstat_dir, "config.py")

        with open(mysqlstat_file, 'w', newline='\n') as f:
            f.write("username = \'%s\'\n" % username)
            if not host:
                f.write("host = \'localhost\'\n")
            else:
                f.write("host = \'%s\'\n" % host)

            if not unix_socket:
                f.write("unix_socket = \'\'\n")
            else:
                f.write("unix_socket = \'%s\'\n" % unix_socket)
            f.write("password = \'%s\'\n" % password)

            if not querystring:
                f.write(
                    "querystring = \'SELECT * FROM information_schema.SCHEMATA\'\n")
            else:
                f.write("querystring = \'%s\'\n" % querystring)

            f.write("return_db_count = True\n")

    print("\n=====mysqlstat client configuration complete=====")


def configure_pgsqlstat(archive_dir, client):
    """ Sets up the client configuration for pgsqlstat metric

    Asks the user for information to connect to their PostgreSQL database
    Places the connection information in the config file
    """

    _utils.seperator()
    print("\n=====Configuring the pgsqlstat metric=====")

    questions = [
        {
            'type': 'input',
            'name': 'username',
            'message': 'What is the database username for authentication'
        },
        {
            'type': 'input',
            'name': 'querystring',
            'message': 'Query to run (empty for default of getting db count)'
        }
    ]

    answers = _utils.confirm_choice(questions)

    username = answers['username']
    querystring = answers['querystring']

    if client == 'POSIX':
        pgsqlstat_dir = "{0}/POSIX/NodePingPUSHClient/modules/pgsqlstat".format(
            archive_dir)
        vars_file = join(pgsqlstat_dir, "variables.sh")

        if not querystring:
            with open(vars_file, 'r', newline='\n') as f:
                for line in f:
                    if "querystring" in line:
                        querystring = line.split('=')[1]

        with open(vars_file, 'w', newline='\n') as f:
            f.write("username=\"%s\"\n" % username)
            f.write("querystring=%s" % querystring)
    else:
        pass

    print("\n=====pgsqlstat client configuration complete=====")


def configure_pingstatus(keys, all_metrics, archive_dir, client):
    """ Puts the pingstatus metric info in its necessary config file

    Uses the data gathered from configure_metrics.py to insert the hosts
    to ping. This function also prompts the user for the timeout time and
    number of pings to send per host.
    """

    _utils.seperator()
    print("\n=====Configuring the pingstatus metric=====")

    hosts = []

    for key in keys:
        data = all_metrics[key]
        host = '.'.join(data['name'].split('.')[1:])

        hosts.append(host)

    questions = [
        {
            'type': 'input',
            'name': 'ping_count',
            'message': 'How many times do you want to ping each host'
        },
        {
            'type': 'input',
            'name': 'timeout',
            'message': 'How many seconds to wait before timing out'
        }
    ]

    answers = _utils.confirm_choice(questions)

    ping_count = answers['ping_count']
    timeout = answers['timeout']

    if client == "POSIX":
        pingstatus_dir = "{0}/POSIX/NodePingPUSHClient/modules/pingstatus".format(
            archive_dir)
        pingstatus_file = join(pingstatus_dir, "variables.sh")

        hosts = ' '.join(hosts)

        with open(pingstatus_file, 'w', newline='\n') as f:
            f.write("ping_hosts=\"%s\"\n" % hosts)
            f.write("ping_count=%s\n" % ping_count)
            f.write("timeout=%s\n" % timeout)

    elif client == 'Python' or client == 'Python3':
        pingstatus_dir = "{0}/{1}/NodePing{1}PUSH/metrics/pingstatus".format(
            archive_dir, client)

        pingstatus_file = join(pingstatus_dir, "config.py")

        with open(pingstatus_file, 'w', newline='\n') as f:
            f.write("ping_hosts = %s\n" % str(hosts))
            f.write("ping_count = \"%s\"\n" % ping_count)
            f.write("timeout = \"%s\"\n" % timeout)


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


def configure_ip_addrs(archive_dir, client):
    """ Sets up the client configuration for ip_addrs metric

    Asks the user for IP addresses that they except to be on their system.
    If any other IP appears, they will be alerted.
    """

    _utils.seperator()
    print("\n=====Configuring the ip_addrs metric=====")

    VAR_NAME = 'acceptable_ips'

    host_ips = []

    adding_ips = True
    complete = False

    while not complete:
        while adding_ips:
            check_questions = [
                {
                    'type': 'input',
                    'name': 'ip',
                    'message': 'Allowed IP address'
                },
                {
                    'type': 'confirm',
                    'name': 'adding_ips',
                    'message': 'Add another IP address'
                }
            ]

            check_answers = prompt(check_questions)

            host_ips.append(check_answers['ip'])
            adding_ips = check_answers['adding_ips']

        print(str(host_ips))

        complete = _utils.inquirer_confirm("Are these IP addresses correct?")

    if client == 'POSIX':
        ip_addrs_dir = "{0}/POSIX/NodePingPUSHClient/modules/ip_addrs".format(
            archive_dir)
        vars_file = join(ip_addrs_dir, "variables.sh")

        ips = ' '.join(host_ips)

        with open(vars_file, 'w', newline='\n') as f:
            f.write("{0}='{1}'\n".format(VAR_NAME, ips))
    elif client == 'Python' or client == 'Python3':
        ip_addrs_dir = "{0}/{1}/NodePing{1}PUSH/metrics/ip_addrs".format(
            archive_dir, client)

        ip_addrs_file = join(ip_addrs_dir, "config.py")

        with open(ip_addrs_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace('acceptable_addrs = ["192.168.0.16"]',
                                    'acceptable_addrs = %s' % host_ips)

        with open(ip_addrs_file, 'w', newline='\n') as f:
            f.write(filedata)
    elif client == 'PowerShell':
        ip_addrs_dir = "{0}/{1}/NodePing{1}PUSH/modules/ip_addrs".format(
            archive_dir, client)

        ip_addrs_file = join(ip_addrs_dir, "ip_addrs.json")

        # Clear contents of the ip_addrs.json file
        open(ip_addrs_file, 'w').close()

        with open(ip_addrs_file, 'w') as f:
            f.write(json.dumps(host_ips, indent=8, sort_keys=True))


def configure_dnslookup(archive_dir, client):
    """ Sets up the client configuration for dnslookup metric

    Asks user for the information to perform a DNS query, such as
    the server to query, query, expected result, and record type
    """

    _utils.seperator()
    print("\n=====Configuring the dnslookup metric=====")

    # False if the user is still adding information. This will be true if
    # the user says the info they input is correct
    complete = False

    while not complete:
        check_questions = [
            {
                'type': 'input',
                'name': 'dns_ip',
                'message': 'IP address of the DNS server to query (optional)'
            },
            {
                'type': 'input',
                'name': 'to_resolve',
                'message': 'Hostname or IP to resolve'
            },
            {
                'type': 'input',
                'name': 'record_type',
                'message': 'Record type to query (A, AAAA, CNAME, etc.)'
            }
        ]

        dns_answers = prompt(check_questions)

        dns_results = []

        # Remains true if the user is still adding IPs that are expected
        # as output from DNS query
        adding_ips = True

        while adding_ips:
            result_questions = [
                {
                    'type': 'input',
                    'name': 'output',
                    'message': 'Expected output'
                },
                {
                    'type': 'confirm',
                    'name': 'adding_ips',
                    'message': 'Are there other expected results from the query?'
                }
            ]

            result_answers = prompt(result_questions)

            dns_results.append(result_answers['output'])
            adding_ips = result_answers['adding_ips']

        print("DNS Server IP: %s" % dns_answers['dns_ip'])
        print("FQDN/IP to resolve: %s" % dns_answers['to_resolve'])
        print("Query type: %s" % dns_answers['record_type'])
        print("Expected results: %s " % str(dns_results))

        complete = _utils.inquirer_confirm("Are these IP addresses correct?")

    if client == 'POSIX':
        dnslookup_dir = "{0}/POSIX/NodePingPUSHClient/modules/dnslookup".format(
            archive_dir)
        vars_file = join(dnslookup_dir, "variables.sh")

        results = ' '.join(dns_results)

        with open(vars_file, 'w', newline='\n') as f:
            f.write("# DNS server IP to query\n")
            f.write("dns_ip='{0}'\n".format(dns_answers['dns_ip']))

            f.write("\n# Hostname to resolve\n")
            f.write("to_resolve='{0}'\n".format(dns_answers['to_resolve']))

            f.write("\n# Expected IP or hostname as output.\n")
            f.write("expected_output='{0}'\n".format(results))

            f.write("record_type='{0}'".format(dns_answers['record_type']))
    elif client == 'Python' or client == 'Python3':
        dnslookup_dir = "{0}/{1}/NodePing{1}PUSH/metrics/dnslookup".format(
            archive_dir, client)

        dnslookup_file = join(dnslookup_dir, "config.py")

        with open(dnslookup_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace('dns_ip = "64.34.204.155"',
                                    'dns_ip = "%s"' % dns_answers['dns_ip'])
        filedata = filedata.replace('to_resolve = "nodeping.com"',
                                    'to_resolve = "%s"' % dns_answers['to_resolve'])
        filedata = filedata.replace('expected_output = "167.114.101.137"',
                                    'expected_output = %s' % str(dns_results))
        filedata = filedata.replace('query_type = "A"',
                                    'query_type = "%s"' % dns_answers['record_type'])

        with open(dnslookup_file, 'w', newline='\n') as f:
            f.write(filedata)


def configure_mongodbstat(archive_dir, client):
    """ Sets up the client configuration for mongodbstat metric

    Asks the user for information such as the comand to evaluate, expected
    output (which would be a substring), optional authentication, and
    optionally the path to the mongo executable
    """

    _utils.seperator()
    print("\n=====Configuring the mongodbstat metric=====")

    # False if the user is still adding information. This will be true if
    # the user says the info they input is correct
    complete = False

    while not complete:
        check_questions = [
            {
                'type': 'input',
                'name': 'eval_string',
                'message': 'Command for mongo to evaluate',
                'default': 'db.runCommand( {connectionStatus: 1});'
            },
            {
                'type': 'input',
                'name': 'expected_output',
                'message': 'Expected output or substring',
                'default': '"ok" : 1'
            },
            {
                'type': 'input',
                'name': 'username',
                'message': 'Username for authentication to database (skip if none)',
                'default': ''
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'Password for authentication to the database',
                'default': '',
                'when': lambda answers: answers['username']
            },
            {
                'type': 'input',
                'name': 'mongo_path',
                'message': 'What is the path to the mongo executable',
                'default': 'mongo'
            }
        ]

        answers = prompt(check_questions)

        if not answers['username']:
            username = None
        else:
            username = answers['username']

        try:
            password = answers['password']
        except KeyError:
            password = None
            answers.update({"password": ""})

        print("Evaluated command: %s" % answers['eval_string'])
        print("Expected response in output: %s" % answers['expected_output'])
        if answers['username']:
            print("Username: %s" % answers['username'])
            print("Password: ****")
        print("Mongo path: %s " % answers['mongo_path'])

        complete = _utils.inquirer_confirm("Is this information correct?")

    if client != "PowerShell":
        answers['expected_output'] = answers['expected_output'].replace(
            '"', r'\"')

    if client == 'POSIX':
        mongodbstat_dir = "{0}/POSIX/NodePingPUSHClient/modules/mongodbstat".format(
            archive_dir)
        vars_file = join(mongodbstat_dir, "variables.sh")

        if not username:
            username = ""
        if not password:
            password = ""

        with open(vars_file, 'w', newline='\n') as f:
            f.write("# This string will be evaluated by mongo with the --eval flag\n")
            f.write("eval_string=\"{0}\"\n".format(answers['eval_string']))

            f.write(
                "# All of or a portion of what you expect in the result to be successful\n")
            f.write("expected_output=\"{0}\"\n".format(
                answers['expected_output']))

            f.write("# Optional user authentication\n")
            f.write("username=\"{0}\"\n".format(username))

            f.write("# Optional password authentication\n")
            f.write("password=\"{0}\"\n".format(password))

    elif client in ("Python", "Python3"):
        mongodbstat_dir = "{0}/{1}/NodePing{1}PUSH/metrics/mongodbstat".format(
            archive_dir, client)

        mongodbstat_file = join(mongodbstat_dir, "config.py")

        with open(mongodbstat_file, 'r', newline='\n') as f:
            filedata = f.read()

        if isinstance(username, str):
            username = '\"%s\"' % username
        if isinstance(password, str):
            password = '\"%s\"' % password

        filedata = filedata.replace('eval_string = "db.runCommand( {connectionStatus: 1});"',
                                    'eval_string = "%s"' % answers['eval_string'])
        filedata = filedata.replace('expected_output = "\"ok\" : 1"',
                                    'expected_output = "%s"' % answers['expected_output'])
        filedata = filedata.replace('username = None',
                                    'username = %s' % username)
        filedata = filedata.replace('password = None',
                                    'password = %s' % password)
        filedata = filedata.replace('mongo_path = r"mongo"',
                                    'mongo_path = r"%s"' % answers['mongo_path'])

        with open(mongodbstat_file, 'w', newline='\n') as f:
            f.write(filedata)

    elif client == 'PowerShell':
        mongodbstat_dir = "{0}/{1}/NodePing{1}PUSH/modules/mongodbstat".format(
            archive_dir, client)

        mongodbstat_file = join(mongodbstat_dir, "mongodbstat.json")

        # Clear contents of the mongodbstat.json file
        open(mongodbstat_file, 'w').close()

        with open(mongodbstat_file, 'w') as f:
            f.write(json.dumps(answers, indent=8, sort_keys=True))


def insert_checktoken(checktoken, _id, unarchived, save_path, client):
    """ Places the checktoken in the client's config file
    """

    if client == 'POSIX':
        configfile = join(
            unarchived, 'POSIX/NodePingPUSHClient/NodePingPUSH.sh')

        with open(configfile, 'r', newline='\n') as f:
            filedata = f.read()

        moduleconfig = '/full/path/to/moduleconfig'
        logfile = '/full/path/to/logfile/NodePingPUSH.log'

        # If server is remote, removes the full remote path to just full path
        try:
            full_path = "{0}/NodePingPUSHClient".format(
                save_path.split('@')[1].split(':')[1])
        except IndexError:
            full_path = "{0}/NodePingPUSHClient".format(save_path)

        # Insert CheckID and checktoken
        filedata = filedata.replace('CHECK_ID_HERE', _id)
        filedata = filedata.replace('CHECK_TOKEN_HERE', checktoken)
        filedata = filedata.replace(
            moduleconfig, "{0}/moduleconfig".format(full_path))
        filedata = filedata.replace(
            logfile, "{0}/NodePingPUSH.log".format(full_path))

        with open(configfile, 'w', newline='\n') as f:
            f.write(filedata)
    elif client == 'Python' or client == 'Python3':
        configfile = join(
            unarchived, '{0}/NodePing{0}PUSH/config.ini'.format(client))

        config = configparser.ConfigParser()
        config.read(configfile)

        config.set('server', 'id', value=_id)
        config.set('server', 'checktoken', value=checktoken)

        _utils.write_config(config, configfile)
    elif client == 'PowerShell':
        configfile = join(
            unarchived, 'PowerShell/NodePingPowerShellPUSH/NodePingPUSH.ps1')

        with open(configfile, 'r') as f:
            filedata = f.read()

        filedata = filedata.replace('Your Check ID here', _id)
        filedata = filedata.replace('Your Check Token here', checktoken)

        with open(configfile, 'w') as f:
            f.write(filedata)


def client_set_executable(path, client):
    """
    """

    if client == 'Python' or client == 'Python3':
        # Make Python script executable
        py_script = join(
            path, "{0}/NodePing{0}PUSH/NodePingPythonPUSH.py".format(client))

        st = os.stat(py_script)
        os.chmod(py_script, st.st_mode | stat.S_IEXEC)
    elif client == 'POSIX':
        # Make POSIX script executable
        sh_script = join(path, "POSIX/NodePingPUSHClient/NodePingPUSH.sh")

        st = os.stat(sh_script)
        os.chmod(sh_script, st.st_mode | stat.S_IEXEC)


def main(metrics, client_zip, client):
    """ Configures the client config file and metrics files
    to contain the necessary information to run
    """

    _utils.seperator()
    print("\nConfiguring client metrics\n")

    completed_checks = []

    # Assigns the token to variables and removes them from the dictionary
    checktoken = metrics['checktoken']
    check_id = metrics['check_id']
    del metrics['checktoken']
    del metrics['check_id']

    final_destination = _get_save_directory(check_id)

    # Assuming the zip file from GitHub is in the same dir as app.py
    if sys.platform == 'windows':
        archive_dir = client_zip.strip(client_zip.split('\\')[-1])
    else:
        archive_dir = client_zip.strip(client_zip.split('/')[-1])

    # The name and path of the GH zip file when unarchived
    unarchived = join(archive_dir, CLIENT_UNZIPPED_DIR)

    # If the zip file isn't unzipped, unzip it
    if isfile(client_zip):
        _unzip(client_zip, archive_dir)

    # Make the config files a clean slate to remove default modules
    _empty_config_file(unarchived, client)

    for key, value in metrics.items():
        name = value['name'].split('.')[0]

        if name in completed_checks:
            continue

        if 'checksum' in name:
            name = 'checksum'
            keys = [key for key in metrics if 'checksum' in key]

            configure_checksum(keys, metrics, unarchived, client)

        elif 'checkpid' in name:
            name = 'checkpid'
            keys = [key for key in metrics if 'checkpid' in key]

            configure_checkpid(keys, metrics, unarchived, client)

        elif 'fileage' in name:
            name = 'fileage'
            keys = [key for key in metrics if 'fileage' in key]

            configure_fileage(keys, metrics, unarchived, client)

        elif 'pingstatus' in name:
            name = 'pingstatus'
            keys = [key for key in metrics if 'pingstatus' in key]

            configure_pingstatus(keys, metrics, unarchived, client)

        elif name == 'mysqlstat':
            configure_mysqlstat(unarchived, client)

        elif name == 'pgsqlstat':
            configure_pgsqlstat(unarchived, client)

        elif name == 'redismaster':
            configure_redismaster(unarchived, client)

        elif name == 'ip_addrs':
            configure_ip_addrs(unarchived, client)

        elif name == 'dnslookup':
            configure_dnslookup(unarchived, client)

        elif name == 'mongodbstat':
            configure_mongodbstat(unarchived, client)

        _add_metric(unarchived, final_destination, name, client)

        completed_checks.append(name)

    # Inserts check token into the proper file
    insert_checktoken(checktoken, check_id, unarchived,
                      final_destination, client)

    # Sets client script to executable
    client_set_executable(unarchived, client)
    # Copies the client to the proper location
    # Gets OS that client was copied to
    os = _place_client(unarchived, final_destination, client, check_id)

    if '@' in final_destination:
        dest = final_destination.split('@')[1].split(':')[1]
        user = final_destination.split('@')[0]
        return {'user': user, 'dest': dest, 'os': os}
    else:
        return {'user': '', 'dest': final_destination, 'os': os}
