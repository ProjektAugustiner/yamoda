###
# utils.coffee
# Various common utility functions
#
# @author dpausp (Tobias Stenzel)
#
###

###-- private module vars --###

MODULE_NAME = "utils"
logg = undefined
that = undefined
asInitVals = []

###-- module functions --###

setup_datatable = ($table, options) ->
  if $table.hasClass("initialized")
    logg.info("table already initialized, doing nothing")
    return
  logg.debug("activating dataTable for query_history_table")
  default_options =
    #sDom: "rltpi"
    bStateSave: false
    sPaginationType: "full_numbers"
    oLanguage:
      sSearch: "Search all columns: "
    resizable: true
  merged_options = $.extend(default_options, options)
  dtable = $table.addClass("initialized").dataTable(merged_options)
  if merged_options.resizable
    logg.debug("creating resizable column table")
    dtable.colResizable()
  return dtable


setup_column_filter_boxes = ($boxes, dtable) ->
  $boxes.keyup((i) ->
    logg.debug("input keyup, index", $boxes.index(this), "value", this.value)
    dtable.fnFilter(this.value, $boxes.index(this))
    return
  )
  $boxes.each((i) ->
    asInitVals[i] = this.value
    return
  )
  $boxes.focus((i) ->
    logg.debug("input focus")
    if $boxes.hasClass("search_init")
      $boxes.removeClass("search_init")
      this.value = ""
    return
  )
  $boxes.blur((i) ->
    logg.debug("input blur")
    if this.value == ""
      $boxes.addClass("search_init")
      this.value = asInitVals[$boxes.index(this)]
    return
  )


###-- READY --###

$ ->
  # module def
  that = yamoda.utils = yamoda.make_module(MODULE_NAME,
    setup_datatable: setup_datatable
    setup_column_filter_boxes: setup_column_filter_boxes
  )
  # other stuff to do
  logg = that.logg
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
