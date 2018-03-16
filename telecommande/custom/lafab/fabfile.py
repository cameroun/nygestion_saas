from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'tarball'

env.roledefs['production'] = {
    'hosts': ['terre.anybox.fr', 'venus.anybox.fr'],
    'domain': 'lafab.odoo.anybox.eu'}
env.roledefs['recette'] = {
    'hosts': ['mercure.anybox.fr'],
    'domain': 'lafab.recette.anybox.eu',
    'testlogo': True}
env.vcs_url = 'https://rhode.anybox.fr/Clients/LAFAB/lafab_buildout'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.account = 'lafab'  # client user account
env.process = 'lafab'  # supervisor process group
env.db = 'lafab'  # name of the main database
env.buildout_dir = 'current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'openerp'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (can be: 6.1, 7, 8)
