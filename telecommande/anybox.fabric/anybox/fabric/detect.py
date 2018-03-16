from fabric.api import sudo


def infra():
    return 'proxmox'


def system():
    version = sudo('cat /etc/debian_version')
    return {'7': 'wheezy', '8': 'jessie'}.get(version[0])
