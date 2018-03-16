from fabric.api import sudo, puts, cd, env
from fabric.contrib.console import confirm
from anybox.fabric.api import dontreplay, void


def home():
    with cd('~{user}'.format(user=env.account)):
        return sudo('pwd', user=env.account)


def disk_usage():
    """Disk usage of the user account"""
    with cd(home()):
        puts('Current disk usage: {}'
             .format(sudo('du -sh .', user=env.account)))


@dontreplay
def delete(user=None):
    user = user or env.account
    home = sudo('getent passwd "{user}"| cut -d: -f6'.format(user=env.account))
    if exists(user) and confirm('Delete system user "{}"?'
                                .format(env.account)):
        pids = [pid.strip() for pid in sudo(
                'ps -u "{user}" -o pid='
                .format(user=env.account), warn_only=True).splitlines()]
        if pids:
            sudo('kill -9 {pids}'.format(pids=' '.join(pids)))
        sudo('crontab -u "{user}" -r'.format(user=env.account))
        sudo('deluser "{user}"'.format(user=env.account))
    command = 'rm -rf "{home}"'.format(home=home)
    if home and confirm('Delete all user data and local dumps ? ({})'
                        .format(command)):
        sudo(command)


@dontreplay
def create():
    if env.account in ('eggs', 'odoo-downloads', 'toolsenv3', 'virtualenv'):
        raise Exception('Username {} is forbidden'.format(env.account))
    sudo('anybox-odoo-add-instance-user "{user}"'
         .format(user=env.account))


@void
def getlist(groups=['openerp', 'odoo']):
    """return the list of accounts
       which are in one of the given list of groups"""
    return list(set(sudo(
        ';'.join(['getent passwd'
                  '|grep :.*:.*:$(getent group {group}|cut -d: -f3):.*:.*:'
                  '|cut -d: -f1'.format(group=group)
                  for group in groups
                  ])).splitlines()))


@void
def exists(user=None):
    user = user or env.account
    return user in getlist()
