$ = jQuery
$.fn.testplugin = (opts) ->
  defaults = {}
  options = $.extend(defaults, opts or {})
  return this.each ->
    console.log("plugin hello")
    return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #

