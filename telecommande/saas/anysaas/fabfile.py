# deployment fabfile
from anybox.fabric.task import instance, customer, db, help, env, buildbot

# deployment configuration
env.api.method = 'vcs'
env.roledefs['small'] = {
    'hosts': ['192.168.112.4'],  # SMALL Could
    'domain': '*.small.nygestion.re',
    'testlogo': False,
}
env.vcs_url = 'https://github.com/cameroun/nygestion_saas'  # URL of the buildout repository
env.vcs_type = 'git'  # type of the buildout repository (hg, git)
env.revision = 'master'  # vcs tag or branch name of the buildout repository
env.account = 'small'  # client user account
env.process = 'small'  # supervisor process group
env.db = 'small'  # name of the main database
env.buildout_dir = 'current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 11  # Major version of Odoo (can be: 6.1, 7, 8, 9)
env.allow_ip = []  # list of IP allowed to access the application. All if empty.
env.allow_xmlrpc = []  # list of IP allowed to access xmlrpc. None if empty.
