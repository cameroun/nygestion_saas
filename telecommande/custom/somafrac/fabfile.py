from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'vcs'
env.roledefs['production'] = {  # use this role with -R role
    'hosts': ['terre.anybox.fr', 'venus.anybox.fr'],
    'domain': 'somafrac.odoo.anybox.eu',
    'testlogo': False}
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'somafrac.recette.anybox.eu',
    'testlogo': True}  # use this role with -R role
env.vcs_url = 'https://rhode.anybox.fr/Clients/Somafrac/Somafrac'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'somafrac'  # client user account
env.process = 'somafrac'  # supervisor process group
env.db = 'somafrac'  # name of the main database
env.buildout_dir = 'Somafrac'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 7  # Major version of Odoo (can be: 6.1, 7, 8)
env.allow_ip = [
    '80.11.3.90',  # somafrac - champigny
    '78.192.28.126',  # Anybox - ccomb paris
    '212.129.13.79', # Anybox - shinken
    '93.88.240.175', # somafrac - Fabio Chelly
]
