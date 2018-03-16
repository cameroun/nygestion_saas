from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'vcs'
env.roledefs['recette'] = {  # use this role with -R role
    'hosts': ['mercure.anybox.fr'],
    'domain': 'prometour_website.recette.anybox.eu',
    'testlogo': True}
env.vcs_url = 'https://rhode.anybox.fr/Clients/Prometour/prometour_website'  # buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.account = 'prometour_website'  # client user account
env.process = 'prometour_website'  # supervisor process group
env.db = 'prometour_website'  # name of the main database
#  env.buildout_dir = 'current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.revision = 'website'
env.buildout_dir = 'vcs'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'openerp'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (can be: 6.1, 7, 8)
