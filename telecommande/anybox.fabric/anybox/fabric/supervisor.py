from fabric.contrib.files import upload_template
from .api import reversible, void, sudo, env
from . import systemuser
from fabric.contrib.console import confirm
from fabric.contrib.files import exists as remote_exists
from os.path import dirname, join


@reversible(_with='unregister')
def register():
    """install the supervisor config file for the instance"""
    env.account_home = systemuser.home()
    template_dir = join(dirname(__file__), 'templates')
    env.buildout_dir = join(systemuser.home(), env.buildout_dir)
    upload_template('supervisor.jinja',
                    '/etc/supervisor/openerp.d/{account}.conf'.format(**env),
                    context=env, use_jinja=True, template_dir=template_dir,
                    use_sudo=True, backup=False)


@reversible(_with='register')
def unregister():
    to_delete = '/etc/supervisor/openerp.d/{process}.conf'.format(**env)
    if (remote_exists(to_delete, use_sudo=True)
            and confirm('Delete {}?'.format(to_delete))):
        sudo('rm "{}"'.format(to_delete))


@void
def status():
    status = sudo('supervisorctl status')
    return [l for l in status.splitlines() if l.startswith(env.process + ':')]


@reversible(_with='start')
def stop():
    s = status()
    if any(['RUNNING' in l for l in s]):
        sudo('supervisorctl stop {process}:*'.format(**env))


@reversible(_with='stop')
def start():
    s = status()
    if any(['STOPPED' in l for l in s]):
        sudo('supervisorctl start {process}:*'.format(**env))


@void
def restart():
    sudo('supervisorctl restart {process}:*'.format(**env))


@void
def refresh():
    sudo('supervisorctl reread')
    sudo('supervisorctl update')  # should start the instance
