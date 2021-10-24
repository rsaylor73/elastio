from ansible.module_utils.basic import AnsibleModule

class ElastioVault(object):
    def __init__(self, module, **kwargs):
        self.state_cmd = {'present': "init", 'absent': "delete"}
        self.module = module
        self.state = module.params['state']
        self.vpc = module.params['vpc']
        self.subnets = module.params['subnets']
        self.scalez_image = module.params['scalez_image']
        self.elastio_path = module.params['elastio_path']

        self.build_cmd()

    def build_cmd(self):
        self.cmd = [self.elastio_path, "vault"]
        self.cmd = self.cmd.append(self.state_cmd[self.state])

        if self.state == "present":
            if self.vpc:
                self.cmd += ["--vpc", self.vpc]
            if len(self.subnets) >= 1:
                self.cmd += ["--subnets", ",".join(self.subnets)]
            if self.scalez_image:
                self.cmd += ["--scalez_image", self.scalez_image]

    def vault_exists(self, vault_name):
        list_cmd = [self.elastio_path, "vault", "list", "--output-format", "json"]
        (rc, out, err) = self.module.run_command(list_cmd)
        
        for vault in out.get('vaults', []):
            if vault['vault_id'] == vault_name:
                return True
        return False

def main():
    argument_spec = {
        'name': {'type': "str", 'required': True},
        'state': {'type': "str", 'choices': ["present", "absent"]},
        'vpc': {'type': "str", 'required': False},
        'subnets': {'type': "list", 'required': False},
        'scalez_image': {'type': "str", 'required': False},
        'elastio_path': {'type': "path", 'default': "/usr/bin/elastio"}
    }

    module = AnsibleModule(argument_spec=argument_spec)
    vault = ElastioVault(module)

if __name__ == "__main__":
    main()