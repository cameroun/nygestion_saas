from fabric.api import task
from .. import buildbot


@task
def create_builder():
    """Create a builder on the buildbot specified by the role"""
    buildbot.local_clone()
    buildbot.create_builder()


@task
def reconfig():
    """ Reconfigure the buildbot immediately with the new builder"""
    buildbot.reconfig()
