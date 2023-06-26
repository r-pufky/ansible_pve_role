#!/usr/bin/python
#
# KVM file validation data. This is the "expected" resultant data from library
# processing of config files in conf/.
#
# Test static config files with all options set. Run from 'module_utils' with
#
#   python3 -m unittest
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html


PCT_ALL_OPTIONS_INFERRED_CLI_LIST = [
    '--arch amd64',
    '--cmode tty',
    '--console 1',
    '--cores 4',
    '--cpulimit 2',
    '--cpuunits 1024',
    '--debug 0',
    '--description Description for the Container.',
    '--features force_rw_sys=1,fuse=1,keyctl=1,mknod=1,mount=nfs;ext4,nesting=1',
    '--hookscript /tmp/hookscript',
    '--hostname test.example.com',
    '--lock migrate',
    '--memory 4096',
    '--mp0 volume=/d,mp=/data,acl=1,backup=1,mountoptions=readonly;fdsk,quota=1,replicate=1,ro=1,shared=1,size=4G',
    '--mp1 volume=/d,mp=/data,acl=1,backup=1,mountoptions=readonly;fdsk,quota=1,replicate=1,ro=1,shared=1,size=4G',
    '--nameserver 1.1.1.2',
    '--net0 name=eth0,bridge=vmbr0,firewall=1,gw=1.1.1.1,gw6=FE08::1,hwaddr=AA:BB:CC:DD:EE:FF,ip=1.1.1.10/24,ip6=FE08::1/64,mtu=1500,rate=100,tag=2,trunks=1;2;3;4,type=veth',
    '--onboot 1',
    '--ostype debian',
    '--protection 1',
    '--rootfs volume=local-lvm:vm-100-disk-0,acl=1,mountoptions=readonly;fsck,quota=1,replicate=1,ro=1,shared=1,size=4G',
    '--searchdomain example.com',
    '--startup order=1,up=1,down=1',
    '--swap 1024',
    '--tags Tags of the Container.',
    '--template 1',
    '--timezone America/Los_Angeles',
    '--tty 2',
    '--unprivileged 1',
    '--unused0 volume=local-lvm:vm-100-disk-1,size=50G',
    '--unused1 volume=local-lvm:vm-100-disk-2,size=50G'
]


PCT_ALL_OPTIONS_INFERRED_CLI_STRING = ' '.join(PCT_ALL_OPTIONS_INFERRED_CLI_LIST)


PCT_ALL_OPTIONS_INFERRED_ANSIBLE = {
    'arch': 'amd64',
    'cmode': 'tty',
    'console': '1',
    'cores': '4',
    'cpulimit': '2',
    'cpuunits': '1024',
    'debug': '0',
    'description': 'Description for the Container.',
    'features': {
      'force_rw_sys': '1',
      'fuse': '1',
      'keyctl': '1',
      'mknod': '1',
      'mount': ['nfs', 'ext4'],
      'nesting': '1'
    },
    'hookscript': '/tmp/hookscript',
    'hostname': 'test.example.com',
    'lock': 'migrate',
    'memory': '4096',
    'mp0': {
      'acl': '1',
      'backup': '1',
      'mountoptions': ['readonly', 'fdsk'],
      'mp': '/data',
      'quota': '1',
      'replicate': '1',
      'ro': '1',
      'shared': '1',
      'size': '4G',
      'volume': '/d'
    },
    'mp1': {
      'acl': '1',
      'backup': '1',
      'mountoptions': ['readonly', 'fdsk'],
      'mp': '/data',
      'quota': '1',
      'replicate': '1',
      'ro': '1',
      'shared': '1',
      'size': '4G',
      'volume': '/d'
    },
    'nameserver': '1.1.1.2',
    'net0': {
      'bridge': 'vmbr0',
      'firewall': '1',
      'gw': '1.1.1.1',
      'gw6': 'FE08::1',
      'hwaddr': 'AA:BB:CC:DD:EE:FF',
      'ip': '1.1.1.10/24',
      'ip6': 'FE08::1/64',
      'mtu': '1500',
      'name': 'eth0',
      'rate': '100',
      'tag': '2',
      'trunks': ['1', '2', '3', '4'],
      'type': 'veth'
    },
    'onboot': '1',
    'ostype': 'debian',
    'protection': '1',
    'rootfs': {
      'acl': '1',
      'mountoptions': ['readonly', 'fsck'],
      'quota': '1',
      'replicate': '1',
      'ro': '1',
      'shared': '1',
      'size': '4G',
      'volume': 'local-lvm:vm-100-disk-0',
    },
    'searchdomain': 'example.com',
    'startup': {'down': '1', 'order': '1', 'up': '1'},
    'swap': '1024',
    'tags': 'Tags of the Container.',
    'template': '1',
    'timezone': 'America/Los_Angeles',
    'tty': '2',
    'unprivileged': '1',
    'unused0': {'size': '50G', 'volume': 'local-lvm:vm-100-disk-1'},
    'unused1': {'size': '50G', 'volume': 'local-lvm:vm-100-disk-2'}
}


