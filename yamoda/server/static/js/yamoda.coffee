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

###-- module functions --###

# create a new logging instance (for a module)
get_logger = (logger_name) ->
  logg.debug("getting logger with name " + logger_name)
  logger = log4javascript.getLogger(logger_name)
  ym_logg.addChild(logger)
  logger


# add constants for `module_name`
add_module_constants = (module_name, new_constants) ->
  logg.debug("add constants for", module_name, new_constants)
  if module_constants[module_name] is undefined
     constants = module_constants[module_name] = {}
  else
     constants = module_constants[module_name]

  for own key, value of new_constants
    constants[key] = value

  # immediately apply constants if module is already defined
  if yamoda[module_name]
    yamoda.apply_module_constants(yamoda[module_name])
    return null

  return constants


# apply stored constants to `module`
apply_module_constants = (module) ->
  constants = module_constants[module.YM_MODULE_NAME] or {}
  if constants
    logg.debug("applying constants for module", module.YM_MODULE_NAME, constants)
    for own key, value of constants
      module[key] = value
    module_constants[module.YM_MODULE_NAME] = {}
  return module


# add a handler function to which is run before yamoda module `module_name` is initialized
before_module_init = (module_name, func) ->
 if module_initializer[module_name] is undefined
    handlers = module_initializer[module_name] = []
 else
    handlers = module_initializer[module_name]

 handlers.push(func)


# run init functions for `module_name`
run_before_init = (module_name) ->
  handlers = module_initializer[module_name] or []
  f() for f in handlers
  return


###-- READY --###

$( () ->
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
    add_module_constants: add_module_constants
    apply_module_constants: apply_module_constants
    before_module_init: before_module_init
    run_before_init: run_before_init
  }

  # ok, all done
  logg.info("yamoda loaded")
  return
)
