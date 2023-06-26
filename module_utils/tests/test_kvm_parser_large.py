#!/usr/bin/python
#
# Valid KVM parsing against minimmum and inferred options, validate against
# explicit configuration. Run from 'module_utils' with
#
#   python3 -m unittest
#
# If needed, set 'self.maxDiff = None' for full diff results.
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html

from tests import params
from tests.data import kvm_file_validation_data
import parsers
import unittest
import os
import sys

class TestAnsibleKvmMinimumParserOutput(unittest.TestCase):
  '''Test each ansible return key separately to keep dict reasonable.'''

  def setUp(self):
    self.ansible = parsers.PveConfig(params.KvmMinimumValid()).Ansible()

  def test_ansible_changed_false(self):
    self.assertFalse(self.ansible['changed'])

  def test_ansible_cli(self):
    self.assertEqual(self.ansible['cli'], '--scsi0 file=local-lvm:vm-100-disk-0,size=4G')

  def test_ansible_cli_list(self):
    self.assertListEqual(self.ansible['cli_list'], ['--scsi0 file=local-lvm:vm-100-disk-0,size=4G'])

  def test_ansible_cloud_init(self):
    self.assertDictEqual(self.ansible['cloud_init'], {})

  def test_ansible_config(self):
    self.assertDictEqual(self.ansible['config'],
        {
          'scsi0': {
            'file': 'local-lvm:vm-100-disk-0',
            'size': '4G'
          }
        }
    )

  def test_ansible_config_list(self):
    self.assertListEqual(self.ansible['config_list'], ['scsi0: file=local-lvm:vm-100-disk-0,size=4G'])

  def test_ansible_config_test(self):
    self.assertEqual(self.ansible['config_text'], 'scsi0: file=local-lvm:vm-100-disk-0,size=4G')

  def test_ansible_disks(self):
    self.assertListEqual(self.ansible['disks'],
        [
          {
            'disk': 'scsi0',
            'file': 'local-lvm:vm-100-disk-0',
            'format': '',
            'fullname': 'vm-100-disk-0',
            'line': 'scsi0: file=local-lvm:vm-100-disk-0,size=4G',
            'name': 'vm-100-disk-0',
            'size': '4G',
            'storage': 'local-lvm',
            'storage-option': '',
            'meta': {
              'create': 'local-lvm:4',
            }
          }
        ]
    )

  def test_ansible_force_stop(self):
    self.assertTrue(self.ansible['force_stop'])

  def test_ansible_isos(self):
    self.assertListEqual(self.ansible['isos'], [])

  def test_ansible_node(self):
    self.assertEqual(self.ansible['node'], 'pm1.example.com')

  def test_ansible_root(self):
    self.assertDictEqual(self.ansible['root'],
        {
          'disk': 'scsi0',
          'file': 'local-lvm:vm-100-disk-0',
          'format': '',
          'fullname': 'vm-100-disk-0',
          'line': 'scsi0: file=local-lvm:vm-100-disk-0,size=4G',
          'name': 'vm-100-disk-0',
          'size': '4G',
          'storage': 'local-lvm',
          'storage-option': '',
          'meta': {
            'create': 'local-lvm:4'
          }
        }
    )

  def test_ansible_template(self):
    self.assertDictEqual(self.ansible['template'], {})

  def test_ansible_vmid(self):
    self.assertEqual(self.ansible['vmid'], 100)


class TestAnsibleKvmAllOptionsInferredParserOutput(unittest.TestCase):
  '''Test each ansible return key separately to keep dict reasonable.'''

  @classmethod
  def setUpClass(cls):
    '''Only read the configuration file once.'''
    with open(os.path.join(sys.path[0], 'tests/conf/qm_all_options_inferred.conf'), 'r') as f:
      config_inferred_text = f.read()
    kvm_params = params.KvmMinimumValid()
    kvm_params['config'] = config_inferred_text
    cls.ansible = parsers.PveConfig(kvm_params).Ansible()
    with open(os.path.join(sys.path[0], 'tests/conf/qm_all_options_explicit.conf'), 'r') as f:
      cls.config_explicit_text = f.read()

  def test_ansible_changed_false(self):
    self.assertFalse(self.ansible['changed'])

  def test_ansible_cli(self):
    self.assertEqual(self.ansible['cli'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_CLI_STRING)

  def test_ansible_cli_list(self):
    self.assertListEqual(self.ansible['cli_list'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_CLI_LIST)

  def test_ansible_cloud_init(self):
    self.assertDictEqual(self.ansible['cloud_init'], {})

  def test_ansible_config(self):
    self.assertDictEqual(self.ansible['config'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_ANSIBLE)

  def test_ansible_config_list(self):
    self.assertListEqual(self.ansible['config_list'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_ANSIBLE_LIST)

  def test_ansible_config_test(self):
    self.assertEqual(self.ansible['config_text'], self.config_explicit_text)

  def test_ansible_disks(self):
    self.maxDiff = None
    self.assertListEqual(self.ansible['disks'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_ANSIBLE_DISKS)

  def test_ansible_force_stop(self):
    self.assertTrue(self.ansible['force_stop'])

  def test_ansible_isos(self):
    self.maxDiff = None
    self.assertListEqual(self.ansible['isos'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_ANSIBLE_ISOS)

  def test_ansible_node(self):
    self.assertEqual(self.ansible['node'], 'pm1.example.com')

  def test_ansible_root(self):
    self.assertDictEqual(self.ansible['root'], kvm_file_validation_data.QM_ALL_OPTIONS_INFERRED_ANSIBLE_ROOT)

  def test_ansible_template(self):
    self.assertDictEqual(self.ansible['template'], {})

  def test_ansible_vmid(self):
    self.assertEqual(self.ansible['vmid'], 100)


if __name__ == '__main__':
  unittest.main()
