from os.path import join, isabs
from fabric.api import sudo, puts, cd, env, abort
from anybox.fabric.api import dontreplay, void, reversible
from fabric.contrib.files import append, exists as remote_exists
from fabric.contrib.console import confirm
from . import buildout
from os.path import dirname


@dontreplay
def install(revision=None):
    """install or purge and reinstall
    """
    revision = revision or env.revision
    url = env.vcs_url
    path = buildout.path()
    if remote_exists(path, use_sudo=True):
        if confirm('The buildout is already installed. Delete it? '
                   '(rm -rf "{}")'.format(path)):
            sudo('rm -rf "{}"'.format(path))
    with cd('~{user}'.format(user=env.account)):
        if env.vcs_type == 'hg':
            sudo('hg clone -u {revision} {url} {path}'
                 .format(revision=revision, url=url, path=path),
                 user=env.account)
        if env.vcs_type == 'git':
            sudo('git clone -n {url} {path} &&'
                 'cd {path} &&'
                 'git checkout origin/{revision}'
                 .format(revision=revision, url=url, path=path),
                 user=env.account)


@void
def remote_vcs_type(abspath, buildout_path=None):
    """ return the type of the repo in the relative path
    """
    buildout_path = buildout_path or buildout.path()
    with cd(join(buildout_path, abspath)):
        for vcs in ('hg', 'git'):
            if sudo('test -d .{vcs}'
                    .format(vcs=vcs), warn_only=True).succeeded:
                return vcs
    if buildout_path != abspath:
        return remote_vcs_type(dirname(abspath), buildout_path)


@void
def ensure_vcs(path):
    """ abort if there is no remote repository here
    """
    vcs = remote_vcs_type(path)
    if not vcs:
        abort('No repository found at {}'.format(path))
    return vcs


@void
def update(path='.', revision=''):
    """Update the specified repo path.
    Directory is absolute or relative to the buildout.
    """
    if not isabs(path):
        path = join(buildout.path(), path)
    vcs = ensure_vcs(path)
    with cd(path):
        puts('Updating {}'.format(path))
        if vcs == 'hg':
            sudo('hg pull; hg up {revision};'
                 .format(revision=revision), user=env.account)
        elif vcs == 'git':
            sudo('if [ "{revision}" == "" ]; then'
                 '       branch=$(git rev-parse --abbrev-ref HEAD);'
                 '       else branch={revision}; fi;'
                 '  git fetch origin $branch;'
                 '  git checkout origin/$branch;'
                 .format(revision=revision), user=env.account)


@dontreplay
def update_modules(modules):
    """ Update the code of the modules"""
    for module in modules:
        update(buildout.module_path(module))


@void
def remote_vcs():
    """Show the URL of the remote repository"""
    with cd(buildout.path()):
        repo = sudo('if [ -d .hg ]; then hg path|cut -d\  -f3; fi')
        repo += sudo('if [ -d .git ]; '
                     'then git remote -v|grep fetch|awk "{print $2}"; fi')
        puts('Repository: {}'.format(repo))
    return repo


@void
def revision(path='.'):
    """returns the revision of the path
    absolute or relative to the buildout"""
    if not isabs(path):
        path = join(buildout.path(), path)
    vcs = remote_vcs_type(path)
    with cd(join(buildout.path(), path)):
        if vcs == 'hg':
            return sudo('hg sum', user=env.account)
        if vcs == 'git':
            return sudo('git status; git show', user=env.account)


@reversible(_with='disable_odoo_git_cache')
def enable_odoo_git_cache():
    # accelerate clones
    puts('Creating a local Odoo clone for caching. Please be patient...')
    if not remote_exists('/srv/git/odoo'):
        sudo('mkdir -p /srv/git')
        sudo('git clone --bare http://github.com/OCA/OCB.git /srv/git/odoo')
    gitprofile = '/etc/profile.d/git_references.sh'
    if not remote_exists(gitprofile):
        sudo('echo export GIT_ALTERNATE_OBJECT_DIRECTORIES='
             '/srv/git/odoo/objects > {}'.format(gitprofile))
    if not remote_exists('/etc/cron.daily/git_reference'):
        append('/etc/cron.daily/git_reference', [
               '#!/bin/sh', 'cd /srv/git/odoo', 'git fetch -q origin'],
               use_sudo=True)
        sudo('chmod 755 /etc/cron.daily/git_reference')


@reversible(_with='enable_odoo_git_cache')
def disable_odoo_git_cache():
    sudo('rm /etc/profile.d/git_references.sh')
    sudo('rm /etc/cron.daily/git_reference')
