# package that contains tasks

# We load the implementations first so they are registered
from . import _instance, _customer  # noqa
from .. import help, fabfile  # noqa
from ..api import env  # noqa
