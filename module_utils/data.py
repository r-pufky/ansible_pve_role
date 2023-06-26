#!/usr/bin/python
#
# Manage configuration data from pct.conf, qm.conf, pct, qm using dataclasses.
#
# Dataclasses are used to encapulsate configuration/cli lines, and return
# formatted values for ansible, qm.conf, and the qm cli. All formats use the
# same {KEY}:{VALUE} format with no distinction in data storage.
#
# Data class parsers are matched on the KEY in the {KEY}:{VALUE} pair for the
# configuration.
#
# Run unittests from module_utils: python3 -m unittest
#
# Reference:
# * https://pve.proxmox.com/wiki/Manual:_qm.conf
# * https://pve.proxmox.com/pve-docs/qm.1.html
# * https://pve.proxmox.com/wiki/Manual:_pct.conf
# * https://pve.proxmox.com/pve-docs/pct.1.html

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from typing import ClassVar
import re


class PveType(Enum):
  '''Configuration line broad classification.'''
  DEFAULT = auto()
  COMMENT = auto()
  DISK = auto()
  SSH_KEYS = auto()
  LXC_EXTENSION = auto()
  MP = auto()
  ROOTFS = auto()
  KEY_VALUE = auto()
  VALUE_ONLY = auto()
  TERTIARY_OPTION = auto()


class PveConfigType(Enum):
  '''Hint for what config a given config option is from.'''
  KVM = auto()
  LXC = auto()


@dataclass
class ImageMap:
  url: str
  checksum: str
  algorithm: str
  file: str = field(init=False)
  name: str = field(init=False)
  extension: str = field(init=False)

  def __post_init__(self):
    '''Parse provided options to generate file, name, extension.'''
    self.file = self.url.split('/')[-1]

    # cover tar.gz, tar.xz
    if '.tar.' in self.url:
      self.name, tar, ext = self.file.rsplit('.', 2)
      self.extension = f'{tar}.{ext}'
    else:
      self.name, self.extension = self.file.rsplit('.', 1)


@dataclass
class LineMatcher:
  '''Matches config lines based on regular expressions.

  Attributes
    regex: re object to match config line. Default any {KEY}:{VALUE} pair.
    type: PveType to match config line to. Default: PveType.Default.
  '''
  regex: re.Pattern
  type: PveType = field(default=PveType.DEFAULT)


@dataclass
class PveSecondaryOption:
  '''Pve secondary option dataclass.

  Secondary (sub-option) key/values are separated by ';'.

  It is assumed that the original line contains ONLY the {VALUE} portion of the
  primary option (e.g. 'mount=nfs;cryptfs' would be 'nfs;cryptfs')

  Passing COMMMENT as type will disable line parsing and store the string with
  COMMENT metadata.

  Attributes
    line: string original secondary option line passed on creation.
    options: list of string parsed {VALUE} options.
    type: PveType KEY_VALUE if a key/value pair or VALUE_ONLY for string.
        COMMMENT if original line is a comment.
  '''
  line: str
  options: list = field(default_factory=list)
  type: PveType = field(default=PveType.VALUE_ONLY)

  def __post_init__(self):
    '''Parse secondary options'''
    # Comments and LXC extensions are considered strings.
    if self.type in (PveType.COMMENT, PveType.LXC_EXTENSION):
      self.options = [self.line.strip()]
      return

    if ';' in self.line:
      self.options = [x.strip() for x in self.line.split(';')]
      self.type = PveType.KEY_VALUE
    else:
      self.options = [self.line.strip()]
      self.type = PveType.VALUE_ONLY

  def __str__(self):
    return f'{";".join(self.options)}'

  def Ansible(self):
    '''Return option list or string for single element.'''
    if len(self.options) == 1:
      return ''.join(self.options)
    return self.options


