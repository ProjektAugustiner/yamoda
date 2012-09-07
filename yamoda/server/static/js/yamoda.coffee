root_logger = log4javascript.getRootLogger()

that = this.yamoda = {
  logg: (() ->
    ym_logger = log4javascript.getLogger("yamoda")
    console_layout = new log4javascript.PatternLayout("%r: %c| %m{1}%n")
    console_appender = new log4javascript.BrowserConsoleAppender()
    console_appender.setLayout(console_layout)
    root_logger.addChild(ym_logger)
    ym_logger.addAppender(console_appender)
    ym_logger
  )()

  get_logger: (logger_name) ->
    that.logg.info("getting logger with name " + logger_name)
    logger = log4javascript.getLogger(logger_name)
    that.logg.addChild(logger)
    logger
  }
