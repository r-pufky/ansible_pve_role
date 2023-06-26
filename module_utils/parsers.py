#!/usr/bin/python
#
# Parse pct.conf, qm.conf, pct, qm configuration options and return cli,
# config, and ansible formatted options. Testing validates config static
# syntax checking, but not runtime values (e.g. proper format).
#
# Run unittests from module_utils: python3 -m unittest
#
# NOTE(upgrade): Every new major release check for parameter changes. Check
#                against conf/{pct,qm}_all_options_explicit.conf to quickly
#                identify new parameters.
#
# Reference:
# * https://pve.proxmox.com/wiki/Manual:_qm.conf
# * https://pve.proxmox.com/pve-docs/qm.1.html

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from dataclasses import asdict

try:
  from ansible.module_utils import data
except:
  import data


class PveConfig(object):
  '''Present KVM config in an ansible-consumable way.

  Attributes
    config_type: PveConfigType representing the source configuration file.
  '''

  def __init__(self, module=None):
    '''Initialize PveConfig.

    Args
      module: dict 'module.params' in which all module options are contained:
          'vmid': int VMID. Required.
          'node': str pve cluster node vm/container resides on.
          'template': dict containing data.ImageMap options. optional.
          'force_stop': bool True to force stop KVM on shutdown. optional.
          'firewall': dict containing firewall options. optional.
          'config': str config file.
          'cloud_init': str cluster/node storage pool (identifies cloud init
              image). optional.

    Raises
      Exception inherited from sub-classes.
    '''
    self.vmid = int(module['vmid'])
    self.node = module['node']
    if 'template' in module:
      self.image = data.ImageMap(**module['template'])
    else:
      self.image = None
    self.force_stop = module.get('force_stop', True)
    self.firewall = module.get('firewall', {})
    self._TokenizeConfig(module['config'])
    self.cloud_init = module.get('cloud_init', '')


  def _TokenizeConfig(self, raw):
    '''Tokenize the provided config into QmeuConfig objects.

    Set config type based on existing known KVM/LXC exclusive required options.

    Args
      raw: str qm.conf or qm cli string.
    '''
    self.tokens = []
    if 'rootfs' in raw:
      self.config_type = data.PveConfigType.LXC
    else:
      self.config_type = data.PveConfigType.KVM

    if ' --' in raw:
      for option in raw.split(' --'):
        if not option or option.lower() == 'qm':
          continue
        self.tokens.append(data.PveConfigOption(option, config=self.config_type))
    else:
      for option in raw.splitlines():
        if not option:
          continue
        self.tokens.append(data.PveConfigOption(option, config=self.config_type))

  def Config(self):
    '''Return dict equivalent for the tokenized config'''
    config = {}
    for token in self.tokens:
      config.update(token.Ansible())
    return config

  def ConfigText(self):
    '''Return str file equivalent for the tokenized config'''
    return '\n'.join(self.ConfigList())

  def ConfigList(self):
    '''Return list file equivalent for the tokenized config'''
    return [x.Config() for x in self.tokens]

  def Cli(self):
    '''Return str CLI equivalent for the tokenized config.'''
    return f'{" ".join(self.CliList())}'

  def CliList(self):
    '''Return list CLI equivalent for the tokenized config.'''
    return list(map(lambda c: c.Cli(), filter(lambda x: x.type != data.PveType.COMMENT, self.tokens)))

  def _Disks(self):
    '''Generate ansible-consumble dict for all system disks.

    This private method returns disks of all types, including rootfs.

    Returns
      list containing all disks for config.
      [
        {
          'disk': 'scsi0',
          'line': 'file=local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1',
          'file': 'local-lvm:103/vm-103-disk-0.raw',
          'fullname': 'vm-103-disk-0.raw',
          'storage': 'local-lvm',
          'storage-option': '103',
          'name': 'vm-103-disk-0',
          'format': 'raw'},
          'size': '2G',
          'ssd': '1',
          'meta': {
            'create': 'local-lvm:2'
          },
        },
        {...},
      ]
    '''
    disks = []
    for token in filter(lambda x: x.type == data.PveType.DISK or x.type == data.PveType.ROOTFS, self.tokens):
      disk = {'disk': token.key, 'line': token.line}
      for option in token.value:
        if option.key == 'file' or option.key == 'volume':
          if '/' in str(option):
            raw_storage, fullname = str(option.value).split('/')
            storage, storage_option = raw_storage.split(':')
          else:
            storage, fullname = str(option.value).split(':')
            storage_option = ''

          if '.' in fullname:
            # cover tar.gz, tar.xz
            if '.tar.' in fullname:
              name, tar, ext = fullname.rsplit('.', 2)
              format = f'{tar}.{ext}'
            else:
              name, format = fullname.rsplit('.', 1)
          else:
            name = fullname
            format = ''
          disk['file'] = str(option.value)
          disk['fullname'] = fullname
          disk['storage'] = storage
          disk['storage-option'] = storage_option
          disk['name'] = name
          disk['format'] = format
          continue

        # Parse standard KEY_VALUE options.
        disk[option.key] = str(option.value)

      if 'size' in disk:
        disk.update({'meta': {'create': f'{disk["storage"]}:{"".join([n for n in disk["size"] if n.isdigit()])}'}})
      disks.append(disk)
    return disks

  def Disks(self):
    '''Generate ansible-consumble dict for all system disks.

    Returns
      list containing all disks for config.
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
          'meta': {
            'create': 'local-lvm:2'
          },
        },
        {...},
      ]
    '''
    disks = []
    for disk in self._Disks():
      if disk['storage-option'] != 'iso':
        disks.append(disk)
    return disks

  def Isos(self):
    '''Generate ansible-consumble dict for all system iso mounts.

    Returns
      list containing all isos for config.
      [
        {
          'disk': 'ide2',
          'line': 'ide2: local:iso/proxmox-ve_6.3-1.iso,media=cdrom',
          'file': 'local:iso/proxmox-ve_6.3-1.iso',
          'fullname': 'proxmox-ve_6.3-1.iso',
          'storage': 'local',
          'storage-option': 'iso',
          'name': 'proxmox-ve_6.3-1',
          'format': 'raw',
          'media': 'cdrom'
        },
        {...},
      ]
    '''
    isos = []
    for disk in self._Disks():
      if disk['storage-option'] == 'iso':
        isos.append(disk)
    return isos

  def RootDisk(self):
    '''Generate ansible-consumble dict for system root disk.

    The root disk is considered to be vm-{ID}-disk-0. If parsing an LXC image
    this is the 'rootfs' disk.

    'create' key is added, which creates a pre-generated auto-create command
    for the device.

    Raises
      KeyError when the primary disk cannot be found.

    Returns
      dict containing root disk.
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
        'ssd': '1',
        'meta': {
          'create': 'local-lvm:50'
        }
      }
    '''
    for disk in self._Disks():
      if 'rootfs' in disk['disk']:
        return disk
      if '-disk-0' in disk['fullname']:
        return disk

    raise KeyError('Primary (root) disk (disk-0) could not be found.')

  def ImageOptions(self):
    '''Return dict containing image template.'''
    if self.image:
      return asdict(self.image)

    return {}

  def CloudInitMap(self):
      '''Generate ansible-consumble string for cloudinit setting location.

      Cloudinit settings may be attached to a KVM instance via a disk mount,
      mapped with 'cloud_init'. This is typically mounted on ideX as an ISO
      using CDROM emulation. This is only checked if 'cloud_init' is defined.

      Raises:
        SyntaxError if a cloudinit image is specified in the KVM config.
        ValueError if there are no free devices to mount a cloudinit image.

      Returns:
        dict disk mountpoint for cloudinit if defined. Empty otherwise.
        {
          'storage': 'local-lvm',
          'mountpoint': 'ide0',
        }
      '''
      if not self.cloud_init:
        return {}

      if len(list(filter(lambda x: 'ide' not in x['disk'], self.Disks()))):
        return {'storage': self.cloud_init, 'mountpoint': 'ide0'}

      for disk in self.Disks():
        if 'cloudinit' in disk['fullname']:
          raise SyntaxError(
            'Cloudinit images should be specified in the cloudinit pve_kvm'
            'parameter, NOT set in the KVM config.')

      for disk in filter(lambda x: 'ide' in x['disk'], self.Disks()):
        for id in range(3):
          if id not in disk['disk']:
            return {'storage': self.cloud_init, 'mountpoint': f'ide{id}'}

      raise ValueError(
          'cloudinit defined but no free IDE devices are available to mount.')

  def Lxc(self):
    '''Generate ansible-consumble dict for all LXC extension mappings.

    LXC extension options are a special case repeated field.

    'meta' contains actionable information pertaining to LXC configuration on
    container creation.

    Returns
      dict {subuid list, subgid list, idmap list}
      {
        'cgroup2.devices.allow': [
              'c 508:* rwm'
            ]
          }
        'mount.entry': [
            '/dev/nvidia-caps /dev/nvidia-caps none bind,optional,create=dir'
          ],
        },
        'idmap': [
            'u 5556 105556 59980',
            'g 5556 105556 59980',
        ]
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
          ...
          ]
        }
      }
    '''
    lxc_idmap = {'subuid': [], 'subgid': [], 'idmap': []}
    lxc = {'meta': {}}
    for token in filter(lambda x: x.type == data.PveType.LXC_EXTENSION, self.tokens):
      lxc.setdefault(token.key, [])
      # LXC extensions are considered strings.
      lxc[token.key].append(str(token.value[0]))

      # Generate LXC ID Map metadata.
      #  user|group, Cont ID start, Host ID start, range
      #  lxc.idmap: u 0 100000 1000
      if token.key == 'lxc.idmap':
        for option in token.value:
          ctype, cid, hid, crange = str(option.value).split(' ')
          if crange == '1':
            if ctype == 'u':
              lxc_idmap['subuid'].append(f'root:{cid}:1')
            else:
              lxc_idmap['subgid'].append(f'root:{cid}:1')
          lxc_idmap['idmap'].append({'ctype': ctype, 'cid': cid, 'hid': hid, 'crange': crange})

    lxc['meta'].update(lxc_idmap)
    return lxc

  def Ansible(self):
    '''Entry point for ansible module

    Return ansible-consumable results from tokenize KVM config. This is
    optimized for easy of use and ansible usage readability, not object size.

    Returns
      dict containing processed config values, per ansible spec.
    '''
    ansible = {'changed': False}
    ansible['vmid'] = self.vmid
    ansible['node'] = self.node
    ansible['force_stop'] = self.force_stop
    ansible['firewall'] = self.firewall
    ansible['root'] = self.RootDisk()
    ansible['config'] = self.Config()
    ansible['config_text'] = self.ConfigText()
    ansible['config_list'] = self.ConfigList()
    ansible['cli'] = self.Cli()
    ansible['cli_list'] = self.CliList()

    if self.config_type == data.PveConfigType.LXC:
      ansible['template'] = self.ImageOptions()
      ansible['lxc'] = self.Lxc()
    else:
      ansible['cloud_init'] = self.CloudInitMap()
      ansible['template'] = self.ImageOptions()
      ansible['disks'] = self.Disks()
      ansible['isos'] = self.Isos()

    return ansible
