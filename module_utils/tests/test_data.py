#!/usr/bin/python
#
# Test data structure and enumeration. Run from 'module_utils' with
#
#   python3 -m unittest
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html

from tests import params
import data
import unittest


class TestImageOption(unittest.TestCase):

  def test_lxc_template(self):
    i = data.ImageMap(**params.TemplateLxc()['template'])
    self.assertEqual(i.url, 'debian-11-standard_11.0-1_amd64.tar.gz')
    self.assertEqual(i.checksum, '')
    self.assertEqual(i.algorithm, '')
    self.assertEqual(i.file, 'debian-11-standard_11.0-1_amd64.tar.gz')
    self.assertEqual(i.name, 'debian-11-standard_11.0-1_amd64')
    self.assertEqual(i.extension, 'tar.gz')

  def test_kvm_template(self):
    i = data.ImageMap(**params.TemplateCloud()['template'])
    self.assertEqual(i.url, 'https://cloud.debian.org/cdimage/cloud/bullseye/20211011-792/debian-11-genericcloud-amd64-20211011-792.tar.xz')
    self.assertEqual(i.checksum, 'ded2dc24ebb876d741ee80bd1e5edba34e32eaded73e2b90820792700c81d512b68a28bae929c8a377b5ec8995b053990616199f5214d07f81fd8603b32e66ce')
    self.assertEqual(i.algorithm, 'sha512')
    self.assertEqual(i.file, 'debian-11-genericcloud-amd64-20211011-792.tar.xz')
    self.assertEqual(i.name, 'debian-11-genericcloud-amd64-20211011-792')
    self.assertEqual(i.extension, 'tar.xz')

  def test_iso_template(self):
    i = data.ImageMap(**params.TemplateIso()['template'])
    self.assertEqual(i.url, 'https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-11.1.0-amd64-netinst.iso')
    self.assertEqual(i.checksum, '02257c3ec27e45d9f022c181a69b59da67e5c72871cdb4f9a69db323a1fad58093f2e69702d29aa98f5f65e920e0b970d816475a5a936e1f3bf33832257b7e92')
    self.assertEqual(i.algorithm, 'sha512')
    self.assertEqual(i.file, 'debian-11.1.0-amd64-netinst.iso')
    self.assertEqual(i.name, 'debian-11.1.0-amd64-netinst')
    self.assertEqual(i.extension, 'iso')


class TestSecondaryOption(unittest.TestCase):

  def test_no_arg_failure(self):
    with self.assertRaises(TypeError):
      data.PveSecondaryOption()

  def test_minimal_good_args(self):
    option = data.PveSecondaryOption('nfs;cryptfs')
    self.assertListEqual(option.options, ['nfs', 'cryptfs'])

  def test_invalid_dynamic_parse(self):
    option = data.PveSecondaryOption('mount=nfs;cryptfs')
    self.assertListEqual(option.options, ['mount=nfs', 'cryptfs'])

  def test_one_option_parse(self):
    option = data.PveSecondaryOption('cryptfs')
    self.assertListEqual(option.options, ['cryptfs'])

  def test_comment(self):
    option = data.PveSecondaryOption('comment', type=data.PveType.COMMENT)
    self.assertListEqual(option.options, ['comment'])
    self.assertEqual(option.type, data.PveType.COMMENT)
    self.assertEqual(option.Ansible(), 'comment')

  def test_ansible_multiple_options(self):
    option = data.PveSecondaryOption('nfs;cryptfs')
    self.assertListEqual(option.Ansible(), ['nfs', 'cryptfs'])

  def test_ansible_single_option(self):
    option = data.PveSecondaryOption('nfs')
    self.assertEqual(option.Ansible(), 'nfs')


