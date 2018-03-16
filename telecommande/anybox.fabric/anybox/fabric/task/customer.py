from anybox.fabric.api import task
from anybox.fabric import systemuser


@task
def getlist():
    """ Display the list of customers
    """
    systemuser.getlist()


@task
def disk_usage():
    """Disk usage of the user account"""
    systemuser.disk_usage()


@task(depends='method')
def create():
    """Create the customer account"""
    raise NotImplementedError  # see _customer.py


@task(depends='system')
def destroy():
    """Completely destroy a customer account and data. Asks confirmation"""
    raise NotImplementedError
