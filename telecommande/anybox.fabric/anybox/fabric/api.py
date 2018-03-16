# coding: utf-8
from fabric.colors import magenta
from fabric.tasks import WrappedCallableTask
from datetime import datetime
import inspect
import importlib
import tempfile
from os import unlink
from os.path import exists, basename
from fabric.api import env, abort, task, warn, puts, prompt, sudo, run, get
from fabric.contrib.console import confirm
from fabric.utils import _AttributeDict
import reg
from . import detect

env.api = _AttributeDict()
env.reg = reg.Registry()

FAILED = '.fabfile.failed'
ROLLBACK = '.fabfile.rollback'


def ftime(t):
    return datetime.strptime(
        '20150526104912', '%Y%m%d%H%M%S').strftime('%X %x')


def dontreplay(func):
    """decorator to manually confirm already played function
    in case of previous failure
    """
    def wrapper(*args, **kw):
        current_step = '.'.join((func.__module__, func.__name__))
        try:
            last_failed = open(FAILED).read().strip().rsplit(':', 1)[1]
        except:
            last_failed = None
        if last_failed and current_step != last_failed.rsplit('.', 1)[1]:
            if not confirm(
                    'Last deployment failed and step "{}" was already run. '
                    'Run this step again anyway?'.format(current_step)):
                return ''  # FIXME
        with open(FAILED, 'w') as f:
            f.write('{date}:{mod}.{func}\n'.format(
                date=env.date, mod=func.__module__, func=func.__name__))
        result = func(*args, **kw)
        if exists(FAILED):
            unlink(FAILED)
        return result
    wrapper._undecorated = func
    return wrapper


def savepoint(restore=None):
    """ decorator to save backup information usable for rollback
    les savepoints servent à définir à la fois les trucs skippables pour
    aller plus vite si pas de risque et aussi à stocker l'info pour
    rollbacker, et à vérifier qu'il existe effectivement une fonction
    de rollback.  Ensuite on peut forcer le fait que le déploiement
    est rollbackable dans la conf du env.rollbackable=True ou
    backup=False TODO: empecher les arguments ?
    """
    def decorator(func):
        def wrapper(*args, **kw):
            if type(restore) not in (str, unicode):
                warn('Savepoint name on function {} should be a str or unicode'
                     .format(func.__name__))
                rollback()
            try:
                modname = func.__module__
                funcname = func.__name__
                getattr(importlib.import_module(modname), funcname)
            except:
                warn('Provided recover function {} cannot be imported'
                     .format(func.__name__))
                rollback()
            result = dontreplay(func)(*args, **kw)
            with open(ROLLBACK, 'a') as f:
                f.write('{date}:{mod}.{func}\n'.format(
                    date=env.date, mod=func.__module__, func=restore))
            env.savepoint = func.__name__
            return result
        wrapper._undecorated = func
        return wrapper
    return decorator


def irreversible(unless=''):
    """ Irreversible functions should always be preceded by a savepoint
    specified with 'unless'"""
    def decorator(func):
        def wrapper(*args, **kw):
            # First ensure that we have a previous savepoint
            if env.get('savepoint') != unless:
                warn('No savepoint run before irreversible function {}'
                     .format(func.__name__))
                rollback()
            result = dontreplay(func)(*args, **kw)
            return result
        wrapper._undecorated = func
        return wrapper
    return decorator


def reversible(_with=''):
    """decorator for tasks that may be rollbacked"""
    def decorator(func):
        def wrapper(*args, **kw):
            # First ensure we have a reverse function
            if not _with or type(_with) not in (str, unicode):
                warn('No reverse function defined for reversible function {}'
                     .format(func.__name__))
                rollback()
            res = dontreplay(func)(*args, **kw)
            with open(ROLLBACK, 'a') as f:
                f.write('{date}:{mod}.{func}\n'.format(
                    date=env.date, mod=func.__module__, func=_with))
            return res
        wrapper._undecorated = func
        return wrapper
    return decorator


def void(func):
    def wrapper(*args, **kw):
        return func(*args, **kw)
    wrapper._undecorated = func
    return wrapper


@task
def rollback():
    """Rollback function that rewinds up to the original state,
       by running the rollback functions"""
    try:
        rollback_lines = open(ROLLBACK).readlines()
    except Exception as e:
        abort('Could not read rollback information file {}: {}'
              .format(ROLLBACK, repr(e)))
    firstdate = None
    for rollback_line in reversed(rollback_lines):
        curdate, fullname = [s.strip() for s in rollback_line.rsplit(':')]
        if not firstdate:  # start the rollback
            if not confirm('Rollback last deployment run on {date}?'
                           .format(date=ftime(curdate)),
                           default=False):
                abort('Rollback cancelled')
            else:
                firstdate = curdate
        if curdate != firstdate:  # end because it's an older rollback
            puts('Rollback finished')
            break
        modname, funcname = fullname.rsplit('.', 1)
        module = importlib.import_module(modname)
        function = getattr(module, funcname)
        code = ''.join(inspect.getsourcelines(function._undecorated)[0][2:])
        if confirm(('Next rollback function is {function}. Code is:\n'
                    + magenta('{code}\n', bold=True) + 'Run?').format(
                        function=fullname, code=code), default=False):
            function()


