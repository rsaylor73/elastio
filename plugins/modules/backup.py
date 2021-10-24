#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Greg Wojtak <greg.wojtak@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import subprocess
import pathlib
import platform
import json
import sys

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.elastio_command import ElastioCommand

DOCUMENTATION = r'''
module: elastio.bac.backup
short_description: Perform elastio backup command
description:
  - Performs backup commands and related tasks
options:
  scalez_stor_url:
    description: URL to the scale-z instance
    type: str
    required: false
  type:
    description: The backup type (file, stream, block, etc.)
    type: str
    required: false
    default: file
  path:
    description: 
      - The path to the file to backup.
      - If I(type) is C(block), this should be a block disk device.
      - If I(type) is C(stream), this is ignored
    type: str
    required: true
    aliases: [ src ]
  hostname:
    description: Use the specified string as the hostname instead of the system's
    type: str
    required: false
  elastio_path:
    description: Override the path to the C(elastio) binary on the system
    type: str
    required: false
  vault_name:
    description: Specify a vault to operate with
    type: str
    required: false
  tags:
    description: Set tags for the backup
    type: dict
    required: false
'''

EXAMPLES = r'''
'''

RETURN = r'''
duration:
    description: List containing C(nanos) and C(secs) of elapsed backup time
    returned: When backup exits
    type: list
    sample: {"nanos": 193844001, "secs": 2}
elastio_path:
    description: The full path to the elastio binary used
    returned: When backup exits
    type: path
    sample: /usr/bin/elastio
existing_bytes:
    description: The number of bytes already stored from previous backups
    returned: When backup exits
    type: int
    sample: 2577920
hostname:
    description: The hostname of the resource that was backed up
    returned: When I(hostname) is not empty
    type: string
items:
    description: Extended information about each backed up file
    returned: When backup exits successfully
    type: list
    sample: [{"description": "/boot/memtest86+.bin", "status": {"data": "b-dgcdxpabivvvlo9m48ga0dch:18", "type": "Succeeded"}}]
new_bytes:
    description: The number of non-de-duped bytes backed up
    returned: When backup exits successfully
    type: int
    sample: 3253254346933
src:
    description: A list of files backed up
    returned: When backup exits successfully
    type: list
    sample: ["/boot/memtest86+.bin", "/boot/memtest86+.elf", "/usr/local/bin/composer"]
tags:
    description: Tags applied to the backed up resources
    returned: When backup exits successfully
    type: dict
    sample: {'environment': "prod", 'costcenter': "infosec"}
total_bytes:
    description: Total number of bytes backed up, whether de-duped or not
    returned: When backup exits successfully
    type: int
    sample: 2577920
total_items:
    description: Number of items requested to be backed up
    type: int
    sample: 3
type:
    description: The type of backup that was performed
    type: string
    sample: "file"
vault_name:
    description: The vault used whilst running the backup
    type: string
    sample: "default"
'''


class ElastioBackup(ElastioCommand):
    def __init__(self, module, **kwargs):
        self.type = module.params['type']
        super().__init__(module, self.type, "backup")
        self.path = module.params['path']
        self.hostname = module.params['hostname']

        self.files = " ".join(self.path)

        for f in self.path:
            p = pathlib.Path(f)
            if not p.exists():
                module.fail_json(msg="File does not exist for 'path' option: {}".format(f))

        if self.type == "file":
            if not p.exists():
                module.fail_json(msg="File '{}' does not exist".format(self.files))
        elif self.type == "block":
            if not p.is_block_device():
                module.fail_json(msg="{} is not a block device for backup type 'block'".format(self.type))

def main():
    rc = None
    out = ""
    err = ""

    mod_args = {
        'scalez_stor_url': {'type': "str", 'required': False},
        'type': {'type': "str", 'required': False, 'default': "file"},
        'path': {'type': "list", 'required': True, 'elements': "path", 'aliases': ["src"]},
        'hostname': {'type': "str", 'required': False},
        'vault_name': {'type': "str", 'required': False, 'default': "default"},
        'elastio_path': {'type': "str", 'required': False, 'default': "/usr/bin/elastio"},
        'tags': {'type': "dict", 'required': False, 'default': {}},
    }

    module = AnsibleModule(argument_spec=mod_args, supports_check_mode=False)
    backup = ElastioBackup(module)
    result = backup.execute()

    module.exit_json(**result)

if __name__ == "__main__":
  main()