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
import paramiko

from . import _utils

CLIENT_UNZIPPED_DIR = "PUSH_Clients-master"


def _add_metric(archive_dir, client_path, name, client):
    """ Adds the metric to the enabled metrics file

    Works with the POSIX, Python/3, and PowerShell clients.
    Removes all default metrics from the metrics file for the specified
    client. Adds the metric that is enabled by the user in manage_checks.py
    """

    if "@" in client_path:
        client_path = client_path.split(":")[-1]

    if client == "POSIX":
        filename = join(archive_dir, "POSIX/NodePingPUSHClient/moduleconfig")

        # Append the location of the module to the moduleconfig file
        with open(filename, "a", newline="\n") as f:
            f.write("{0}\n".format(name))

        # Make the module executable
        sh_script = join(
            archive_dir, "POSIX/NodePingPUSHClient/modules/{0}/{0}.sh".format(name)
        )

        st = os.stat(sh_script)
        os.chmod(sh_script, st.st_mode | stat.S_IEXEC)

    # Use configparser to add the metric to the [modules] section
    elif client == "Python" or client == "Python3":
        filename = join(archive_dir, "{0}/NodePing{0}PUSH/config.ini".format(client))

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(filename)

        config.set("modules", name, value="yes")
        _utils.write_config(config, filename)
    elif client == "PowerShell":
        filename = join(
            archive_dir, "PowerShell/NodePingPowerShellPUSH/moduleconfig.json"
        )

        module = "modules\\{0}\\{0}.ps1".format(name)

        # Data for the new module that will go in the moduleconfig file for PS
        array = {"name": name, "FileName": "powershell.exe", "Arguments": module}

        with open(filename, "r") as f:
            json_data = json.load(f)

        # Append the new module info to the config dictionary
        json_data.append(array)

        # Dump the modules dictionary over the file in JSON format
        with open(filename, "w") as f:
            f.write(json.dumps(json_data, indent=8, sort_keys=True))


def _empty_config_file(path, client):
    """ Clears all the contents in a config file

    Clears the contents so the defaults do not conflict with the user
    specified checks they want to enable
    """

    if client == "POSIX":
        filename = join(path, "POSIX/NodePingPUSHClient/moduleconfig")

        open(filename, "w").close()

    elif client == "Python" or client == "Python3":
        filename = join(path, "{0}/NodePing{0}PUSH/config.ini".format(client))

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(filename)

        config.remove_option("modules", "diskfree")
        config.remove_option("modules", "load")
        config.remove_option("modules", "memfree")

        _utils.write_config(config, filename)
    elif client == "PowerShell":
        filename = join(path, "PowerShell/NodePingPowerShellPUSH/moduleconfig.json")

        with open(filename, "w") as f:
            f.write("[]\n")


