from ansible.module_utils.basic import AnsibleModule

import fnmatch
import json

from ..module_utils.util import noop

def main():
    argument_spec = {
        'elastio_path': {'default': "/usr/bin/elastio", 'type': "path"},
        'filter': {'type': "list", 'elements': "dict"}
    }
    module = AnsibleModule(argument_spec=argument_spec)
    cmd = [
      module.params['elastio_path'], "vault", "list", "--output-format", "json"
    ]
    (rc, out, err) = module.run_command(cmd)
    
    if module.params['filter']:
      vaults = []
      for vault in json.loads(out).get('vaults'):
        for vault_filter in module.params['filter']:
          for k, v in vault_filter.items():
            if fnmatch.fnmatch(vault[k], v):
              vaults.append(vault)
    else:
      vaults = json.loads(out).get('vaults')

    fact = {'elastio_vaults': vaults}
    module.exit_json(ansible_facts=fact)

main() if __name__ == "__main__" else noop()
