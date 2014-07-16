__version__ = '1.0'
__docformat__ = 'restructuredtext'

from conf_tools.utils import col_logging  # colored logging

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .utils import *  # XXX
from .configuration import *
from .interfaces import *
from . import library
from .programs import *

# 
# def get_comptests():
#     from . import unittests 
#     from comptests import get_comptests_app
#     app = get_comptests_app(get_dp_config())
#     return [app]


def jobs_comptests(context):
    from . import unittests
    from comptests import jobs_registrar
    config = get_dp_config()
    return jobs_registrar(context, config)
