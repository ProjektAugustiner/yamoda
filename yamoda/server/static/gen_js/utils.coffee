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
filter_init_vals = []

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
  $boxes.each((i) ->
    column_num = $(this).data("column_num")
    filter_init_vals[column_num] = this.value
    return
  )
  $boxes.keyup((i) ->
    column_num = $(this).data("column_num")
    logg.debug("input keyup, index", column_num, "value", this.value, i)
    dtable.fnFilter(this.value, column_num)
    return
  )
  $boxes.focus((i) ->
    logg.debug("input focus")
    $this = $(this)
    if $this.hasClass("filter-init")
      $this.removeClass("filter-init")
      this.value = ""
    return
  )
  $boxes.blur((i) ->
    column_num = $(this).data("column_num")
    logg.debug("input blur")
    if this.value == ""
      $boxes.addClass("filter-init")
      this.value = filter_init_vals[column_num]
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
