#!/usr/bin/python
#
# Test parsers. Run from 'module_utils' with
#
#   python3 -m unittest
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html

from tests import params
import parsers
import unittest


class TestParserDisks(unittest.TestCase):

  def setUp(self):
    self.params = params.PveRequired()

  def test_disks_store_vmid_disk_extension(self):
    self.params['config'] = 'scsi0: local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1'
    self.assertListEqual(parsers.PveConfig(self.params)._Disks(),
        [
          {
            'disk': 'scsi0',
            'line': 'scsi0: file=local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1',
            'size': '2G',
            'ssd': '1',
            'file': 'local-lvm:103/vm-103-disk-0.raw',
            'fullname': 'vm-103-disk-0.raw',
            'storage': 'local-lvm',
            'storage-option': '103',
            'name': 'vm-103-disk-0',
            'format': 'raw',
            'meta': {
              'create': 'local-lvm:2',
            }
          }
        ]
    )

  def test_disks_store_vmid_disk_extension_explicit(self):
    self.params['config'] = 'scsi0: file=local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1'
    self.assertListEqual(parsers.PveConfig(self.params)._Disks(),
        [
          {
            'disk': 'scsi0',
            'line': 'scsi0: file=local-lvm:103/vm-103-disk-0.raw,size=2G,ssd=1',
            'size': '2G',
            'ssd': '1',
            'file': 'local-lvm:103/vm-103-disk-0.raw',
            'fullname': 'vm-103-disk-0.raw',
            'storage': 'local-lvm',
            'storage-option': '103',
            'name': 'vm-103-disk-0',
            'format': 'raw',
            'meta': {
              'create': 'local-lvm:2',
            }
          }
        ]
    )

  def test_disks_store_iso_image_extension(self):
    self.params['config'] = 'ide0: local:iso/proxmox-ve_6.3-1.iso,media=cdrom'
    self.assertListEqual(parsers.PveConfig(self.params)._Disks(),
        [
          {
            'disk': 'ide0',
            'line': 'ide0: file=local:iso/proxmox-ve_6.3-1.iso,media=cdrom',
            'media': 'cdrom',
            'file': 'local:iso/proxmox-ve_6.3-1.iso',
            'fullname': 'proxmox-ve_6.3-1.iso',
            'storage': 'local',
            'storage-option': 'iso',
            'name': 'proxmox-ve_6.3-1',
            'format': 'iso',
          }
        ]
    )

  def test_disks_store_no_vmid_extension(self):
    self.params['config'] = 'scsi0: local-lvm:vm-100-disk-0,size=4G'
    self.assertListEqual(parsers.PveConfig(self.params)._Disks(),
        [
          {
            'disk': 'scsi0',
            'line': 'scsi0: file=local-lvm:vm-100-disk-0,size=4G',
            'size': '4G',
            'file': 'local-lvm:vm-100-disk-0',
            'fullname': 'vm-100-disk-0',
            'storage': 'local-lvm',
            'storage-option': '',
            'name': 'vm-100-disk-0',
            'format': '',
            'meta': {
              'create': 'local-lvm:4',
            }
          }
        ]
    )


class TestParserDisksPruned(unittest.TestCase):

  def setUp(self):
    self.kvm = parsers.PveConfig(params.KvmMediumValid())

  def test_iso_detection(self):
    self.assertListEqual(self.kvm.Isos(),
        [
          {
            'disk': 'ide2',
            'line': 'ide2: file=local:iso/proxmox-ve_6.3-1.iso,media=cdrom',
            'media': 'cdrom',
            'file': 'local:iso/proxmox-ve_6.3-1.iso',
            'fullname': 'proxmox-ve_6.3-1.iso',
            'storage': 'local',
            'storage-option': 'iso',
            'name': 'proxmox-ve_6.3-1',
            'format': 'iso',
          }
        ]
    )

  def test_disk_detection(self):
    self.assertListEqual(self.kvm.Disks(),
        [
          {
            'disk': 'scsi0',
            'line': 'scsi0: file=local-lvm:vm-100-disk-0,size=4G',
            'size': '4G',
            'file': 'local-lvm:vm-100-disk-0',
            'fullname': 'vm-100-disk-0',
            'storage': 'local-lvm',
            'storage-option': '',
            'name': 'vm-100-disk-0',
            'format': '',
            'meta': {
              'create': 'local-lvm:4',
            }
          }
        ]
    )

  def test_kvm_root_disk_detection(self):
    self.assertDictEqual(self.kvm.RootDisk(),
        {
          'disk': 'scsi0',
          'line': 'scsi0: file=local-lvm:vm-100-disk-0,size=4G',
          'size': '4G',
          'file': 'local-lvm:vm-100-disk-0',
          'fullname': 'vm-100-disk-0',
          'storage': 'local-lvm',
          'storage-option': '',
          'name': 'vm-100-disk-0',
          'format': '',
          'meta': {
            'create': 'local-lvm:4'
          }
        }
    )

  def test_lxc_root_disk_detection(self):
    self.assertDictEqual(parsers.PveConfig(params.LxcMinimumValid()).RootDisk(),
        {
          'disk': 'rootfs',
          'line': 'rootfs: volume=local-lvm:vm-100-disk-0,size=4G',
          'size': '4G',
          'file': 'local-lvm:vm-100-disk-0',
          'fullname': 'vm-100-disk-0',
          'storage': 'local-lvm',
          'storage-option': '',
          'name': 'vm-100-disk-0',
          'format': '',
          'meta': {
            'create': 'local-lvm:4'
          }
        }
    )