PCT_ALL_OPTIONS_INFERRED_ANSIBLE_LIST = [
    'arch: amd64',
    'cmode: tty',
    'console: 1',
    'cores: 4',
    'cpulimit: 2',
    'cpuunits: 1024',
    'debug: 0',
    'description: Description for the Container.',
    'features: force_rw_sys=1,fuse=1,keyctl=1,mknod=1,mount=nfs;ext4,nesting=1',
    'hookscript: /tmp/hookscript',
    'hostname: test.example.com',
    'lock: migrate',
    'memory: 4096',
    'mp0: volume=/d,mp=/data,acl=1,backup=1,mountoptions=readonly;fdsk,quota=1,replicate=1,ro=1,shared=1,size=4G',
    'mp1: volume=/d,mp=/data,acl=1,backup=1,mountoptions=readonly;fdsk,quota=1,replicate=1,ro=1,shared=1,size=4G',
    'nameserver: 1.1.1.2',
    'net0: name=eth0,bridge=vmbr0,firewall=1,gw=1.1.1.1,gw6=FE08::1,hwaddr=AA:BB:CC:DD:EE:FF,ip=1.1.1.10/24,ip6=FE08::1/64,mtu=1500,rate=100,tag=2,trunks=1;2;3;4,type=veth',
    'onboot: 1',
    'ostype: debian',
    'protection: 1',
    'rootfs: '
    'volume=local-lvm:vm-100-disk-0,acl=1,mountoptions=readonly;fsck,quota=1,replicate=1,ro=1,shared=1,size=4G',
    'searchdomain: example.com',
    'startup: order=1,up=1,down=1',
    'swap: 1024',
    'tags: Tags of the Container.',
    'template: 1',
    'timezone: America/Los_Angeles',
    'tty: 2',
    'unprivileged: 1',
    'unused0: volume=local-lvm:vm-100-disk-1,size=50G',
    'unused1: volume=local-lvm:vm-100-disk-2,size=50G'
]


PCT_ALL_OPTIONS_INFERRED_ANSIBLE_ROOT = {
    'acl': '1',
    'disk': 'rootfs',
    'file': 'local-lvm:vm-100-disk-0',
    'format': '',
    'fullname': 'vm-100-disk-0',
    'line': 'rootfs: volume=local-lvm:vm-100-disk-0,acl=1,mountoptions=readonly;fsck,quota=1,replicate=1,ro=1,shared=1,size=4G',
    'mountoptions': 'readonly;fsck',
    'name': 'vm-100-disk-0',
    'quota': '1',
    'replicate': '1',
    'ro': '1',
    'shared': '1',
    'size': '4G',
    'storage': 'local-lvm',
    'storage-option': '',
    'meta': {
      'create': 'local-lvm:4'
    }
}