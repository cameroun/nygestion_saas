from fabric.api import local, task
from .api import dontreplay, reversible, irreversible, savepoint, void


@dontreplay
def create():
    local('touch testfile')


@savepoint(restore='recover')
def backup():
    local('cp testfile testfile.bkp')


@irreversible(unless='backup')
def delete():
    local('rm testfile')


@reversible(_with='rename2')
def rename():
    local('mv testfile.bkp testfile.old')


@reversible(_with='rename')
def rename2():
    local('mv testfile.old testfile.bkp')


@reversible(_with='nonexisting')
def rename3():
    local('mv testfile.old testfile.bkp')


@void
def recover():
    local('cp testfile.bkp testfile')


@dontreplay
def fail1():
    local('ls kjhkjhkjhj')


@task
def test1():
    """should be rollbackable"""
    create()
    backup()
    delete()
    rename()


@task
def test2():
    """ Should fail because no savepoint"""
    create()
    delete()
    rename()


@task
def test3():
    """ Should fail because reversible function without reverse function"""
    create()
    backup()
    rename3()
