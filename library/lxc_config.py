#!/usr/bin/python
#
# Ansible interface to kvm module.
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-a-module
# * https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils import parsers
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: lxc_config

short_description: Parse a given PCT (LXC) config into key/value pairs.

version_added: '1.0.0'

description: Parse a PCT config (https://pve.proxmox.com/wiki/Manual:_pct.conf)
  into a dictionary containing processed config information for ease of
  ansible use. Blank lines are silently dropped, and invalid configuration
  lines will result in a failed state.

options:
  vmid:
    description: Proxmox container ID.
    required: true
    type: str
  node:
    description: Proxmox cluster node container should reside on.
    required: true
    type: str
  template:
    description: String Disk or ISO image to mount in VM using the template
                 mapping. Default: None.
    required: false
    type: dict
  force_stop:
    description: Should the container be forced stopped? Default: true.
    required: false
    type: str
  firewall:
    description: Firewall configuration. Default: {}.
    required: false
    type: dict
  config:
    description: Configuration to process (qm.conf).
    required: true
    type: str

author:
    - Robert Pufky (@r-pufky)
'''

EXAMPLES = r'''
# Parse config for LXC.
- name: 'Get LXC configuration'
  lxc_config:
    vmid:       '{{ host.pve_lxc.vmid }}'
    node:       '{{ host.pve_lxc.node }}'
    template:   '{{ pve_image_map[host.pve_lxc.template]|default(omit) }}'
    force_stop: '{{ host.pve_lxc.force_stop|default(omit) }}'
    firewall:   '{{ host.pve_lxc.firewall|default({}) }}'
    config:     '{{ host.pve_lxc.config  }}'
  register: _pve_vm
'''

RETURN = r'''
vmid:
    description: VM ID.
    type: integer
    returned: always
    sample:
    100
node:
    description: Cluster node VM should be created/reside on.
    type: string
    returned: always
    sample:
    'pm1.example.com'
force_stop:
    description: Whether the VM should be forced stop if it cannot be shutdown
                 cleanly. Default: 'True'.
    type: boolean
    returned: always
    sample:
    True
template:
    description: Container image to use. Images can be obtained through GUI or
                 'pveam update && pveam available'.
    type: dict
    returned: always
    sample:
    {
      'url': 'debian-11-standard_11.0-1_amd64.tar.gz'
      'file': 'debian-11-standard_11.0-1_amd64.tar.gz'
      'name': 'debian-11-standard_11.0-1_amd64'
      'extension': 'tar.gz'
    }
root:
    description: Root system disk for the LXC image.
    type: dict
    returned: always
    sample:
    {
      'acl': '1',
      'disk': 'rootfs',
      'file': 'local-lvm:vm-100-disk-0.raw',
      'format': 'raw',
      'fullname': 'vm-100-disk-0',
      'line': 'rootfs: volume=local-lvm:vm-100-disk-0.raw,acl=1,mountoptions=readonly;fsck,quota=1,replicate=1,ro=1,shared=1,size=4G',
      'mountoptions': 'readonly;fsck',
      'name': 'vm-100-disk-0',
      'quota': '1',
      'replicate': '1',
      'ro': '1',
      'shared': '1',
      'size': '4G',
      'storage': 'local-lvm',
      'storage-option': 'raw'
      'meta': {
        create': 'local-lvm:4'
      }
    }
config_list:
    description: List of strings containing each line from the config file.
    type: list
    returned: always
    sample:
    [
      '# comment line',
      'arch: amd64'
      'cores: 64'
      'hostname: lxc-vm-example'
      'memory: 127000'
      'mp0: mp=/d,/d'
      'lxc.idmap: u 0 100000 300'
      'rootfs: local-lvm:vm-200-disk-0,size=4G'
      ...
    ]
config_text:
    description: String containing entire config file.
    type: string
    returned: always
    sample:
      '# comment line\narch: amd64\ncores: 64\nhostname: lxc-vm-example ...'
firewall:
    description: Firewall configuration.
    type: dict
    returned: optional
    sample:
    {
      'dhcp': True
      'enable': False
      'ipfilter': False
      'log_level_in': 'nolog'
      'log_level_out': 'nolog'
      'macfilter': True
      'ndp': True
      'policy_in': 'DROP'
      'policy_out': 'ACCEPT'
      'radv': False
      'rules': []
      'ipset': []
      'ip_aliases': []
    }
config:
    description: Dict processed config file. Note: LXC Extensions are not
                 considered to be part of the main config. See 'lxc' dict.
    type: dict
    returned: always
    sample:
    {
      'arch': {
        'default': 'amd64',
        'meta': {
          'key': 'arch',
          'line': 'amd64'
        }
      },
      'cores': {
        'default': '4',
        'meta': {
          'key': 'cores',
          'line': '4'
        }
      },
      'features': {
        'meta': {
          'key': 'features',
          'line': 'nesting=1'
        },
        'nesting': '1'
      },
      'hostname': {
        'default': 'xpihole',
        'meta': {
          'key': 'hostname',
          'line': 'xpihole'
        }
      },
      'rootfs': {
        'file': 'local-lvm:vm-200-disk-0',
        'create': 'local-lvm:4',
        'format': '',
        'fullname': 'vm-200-disk-0',
        'key': 'rootfs',
        'line': 'local-lvm:vm-200-disk-0,size=4G',
        'name': 'vm-200-disk-0',
        'storage': 'local-lvm',
        'storage-option': ''
        'size': '4G'
      }
      ...
lxc:
    description: LXC extension mappings. LXC extensions are not part of the
                 general proxmox container config definitions and are processed
                 in a lxc specific section. Keyed by the full classifier.
                 See: https://linuxcontainers.org/lxc/manpages/man5/lxc.container.conf.5.html#lbAR
    type: dict
    returned: always
    sample:
    {
      'lxc.cgroup2.devices.allow': [
        'c 508:* rwm',
      ],
      'lxc.mount.entry": [
        '/dev/nvidia-caps /dev/nvidia-caps none bind,optional,create=dir'
      ],
      'lxc.init_cmd': [
        '/sbin/my_own_init',
        '/sbin/command2',
      ],
      'lxc.idmap': [
        'u 0 100000 1005',
        'g 0 100000 1005',
        'u 1005 1005 1',
        'g 1005 1005 1',
        'u 1006 101006 64530',
        'g 1006 101006 64530',
      ],
      '...': [...],
      'meta': {
        'subuid': ['root:1005:1'],
        'subgid': ['root:1005:1'],
        'idmap': [
          {
            'ctype': 'u',
            'cid': '0',
            'hid': '100000',
            'crange': '1005'
          },
          {
            'ctype': 'g',
            'cid': '0',
            'hid': '100000',
            'crange': '1005'
          },
          {
            'ctype': 'u',
            'cid': '1005',
            'hid': '1005',
            'crange': '1'
          },
        ],
      }
    }
cli_list:
    description: List of configuration file as command line options.
    type: list
    returned: always
    sample:
    [
      '--arch amd64',
      '--cmode tty',
      '--console 1',
      '--cores 4',
      '--cpulimit 2',
      '--cpuunits 1024',
      '--debug 0',
      '--description Description for the Container.',
      ...
    ]
cli:
    description: String configuration file as command line options.
    type: string
    returned: always
    sample:
      '--arch amd64 --cmode tty --console 1 --cores 4 --cpulimit 2 ...'
'''

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
      vmid=dict(type='str', required=True),
      node=dict(type='str', required=True),
      template=dict(type='dict', required=False),
      force_stop=dict(type='bool', required=False, default=True),
      firewall=dict(type='dict', required=False),
      config=dict(type='str', required=True),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    try:
      result = parsers.PveConfig(module.params).Ansible()
    except Exception as e:
      module.fail_json(msg='unable to parse config: %s' % e.message, **result)

    # if the user is working with this module in only check mode we do not
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
