from fabric.api import sudo, cd, env, abort, warn, local, open_shell
from fabric.contrib.console import confirm
from anybox.fabric.api import savepoint, local_get
from anybox.fabric import systemuser
from fabric.contrib.files import exists as remote_exists
from os.path import exists

DISABLE_MAIL = '''
update fetchmail_server set active=false;
update ir_mail_server set active=false;
INSERT INTO ir_mail_server
      (smtp_host, smtp_port, name, smtp_encryption, active)
      VALUES ('disabled.test', 25, 'Disabled', 'none', true);
'''


def is_master():
    """return True if this host owns the master db"""
    if env.master.get(env.host):
        return env.master[env.host]  # cached value
    env.master[env.host] = sudo(
        "python -c '"
        "from anybox.hosting.postgresql import is_replication_slave;"
        "print(is_replication_slave())'", user='postgres') == 'False'
    is_master = env.master[env.host]
    warn('{host} is a replication {kind}'
         .format(host=env.host, kind='master' if is_master else 'slave'))
    return is_master


def kill_connections(db=None):
    db = db or env.db
    pgversion = sudo('psql -tc "select version()"', user='postgres')
    pid = 'pid' if pgversion[:14] >= "PostgreSQL 9.2" else 'procpid'
    sudo('psql -c '
         '"SELECT pg_terminate_backend(pg_stat_activity.{pid})'
         ' FROM pg_stat_activity '
         ' WHERE pg_stat_activity.datname=\'{db}\''
         ' AND {pid} <> pg_backend_pid()"'
         .format(db=db, pid=pid), user='postgres')


def listdb():
    dbs = sudo('python -c \''
               'from anybox.hosting.postgresql import list_databases;'
               ' print("\\n".join(list_databases(owner="{user}")))\''
               .format(user=env.account),
               user='postgres')
    return [db.strip() for db in dbs.splitlines() if db.strip()]


def listdumps():
    with cd('~{account}/'.format(**env)):
        if not remote_exists('dumps/', use_sudo=True):
            return []
    with cd('~{account}/dumps/'.format(**env)):
        return [d.strip().rsplit('.', 1)[0]
                for d in sudo('ls -1 *\.dump').splitlines()]


def createdb(db=None):
    db = db or env.db
    sudo('createdb "{}"'.format(db), user=env.account)


def dropdb(db=None):
    """ drop a single db"""
    db = db or env.db
    if db_exists(db) and confirm('Drop database {}?'.format(db)):
        kill_connections(db)
        sudo('dropdb --if-exists "{}"'.format(db), user='postgres')
    filestore = filestore_path(db)
    if float(env.version) >= 8 and remote_exists(filestore, use_sudo=True):
        filestore_exists = sudo('test -d {}'.format(filestore),
                                user=env.account, warn_only=True).succeeded
        if filestore_exists:
            if confirm('Delete filestore ? (rm -r {})'.format(filestore)):
                sudo('rm -r {}'.format(filestore), user=env.account)


def restoredb(db, dumpname):
    """restore ~/dumps/dumpname (dump and filestore) as db
    """
    with cd('~{account}/dumps/'.format(**env)):
        sudo('pg_restore -Fc -O -d {db} {dumpname}.dump'
             .format(db=db, dumpname=dumpname),
             user=env.account, warn_only=True)
        if not sudo("psql -c '\d' {db}|wc -l"
                    .format(db=db), user=env.account) > '10':
            abort('DB restoration failed')
        # filestore
        if float(env.version) >= 8:
            backup = '{dumpname}.filestore'.format(dumpname=dumpname)
            if remote_exists(backup, use_sudo=True):
                filestore = filestore_path(db)
                sudo('cp -ra {backup} {filestore}'.format(
                    backup=backup, filestore=filestore), user=env.account)


def dropuser(user=None):
    user = user or env.account
    if confirm('Delete Postgres user: {}?'.format(user)):
        sudo('dropuser --if-exists "{}"'.format(user), user='postgres')


def filestore_path(db):
    return '~{user}/.local/share/Odoo/filestore/{db}'.format(
        db=db, user=env.account)


@savepoint('dump')
def dumpdb(db=None):
    db = db or env.db
    if not db or not db_exists(db):
        warn('No such db {}'.format(db))
        return
    with cd('~{account}'.format(**env)):
        env.odoogrp = 'openerp' if 'system' in env.api and env.api.system == 'wheezy' else 'odoo'
        sudo('mkdir -p dumps && chown {account}:{odoogrp} dumps'.format(**env))
        sudo('pg_dump -Fc -O -f dumps/{db}-{date}.dump {db}'
             .format(db=db, date=env.date), user=env.account)
        filestore = filestore_path(db)
        if float(env.version) >= 8 and remote_exists(filestore, use_sudo=True):
            backup = '~{account}/dumps/{db}-{date}.filestore'.format(**env)
            sudo('cp -ra {filestore} {backup}'
                 .format(filestore=filestore, backup=backup),
                 user=env.account)


def db_exists(db):
    if sudo('psql {db} -c "select version()"'
            .format(db=db), user='postgres', warn_only=True).succeeded:
        return True
    else:
        return False


def local_restore(db):
    """ restore the local dump named <db>.dump (and filestore)"""
    local('createdb {db} && pg_restore -Fc -O -d {db} {db}.dump || echo'
          .format(db=db))
    if not local('psql {db} -c "select version()"'.format(db=db)).succeeded:
        raise Exception('db not restored')
    if exists('{}.filestore'.format(db)):
        local('cp -ra {db}.filestore ~/.local/share/Odoo/filestore/{db}'
              .format(db=db))
    local('psql {db} -c "{sql}"'.format(db=db, sql=DISABLE_MAIL))


def download(name):
    home = systemuser.home()
    local_get('{home}/dumps/{name}.dump'.format(home=home, name=name))
    filestore = '{home}/dumps/{name}.filestore'.format(home=home, name=name)
    if remote_exists(filestore, use_sudo=True):
        local_get(filestore)


def disable_mail_config(db):
    sudo('psql {db} -c "{sql}"'.format(db=db, sql=DISABLE_MAIL),
         user=env.account)


def shell(db):
    env.db = db
    open_shell(command='sudo -u {account} psql {db} && exit'.format(**env))


def purge_dumps_directory():
    """
    Delete the dumps directory and create a new one with correct user:group
    """
    with cd('~{account}/'.format(**env)):
        if remote_exists('dumps/', use_sudo=True):            
            sudo('rm -R dumps && mkdir dumps && chown --reference ~{account} dumps'.format(**env))


def purge_dumps(dumps):
    """delete dumps passed as parameter"""
    for dump in dumps:
        dump_file = "~{account}/dumps/{dump}.dump".format(dump=dump.strip(), **env)
        filestore = "~{account}/dumps/{dump}.filestore".format(dump=dump.strip(), **env)
        if remote_exists(dump_file, use_sudo=True):
            sudo('rm {d}'.format(d=dump_file))
        if remote_exists(filestore, use_sudo=True):
            sudo('rm -R {f}'.format(f=filestore))