def _get_save_directory(check_id):
    """ Asks the user the path where the client will be stored

    This is primarily necessary for POSIX, as the other clients are
    able to operate from any relative path
    """

    check_questions = [
        {
            "type": "confirm",
            "name": "run_remote",
            "message": "Will the client run on a remote machine?",
        },
        {
            "type": "input",
            "name": "remote_user",
            "message": "What remote user you will use for remote copy?",
            "when": lambda answers: answers.get("run_remote", True),
        },
        {
            "type": "input",
            "name": "remote_host",
            "message": "What is the IP/FQDN of the remote server?",
            "when": lambda answers: answers.get("run_remote", True),
        },
        {
            "type": "input",
            "name": "save_destionation",
            "message": "What directory do you want the client stored in?",
        },
    ]

    answers = _utils.confirm_choice(check_questions)

    if not answers["run_remote"]:
        save_destionation = expanduser(answers["save_destionation"])
        return "{0}/{1}".format(save_destionation, check_id)
    else:
        user = answers["remote_user"]
        server = answers["remote_host"]
        save_dir = expanduser(answers["save_destionation"])
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

    if client == "POSIX":
        client_dir = join(src, "POSIX/NodePingPUSHClient")
    else:
        client_dir = join(src, "{0}/NodePing{0}PUSH".format(client))

    if "@" in dest:
        username = dest.split("@")[0]
        host = dest.split("@")[1].split(":")[0]
        # Destination dir being copied to
        dirname = dest.split("@")[1].split(":")[1]

        connected = False

        print("Gathering SSH information")

        while not connected:

            ssh_questions = [
                {
                    "type": "list",
                    "name": "use_password",
                    "message": "Will you use ssh keys or a password",
                    "choices": ["keys", "password"],
                },
                {
                    "type": "password",
                    "name": "password",
                    "message": "Enter the remote user's password",
                    "when": lambda answers: answers["use_password"] == "password",
                },
                {
                    "type": "input",
                    "name": "ssh_key",
                    "message": "Specify the path to the ssh keys to use",
                    "when": lambda answers: answers["use_password"] == "keys",
                },
                {
                    "type": "password",
                    "name": "ssh_key_pass",
                    "message": "Password for ssh key (if one exists)",
                    "when": lambda answers: answers["use_password"] == "keys",
                },
                {
                    "type": "input",
                    "name": "ssh_port",
                    "message": "Specify the ssh port (Default 22)",
                    "default": "22",
                },
                {
                    "type": "list",
                    "name": "remote_os",
                    "message": "What is the OS the client will be copied to",
                    "choices": ["Windows", "Other"],
                },
            ]

            answers = _utils.confirm_choice(ssh_questions)

            if not answers["ssh_port"]:
                port = 22
            else:
                port = int(answers["ssh_port"])

            try:
                transport = paramiko.Transport((host, port))
            except paramiko.ssh_exception.SSHException:
                input("Unable to connect. Press enter to continue")

                reconnect = "Do you want to try to reconnect?"
                connect_answer = _utils.inquirer_confirm(reconnect)
                print(connect_answer)

                if not connect_answer:
                    return answers["remote_os"]

                continue

            if answers["use_password"] == "password":
                try:
                    transport.connect(username=username, password=answers["password"])

                except paramiko.ssh_exception.AuthenticationException:
                    print("SSH authentication failed. Not copying files. Continuing")
                except paramiko.ssh_exception.SSHException:
                    print("SSH Authentication issue. No acceptable MACs")
                else:
                    connected = True

            else:
                key = _utils.get_sshkey(
                    expanduser(answers["ssh_key"]), answers["ssh_key_pass"]
                )

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
        _utils.make_missing_dirs(sftp, dirname, answers["remote_os"])

        os.chdir(path_split(client_dir)[0])
        parent = path_split(client_dir)[1]

        for item in os.walk(parent):
            local_subdir = item[0]
            files = item[2]

            make_dir = join(dirname, local_subdir)

            if answers["remote_os"] == "Windows":
                make_dir = _utils.nix_to_win_path(make_dir)
            else:
                make_dir = _utils.win_to_other_path(make_dir)

            sftp.mkdir(make_dir)

            for i in files:
                src_file = join(local_subdir, i)
                dest_file = join(dirname, src_file)

                if answers["remote_os"] == "Windows":
                    dest_file = _utils.nix_to_win_path(dest_file)
                else:
                    dest_file = _utils.win_to_other_path(dest_file)

                sftp.put(src_file, dest_file)

                # Make remote shell scripts executable
                if ".sh" in dest_file or ".py" in dest_file:
                    sftp.chmod(dest_file, 0o750)

        sftp.close()
        transport.close()

        return answers["remote_os"]

    else:
        if os.name == "nt":
            os_name = "Windows"
        else:
            os_name = "Other"

        if client == "POSIX":
            dest = join(dest, "NodePingPUSHClient")
        else:
            dest = join(dest, "NodePing{0}PUSH".format(client))

        try:
            os.makedirs(dest)
        except PermissionError:
            print("You do not have permissions to create this directory")
            print("You can find the configured client in {0}\n".format(client_dir))
            input("Press enter to continue: ")

            return os_name

        try:
            copy_tree(client_dir, dest)
        except distutils.errors.DistutilsFileError:
            print("You do not have permissions to copy files to this directory")
            print("You can find the configured client in {0}\n".format(client_dir))
            input("Press enter to continue: ")

        return os_name


def _unzip(zip_archive, dest_dir):
    """ Unzips a .zip archive
    """

    with zipfile.ZipFile(zip_archive, "r") as master_zip:
        master_zip.extractall(dest_dir)


def insert_checktoken(checktoken, _id, unarchived, save_path, client):
    """ Places the checktoken in the client's config file
    """

    if client == "POSIX":
        configfile = join(unarchived, "POSIX/NodePingPUSHClient/NodePingPUSH.sh")

        with open(configfile, "r", newline="\n") as f:
            filedata = f.read()

        moduleconfig = "/full/path/to/moduleconfig"
        logfile = "/full/path/to/logfile/NodePingPUSH.log"

        # If server is remote, removes the full remote path to just full path
        try:
            full_path = "{0}/NodePingPUSHClient".format(
                save_path.split("@")[1].split(":")[1]
            )
        except IndexError:
            full_path = "{0}/NodePingPUSHClient".format(save_path)

        # Insert CheckID and checktoken
        filedata = filedata.replace('CHECK_ID=""', 'CHECK_ID="{0}"'.format(_id))
        filedata = filedata.replace('CHECK_TOKEN=""', 'CHECK_TOKEN="{0}"'.format(checktoken))
        filedata = filedata.replace(moduleconfig, "{0}/moduleconfig".format(full_path))
        filedata = filedata.replace(logfile, "{0}/NodePingPUSH.log".format(full_path))

        with open(configfile, "w", newline="\n") as f:
            f.write(filedata)
    elif client == "Python" or client == "Python3":
        configfile = join(unarchived, "{0}/NodePing{0}PUSH/config.ini".format(client))

        config = configparser.ConfigParser()
        config.read(configfile)

        config.set("server", "id", value=_id)
        config.set("server", "checktoken", value=checktoken)

        _utils.write_config(config, configfile)
    elif client == "PowerShell":
        configfile = join(
            unarchived, "PowerShell/NodePingPowerShellPUSH/NodePingPUSH.ps1"
        )

        with open(configfile, "r") as f:
            filedata = f.read()

        filedata = filedata.replace("Your Check ID here", _id)
        filedata = filedata.replace("Your Check Token here", checktoken)

        with open(configfile, "w") as f:
            f.write(filedata)


