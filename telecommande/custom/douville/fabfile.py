from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'vcs'
env.roledefs['production'] = {  # use this role with -R role
    'hosts': ['terre.anybox.fr', 'venus.anybox.fr'],
    'domain': 'douville.odoo.anybox.eu',
    'testlogo': False}
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'douville.recette.anybox.eu',
    'testlogo': True}  # use this role with -R role
env.vcs_url = 'https://rhode.anybox.fr/Clients/Douville/douville'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'douville'  # client user account
env.process = 'douville'  # supervisor process group
env.db = 'douville'  # name of the main database
env.buildout_dir = 'douville'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8.0  # Major version of Odoo (can be: 6.1, 7, 8)
