from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'tarball'
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'snesup8.recette.anybox.eu',
    'testlogo': False}
env.vcs_url = 'https://rhode.anybox.fr/Clients/SNESUP/Snesupv8'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'snesup8'  # client user account
env.process = 'snesup8'  # supervisor process group
env.db = 'snesup8'  # name of the main database
env.buildout_dir = 'demov8/current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'openerp'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (can be: 6.1, 7, 8)
