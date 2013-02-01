###
# yamoda.coffee
# root module for YAMODA
#
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

logg = ym_logg = undefined
that = this
module_initializer = {}
module_constants = {}
defined_modules = {}


###-- module functions --###

get_logger = (logger_name) ->
  # create a new logging instance (for a module)
  # :param logger_name: name for the logger, will also be printed with each
  # log message
  logg.debug("getting logger with name", logger_name)
  logger = log4javascript.getLogger(logger_name)
  ym_logg.addChild(logger)
  logger


is_module_defined = (module_name) ->
  # :param module_name: module name like 'yamoda.testmodule'
  if module_name of defined_modules
    true
  else
    false


add_module_constants = (module_name, new_constants) ->
  # Add constants for `module_name`
  # :param module_name: module name like 'yamoda.testmodule'
  # :param new_constants: object with constants to add
  logg.debug("add constants for", module_name, new_constants)
  if module_constants[module_name] is undefined
    constants = module_constants[module_name] = {}
  else
    constants = module_constants[module_name]

  for own key, value of new_constants
    constants[key] = value

  # immediately apply constants if module is already defined
  if module_name of defined_modules
    yamoda.apply_module_constants(defined_modules[module_name])
    return null
  else
    return constants


before_module_init = (module_name, func) ->
  # Add a function to module initializer list.
  # :param module_name: module name like 'yamoda.testmodule'
  # :param func: function to run before module `module_name` is created
  if module_initializer[module_name] is undefined
    handlers = module_initializer[module_name] = []
  else
    handlers = module_initializer[module_name]
  handlers.push(func)


run_before_init = (module_name) ->
  # Run init functions for module
  # :param module_name:
  handlers = module_initializer[module_name] or []
  f() for f in handlers
  return


apply_module_constants = (module) ->
  # apply stored constants to `module`
  # :param module: module object created by `make_module`
  constants = module_constants[module.MODULE_NAME] or {}
  if constants
    logg.debug("applying constants for module", module.MODULE_NAME,
      constants)
    for own key, value of constants
      module[key] = value
    module_constants[module.MODULE_NAME] = {}
  return module


make_module = (module_name, attributes) ->
  # Make module and return it.
  # 1. Run init functions for `module_name`
  # 2. Create module
  # 3. Apply module constants
  # :param module_name: name like 'yamoda.testmodule', will be included in
  # module as MODULE_NAME
  # :param attributes: object, attributes will be included in module
  already_defined_module = defined_modules[module_name]
  if already_defined_module
    yamoda.logg.warn(module_name, "already defined, skipping!")
    return already_defined_module
  else
    logger = get_logger(module_name)
    run_before_init(module_name)
    module = attributes
    module.MODULE_NAME = module_name
    module.logg = logger
    apply_module_constants(module)
    defined_modules[module_name] = module
    logger.info(module_name, "loaded")
    return module


###-- READY --###

$ ->
  if that.yamoda
    console.log("yamoda already defined, skipping!")
    return
  # module init
  root_logger = log4javascript.getRootLogger()
  ym_logg = log4javascript.getLogger("yamoda")
  console_layout = new log4javascript.PatternLayout("%r: %c| %m{1}%n")
  console_appender = new log4javascript.BrowserConsoleAppender()
  console_appender.setLayout(console_layout)
  root_logger.addChild(ym_logg)
  ym_logg.addAppender(console_appender)
  logg = ym_logg

  logg.info("yamoda init")

  # module def
  yamoda = that.yamoda = {
    # logg is used as common logger for code without own logging instance
    logg: logg
    get_logger: get_logger
    is_module_defined: is_module_defined
    add_module_constants: add_module_constants
    apply_module_constants: apply_module_constants
    before_module_init: before_module_init
    run_before_init: run_before_init
    make_module: make_module
  }

  # ok, all done
  logg.info("yamoda root module loaded")
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