class TestParserCloudInitDisk(unittest.TestCase):

  def test_cloud_init_disk_first_ide(self):
    map = parsers.PveConfig(params.KvmMediumValid()).CloudInitMap()
    self.assertDictEqual(map, {'storage': 'local-lvm', 'mountpoint': 'ide0'})

  def test_cloud_init_defined(self):
    map = parsers.PveConfig(params.KvmCloudInitNoMount())
    with self.assertRaises(SyntaxError):
      map.CloudInitMap()

  def test_cloud_init_full(self):
    map = parsers.PveConfig(params.KvmCloudInitFullMount())
    with self.assertRaises(ValueError):
      map.CloudInitMap()


class TestParserConfig(unittest.TestCase):

  def setUp(self):
    self.params = params.KvmMinimumValid()
    self.params['config'] += '\nboot: order=scsi0\nmemory: 4096'
    self.kvm = parsers.PveConfig(self.params)

  def test_config_string(self):
    self.assertEqual(self.kvm.ConfigText(), self.params['config'])

  def test_config_list(self):
    self.assertEqual(self.kvm.ConfigList(), self.params['config'].split('\n'))

  def test_cli_string(self):
    self.assertEqual(self.kvm.Cli(),
        '--scsi0 file=local-lvm:vm-100-disk-0,size=4G --boot order=scsi0 --memory 4096'
    )

  def test_cli_list(self):
    self.assertEqual(self.kvm.CliList(),
        [
          '--scsi0 file=local-lvm:vm-100-disk-0,size=4G',
          '--boot order=scsi0',
          '--memory 4096'
        ]
    )

  def test_template_image(self):
    kvm = parsers.PveConfig(params.KvmMediumValid())
    self.assertDictEqual(kvm.ImageOptions(),
        {
          'url': 'https://cloud.debian.org/cdimage/cloud/bullseye/20211011-792/debian-11-genericcloud-amd64-20211011-792.tar.xz',
          'checksum':  'ded2dc24ebb876d741ee80bd1e5edba34e32eaded73e2b90820792700c81d512b68a28bae929c8a377b5ec8995b053990616199f5214d07f81fd8603b32e66ce',
          'algorithm': 'sha512',
          'extension': 'tar.xz',
          'file': 'debian-11-genericcloud-amd64-20211011-792.tar.xz',
          'name': 'debian-11-genericcloud-amd64-20211011-792',
        }
    )


class TestLxcParserConfig(unittest.TestCase):

  def test_lxc_init_cmd(self):
    self.maxDiff = None
    self.assertDictEqual(parsers.PveConfig(params.LxcInitCmdValid()).Lxc(),
        {
          'lxc.init_cmd': [
            '/sbin/my_own_init',
            '/sbin/command2',
          ],
          'meta': {
            'subuid': [],
            'subgid': [],
            'idmap': [],
          }
        }
    )

  def test_lxc_idmap(self):
    self.maxDiff = None
    self.assertDictEqual(parsers.PveConfig(params.LxcIdmapValid()).Lxc(),
        {
          'lxc.idmap': [
            'u 0 100000 1005',
            'g 0 100000 1005',
            'u 1005 1005 1',
            'g 1005 1005 1',
            'u 1006 101006 64530',
            'g 1006 101006 64530',
          ],
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
              {
                'ctype': 'g',
                'cid': '1005',
                'hid': '1005',
                'crange': '1'
              },
              {
                'ctype': 'u',
                'cid': '1006',
                'hid': '101006',
                'crange': '64530'
              },
              {
                'ctype': 'g',
                'cid': '1006',
                'hid': '101006',
                'crange': '64530'
              }
            ]
          }
        }
    )

  def test_lxc_init_cmd(self):
    self.maxDiff = None
    self.assertDictEqual(parsers.PveConfig(params.LxcInitCmdValid()).Lxc(),
        {
          'lxc.init_cmd': [
            '/sbin/my_own_init',
            '/sbin/command2',
          ],
          'meta': {
            'subuid': [],
            'subgid': [],
            'idmap': [],
          }
        }
    )

  def test_lxc_all_extensions(self):
    self.maxDiff = None
    self.assertDictEqual(parsers.PveConfig(params.LxcAllExtensionsValid()).Lxc(),
        {
          'lxc.idmap': [
            'u 0 100000 1005',
            'g 0 100000 1005',
            'u 1005 1005 1',
            'g 1005 1005 1',
            'u 1006 101006 64530',
            'g 1006 101006 64530',
          ],
          'lxc.init_cmd': [
            '/sbin/my_own_init',
            '/sbin/command2',
          ],
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
              {
                'ctype': 'g',
                'cid': '1005',
                'hid': '1005',
                'crange': '1'
              },
              {
                'ctype': 'u',
                'cid': '1006',
                'hid': '101006',
                'crange': '64530'
              },
              {
                'ctype': 'g',
                'cid': '1006',
                'hid': '101006',
                'crange': '64530'
              }
            ]
          }
        }
    )

if __name__ == '__main__':
  unittest.main()
