from .api import reversible, void, sudo, env
from . import systemuser
from os.path import join, dirname
from fabric.contrib.files import upload_template, exists as remote_exists
from fabric.contrib.console import confirm

UNIT = "{account_home}/.config/systemd/user/odoo-workers.service"


@reversible(_with='uninstall_service')
def install_service():
    """install the systemd unit file for the instance"""
    env.account_home = systemuser.home()
    template_dir = join(dirname(__file__), 'templates')
    env.buildout_dir = join(systemuser.home(), env.buildout_dir)
    sudo('mkdir -p `dirname "{unit}"`'.format(unit=UNIT.format(**env)),
         user=env.account)
    upload_template('systemd-service.jinja', UNIT.format(**env),
                    context=env, use_jinja=True, template_dir=template_dir,
                    use_sudo=True, backup=False)
    sudo('chown {user}: {unit}'
         .format(user=env.account, unit=UNIT.format(**env)))


@reversible(_with='install_service')
def uninstall_service():
    env.account_home = systemuser.home()
    unit = UNIT.format(**env)
    if remote_exists(unit) and confirm('Delete {}?'.format(unit)):
        sudo('rm "{}"'.format(unit))


@reversible(_with='stop_systemd_user')
def start_systemd_user():
    sudo('loginctl enable-linger {user}'
         .format(user=env.account))
    sudo('systemctl start user@`id {user} -u`.service'
         .format(user=env.account))


@reversible(_with='start_systemd_user')
def stop_systemd_user():
    sudo('systemctl stop user@`id {user} -u`.service'
         .format(user=env.account))
    sudo('loginctl disable-linger {user}'
         .format(user=env.account))


@reversible(_with='disable')
def enable():
    """allow to start at boot"""
    sudo('userctl enable odoo.target', user=env.account)


@reversible(_with='enable')
def disable():
    """allow to start at boot"""
    sudo('userctl disable odoo.target', user=env.account)


@void
def reload():
    sudo('userctl daemon-reload', user=env.account)


@void
def status():
    # memo: userctl is: XDG_RUNTIME_DIR=/run/user/`id -u` systemctl --user
    return sudo('userctl status odoo-workers',
                warn_only=True, user=env.account)


@reversible(_with='start')
def stop():
    if status().succeeded:
        sudo('userctl stop odoo-workers', user=env.account)


@reversible(_with='stop')
def start():
    if status().failed:
        sudo('userctl start odoo-workers', user=env.account)


@void
def restart():
    sudo('userctl restart odoo-workers', user=env.account)