class TestPrimaryOption(unittest.TestCase):

  def test_no_arg_failure(self):
    with self.assertRaises(TypeError):
      data.PvePrimaryOption()

  def test_minimal_good_args(self):
    secondary = data.PveSecondaryOption('kvm64')
    option = data.PvePrimaryOption('cputype=kvm64')
    self.assertEqual(option.type, data.PveType.KEY_VALUE)
    self.assertEqual(option.key, 'cputype')
    self.assertEqual(option.value, secondary)

  def test_one_arg_good(self):
    secondary = data.PveSecondaryOption('x86_64')
    option = data.PvePrimaryOption(' x86_64')
    self.assertEqual(option.type, data.PveType.VALUE_ONLY)
    self.assertEqual(option.key, None)
    self.assertEqual(option.value, secondary)

  def test_complex_option(self):
    secondary = data.PveSecondaryOption('nfs;cryptfs')
    option = data.PvePrimaryOption('mount=nfs;cryptfs')
    self.assertEqual(option.type, data.PveType.KEY_VALUE)
    self.assertEqual(option.key, 'mount')
    self.assertEqual(option.value, secondary)

  def test_comment(self):
    option = data.PvePrimaryOption('comment', type=data.PveType.COMMENT)
    options = data.PveSecondaryOption('comment', type=data.PveType.COMMENT)
    self.assertEqual(option.value, options)
    self.assertEqual(option.key, None)
    self.assertEqual(option.type, data.PveType.COMMENT)
    self.assertEqual(option.Ansible(), 'comment')

  def test_ansible_multiple_options(self):
    option = data.PvePrimaryOption('order=scsi0;ide2')
    self.assertDictEqual(option.Ansible(), {'order': ['scsi0', 'ide2']})

  def test_ansible_single_key_option(self):
    option = data.PvePrimaryOption('order=scsi0')
    self.assertDictEqual(option.Ansible(), {'order': 'scsi0'})

  def test_ansible_single_keyless_option(self):
    option = data.PvePrimaryOption('scsi0')
    self.assertEqual(option.Ansible(), 'scsi0')