@dataclass
class PvePrimaryOption:
  '''Pve primary option dataclass.

  Primary (option) key/values are separated by '='.

  It is assumed that the original line contains ONLY one option key/value pair
  (e.g. 'cpu: cputype=kvm64,hidden=1' would be two primary options
  'cputype=kvm64' and 'hidden=1'' 'arch: x86_64' would be 'x86_64')

  Passing COMMMENT as type will disable line parsing and store the string with
  COMMENT metadata.

  Attributes
    line: string original primary option line passed on creation.
    key: string primary option key; if option only has a value this will be set
        to None, and type will be set to VALUE_ONLY.
    value: PveSecondaryOption representing the fully processed option,
        including any sub-options.
    type: PveType configuration line broad classification.
  '''
  line: str
  key: str = field(init=False)
  value: PveSecondaryOption = field(init=False)
  type: PveType = field(default=PveType.KEY_VALUE)

  def __post_init__(self):
    '''Parse primary options'''
    # Comments and LXC extensions are considered strings.
    if self.type in (PveType.COMMENT, PveType.LXC_EXTENSION):
      self.key = None
      self.value = PveSecondaryOption(self.line.strip(), type=self.type)
      return

    if '=' in self.line:
      self.key, value = [x.strip() for x in self.line.split('=', 1)]
      self.value = PveSecondaryOption(value)
      self.type = PveType.KEY_VALUE
    else:
      self.key = None
      self.value = PveSecondaryOption(self.line.strip())
      self.type = PveType.VALUE_ONLY

  def __str__(self):
    if self.type in (PveType.VALUE_ONLY, PveType.COMMENT, PveType.LXC_EXTENSION):
      return f'{self.value}'

    return f'{self.key}={self.value}'

  def Ansible(self):
    '''Return dict/list formatted for ansible consumption.

    'asdict' creates a nested dictionary, but does not flatten values.
    '''
    if self.type in [PveType.VALUE_ONLY, PveType.COMMENT]:
      return self.value.Ansible()

    return {self.key: self.value.Ansible()}


