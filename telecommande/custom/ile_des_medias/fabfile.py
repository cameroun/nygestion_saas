from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'tarball'
env.roledefs['recette'] = {
    'hosts': ['mercure2.anybox.fr'],
    'domain': 'idm.recette2.anybox.eu',
    'testlogo': True}
env.vcs_url = 'https://rhode.anybox.fr/Clients/IDM/idm'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.account = 'idm'  # client user account
env.process = 'idm'  # supervisor process group
env.db = 'idm'  # name of the main database
env.buildout_dir = 'current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.revision = 'default'  # vcs tag or branch name (if vcs)
env.version = 8  # Major version of Odoo (6.1, 7, 8)
