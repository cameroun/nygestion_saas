# coding: utf-8
from fabric.api import sudo, cd
from anybox.fabric.api import task
from anybox.fabric import systemuser
from anybox.fabric.task import instance, customer, db, buildbot, env, help, demo

env.api.method = 'vcs'
env.roledefs['demo'] = {
    'hosts': ['jupiter.anybox.fr'],
    'domain': '*.demov9.anybox.eu'}
env.vcs_url = 'https://rhode.anybox.fr/Generique/demov9'  # URL of the buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'demov9'  # client user account
env.process = 'demov9'  # supervisor process group
env.db = ''  # name of the main database
env.buildout_dir = 'demov9'  # Relative path to the buildout. Ex: client_buildout
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 9  # Major version of Odoo (can be: 6.1, 7, 8)
env.https = False  # deploy on http