def client_set_executable(path, client):
    """
    """

    if client == "Python" or client == "Python3":
        # Make Python script executable
        py_script = join(
            path, "{0}/NodePing{0}PUSH/NodePingPythonPUSH.py".format(client)
        )

        st = os.stat(py_script)
        os.chmod(py_script, st.st_mode | stat.S_IEXEC)
    elif client == "POSIX":
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
    checktoken = metrics["checktoken"]
    check_id = metrics["check_id"]
    del metrics["checktoken"]
    del metrics["check_id"]

    final_destination = _get_save_directory(check_id)

    # Assuming the zip file from GitHub is in the same dir as app.py
    if sys.platform == "windows":
        archive_dir = client_zip.strip(client_zip.split("\\")[-1])
    else:
        archive_dir = client_zip.strip(client_zip.split("/")[-1])

    # The name and path of the GH zip file when unarchived
    unarchived = join(archive_dir, CLIENT_UNZIPPED_DIR)

    # If the zip file isn't unzipped, unzip it
    if isfile(client_zip):
        _unzip(client_zip, archive_dir)

    # Make the config files a clean slate to remove default modules
    _empty_config_file(unarchived, client)

    for key, value in metrics.items():
        name = value["name"].split(".")[0]

        if name in completed_checks:
            continue

        if "checksum" in name:
            name = "checksum"
            keys = [key for key in metrics if "checksum" in key]

            import modules.metrics.checksum as checksum

            checksum.configure_checksum(keys, metrics, unarchived, client)

        elif "checkpid" in name:
            name = "checkpid"
            keys = [key for key in metrics if "checkpid" in key]

            import modules.metrics.checkpid as checkpid

            checkpid.configure_checkpid(keys, metrics, unarchived, client)

        elif "fileage" in name:
            name = "fileage"
            keys = [key for key in metrics if "fileage" in key]

            import modules.metrics.fileage as fileage

            fileage.configure_fileage(keys, metrics, unarchived, client)

        elif "pingstatus" in name:
            name = "pingstatus"
            keys = [key for key in metrics if "pingstatus" in key]

            import modules.metrics.pingstatus as pingstatus

            pingstatus.configure_pingstatus(keys, metrics, unarchived, client)

        elif "httpcheck" in name:
            name = "httpcheck"
            keys = [key for key in metrics if name in key]

            # configure_httpcheck(keys, metrics, unarchived, client)
            import modules.metrics.httpcheck as httpcheck

            httpcheck.configure_httpcheck(unarchived, client)

        elif name == "mysqlstat":
            import modules.metrics.sqlstat as sqlstat

            sqlstat.configure_mysqlstat(unarchived, client)

        elif name == "pgsqlstat":
            import modules.metrics.sqlstat as sqlstat

            sqlstat.configure_pgsqlstat(unarchived, client)

        elif name == "redismaster":
            import modules.metrics.redismaster as redismaster

            redismaster.configure_redismaster(unarchived, client)

        elif name == "ip_addrs":
            import modules.metrics.ip_addrs as ip_addrs

            ip_addrs.configure_ip_addrs(unarchived, client)

        elif name == "dnslookup":
            import modules.metrics.dnslookup as dnslookup

            dnslookup.configure_dnslookup(unarchived, client)

        elif name == "mongodbstat":
            import modules.metrics.mongodbstat as mongodbstat

            mongodbstat.configure_mongodbstat(unarchived, client)

        elif name == "net_utilization":
            keys = [key for key in metrics if "net_utilization" in key]
            import modules.metrics.net_utilization as net_utilization

            net_utilization.configure_net_utilization(keys, metrics, unarchived, client)

        elif name == "smartctl":
            keys = [key for key in metrics if "smartctl" in key]

            import modules.metrics.smartctl as smartctl

            smartctl.configure_smartctl(keys, metrics, unarchived, client)

        elif name == "zpool":
            keys = [key for key in metrics if "zpool" in key]

            import modules.metrics.zpool as zpool

            zpool.configure_zpool(keys, metrics, unarchived, client)

        _add_metric(unarchived, final_destination, name, client)

        completed_checks.append(name)

    # Inserts check token into the proper file
    insert_checktoken(checktoken, check_id, unarchived, final_destination, client)

    # Sets client script to executable
    client_set_executable(unarchived, client)
    # Copies the client to the proper location
    # Gets OS that client was copied to
    user_os = _place_client(unarchived, final_destination, client, check_id)

    if "@" in final_destination:
        dest = final_destination.split("@")[1].split(":")[1]
        user = final_destination.split("@")[0]
        return {"user": user, "dest": dest, "os": user_os}

    return {"user": "", "dest": final_destination, "os": user_os}