def promptlist(msg, lst, multi=False):
    def validate_choice(input):
        for elt in input.split(','):
            if elt.strip() not in lst:
                raise Exception('"{}"" is not a valid dump entry'.format(elt.strip()))
        return input

    if multi:
        v = validate_choice
    else:
        v = lambda x: lst[lst.index(x)]
    return prompt(msg + ' ({})'.format(', '.join(lst)),
                  validate=v)


def remote_get(file_uri, dest_dir):
    """download remote_file to current host using a tempfile
    because of limited login
    """
    tmpfile = tempfile.mktemp(dir='')
    filename = basename(file_uri)
    run('scp "{file_uri}" "{tmpfile}"'
        .format(file_uri=file_uri, tmpfile=tmpfile))
    sudo('chown {account}: {tmpfile} '
         '&& mkdir -p {dest_dir} '
         '&& mv {tmpfile} {dest_dir}/{filename}'
         .format(account=env.account, tmpfile=tmpfile,
                 dest_dir=dest_dir, filename=filename),
         user='root')


def local_get(filepath):
    """ download a remote_file locally (standard fabric get doesnt work for us)
    """
    tmpfile = tempfile.mktemp(dir='/tmp/')
    sudo('cp -ra {filepath} {tmpfile} && chown -R {account}: {tmpfile}'
         .format(filepath=filepath, tmpfile=tmpfile, account=env.account))
    get(tmpfile, basename(filepath))
    sudo('rm -rf {}'.format(tmpfile))


def remote_put(source_file, dir_uri):
    """upload source_file from current host to dir_uri"""
    raise NotImplementedError


def multiline_question(question, example=''):
    puts('This is a multi-value option')
    if example:
        puts('Example of values: {} : '.format(example))
    values, line = [], ' '
    while line:
        if values:
            puts('\n    '.join(['\nCurrent values:'] + values))
        puts('Enter a new value, or "restart" or [Enter] if finished')
        line = prompt(question)
        if line:
            values.append(line)
        if line == 'restart':
            values = []
    return values


class CustomWrappedCallableTask(WrappedCallableTask):
    """Custom Task class to dispatch to the expected fabric task implementation
    """
    def __init__(self, callable, *a, **kw):
        self.depends = kw.get('depends')
        if isinstance(self.depends, basestring):
            self.depends = (self.depends,)
        super(CustomWrappedCallableTask, self).__init__(callable, *a, **kw)

    def run(self, *args, **kwargs):
        if self.depends:
            global env
            for depend in self.depends:
                # add the detected depend value in env.api (ex: system, method)
                setattr(env.api, depend,
                        env.api.get(depend) or getattr(detect, depend)())
            kwargs['lookup'] = env.reg.lookup()
        return self.wrapped(*args, **kwargs)

    __call__ = run


def env_api_getter(depend):
    def closure():
        global env
        return env.api.get(depend)
    return closure


def task(*args, **kwargs):
    """ Rewrite the fabric task decorator
    """
    invoked = bool(not args or kwargs)
    task_class = kwargs.pop("task_class", CustomWrappedCallableTask)
    if not invoked:
        func, args = args[0], ()

    def wrapper(func):
        # advertise fabfile-specific tasks in the help
        if func.__module__ == 'fabfile':
            func.__doc__ = '[SPECIFIC] ' + (func.__doc__ or '')
        # dispatch the generic task to its implementation, based on env.api
        if kwargs.get('depends'):
            depends = kwargs.get('depends', [])
            if isinstance(depends, basestring):
                depends = (depends,)
            predicates = [reg.match_key(depend, env_api_getter(depend))
                          for depend in depends]
            return task_class(reg.dispatch(*predicates)(func), *args, **kwargs)
        return task_class(func, *args, **kwargs)

    return wrapper if invoked else wrapper(func)


def implements(task, **kw):
    """decorator used to register an implementation of a generic task
    for a specific system, method, or other predicates
    """
    def decorator(func):
        global env
        try:
            env.reg.register_function(task, func, **kw)
        except AttributeError:
            raise Exception(
                'Found an implementation of task "{}" for {} but this task is '
                'missing the "depends" decorator argument. Or maybe you used '
                'fabric.api.task instead of anybox.fabric.api.task?'
                .format(task.wrapped.func_name, repr(kw.values())))

        def wrapper(*args, **kw):
            return func(*args, **kw)
        return wrapper
    return decorator
