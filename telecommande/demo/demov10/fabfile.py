# coding: utf-8
from fabric.api import sudo, cd
from anybox.fabric.api import task
from anybox.fabric import systemuser
from anybox.fabric.task import instance, customer, db, buildbot, env, help, demo

env.api.method = 'vcs'
env.roledefs['demo'] = {
    'hosts': ['jupiter.anybox.fr'],
    'domain': '*.demov10.anybox.eu'}
env.vcs_url = 'https://rhode.anybox.fr/Generique/demov10'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'demov10'  # client user account
env.process = 'demov10'  # supervisor process group
env.db = ''  # name of the main database
env.buildout_dir = 'demov10'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 10  # Major version of Odoo (can be: 6.1, 7, 8)
env.https = False  # deploy on http
