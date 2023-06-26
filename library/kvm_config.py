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
module: kvm_config

short_description: Parse a given QEMU config into corresponding key/value pairs.

version_added: '1.0.0'

description: Parse a QEMU config (https://pve.proxmox.com/wiki/Manual:_qm.conf)
  into a dictionary containing processed config information for ease of
  ansible use. Blank lines are silently dropped, and invalid configuration
  lines will result in a failed state.

options:
  vmid:
    description: Proxmox VM ID.
    required: true
    type: str
  node:
    description: Proxmox cluster node VM should reside on.
    required: true
    type: str
  template:
    description: String Disk or ISO image to mount in VM using the template
                 mapping. Default: None.
    required: false
    type: dict
  force_stop:
    description: Should the VM be forced stopped? Default: true.
    required: false
    type: str
  cloud_init:
    description: Location of cloud init image on local cluster node.
                 e.g. 'local-lvm'. Default: ''.
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
# Parse config for KVM.
- name: 'Get KVM configuration'
  kvm_config:
    vmid:       '{{ host.pve_kvm.vmid }}'
    node:       '{{ host.pve_kvm.node }}'
    template:   '{{ pve_image_map[host.pve_kvm.template]|default(omit) }}'
    force_stop: '{{ host.pve_kvm.force_stop|default(omit) }}'
    cloud_init: '{{ host.pve_kvm.cloud_init|default(omit) }}'
    firewall:   '{{ host.pve_kvm.firewall|default({}) }}'
    config:     '{{ host.pve_kvm.config  }}'
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
cloud_init:
    description: Cloud init settings ISO autocalculated mountpoint. This is a
                 free mountpoint based on the configuration file that the
                 cloud init settings image can be mounted on. Will be empty if
                 not defined.
    type: string
    returned: always
    sample:
    'ide2'
template:
    description: ISO or Cloud init disk image for VM. If cloud_init is set this
                 will be cloud init root disk information. If unset it will be
                 ISO image information.
    type: dict
    returned: always
    sample:
    {
      'algorithm': 'sha512',
      'checksum': 'ded2dc24ebb876d741ee80bd1e5edba34e32eaded73e2b90820792700c81d512b68a28bae929c8a377b5ec8995b053990616199f5214d07f81fd8603b32e66ce',
      'extension': 'tar.xz',
      'file': 'debian-11-genericcloud-amd64-20211011-792.tar.xz',
      'name': 'debian-11-genericcloud-amd64-20211011-792',
      'url': 'https://cloud.debian.org/cdimage/cloud/bullseye/20211011-792/debian-11-genericcloud-amd64-20211011-792.tar.xz'
    }
disks:
    description: Identified 'disk-like' devices in the configuration file.
    type: list
    returned: always
    sample:
    [
      {
        'disk': 'scsi0',
        'line': 'local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1',
        'file': 'local-lvm:103/vm-103-disk-0.raw',
        'fullname': 'vm-103-disk-0.raw',
        'storage': 'local-lvm',
        'storage-option': '103',
        'name': 'vm-103-disk-0',
        'format': 'raw'},
        'size': '2G',
        'ssd': '1'
      },
      {...},
    ]
isos:
    description: Identified devices mounting ISO images in the configuration
                 file.
    type: list
    returned: always
    sample:
    [
      {
        'disk': 'ide2',
        'line': 'ide2: local:iso/proxmox-ve_6.3-1.iso,media=cdrom',
        'file': 'local:iso/proxmox-ve_6.3-1.iso',
        'fullname': 'proxmox-ve_6.3-1.iso',
        'storage': 'local',
        'storage-option': '',
        'name': 'proxmox-ve_6.3-1',
        'format': 'iso',
        'media': 'cdrom'
      },
      {...},
    ]
root:
    description: Identified root filesystem attributes. Root filesystem is
                 detected as 'disk-0' in the VM.
    type: dict
    returned: always
    sample:
    {
      'disk': 'scsi0',
      'line': 'local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1',
      'file': 'local-lvm:103/vm-103-disk-0.raw',
      'fullname': 'vm-103-disk-0.raw',
      'storage': 'local-lvm',
      'storage-option': '103',
      'name': 'vm-103-disk-0',
      'format': 'raw'},
      'size': '2G',
      'ssd': '1'
      'meta': {
        create': 'local-lvm:4'
      }
    }
config_list:
    description: List of strings from config file.
    type: list
    returned: always
    sample:
    [
      'acpi: 1',
      'agent: enabled=1,fstrim_cloned_disks=1,type=virtio',
      'arch: x86_64',
      'args: -no-reboot -no-hpet',
      'audio0: device=intel-hda,driver=spice',
      'autostart: 1',
      'balloon: 4096',
      'bios: ovmf',
      'boot: order=scsi0;ide0',
      'cdrom: ide2',
    ],
config_text:
    description: String containing entire config file.
    type: string
    returned: always
    sample:
      '# comment line\apci: 1\narch: x86_64\nautostart: 1...'
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
    description: Dict processed config file.
    type: dict
    returned: always
    sample:
    {
      'acpi': '1',
      'agent': {
        'enabled': '1',
        'fstrim_cloned_disks': '1',
        'type': 'virtio'
      },
      'arch': 'x86_64',
      'args': '-no-reboot -no-hpet',
      'audio0': {'device': 'intel-hda', 'driver': 'spice'},
      'autostart': '1',
      'balloon': '4096',
      'bios': 'ovmf',
      'boot': {'order': ['scsi0', 'ide0']},
      'cdrom': 'ide2',
      'cicustom': {
        'meta': '/tmp/meta',
        'network': '/tmp/network',
        'user': '/tmp/user',
        'vendor': '/tmp/user'
      }
      ...
    }
cli_list:
    description: List of configuration file as command line options.
    type: list
    returned: always
    sample:
    [
      '--acpi 1',
      '--agent enabled=1,fstrim_cloned_disks=1,type=virtio',
      '--arch x86_64',
      '--args -no-reboot -no-hpet',
      '--audio0 device=intel-hda,driver=spice',
      '--autostart 1',
      '--balloon 4096',
      '--bios ovmf',
      ...
    ]
cli:
    description: String configuration file as command line options.
    type: string
    returned: always
    sample:
      '--acpi 1 --agent enabled=1,fstrim_cloned_disks=1,type=virtio ...'
'''

def run_module():
    # define available arguments/parameters a user can pass to the module; see
    # defaults/kvm.yml.pve_kvm for defintions.
    module_args = dict(
      vmid=dict(type='str', required=True),
      node=dict(type='str', required=True),
      template=dict(type='dict', required=False),
      force_stop=dict(type='bool', required=False, default=True),
      firewall=dict(type='dict', required=False),
      config=dict(type='str', required=True),
      cloud_init=dict(type='str', required=False, default=None),
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
