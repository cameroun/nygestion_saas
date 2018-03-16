from os import makedirs
from os.path import exists, dirname
from fabric.operations import prompt
from fabric.api import task, local
from fabric.decorators import hosts
from fabric.utils import puts
from fabric.contrib.console import confirm
from .api import promptlist

fab_template = '''# deployment fabfile
from anybox.fabric.task import instance, customer, db, help, env, buildbot

# deployment configuration
env.api.method = '{method}'
{roledefs}
env.vcs_url = '{vcs_url}'  # URL of the buildout repository
env.vcs_type = '{vcs_type}'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = ''  # client user account
env.process = ''  # supervisor process group
env.db = ''  # name of the main database
env.buildout_dir = '{buildout_dir}'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = ''  # Major version of Odoo (can be: 6.1, 7, 8, 9)
env.allow_ip = []  # list of IP allowed to access the application. All if empty.
env.allow_xmlrpc = []  # list of IP allowed to access xmlrpc. None if empty.
'''


@hosts('localhost')
@task
def create(fabpath=None):
    '''Create the fabfile '''
    if not fabpath:
        puts('Current existing fabfiles:', show_prefix=False)
        local('hg mani|grep fabfile.py|sed "s/^/   /"')
        fabpath = prompt(u'Name of the new fabfile to create (subdirs will be created):',
                         default="fabfile.py")
    vcs_type = ''
    vcs_url = prompt(u'URL of the repository to deploy? (Keep empty if no repository yet)')
    if vcs_url:
        vcs_type = promptlist(u'Which type of vcs is this repo?', ('hg', 'git'))
    method = promptlist(u'Which deployment method?', ('tarball', 'vcs'))
    buildout_dir = 'current_buildout' if method == 'tarball' else ''
    roles = prompt(u'Comma separated list of roles? (ex: "production, recette"', default='recette')
    roledefs = '\n'.join([
        "env.roledefs['{}'] = {{\n"  # use this role with -R role
        "    'hosts': ['foo2.anybox.fr', 'bar2.anybox.fr'],\n"
        "    'domain': 'XXXX.anybox.eu',\n"  # Domain name of the instance
        "    'testlogo': False,\n"  # Replace the logo with a TEST image
        "}}".format(role)
        for role in [t.strip() for t in roles.split(',')]])
    fabfile = fab_template.format(method=method, roledefs=roledefs,
                                  vcs_url=vcs_url, vcs_type=vcs_type, buildout_dir=buildout_dir)
    if not exists(fabpath) or confirm('Overwrite {}?'.format(fabpath)):
        if dirname(fabpath) and not exists(dirname(fabpath)):
            makedirs(dirname(fabpath))
        with open(fabpath, 'w') as f:
            f.write(fabfile)
    puts('Now please edit {} with needed informations'.format(fabpath))
