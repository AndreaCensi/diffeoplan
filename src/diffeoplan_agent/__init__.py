from .dp_agent_simple import *
from .dp_servo_simple import *




def jobs_comptests(context):
    from pkg_resources import resource_filename  # @UnresolvedImport
    dirname = resource_filename("diffeoplan_agent", "configs")

    from bootstrapping_olympics import get_boot_config
    from comptests import jobs_registrar

    boot_config = get_boot_config()
    boot_config.load(dirname)

    # unittests for boot olympics
    import bootstrapping_olympics.unittests
    j1 = jobs_registrar(context, boot_config)

    return j1


