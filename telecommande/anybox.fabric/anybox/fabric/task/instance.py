from fabric.api import settings
from anybox.fabric.api import task
from anybox.fabric import nginx, buildout, postgres


@task
def local_release():
    """Locally freeze and tag the project (shortcut for local oe_hg_release)"""
    buildout.release()


@task(depends=('method', 'system'))
def install():
    """Deploy the buildout in the target server (first install, or reinstall)
    """
    raise NotImplementedError


@task(depends='system')
def upgrade_all():
    """Stop, dump, upgrade all modules, start. A few minutes downtime."""
    raise NotImplementedError


@task(depends='method')
def update_modules(*modules):
    """ Update the code of the specified modules (vcs pull)
    """
    raise NotImplementedError


@task
def upgrade_modules(*modules):
    """Backup and upgrade the specified modules in the database"""
    if postgres.is_master():
        postgres.dumpdb()
        buildout.upgrade_modules(modules)


@task(depends='method')
def version(path='.'):
    """ Display the remote revision info of the specified relative path"""
    raise NotImplementedError


@task
def admin_passwd():
    """ Show the admin password of the instance
    """
    buildout.admin_passwd()


@task
def open_shell():
    """ Open an interactive session in the odoo Python shell"""
    buildout.shell()


@task(depends='system')
def activate():
    """Add the instance in Nginx and process manager config, and start
    """
    raise NotImplementedError


@task(depends='system')
def disable():
    """Stop the instance and remove it from Nginx and process manager configs
    """
    raise NotImplementedError


@task(depends='system')
def status():
    """ Supervisor status"""
    raise NotImplementedError


@task(depends='system')
def stop():
    """Stop the instance"""
    raise NotImplementedError


@task(depends='system')
def start():
    """Start the instance"""
    raise NotImplementedError


@task(depends='system')
def restart():
    """Restart Odoo"""
    raise NotImplementedError


@task
def logfile():
    """Show the Odoo logfile (Ctrl-C to interrupt)"""
    buildout.logfile()


@task
def unprotect():
    """ Recreate the nginx config without IP protection.
    (doesnt change xmlrpc whitelist)
    """
    with settings(allow_ip=[], allow_xmlrpc=[]):
        nginx.register()
    nginx.reload()


@task
def protect():
    """ Recreate the standard nginx config without IP protection"""
    nginx.register()
    nginx.reload()


@task
def master_and_slave():
    """Allow to know which are the master and the slave"""
    postgres.is_master()