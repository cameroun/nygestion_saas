from anybox.fabric.task import instance, customer, db, help, buildbot, env
# deployment fabfile

# deployment configuration
env.api.method = 'vcs'
env.api.system = 'jessie'
env.roledefs['recette'] = {
    'hosts': ['mercure4.anybox.fr'],
    'domain': 'anybox.recette.anybox.eu',
    'testlogo': True,
}
env.roledefs['production'] = {
    'hosts': ['io.anybox.fr', 'europe.anybox.fr'],
    'domain': 'odoo.anybox.fr',
    'testlogo': False,
}
env.vcs_url = 'https://rhode.anybox.fr/Anybox/openerp.anybox.fr'  # buildout repository
env.vcs_type = 'hg'  # type of the buildout repository (hg, git)
env.revision = 'default'  # vcs tag or branch name of the buildout repository
env.account = 'anybox'  # client user account
env.process = 'odoo'  # systemd process group
env.db = 'anybox'  # name of the main database
env.buildout_dir = 'anybox'  # Relative path to the buildout.
env.odoo = 'odoo'  # name of the buildout part of odoo
env.version = 8  # Major version of Odoo (can be: 6.1, 7, 8, 9)
env.allow_ip = []  # list of IP allowed to access the application. All if empty
env.allow_xmlrpc = []  # list of IP allowed to access xmlrpc. None if empty.
