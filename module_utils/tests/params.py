# Manual module.params options to be integrated later.

def TemplateCloud() -> dict:
  return {
    'template': {
      'url': 'https://cloud.debian.org/cdimage/cloud/bullseye/20211011-792/debian-11-genericcloud-amd64-20211011-792.tar.xz',
      'checksum':  'ded2dc24ebb876d741ee80bd1e5edba34e32eaded73e2b90820792700c81d512b68a28bae929c8a377b5ec8995b053990616199f5214d07f81fd8603b32e66ce',
      'algorithm': 'sha512'
    }
  }

def TemplateLxc() -> dict:
  return {
    'template': {
      'url': 'debian-11-standard_11.0-1_amd64.tar.gz',
      'checksum': '',
      'algorithm': '',
    }
  }

def TemplateIso() -> dict:
  return {
    'template': {
      'url': 'https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-11.1.0-amd64-netinst.iso',
      'checksum': '02257c3ec27e45d9f022c181a69b59da67e5c72871cdb4f9a69db323a1fad58093f2e69702d29aa98f5f65e920e0b970d816475a5a936e1f3bf33832257b7e92',
      'algorithm': 'sha512',
    }
  }

def PveRequired() -> dict:
  return {
    'vmid': 100,
    'node': 'pm1.example.com',
  }

def KvmMinimumValid() -> dict:
  base = PveRequired()
  base.update({'config': 'scsi0: file=local-lvm:vm-100-disk-0,size=4G'})
  return base

def KvmMediumValid() -> dict:
  base = PveRequired()
  base.update(TemplateCloud())
  base['force_stop'] = True
  base['cloud_init'] = 'local-lvm'
  # Move large config strings to files or static blocks at bottom. Load once per return.
  base['config'] = '''acpi: 1\nagent: enabled=1,fstrim_cloned_disks=1,type=virtio\ncores: 4\nsockets: 1\ncpu: cputype=kvm64,hidden=1\nautostart: 1\nballoon: 1024\nmemory: 2048\nbios: ovmf\nboot: order=scsi0\nkvm: 1\nmachine: q35\nname: vtest.example.com\nnameserver: 10.9.9.2\nsearchdomain: example.com\nnet0: virtio=02:C3:03:86:52:96,bridge=vmbr0,firewall=1\nipconfig0: gw=10.9.9.1,ip=10.9.9.252/24\nonboot: 1\nostype: l26\nscsi0: local-lvm:vm-100-disk-0,size=4G\nscsihw: virtio-scsi-pci\nstartup: order=1\nciuser: root\ncipassword: {{ pve_vm_initial_password }}\ncitype: nocloud\nide2: local:iso/proxmox-ve_6.3-1.iso,media=cdrom\nsshkeys: ssh-rsa AA+HA/56+/kmx3kZ/bzz/KD9== user@testcase'''
  return base

def KvmCloudInitRequired() -> dict:
  base = PveRequired()
  base['cloud_init'] = 'local-lvm'
  return base

def KvmCloudInitNoMount() -> dict:
  base = KvmCloudInitRequired()
  base['config'] = 'ide0: local-lvm:cloudinit'
  return base

def KvmCloudInitFullMount() -> dict:
  base = KvmCloudInitRequired()
  base['config'] = '''ide0: local:iso/proxmox-ve_6.3-1.iso,media=cdrom\nide1: local:iso/proxmox-ve_6.3-1.iso,media=cdrom\nide2: local:iso/proxmox-ve_6.3-1.iso,media=cdrom'''
  return base

def LxcMinimumValid() -> dict:
  base = PveRequired()
  base.update({'config': 'rootfs: local-lvm:vm-100-disk-0,size=4G'})
  return base

def LxcIdmapValid() -> dict:
  base = PveRequired()
  base.update({'config': '''\nlxc.idmap: u 0 100000 1005\nlxc.idmap: g 0 100000 1005\nlxc.idmap: u 1005 1005 1\nlxc.idmap: g 1005 1005 1\nlxc.idmap: u 1006 101006 64530\nlxc.idmap: g 1006 101006 64530'''})
  return base

def LxcInitCmdValid() -> dict:
  base = PveRequired()
  base.update({'config': '''\nlxc.init_cmd: /sbin/my_own_init\nlxc.init_cmd: /sbin/command2'''})
  return base

def LxcAllExtensionsValid() -> dict:
  base = PveRequired()
  base.update({'config': '''\nlxc.idmap: u 0 100000 1005\nlxc.idmap: g 0 100000 1005\nlxc.idmap: u 1005 1005 1\nlxc.idmap: g 1005 1005 1\nlxc.idmap: u 1006 101006 64530\nlxc.idmap: g 1006 101006 64530\nlxc.init_cmd: /sbin/my_own_init\nlxc.init_cmd: /sbin/command2'''})
  return base
