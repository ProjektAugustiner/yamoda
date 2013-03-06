###
# datalist.coffee
# table view of data (not JQuery.datatable!)
#
# @author dpausp (Tobias Stenzel)
#
###

###-- private module vars --###

MODULE_NAME = "yamoda.datalist"
logg = undefined
that = undefined

###-- module functions --###


setup_datalist = ->
  yamoda.entry.sparkline_setup($("td.valuecolumn>.sparkline"))
  $table = $("#datalist_table")
  dtable = yamoda.utils.setup_datatable($table)
  logg.info("setting up 2d preview")
  yamoda.entry.fetch_2D_preview_images($("#datalist_table td.2d-preview"), "100%")
  $("#datalist_table_wrapper .datatables-bottom-right-bar").append($("#data_action").remove())
  yamoda.utils.setup_column_filter_boxes($("#datalist_table th.footer input.filter-input"), dtable)
  yamoda.utils.setup_datatable_selection($table)
  $('a[rel=tooltip]').tooltip()

  get_selected_data_rows = ->
    $("#datalist_table>tbody>tr.row-selected")

  get_selected_data_ids = ->
    get_selected_data_rows().children("td.data-id").map( (i, e) ->
      $(e).text()).get()

  $("#delete_data_action").click ->
    ids = get_selected_data_ids()
    logg.info("selected ids:", ids)
    if not ids
      logg.debug("nothing selected, doing nothing")
      return
    $("#data_action button").button("loading")
    $.ajax(
      url: yamoda.datalist.delete_url
      type: "POST"
      data:
        ids: ids
      success: ->
        window.location.reload()
      error: (xhr, st, err) ->
        $("#data_action button").button("reset")
        $("#actionerror").text(err).show()
    )

###-- READY --###

$ ->
  # module def
  that = yamoda.datalist = yamoda.make_module(MODULE_NAME,
    {}
  )
  # other stuff to do
  logg = that.logg
  setup_datalist()
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
