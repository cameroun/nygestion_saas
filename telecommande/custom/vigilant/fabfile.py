from anybox.fabric.task import instance, customer, db, buildbot, help, env

env.api.method = 'vcs'
env.roledefs['production'] = {  # use this role with -R role
    'hosts': ['terre.anybox.fr', 'venus.anybox.fr'],
    'domain': 'vigilant.odoo.anybox.eu',
    'testlogo': False}
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'vigilant.recette.anybox.eu',
    'testlogo': True}  # use this role with -R role
env.vcs_url = 'https://rhode.anybox.fr/Clients/CGSH/vigilant'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'vigilant'  # client user account
env.process = 'vigilant'  # supervisor process group
env.db = 'vigilant'  # name of the main database
env.buildout_dir = 'vigilant'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8.0  # Major version of Odoo (can be: 6.1, 7, 8)
