import random
from os.path import join
from StringIO import StringIO
from fabric.contrib.files import exists as remote_exists
from fabric.contrib.console import confirm
from fabric.api import env, sudo, cd, settings
from fabric.api import put, prompt, open_shell, local, puts
from .api import dontreplay, void
from . import postgres, systemuser


def taken_ports():
    """ Return the sorted list of ports already taken"""
    odoo = 'odoo' if env.api.system != 'wheezy' else 'openerp'
    ports = sudo('grep _port /srv/{odoo}/*/*cfg /srv/{odoo}/*/*/*cfg'
                 '|cut -d= -f2|sort|uniq'
                 .format(odoo=odoo)).splitlines()
    ports += sudo('grep \.bind  /srv/{odoo}/*/*cfg /srv/{odoo}/*/*/*cfg'
                  '|cut -d= -f2|cut -d: -f2|sort|uniq'
                  .format(odoo=odoo)).splitlines()
    ports = sorted(set(int(p.strip()) for p in ports if p.strip().isdigit()))
    puts('Already taken ports: {}'.format(', '.join(str(p) for p in ports)))
    if not ports:  # assume 8000 is taken and is the first
        ports = [8000]
    return ports


def deploy_cfg():
    """name of the deployment buildout"""
    return '{buildout}.cfg'.format(buildout=env.host.split('.')[0])


def path():
    """ buildout path"""
    return join(systemuser.home(), env.buildout_dir)


def module_path(module):
    """Return the path of the module, or the paths of the modules
    """
    with cd(path()):
        return sudo(
            './bin/python_{odoo} -c "from openerp import modules;'
            'print modules.get_module_path(\'{module}\')"'
            .format(odoo=env.odoo, module=module),
            user=env.account)


@dontreplay
def create_deployment_cfg():
    """create the deployment buildout"""
    buildout = deploy_cfg()
    with cd('~{user}'.format(user=env.account)):
        if remote_exists(buildout, use_sudo=True):
            if not confirm('The deployment buildout {} already exists! '
                           'Create a new one?'
                           .format(buildout)):
                return
            sudo('rm "{}"'.format(buildout))
        port = taken_ports()[-1] + 1
        puts('Chosen standard port: {}'.format(port))
        lport = lpolling_option = ''
        if env.version >= '8':
            lport = taken_ports()[-1] + 2
            puts('Chosen longpolling port: {}'.format(lport))
            lpolling_option = 'options.longpolling_port = {}\n'.format(lport)
        home = systemuser.home()
        buildout_dir = join(home, env.buildout_dir)
        sudo('mkdir -p log', user=env.account)
        admin_passwd = str(random.randint(0, 10**12))
        put(StringIO(
            '[buildout]\n'
            'extends = {buildout_dir}/{buildout}\n'
            'directory = {buildout_dir}\n\n'
            '[{odoo}]\n'
            'options.admin_passwd = {admin_passwd}\n'
            'options.db_user = {account}\n'
            'options.xmlrpc_interface = localhost\n'
            'options.xmlrpc_port = {port}\n'
            '{lpolling_option}'
            'options.netrpc = False\n'
            'options.workers = 4\n'
            'options.limit_time_cpu = 300\n'
            'options.limit_time_real = 360\n'
            'options.proxy_mode = True\n'
            'options.logfile = {home}/log/{odoo}-server.log'.format(
                buildout_dir=buildout_dir, odoo=env.odoo, account=env.account,
                port=port, lport=lport, admin_passwd=admin_passwd,
                lpolling_option=lpolling_option, home=home,
                buildout=env.get('buildout', 'buildout.cfg'))),
            join(home, buildout), use_sudo=True)


def bootstrap():
    odoo = 'odoo' if env.api.system != 'wheezy' else 'openerp'
    with cd(path()):
        sudo('if [ -e /srv/{odoo}/virtualenv/bin/python ];'
             ' then /srv/{odoo}/virtualenv/bin/python bootstrap.py;'
             ' else virtualenv pyenv --no-site-packages'
             '   && pyenv/bin/pip install setuptools --upgrade'
             '   && pyenv/bin/python bootstrap.py;'
             'fi'.format(odoo=odoo), user=env.account)


@dontreplay
def build(buildout=None, newest=False):
    """ Run the buildout, using the default deployment config
    (`hostname`.cfg) or specify an alternate buildout
    """
    n = 'n' if newest else 'N'
    with cd(path()):
        if not buildout:  # then use the deployment config
            buildout = '../{buildout}'.format(buildout=deploy_cfg())
            if not remote_exists(buildout, use_sudo=True):
                buildout = buildout[3:]
        sudo('bin/buildout -{n} -c {buildout}'.format(buildout=buildout, n=n),
             user=env.account)


@dontreplay
def upgrade_script():
    """run the full upgrade procedure with upgrade.py script
    """
    if postgres.db_exists(env.db):
        with cd(path()):
            sudo('bin/upgrade_{odoo} -d {db} '.format(**env), user=env.account)


@dontreplay
def upgrade_modules(modules):
    with settings(modules=','.join(modules)):
        with cd(path()):
            sudo('bin/start_{odoo} -d {db} -u {modules} '
                 '--workers=0 --no-xmlrpc --no-xmlrpcs --stop-after-init'
                 .format(**env), user=env.account)


@void
def admin_passwd():
    with cd(path()):
        sudo('grep admin_passwd etc/{odoo}.cfg'.format(**env),
             user=env.account)


@void
def shell():
    if not postgres.is_master():
        return
    with cd(path()):
        open_shell(command='sudo -u {account} '
                           '~{account}/{buildout_dir}/bin/python_{odoo} '
                           '&& exit'.format(**env))


@void
def logfile():
    with cd(path()):
        logfile = sudo(
            "./bin/python_{odoo} -c \""
            "from zc.buildout.buildout import Buildout as B;"
            "print(B('{buildout_path}', [])['{odoo}']['options.logfile'])\""
            .format(odoo=env.odoo, buildout_path=join('..', deploy_cfg())),
            user=env.account).splitlines()[-1]
        sudo('tail -f {}'.format(logfile), user=env.account)


@void
def release():
    with settings(host_string='localhost'):
        local('hg tags')
        default_tag = local('test -e VERSION.txt && cat VERSION.txt',
                            capture=True)
        tag = prompt('Release under which new tag?', default=default_tag)
        next_tag = prompt('Next tag will be?')
        local('oe_hg_release buildout.cfg {tag} '
              '--future-version {next_tag} --parts {odoo}'
              .format(odoo=env.odoo, tag=tag, next_tag=next_tag))