@dataclass
class PveConfigOption:
  '''Pve config option dataclass.

  Pve configs for both the CLI and file use a simple {KEY}: {VALUE}
  method for storing data. primary option/values are separated by '=' and
  secondary (sub-option) values are separated by ';'.

  CLI options are prefixed with '--'.

  Some config lines have optional first primary option keys. Lines missing
  these keys are detected and inserted to standardize line formats.

  Reference
  * https://pve.proxmox.com/wiki/Manual:_qm.conf
  * https://pve.proxmox.com/pve-docs/qm.1.html

  Attributes
    line: string original line passed on creation.
    key: string parsed {KEY} value. If comment this is set to None, and type
        will be set to COMMENT.
    value: list of PvePrimaryOption parsed {VALUE} options. String if comment.
    type: PveType category. Optional, default: PveType.DEFAULT.
    config: PveConfig category config hint. Optional, default: PveConfig.KVM.
  '''
  line: str
  config: PveConfigType = field(default=PveConfigType.KVM)
  key: str = field(init=False)
  value: list = field(init=False, default_factory=list)
  type: PveType = field(init=False, default=PveType.DEFAULT)
  _matcher: ClassVar[LineMatcher] = [
    LineMatcher(re.compile('(^scsi|sata|ide|virtio|efidisk)(\d+)'), PveType.DISK),
    LineMatcher(re.compile('(^mp)(\d+)'), PveType.MP),
    LineMatcher(re.compile('^rootfs'), PveType.ROOTFS),
    LineMatcher(re.compile('^lxc'), PveType.LXC_EXTENSION),
    LineMatcher(re.compile('^sshkeys'), PveType.SSH_KEYS),
    LineMatcher(re.compile('^.*'), PveType.DEFAULT),
  ]
  _optional_keys: ClassVar[dict[str, str]] = {
    'agent': 'enabled',
    #'boot': 'legacy',   # Deprecated; do not support.
    'cpu': 'cputype',
    'efidisk': 'file',
    'hostpci': 'host',
    'ide': 'file',
    'rng': 'source',
    'sata': 'file',
    'scsi': 'file',
    'startup': 'order',
    'tpmstate': 'file',
    'usb': 'host',
    'vga': 'type',
    'virtio': 'file',
    'watchdog': 'model',
    'mp': 'volume',
    'rootfs': 'volume',
    'startup': 'order',
    #'unused': 'file/volume', KVM specific mapping, see OptionalKeyMapping.
    #'net': 'model/<model_enum', KVM specific mapping. See OptionalKeyMapping.
    '_net_model_enum': [
        'e1000', 'e1000-82540em', 'e1000-82544gc', 'e1000-82545em', 'e1000e',
        'i82551', 'i82557b', 'i82559er', 'ne2k_isa', 'ne2k_pci', 'pcnet',
        'rtl8139', 'virtio', 'vmxnet3'
    ]
  }

  def _OptionalKeyMapping(self, option) -> str:
    '''Map default key for optional primary option.

    These are config lines in which the primary option can be specified without
    the key, such as scsi0. All trailing integers are removed, even if there is
    only one option, such as 0. Include deprecated options until removed from
    configuration files.

    KVM/LXC config type will set value if there are duplicate keys.

    Args
      str primary option (key=value;value2).

    Returns
      str containing mapping or empty string if no optional key detected.
    '''
    stripped_key = self.key.rstrip('0123456789')
    if stripped_key == 'unused':
      return 'file' if self.config == PveConfigType.KVM else 'volume'

    # KVM net has three possible values: model=, <model_enum>=, <model_enum>.
    if stripped_key == 'net' and self.config == PveConfigType.KVM:
      for model_enum in self._optional_keys['_net_model_enum']:
        if option.startswith(f'{model_enum}='):
          return ''
        if model_enum == option:
          return 'model'

    return self._optional_keys.get(stripped_key, '')

  def __post_init__(self):
    '''Parse primary options'''
    # Special case, comments do not follow key/value pairing.
    if self.line.startswith('#'):
      self.key = None
      self.value = [PvePrimaryOption(self.line.split('#', 1)[1].strip(), type=PveType.COMMENT)]
      self.type = PveType.COMMENT
      return

    if self.line.startswith('--'):
      key, value = [x.strip() for x in self.line.split(' ', 1)]
      self.key = key.strip('-')
      header = '--'
      delim = ' '
    else:
      self.key, value = [x.strip() for x in self.line.split(':', 1)]
      header = ''
      delim = ':'

    # LXC extensions are considered full strings.
    if self.key.startswith('lxc'):
      self.value = [PvePrimaryOption(value, type=PveType.LXC_EXTENSION)]
      self.type = PveType.LXC_EXTENSION
      return

    # Affinity is a tertiary option (,) with no primary/secondary options.
    if self.key.startswith('affinity'):
      self.value = [PvePrimaryOption(value, type=PveType.TERTIARY_OPTION)]
      self.type = PveType.TERTIARY_OPTION
      return

    # Standardize option key for keyless options (only appear as first primary
    # option). Need to munge self.line with the correct option_key to fix other
    # processing, else line != values parsed.
    for i, option in enumerate(value.split(',')):
      if i == 0:
        option_key = self._OptionalKeyMapping(option)
        if option_key not in option:
          self.line = f'{header}{self.key}{delim} {option_key}={value}'
          self.value.append(PvePrimaryOption(f'{option_key}={option}'))
          continue

      self.value.append(PvePrimaryOption(option))

    for matcher in self._matcher:
      if matcher.regex.match(self.key):
        self.type = matcher.type
        break
    else:
      raise ValueError(f'Unable to match option: {self.line}')

  def _ValueAsString(self, delim='') -> str:
    '''Return current value data as string using delim to combine.'''
    return delim.join([str(x) for x in self.value])

  def Config(self) -> str:
    '''Return data as a ready to use qm.conf line. No Spaces.'''
    if self.type == PveType.COMMENT:
      return f'# {self._ValueAsString()}'

    return f'{self.key}: {self._ValueAsString(",")}'

  def Cli(self) -> str:
    '''Return data as a ready to execute qm cli option. No spaces.

    Raises
      TypeError if comments are used in CLI output (cannot be used).
    '''
    if self.type == PveType.COMMENT:
      raise TypeError('Comments cannot be exported to CLI')

    return f'--{self.key} {self._ValueAsString(",")}'

  def Ansible(self) -> dict:
    '''Return dict formatted for easy ansible consumption.

    'asdict' creates a nested dictionary, but does not flatten values or
    convert nested dataclasses; resulting in a messy, hard to predict dict when
    using in ansible. Ensure 'ansible-task' use is easy and implicitly does
    'the right thing', e.g.

      _pve_vm.config.root.disk
      _pve_vm.config.hostname
    '''
    ansible = {self.key: {}}
    for option in self.value:
      if option.type in (PveType.COMMENT, PveType.LXC_EXTENSION):
        continue
      if option.type == PveType.VALUE_ONLY:
        ansible[self.key] = option.value.Ansible()
      else:
        ansible[self.key].update({option.key: option.value.Ansible()})
    return ansible
