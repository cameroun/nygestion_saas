# deployment fabfile
from anybox.fabric.task import instance, customer, db, buildbot, help, env, local

# deployment configuration
env.api.method = 'vcs'

env.roledefs['production'] = {  # use this role with -R role
    'hosts': ['io.anybox.fr', 'europe.anybox.fr'],
    'domain': 'itsra.bdes.info'}
#env.roledefs['recette'] = {
#    'hosts': ['mercure4.anybox.fr'],
#    'domain': 'itsra_bdes.recette2.anybox.eu'}  # use this role with -R role
env.vcs_url = 'https://bitbucket.org/anybox/bdes'
env.vcs_type = 'hg'
env.revision = 'stable'  # vcs tag or branch name
env.account = 'bdes_itsra'  # client user account
env.process = 'bdes_itsra'  # supervisor process group
env.db = 'itsra'  # name of the main database
env.buildout_dir = 'bdes'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (6.1, 7, 8)
