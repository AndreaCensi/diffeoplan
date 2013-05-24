__version__ = '1.0'
__docformat__ = 'restructuredtext'

from conf_tools.utils import col_logging  # colored logging

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from . import utils
from .configuration import *
from .interfaces import *
from . import library
from .programs import *
