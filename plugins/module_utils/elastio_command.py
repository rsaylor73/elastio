# -*- coding: utf-8 -*-
#
import pathlib
import json

class ElastioCommand(object):
    def __init__(self, module, subcmd, action, **kwargs):
        self.module = module
        self.subcmd = subcmd
        self.action = action
        self.scalez_stor_url = module.params['scalez_stor_url']
        self.src = module.params['src']
        self.hostname = module.params['hostname']
        self.elastio_path = module.params['elastio_path']
        self.vault_name = module.params['vault_name']
        self.tags = module.params['tags']

        self.validate()
        self.build_cmd()

    def validate(self):
        if self.scalez_stor_url and self.skip_url_check:
            try:
                from validators import url
            except (ModuleNotFoundError, ImportError):
                self.module.warn(
                    ("Unable to import `url' validator from `validators' package.  "
                    "To enable this, install the `validators' package.  To disable this warning, "
                    "set `skip_url_check' to `true'.")
                )
            else:
                if not url(self.scalez_stor_url):
                    module.fail_json(msg="Malformed url for 'scalez_stor_url': {}".format(self.scalez_stor_url))
        
        p = pathlib.Path(self.elastio_path)
        if not p.is_file():
            module.fail_json(msg="Unable to find elastio binary at {}".format(self.elastio_path))
        
        if self.subcmd == "block":
            for f in self.src:
                p = pathlib.Path(f)
                if not p.is_block_device():
                    module.fail_json(msg="{} is not a block device suitable for a block device backup")


    def build_cmd(self):
        self.cmd = [self.elastio_path, self.subcmd, self.action]
        if self.scalez_stor_url:
            self.cmd += ["--scalez_stor_url", self.scalez_stor_url]
        
        if self.vault_name:
            self.cmd += ["--vault", self.vault_name]

        if self.hostname:
            self.cmd += ["--hostname-override", self.hostname]

        for k, v in self.tags.items():
            self.cmd += ["--tag", f"{k}:{v}"]

        self.cmd += ["--output-format", "json"]
        self.cmd += self.src

    def execute(self) -> dict:
        return_output = self.module.run_command(self.cmd)
        rc = return_output[0]
        out = json.loads(return_output[1])
        err = json.loads(return_output[2])

        result = out['data']
        result['changed'] = True if out['data']['new_bytes'] > 0 else False
        result.update(self.module.params)

        return result
