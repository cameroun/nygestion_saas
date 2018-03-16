# deployment fabfile
from anybox.fabric.task import instance, customer, db, help, env, buildbot

# deployment configuration
env.api.method = 'vcs'
env.roledefs['recette'] = {
    'hosts': ['mercure3.anybox.fr'],
    'domain': 'rea.recette.anybox.eu',
    'testlogo': False,
}
env.vcs_url = 'https://bitbucket.org/anybox/rea'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'rea'  # client user account
env.db = 'rea'  # name of the main database
env.buildout_dir = 'rea'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 9  # Major version of Odoo (can be: 6.1, 7, 8, 9)
env.allow_ip = []  # list of IP allowed to access the application. All if empty.
env.allow_xmlrpc = []  # list of IP allowed to access xmlrpc. None if empty.
