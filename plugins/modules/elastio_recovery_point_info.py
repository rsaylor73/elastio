from ansible.module_utils.basic import AnsibleModule

import json

from ..module_utils.util import noop

def main():
    argument_spec = {
        'elastio_path': {'default': "/usr/bin/elastio", 'type': "path"},
        'tags': {'type': "list", 'elements': "string", 'default': []},
        'types': {'type': "list", 'elements': "string", 'default': []},
        'host': {'type': "str"},
        'ebs': {'type': "str"},
        'ec2': {'type': "str"},
        'efs': {'type': "str"},
        'limit': {'type': "int"},
        'region': {'type': "str"},
        'before': {'type': "str"},
        'after': {'type': "str"}
    }
    out = "{}"
    module = AnsibleModule(argument_spec=argument_spec)
    cmd = [module.params['elastio_path'], "recovery-point", "list", "--output-format", "json"]

    for tag in module.params['tags']:
        cmd += ["--tag", tag]
    
    for t in module.params['types']:
        cmd += ["--type", t]

    for a in ["host", "ebs", "ec2", "limit", "region"]:
        if module.params.get(a):
            cmd += [f"--{a}", module.params[a]]

    if module.params['before']:
        cmd += ["--older-than", module.params['before']]
    
    if module.params['after']:
        cmd += ["--newer-than", module.params['after']]

    (rc, out, err) = module.run_command(cmd)
    out = out.strip().split("\n")
    out = f"[{','.join(out)}]"
    module.exit_json(ansible_facts={'elastio_recovery_point': json.loads(out)})

main() if __name__ == "__main__" else noop()