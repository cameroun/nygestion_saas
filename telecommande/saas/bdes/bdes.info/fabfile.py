# deployment fabfile
from anybox.fabric.task import instance, customer, db, buildbot, env, help


# deployment configuration
env.api.method = 'vcs'
env.api.version = 1  # double check before changing version!

env.roledefs['production'] = {
    'hosts': ['io.anybox.fr', 'europe.anybox.fr'],
    'domain': 'bdes.info'}
env.vcs_url = 'http://ccomb@rhode.anybox.fr/Anybox/bdes.info'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'bdes_info'  # client user account
env.process = 'bdes_info'  # supervisor process group
env.db = 'bdes_info'  # name of the main database
env.buildout_dir = 'current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (can be: 6.1, 7, 8)
