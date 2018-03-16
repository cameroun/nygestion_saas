from .api import reversible, void
from fabric.contrib.files import upload_template
from fabric.contrib.console import confirm
from fabric.api import sudo, env, cd, abort, warn, put
from fabric.contrib.files import exists as remote_exists
from os.path import dirname, join
from . import buildout


@reversible(_with='unregister')
def register():
    """like anybox-odoo-register but:
    - separated from supervisor
    - supports ip filter protection
    - forbids accessing /website/info on v8
    - supports unsecure http for demos
    - supports wildcard domains (http only)
    - supports alternative logo for "recette"
    """
    assert len(env.effective_roles) == 1
    env.domain = env.roledefs[
        env.effective_roles[0]]['domain']  # remove as of fabric 1.11
    env.testlogo = env.roledefs[
        env.effective_roles[0]].get('testlogo', False)  # idem
    env.domains = env.domain  # for server_name
    # add the www as alternative domain if secondary level domain
    if len(env.domain.split('.')) == 2:
        env.domains += ' www.' + env.domain
    # get the upper domain, unless its a secondary level domain
    splitdomain = env.domain.split('.')
    env.updomain = '.'.join(
        splitdomain[1:] if len(splitdomain) > 2 else splitdomain)
    # retrieve the port numbers
    with cd('~{user}'.format(user=env.account)):
        deploy_cfg = buildout.deploy_cfg()
        # try alternative paths
        if not remote_exists(deploy_cfg, use_sudo=True):
            other_deploy_cfg = env.buildout_dir + '/' + deploy_cfg
            warn("Deployment buildout {} not found. Trying {}"
                 .format(deploy_cfg, other_deploy_cfg))
            deploy_cfg, old_cfg = other_deploy_cfg, deploy_cfg
        if not remote_exists(deploy_cfg, use_sudo=True):
            other_deploy_cfg = env.buildout_dir + '/../' + old_cfg
            warn("Deployment buildout {} not found. Trying {}"
                 .format(deploy_cfg, other_deploy_cfg))
            deploy_cfg, old_cfg = other_deploy_cfg, deploy_cfg
        if not remote_exists(deploy_cfg, use_sudo=True):
            abort("Deployment buildout {} not found".format(old_cfg))
        env.rpcport = sudo('grep xmlrpc_port {} | cut -d= -f2'
                           .format(deploy_cfg)).strip()
        env.lport = sudo('grep longpolling_port {} | cut -d= -f2'
                         .format(deploy_cfg)).strip()

    # create the nginx conf base on the nginx template
    template_dir = join(dirname(__file__), 'templates')
    nginxconf = env.domain.replace('*.', 'wildcard-')
    # change the logo to a test logo if asked
    if env.get('testlogo'):
        sudo('mkdir -p /var/www')
        put(template_dir + '/test.png', '/var/www/', use_sudo=True)
        sudo('chown www-data: /var/www/test.png')
    upload_template('nginx.https.jinja'
                    if env.get('https', True)
                    else 'nginx.http.jinja',
                    '/etc/nginx/sites-available/{}'.format(nginxconf),
                    context=env, use_jinja=True, template_dir=template_dir,
                    use_sudo=True, backup=False)
    sudo('ln -sf /etc/nginx/sites-available/{filename} '
         '/etc/nginx/sites-enabled/{filename}'
         .format(filename=nginxconf))


@reversible(_with='register')
def unregister():
    assert len(env.effective_roles) == 1
    env['domain'] = env.roledefs[
        env.effective_roles[0]]['domain']  # remove as of fabric 1.11
    nginxconf = env.domain.replace('*.', 'wildcard-')
    to_delete = (
        '/etc/nginx/sites-enabled/{}'.format(nginxconf),
        '/etc/nginx/sites-available/{}'.format(nginxconf),
    )
    for f in to_delete:
        if remote_exists(f, use_sudo=True) and confirm('Delete {}?'.format(f)):
            sudo('rm "{}"'.format(f))


@void
def reload():
    if status().failed:
        restart()
    sudo('service nginx reload')


@void
def status():
    return sudo('service nginx status', warn_only=True)


@reversible(_with='start')
def stop():
    sudo('service nginx start')


@reversible(_with='stop')
def start():
    sudo('service nginx start')


@void
def restart():
    sudo('service nginx restart')