class TestPveConfig(unittest.TestCase):

  def test_no_arg_failure(self):
    with self.assertRaises(TypeError):
      data.PveConfigOption()

  def test_invalid_type(self):
    with self.assertRaises(TypeError):
      data.PveConfigOption(type='bad_option')

  def test_option_mapping_unused(self):
    kvm_option = data.PveConfigOption('unused0: local-lvm:vm-100-disk-6,size=4G', config=data.PveConfigType.KVM)
    lxc_option = data.PveConfigOption('unused0: local-lvm:vm-100-disk-6,size=4G', config=data.PveConfigType.LXC)
    self.assertEqual(kvm_option.value[0].key, 'file')
    self.assertEqual(lxc_option.value[0].key, 'volume')

  def test_option_mapping_net(self):
    net_model = data.PveConfigOption('net0: model=virtio,bridge=vmbr0', config=data.PveConfigType.KVM)
    self.assertEqual(net_model.value[0].key, 'model')
    net_virtio_bare = data.PveConfigOption('net0: virtio,bridge=vmbr0', config=data.PveConfigType.KVM)
    self.assertEqual(net_virtio_bare.value[0].key, 'model')
    net_virtio_mac = data.PveConfigOption('net0: virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0', config=data.PveConfigType.KVM)
    self.assertEqual(net_virtio_mac.value[0].key, 'virtio')
    lxc_net = data.PveConfigOption('net0: name=eth0,bridge=vmbr0', config=data.PveConfigType.LXC)
    self.assertEqual(lxc_net.value[0].key, 'name')

  def test_comment_special_case(self):
    options = data.PvePrimaryOption('standard comment', type=data.PveType.COMMENT)
    options_config = data.PvePrimaryOption('boot: order=scsi0', type=data.PveType.COMMENT)
    options_cli = data.PvePrimaryOption('--boot order=scsi0', type=data.PveType.COMMENT)
    comment = data.PveConfigOption('# standard comment')
    config_comment = data.PveConfigOption('#boot: order=scsi0')
    cli_comment = data.PveConfigOption('#--boot order=scsi0')
    self.assertIsNone(comment.key)
    self.assertEqual(comment.value, [options])
    self.assertEqual(comment.type, data.PveType.COMMENT)
    self.assertIsNone(config_comment.key)
    self.assertEqual(config_comment.value, [options_config])
    self.assertEqual(config_comment.type, data.PveType.COMMENT)
    self.assertIsNone(cli_comment.key)
    self.assertEqual(cli_comment.value, [options_cli])
    self.assertEqual(cli_comment.type, data.PveType.COMMENT)

  def test_minimal_good_args(self):
    options = data.PvePrimaryOption('order=scsi0')
    options_config = data.PveConfigOption('boot: order=scsi0')
    options_cli = data.PveConfigOption('--boot order=scsi0')
    self.assertEqual(options_config.key, 'boot')
    self.assertEqual(options_config.line, 'boot: order=scsi0')
    self.assertEqual(options_config.value, [options])
    self.assertEqual(options_config.type, data.PveType.DEFAULT)
    self.assertEqual(options_cli.key, 'boot')
    self.assertEqual(options_cli.line, '--boot order=scsi0')
    self.assertEqual(options_cli.value, [options])
    self.assertEqual(options_cli.type, data.PveType.DEFAULT)

  def test_primay_option_missing_args(self):
    option1 = data.PvePrimaryOption('file=local-lvm:vm-100-disk-0')
    option2 = data.PvePrimaryOption('size=4G')
    config1 = data.PveConfigOption('scsi0: local-lvm:vm-100-disk-0,size=4G')
    config2 = data.PveConfigOption('scsi0: file=local-lvm:vm-100-disk-0,size=4G')
    self.assertEqual(config1.type, data.PveType.DISK)
    self.assertEqual(config2.type, data.PveType.DISK)
    self.assertEqual(config1.key, 'scsi0')
    self.assertEqual(config2.key, 'scsi0')
    self.assertEqual(config1.value, [option1, option2])
    self.assertEqual(config2.value, [option1, option2])

  def test_disk_match(self):
    option1 = data.PvePrimaryOption('file=local-lvm:vm-100-disk-0')
    option2 = data.PvePrimaryOption('size=4G')
    config = data.PveConfigOption('scsi0: local-lvm:vm-100-disk-0,size=4G')
    cli = data.PveConfigOption('--scsi0 local-lvm:vm-100-disk-0,size=4G')
    self.assertEqual(config.type, data.PveType.DISK)
    self.assertEqual(cli.type, data.PveType.DISK)
    self.assertEqual(config.key, 'scsi0')
    self.assertEqual(cli.key, 'scsi0')
    self.assertEqual(config.value, [option1, option2])
    self.assertEqual(cli.value, [option1, option2])

  def test_mp_match(self):
    option1 = data.PvePrimaryOption('volume=/test/dir')
    option2 = data.PvePrimaryOption('mp=/local/dir')
    config = data.PveConfigOption('mp2: volume=/test/dir,mp=/local/dir')
    cli = data.PveConfigOption('--mp2 volume=/test/dir,mp=/local/dir')
    self.assertEqual(config.type, data.PveType.MP)
    self.assertEqual(cli.type, data.PveType.MP)
    self.assertEqual(config.key, 'mp2')
    self.assertEqual(cli.key, 'mp2')
    self.assertEqual(config.value, [option1, option2])
    self.assertEqual(cli.value, [option1, option2])

  def test_rootfs_match(self):
    option1 = data.PvePrimaryOption('volume=local-lvm:vm-400-disk-0')
    option2 = data.PvePrimaryOption('size=6G')
    config = data.PveConfigOption('rootfs: local-lvm:vm-400-disk-0,size=6G')
    cli = data.PveConfigOption('--rootfs local-lvm:vm-400-disk-0,size=6G')
    self.assertEqual(config.type, data.PveType.ROOTFS)
    self.assertEqual(cli.type, data.PveType.ROOTFS)
    self.assertEqual(config.key, 'rootfs')
    self.assertEqual(cli.key, 'rootfs')
    self.assertEqual(config.value, [option1, option2])
    self.assertEqual(cli.value, [option1, option2])

  def test_lxc_extension_match(self):
    option = data.PvePrimaryOption('/dev/dri dev/dri none bind,optional,create=dir', type=data.PveType.LXC_EXTENSION)
    config = data.PveConfigOption('lxc.mount.entry: /dev/dri dev/dri none bind,optional,create=dir')
    cli = data.PveConfigOption('--lxc.mount.entry /dev/dri dev/dri none bind,optional,create=dir')
    self.assertEqual(config.type, data.PveType.LXC_EXTENSION)
    self.assertEqual(cli.type, data.PveType.LXC_EXTENSION)
    self.assertEqual(config.key, 'lxc.mount.entry')
    self.assertEqual(cli.key, 'lxc.mount.entry')
    self.assertEqual(config.value, [option])
    self.assertEqual(cli.value, [option])

  def test_ssh_keys_match(self):
    options = data.PvePrimaryOption('AAAAA=sdf/s234+234/342/adfsd/+sdf=== user@test')
    config = data.PveConfigOption('sshkeys: AAAAA=sdf/s234+234/342/adfsd/+sdf=== user@test')
    cli = data.PveConfigOption('--sshkeys AAAAA=sdf/s234+234/342/adfsd/+sdf=== user@test')
    self.assertEqual(config.type, data.PveType.SSH_KEYS)
    self.assertEqual(cli.type, data.PveType.SSH_KEYS)
    self.assertEqual(config.key, 'sshkeys')
    self.assertEqual(cli.key, 'sshkeys')
    self.assertEqual(config.value, [options])
    self.assertEqual(cli.value, [options])

  def test_ssh_keys_file(self):
    options = data.PvePrimaryOption('~/home/.ssh/authorized_keys')
    config = data.PveConfigOption('sshkeys: ~/home/.ssh/authorized_keys')
    cli = data.PveConfigOption('--sshkeys ~/home/.ssh/authorized_keys')
    self.assertEqual(config.type, data.PveType.SSH_KEYS)
    self.assertEqual(cli.type, data.PveType.SSH_KEYS)
    self.assertEqual(config.key, 'sshkeys')
    self.assertEqual(cli.key, 'sshkeys')
    self.assertEqual(config.value, [options])
    self.assertEqual(cli.value, [options])

  def test_ansible_multiple_options(self):
    option = data.PveConfigOption('features: force_rw_sys=1,fuse=1,keyctl=1,mknod=1,mount=nfs;ext4,nesting=1')
    self.assertDictEqual(option.Ansible(),
        {
          'features': {
            'force_rw_sys': '1',
            'fuse': '1',
            'keyctl': '1',
            'mknod': '1',
            'mount': ['nfs', 'ext4'],
            'nesting': '1',
          }
        }
    )

  def test_ansible_single_key_option(self):
    option = data.PveConfigOption('scsi0: file=local-lvm:vm-100-disk-0,size=4G')
    self.assertDictEqual(option.Ansible(), {'scsi0': {'file': 'local-lvm:vm-100-disk-0', 'size': '4G'}})

  def test_ansible_single_keyless_option(self):
    option = data.PveConfigOption('scsi0: local-lvm:vm-100-disk-0,size=4G')
    self.assertDictEqual(option.Ansible(), {'scsi0': {'file': 'local-lvm:vm-100-disk-0', 'size': '4G'}})


class TestStringConversion(unittest.TestCase):

  def test_config_string(self):
    config = data.PveConfigOption('scsi0: local-lvm:vm-100-disk-0,size=4G')
    self.assertEqual(config.Config(), 'scsi0: local-lvm:vm-100-disk-0,size=4G')
    self.assertEqual(config.Cli(), '--scsi0 local-lvm:vm-100-disk-0,size=4G')

  def test_config_string(self):
    cli = data.PveConfigOption('--scsi0 local-lvm:vm-100-disk-0,size=4G')
    self.assertEqual(cli.Config(), 'scsi0: local-lvm:vm-100-disk-0,size=4G')
    self.assertEqual(cli.Cli(), '--scsi0 local-lvm:vm-100-disk-0,size=4G')

  def test_config_string(self):
    comment = data.PveConfigOption('#test comment')
    self.assertEqual(comment.Config(), '# test comment')
    with self.assertRaises(TypeError):
      comment.Cli()


if __name__ == '__main__':
  unittest.main()
