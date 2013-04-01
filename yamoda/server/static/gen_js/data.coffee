###
# data.coffee
# 
#
# @author dpausp (Tobias Stenzel)
#
###

###-- private module vars --###

MODULE_NAME = "data"
logg = undefined
that = undefined

selected_rows = []


###-- module functions --###

plot_current_selection = ->
  entry_x_url = $(selected_rows[0]).find(".url-column>a").attr("href")
  entry_y_url = $(selected_rows[1]).find(".url-column>a").attr("href")
  height = $(window).height() * 0.45
  yamoda.logg.info("new height of plot", height)
  $("#plot .plot-area").height(height)
  yamoda.entry.get_two(entry_x_url, entry_y_url, (ex, ey) ->
    yamoda.entry.plot_1D_1D(ex, ey, $("#plot"))
    selected_rows = []
    $("#entrytable tr").removeClass("info").removeClass("warning").removeClass("row-selected")
  )
  return


###-- READY --###

$ ->
  # module def
  that = yamoda.data = yamoda.make_module(MODULE_NAME, {})
  # other stuff to do
  logg = that.logg

  yamoda.entry.sparkline_setup($("#entrytable td.valuecolumn .sparkline"))
  dtable = yamoda.utils.setup_datatable($("#entrytable"),
    resizable: false
    aaSorting: [[7, "desc"], [5, "asc"], [1, "asc"]]
  )
  yamoda.utils.setup_column_filter_boxes($("#entrytable th.footer input.filter-input"), dtable)
  # 2D preview image setup
  yamoda.entry.fetch_2D_preview_images($("#entrytable td.2d-preview"), "35%")
  yamoda.entry.flot_setup($("#plot"))
  #$('a[rel=tooltip]').tooltip()

  $("#plot_btn").click(plot_current_selection)

  # row (entry) selection logic. 
  # The first selected entry will be used as data source for the x-axis, the second for y
  $("#entrytable tr").click ->
    $this = $(this)
    url = $this.find(".url-column>a").attr("href")
    if $this.children(".1d").length == 0
      return
    if $this.hasClass("row-selected")
      yamoda.logg.info("unselected", url)
      $this.removeClass("row-selected info warning")
      selected_rows = _.without(selected_rows, this)
    else
      yamoda.logg.info("selected", url)
      $this.addClass("row-selected")
      if _.size(selected_rows) == 2
        $(selected_rows[0]).removeClass("row-selected info warning")
        selected_rows = _.tail(selected_rows)
      selected_rows.push(this)
    if selected_rows.length == 0
      $("#plot_btn").addClass("disabled")
    else if selected_rows.length == 1
      $("#plot_btn").addClass("disabled")
      $(selected_rows[0]).removeClass("info").addClass("warning")
    else if selected_rows.length == 2
      $("#plot_btn").removeClass("disabled")
      $(selected_rows[0]).removeClass("info").addClass("warning")
      $(selected_rows[1]).removeClass("warning").addClass("info")
    return
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
