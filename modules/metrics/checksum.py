#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from importlib.machinery import SourceFileLoader
from os.path import expanduser, isfile, join
from pprint import pprint
from InquirerPy import prompt


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
