from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'vcs'
env.roledefs['production'] = {  # use this role with -R role
    'hosts': ['terre.anybox.fr', 'venus.anybox.fr'],
    'domain': 'dm_industries.odoo.anybox.eu',
    'testlogo': False}
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'dm_industries.recette.anybox.eu',
    'testlogo': True}  # use this role with -R role
env.vcs_url = 'https://rhode.anybox.fr/Clients/dm_industries'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'dm_industries'  # client user account
env.process = 'dm_industries'  # supervisor process group
env.db = 'dm_industries'  # name of the main database
env.buildout_dir = 'dm_industries'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8.0  # Major version of Odoo (can be: 6.1, 7, 8)
