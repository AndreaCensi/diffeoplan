from quickapp.quick_multi_app import QuickMultiCmdApp
from conf_tools import GlobalConfig


class DP(QuickMultiCmdApp):
    """         
        See the manual at 

            http://github.com/AndreaCensi/surf12adam/wiki/
        
    """
    
    cmd = 'dp'
    
    def define_multicmd_options(self, options):
        options.add_flag('dummy', help='workaround for a bug')
        options.add_string('directory', short='d',
                                help='Configuration directory',
                               default='default')
  
    def initial_setup(self):
        options = self.get_options()
        # Load configurations for all modules
        self.info('loading config: %r' % options.directory)
        GlobalConfig.global_load_dir(options.directory)
            
dpmain = DP.get_sys_main()    


# 
#     
# def dp(arguments):
#     usage = substitute(usage_pattern, commands_list=commands_list,
#                        cmd=MAIN_CMD_NAME)
# 
#     parser = MyOptionParser(prog=MAIN_CMD_NAME, usage=usage)
#     parser.disable_interspersed_args()
# 
#     parser.add_option("--contracts", default=False, action='store_true',
#                       help="Activate PyContracts (disabled by default)")
# 
#     parser.add_option("--profile", default=False, action='store_true',
#                       help="Use Python profiler")
# 
#     parser.add_option("-d", "--directory", default="default:.",
#                       help="Configuration directory")
# 
#     (options, args) = parser.parse_args(arguments)
# 
#     if not options.contracts:
#         logger.warning('PyContracts disabled for speed. Use --contracts to activate.')
#         contracts.disable_all()
# 
#     if not args:
#         msg = ('Please supply a command.\nAvailable commands:\n%s' % commands_list)
#         raise UserError(msg)
# 
#     cmd = args[0]
#     cmd_args = args[1:]
# 
#     if not cmd in Storage.commands:
#         msg = ('Unknown command %r. Available: %s.' % 
#                (cmd, ", ".join(Storage.commands.keys())))
#         raise UserError(msg)
# 
#     confdir = options.directory
#     config = DiffeoplanConfigMaster()
#     config.load()
#     if confdir is not None:
#         config.load(confdir)
#     
#     set_current_config(config)
# 
#     function = Storage.commands[cmd]
#     usage = function.short_usage 
#     parser = CmdOptionParser(prog='%s %s' % (MAIN_CMD_NAME, cmd), usage=usage,
#                              args=cmd_args)
#     parser.enable_interspersed_args()
#     
#     def go():
#         return function(config, parser)
# 
#     if not options.profile:
#         go()
#     else:
#         logger.warning('Note: the profiler does not work when using '
#                        'parallel execution. (use "make" instead of "parmake").')
#         import cProfile
#         cProfile.runctx('go()', globals(), locals(), 'dp_prof')
#         import pstats
#         p = pstats.Stats('dp_prof')
#         n = 30
#         p.sort_stats('cumulative').print_stats(n)
#         p.sort_stats('time').print_stats(n)
# 
# def dpmain():
#     exceptions_no_traceback = (UserError, ConfToolsException)
#     return wrap_script_entry_point(dp, logger,
#                         exceptions_no_traceback=exceptions_no_traceback)


