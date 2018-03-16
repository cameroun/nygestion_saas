from fabric.api import prompt, abort, puts
from fabric.context_managers import settings
from anybox.fabric.api import promptlist, remote_get, env, task
from anybox.fabric import postgres, systemuser, buildout
from fabric.contrib.console import confirm


@task
def list():
    """ List databases """
    postgres.listdb()


@task
def create(db=None):
    """ Create the default db or specified db"""
    if not db:
        db = env.db
    if postgres.is_master():
        postgres.createdb(db)
        buildout.upgrade_script()


@task
def drop():
    """ Drop user databases (Asks confirmation)"""
    if postgres.is_master():
        dbs = postgres.listdb()
        if not dbs:
            abort('No database to drop')
        db = promptlist('Drop which db?', dbs)
        postgres.dropdb(db)


@task(depends='system')
def backup():
    """ Backup the specified databases and filestore (if any)"""
    if len(env.all_hosts) == 1 or not postgres.is_master():
        dbs = postgres.listdb()
        db = promptlist('Which database do you want to backup?', dbs)
        postgres.dumpdb(db)


@task(depends='system')
def restore():
    """ Restore a remote existing backup """
    if not postgres.is_master():
        return
    dumps = postgres.listdumps()
    if not dumps:
        abort('Nothing to restore!')
    dumpname = promptlist('Restore which dump?', dumps)
    puts('Existing DBs: {}'.format(','.join(postgres.listdb())))
    db = prompt('Restore dump as which db name?')
    if postgres.db_exists(db):
        postgres.dumpdb(db)
        postgres.dropdb(db)
    postgres.createdb(db)
    postgres.restoredb(db, dumpname)
    if confirm('Disable e-mail configuration in the restored database?'):
        postgres.disable_mail_config(db)


@task
def transfer(host=None):
    """Download a backup from another host"""
    if not postgres.is_master():
        return
    host = host or prompt('Retrieve backup from which host?')
    with settings(host_string=host):
        accounts = systemuser.getlist()
        remote_account = promptlist(
            'Retrieve backup on {host} from which customer?'
            .format(host=host), accounts)
        with settings(account=remote_account):
            dumpname = promptlist('Retrieve which backup?',
                                  postgres.listdumps())
    remote_get('{host}:~{remote_account}/dumps/{dumpname}.dump'
               .format(host=host, remote_account=remote_account,
                       dumpname=dumpname),
               '~{account}/dumps/'.format(account=env.account))


@task
def download():
    """ Download an existing backup and restore it locally
    """
    if postgres.is_master():
        return
    dumps = postgres.listdumps()
    if not dumps:
        abort('No backup to download. Try db.backup first')
    name = promptlist('Download which backup?', dumps)
    postgres.download(name)
    postgres.local_restore(name)


@task
def disable_mail_config():
    """ Disable ingoing and outgoing e-mail configuration to avoid spam
    """
    if postgres.is_master():
        dbs = postgres.listdb() + ['*']
        db = promptlist(
            'Disable mail config for which db? (or type * for all)', dbs)
        if db == '*':
            for db in dbs[:-1]:
                postgres.disable_mail_config(db)
        else:
            postgres.disable_mail_config(db)


@task
def inspect(db=None):
    """Open an sql shell on the database
    """
    if postgres.is_master():
        db = db or promptlist('Which database?', postgres.listdb())
        postgres.shell(db)


@task
def masterslave():
    """Allow to know which is the master and the slave"""
    postgres.is_master()


@task
def purge_dumps():
    """Delete old dumps"""
    dumps = postgres.listdumps() + ['*']
    desireds_dumps = promptlist('Which (comma separated) dumps do you want to delete ? (* for all)', dumps, True)
    desireds_dumps = desireds_dumps.split(',')
    if '*' in desireds_dumps:
        postgres.purge_dumps_directory()
    else:
        postgres.purge_dumps(desireds_dumps)
