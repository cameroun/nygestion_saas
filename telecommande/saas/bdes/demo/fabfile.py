# deployment fabfile
from anybox.fabric.task import instance, env, help, db, customer, demo
from anybox.fabric.api import task
from fabric.api import sudo, cd, put
from anybox.fabric import systemuser

env.api.method = 'vcs'
env.roledefs['demo'] = {
    'hosts': ['jupiter.anybox.fr'],
    'domain': '*.demo.bdes.info'}
env.vcs_url = 'https://bitbucket.org/anybox/bdes'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'bdes_demo'  # client user account
env.process = 'bdes_demo'  # supervisor process group
env.db = ''  # name of the main database
env.buildout_dir = 'bdes_demo'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.revision = 'default'  # vcs tag or branch name
env.version = 8  # Major version of Odoo (6.1, 7, 8)
