from ..api import implements
from . import customer
from .. import systemuser, vcs, supervisor, postgres, nginx, cron, systemctl


@implements(customer.create)
def create():
    systemuser.create()
    # only on jessie! Anyway already done by add-instance-user:
    # systemctl.start_systemd_user()


@implements(customer.create, method='vcs')
def create_vcs():
    systemuser.create()
    vcs.enable_odoo_git_cache()


@implements(customer.destroy, system='wheezy')
def destroy_wheezy():
    if postgres.is_master():
        supervisor.stop()
    cron.disable_backup()
    nginx.unregister()
    supervisor.unregister()
    if postgres.is_master():
        for db in postgres.listdb():
            postgres.kill_connections(db)
            postgres.dropdb(db)
        postgres.dropuser()
    systemuser.delete()


@implements(customer.destroy, system='jessie')
def destroy_jessie():
    if postgres.is_master():
        systemctl.stop()
    cron.disable_backup()
    nginx.unregister()
    systemctl.uninstall_service()
    systemctl.stop_systemd_user()
    if postgres.is_master():
        for db in postgres.listdb():
            postgres.kill_connections(db)
            postgres.dropdb(db)
        postgres.dropuser()
    systemuser.delete()
