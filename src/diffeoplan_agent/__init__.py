from .dp_agent_simple import *
from .dp_servo_simple import *




def jobs_comptests(context):
    
    config_dirs = [
        'diffeoplan_agent.configs',
    ]

    GlobalConfig.global_load_dirs(config_dirs)

    from bootstrapping_olympics import get_boot_config
    from comptests import jobs_registrar

    # unittests for boot olympics
    import bootstrapping_olympics.unittests
    jobs_registrar(context, boot_config)


