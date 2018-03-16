from fabric.api import env, puts, task, local
from fabric.colors import cyan
from fabric.contrib.console import confirm
import urllib2
import sys
import time
from os.path import dirname, join, exists

env.date = time.strftime('%Y%m%d%H%M%S')
env.master = {}  # determined during execution
env.colorize_errors = True
env.forward_agent = True


COUNTER = lambda: join(dirname(dirname(sys.argv[0])), '.last_upgrade')


def latest_available():
    """Check online if there is a new version"""
    try:
        latest = int(urllib2.urlopen(
            'http://telecommande.anybox.fr/telecommande/check'
        ).read())
        if not exists(COUNTER()):
            return latest
        current = int(open(COUNTER()).read())
        if current < latest:
            return latest
    except Exception:
        return False
    return False


def autoupgrade(latest):
    """launch the upgrade"""
    puts('Upgrading')
    # FIXME anybox.fabric doesn't know about a buildout
    local('cd {} && hg pull -u && ./bin/buildout'
          .format(dirname(dirname(sys.argv[0]))))
    with open(COUNTER(), 'w') as f:
        f.write(str(latest))


@task
def help():
    """ Show available syntax, roles and commands """
    puts('\nSyntax: bin/fab [-R <role>] <command>\n')
    if type(env.roledefs) is list:
        hosts = env.roledefs.items()
    elif type(env.roledefs) is dict:
        hosts = [(role, env.roledefs[role]
                 if type(env.roledefs[role]) is list
                 else env.roledefs[role]['hosts']) for role in env.roledefs]
    puts('Available roles:\n    {}\n'.format('\n    '.join(
        [i[0] + ':\t' + ', '.join(i[1]) for i in hosts])))
    from fabric.main import list_commands
    puts('\n'.join(list_commands('', 'normal')) + '\n')

    # auto upgrade?
    latest = latest_available()
    if latest is not False:
        if confirm(cyan('New version available. Upgrade telecommande?'),
                   default=False):
            autoupgrade(latest)
            puts('Upgrade finished. Please relaunch fab help')
        else:
            puts('Upgrade canceled')
