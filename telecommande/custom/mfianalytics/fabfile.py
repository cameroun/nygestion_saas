from anybox.fabric.task import instance, customer, db, buildbot, env, help

env.api.method = 'tarball'
env.roledefs['oldproduction'] = {
    'hosts': ['terre.anybox.fr', 'venus.anybox.fr'],
    'domain': 'mfianalytics.odoo.anybox.eu'}
env.roledefs['production'] = {
    'hosts': ['terre3.anybox.fr', 'venus3.anybox.fr'],
    'domain': 'mfianalytics.odoo.anybox.eu'}
env.roledefs['recette'] = {
    'hosts': ['mercure3.anybox.fr'],
    'domain': 'mfianalytics.recette.anybox.eu',
    'testlogo': True}
env.vcs_url = 'https://rhode.anybox.fr/Clients/MFIAnalytics/mfianalytics'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'mfianalytics'  # client user account
env.process = 'mfianalytics'  # supervisor process group
env.db = 'mfianalytics'  # name of the main database
env.buildout_dir = 'current_buildout'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (can be: 6.1, 7, 8)
