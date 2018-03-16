"""Implementations of tasks for the different systems or methods
"""
from fabric.contrib.console import confirm
from fabric.api import settings, sudo, prompt
from .. import vcs, supervisor, postgres, buildout, cron, systemctl
from .. import tarball, nginx
from ..api import implements
from . import instance


@implements(instance.install, method='vcs', system='wheezy')
def install_vcs_on_wheezy():
    supervisor.stop()
    cron.enable_backup()
    vcs.install()
    vcs.update()
    buildout.create_deployment_cfg()
    buildout.bootstrap()
    buildout.build()


@implements(instance.install, method='vcs', system='jessie')
def install_vcs_on_jessie():
    systemctl.stop()
    cron.enable_backup()
    vcs.install()
    vcs.update()
    buildout.create_deployment_cfg()
    buildout.bootstrap()
    buildout.build()


@implements(instance.install, method='tarball')
def install_tarball():
    supervisor.stop()
    with settings(host_string='livraison.anybox.eu'):
        sudo('ls /var/www/livraison/')
    folder = prompt('Which release folder?')
    with settings(host_string='livraison.anybox.eu'):
        sudo('ls /var/www/livraison/{folder}/'.format(folder=folder))
    archive = prompt('Install which archive?')
    tarball.deploy(folder, archive)


@implements(instance.activate, system='wheezy')
def activate_on_wheezy():
    nginx.register()
    supervisor.register()
    if postgres.is_master():
        supervisor.refresh()
    nginx.reload()


@implements(instance.activate, system='jessie')
def activate_on_jessie():
    nginx.register()
    systemctl.install_service()
    if postgres.is_master():
        systemctl.enable()
    if nginx.status().failed:
        nginx.restart()
    nginx.reload()


@implements(instance.disable, system='wheezy')
def disable_on_wheezy():
    if postgres.is_master():
        supervisor.stop()
    nginx.unregister()
    supervisor.unregister()
    if postgres.is_master():
        supervisor.refresh()
    nginx.reload()


@implements(instance.disable, system='jessie')
def disable_on_jessie():
    if postgres.is_master():
        systemctl.stop()
    nginx.unregister()
    systemctl.disable()
    systemctl.uninstall_service()
    nginx.reload()


@implements(instance.status, system='wheezy')
def status_on_wheezy():
    supervisor.status()


@implements(instance.status, system='jessie')
def status_on_jessie():
    systemctl.status()


@implements(instance.upgrade_all, system='wheezy')
def upgrade_all_on_wheezy():
    """Stop, dump, update and run the buildout, upgrade_script, start.
       A few minutes downtime"""
    if postgres.is_master():
        supervisor.stop()
        postgres.dumpdb()
        buildout.upgrade_script()
        supervisor.start()


@implements(instance.upgrade_all, system='jessie')
def upgrade_all_on_jessie():
    """Stop, dump, update and run the buildout, upgrade_script, start.
       A few minutes downtime"""
    if postgres.is_master():
        systemctl.stop()
        postgres.dumpdb()
        buildout.upgrade_script()
        systemctl.start()


@implements(instance.update_modules, method='vcs')
def update_modules(*modules):
    if not confirm('Warning: updating the code of this modules '
                   'will also update everything in the same repository',
                   default=True):
        return
    vcs.update_modules(modules)


@implements(instance.version, method='vcs')
def version(path='.'):
    """ Display the remote revision info of the specified relative path"""
    vcs.revision(path)


@implements(instance.start, system='wheezy')
def start_on_wheezy():
    if postgres.is_master():
        supervisor.start()


@implements(instance.start, system='jessie')
def start_on_jessie():
    if postgres.is_master():
        systemctl.start()


@implements(instance.restart, system='wheezy')
def restart_on_wheezy():
    if postgres.is_master():
        supervisor.restart()


@implements(instance.restart, system='jessie')
def restart_on_jessie():
    if postgres.is_master():
        systemctl.restart()


@implements(instance.stop, system='wheezy')
def stop_on_wheezy():
    if postgres.is_master():
        supervisor.stop()


@implements(instance.stop, system='jessie')
def stop_on_jessie():
    if postgres.is_master():
        systemctl.stop()
