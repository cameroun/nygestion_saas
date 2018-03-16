from fabric.api import env, sudo, cd, settings
from fabric.contrib.files import exists as remote_exists
from .buildout import deploy_cfg, taken_ports


def deploy(release_folder, archive):
    """ deploy the archive found in the release_folder"""
    with cd('~{user}'.format(user=env.account)):
        with settings(sudo_prefix="sudo -E -S -p '%(sudo_prompt)s' " % env):
            ports = ''
            if not remote_exists(deploy_cfg(), use_sudo=True):
                ports = '-p {}'.format(taken_ports()[-1]+1)
                if env.version >= '8':
                    ports += ' --longpolling-port={}'.format(
                        taken_ports()[-1]+2)
            sudo('anybox-odoo-deploy -v {version} {ports}'
                 ' --buildout-part {odoo} {instance} {archive} '
                 ' --remote-subdir {release_folder}'
                 .format(release_folder=release_folder, archive=archive,
                         version=env.version, ports=ports, odoo=env.odoo,
                         instance=env.account))
