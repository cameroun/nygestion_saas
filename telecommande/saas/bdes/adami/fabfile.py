# deployment fabfile
from anybox.fabric.task import instance, customer, db, buildbot, help, env

# deployment configuration
env.api.method = 'vcs'

env.roledefs['oldproduction'] = {  # use this role with -R role
    'hosts': ['terre2.anybox.fr', 'venus2.anybox.fr'],
    'domain': 'adami.bdes.info'}
env.roledefs['production'] = {  # use this role with -R role
    'hosts': ['io.anybox.fr', 'europe.anybox.fr'],
    'domain': 'adami.bdes.info'}
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'adami_bdes.recette.anybox.eu'}  # use this role with -R role
env.vcs_url = 'https://bitbucket.org/anybox/bdes'
env.vcs_type = 'hg'
env.revision = 'f22d9ec80b86'  # vcs tag or branch name
env.account = 'bdes_adami'  # client user account
env.process = 'bdes_adami'  # supervisor process group
env.db = 'adami'  # name of the main database
env.buildout_dir = 'bdes'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (6.1, 7, 8)
