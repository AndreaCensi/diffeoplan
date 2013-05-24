from .script_utils import *
from .lenient_option_parser import *
from .matrices import *
from .memoization import *
from .with_internal_log import * 
from .resampling_signal import *

from numpy.testing.utils import assert_allclose
from bootstrapping_olympics.interfaces.with_internal_log import BootWithInternalLog
import warnings

warnings.warn('remove dependency')
WithInternalLog = BootWithInternalLog
