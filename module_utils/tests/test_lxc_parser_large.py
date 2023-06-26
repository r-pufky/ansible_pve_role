#!/usr/bin/python
#
# Valid LXC parsing against minimmum and inferred options, validate against
# explicit configuration. Run from 'module_utils' with
#
#   python3 -m unittest
#
# If needed, set 'self.maxDiff = None' for full diff results.
#
# Reference:
# * https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html

from tests import params
from tests.data import lxc_file_validation_data
import parsers
import unittest
import os
import sys

class TestAnsibleLxcMinimumParserOutput(unittest.TestCase):
  '''Test each ansible return key separately to keep dict reasonable.'''

  def setUp(self):
    self.ansible = parsers.PveConfig(params.LxcMinimumValid()).Ansible()

  def test_ansible_changed_false(self):
    self.assertFalse(self.ansible['changed'])

  def test_ansible_cli(self):
    self.assertEqual(self.ansible['cli'], '--rootfs volume=local-lvm:vm-100-disk-0,size=4G')

  def test_ansible_cli_list(self):
    self.assertListEqual(self.ansible['cli_list'], ['--rootfs volume=local-lvm:vm-100-disk-0,size=4G'])

  def test_ansible_config(self):
    self.assertDictEqual(self.ansible['config'],
        {
          'rootfs': {
            'volume': 'local-lvm:vm-100-disk-0',
            'size': '4G'
          }
        }
    )

  def test_ansible_config_list(self):
    self.assertListEqual(self.ansible['config_list'], ['rootfs: volume=local-lvm:vm-100-disk-0,size=4G'])

  def test_ansible_config_test(self):
    self.assertEqual(self.ansible['config_text'], 'rootfs: volume=local-lvm:vm-100-disk-0,size=4G')

  def test_ansible_force_stop(self):
    self.assertTrue(self.ansible['force_stop'])

  def test_ansible_node(self):
    self.assertEqual(self.ansible['node'], 'pm1.example.com')

  def test_ansible_root(self):
    self.assertDictEqual(self.ansible['root'],
        {
          'disk': 'rootfs',
          'file': 'local-lvm:vm-100-disk-0',
          'format': '',
          'fullname': 'vm-100-disk-0',
          'line': 'rootfs: volume=local-lvm:vm-100-disk-0,size=4G',
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

class TestAnsibleLxcAllOptionsInferredParserOutput(unittest.TestCase):
  '''Test each ansible return key separately to keep dict reasonable.'''


  @classmethod
  def setUpClass(cls):
    '''Only read the configuration file once.'''
    with open(os.path.join(sys.path[0], 'tests/conf/pct_all_options_inferred.conf'), 'r') as f:
      config_inferred_text = f.read()
    lxc_params = params.LxcMinimumValid()
    lxc_params['config'] = config_inferred_text
    cls.ansible = parsers.PveConfig(lxc_params).Ansible()
    with open(os.path.join(sys.path[0], 'tests/conf/pct_all_options_explicit.conf'), 'r') as f:
      cls.config_explicit_text = f.read()

  def test_ansible_changed_false(self):
    self.assertFalse(self.ansible['changed'])

  def test_ansible_cli(self):
    self.assertEqual(self.ansible['cli'], lxc_file_validation_data.PCT_ALL_OPTIONS_INFERRED_CLI_STRING)

  def test_ansible_cli_list(self):
    self.assertListEqual(self.ansible['cli_list'], lxc_file_validation_data.PCT_ALL_OPTIONS_INFERRED_CLI_LIST)

  def test_ansible_config(self):
    self.assertDictEqual(self.ansible['config'], lxc_file_validation_data.PCT_ALL_OPTIONS_INFERRED_ANSIBLE)

  def test_ansible_config_list(self):
    self.assertListEqual(self.ansible['config_list'], lxc_file_validation_data.PCT_ALL_OPTIONS_INFERRED_ANSIBLE_LIST)

  def test_ansible_config_test(self):
    self.assertEqual(self.ansible['config_text'], self.config_explicit_text)

  def test_ansible_force_stop(self):
    self.assertTrue(self.ansible['force_stop'])

  def test_ansible_node(self):
    self.assertEqual(self.ansible['node'], 'pm1.example.com')

  def test_ansible_root(self):
    self.assertDictEqual(self.ansible['root'], lxc_file_validation_data.PCT_ALL_OPTIONS_INFERRED_ANSIBLE_ROOT)

  def test_ansible_template(self):
    self.assertDictEqual(self.ansible['template'], {})

  def test_ansible_vmid(self):
    self.assertEqual(self.ansible['vmid'], 100)

if __name__ == '__main__':
  unittest.main()
