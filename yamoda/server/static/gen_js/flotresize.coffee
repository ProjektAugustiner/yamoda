options = { } # no options

init = (plot) ->
  on_resize = ->
    placeholder = plot.getPlaceholder()
    yamoda.logg.info("resizing plot to x", placeholder.width(), "y ", placeholder.height())
    # somebody might have hidden us and we can't plot
    # when we don't have the dimensions
    if (placeholder.width() == 0 || placeholder.height() == 0)
      return

    plot.resize()
    plot.setupGrid()
    plot.draw()
    return
  
  bindEvents = (plot, eventHolder) ->
    placeholder = $(plot.getPlaceholder())
    yamoda.logg.debug("plotdisplay container: ", placeholder[0].id)
    yamoda.logg.info($._data(placeholder[0], "events"))
    placeholder.resize(on_resize)
    yamoda.logg.info($._data(placeholder[0], "events"))
    return
  

  shutdown = (plot, eventHolder) ->
    placeholder = $(plot.getPlaceholder())
    yamoda.logg.debug("unbinding from ", placeholder[0].id)
    placeholder.unbind("resize", on_resize)
    return
  
  
  plot.hooks.bindEvents.push(bindEvents)
  plot.hooks.shutdown.push(shutdown)

$.plot.plugins.push(
  init: init
  options: options
  name: 'resizeyamoda'
  version: '1.0'
)

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #


