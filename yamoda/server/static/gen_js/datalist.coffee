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

get_selected_data_rows = ->
  $("#datalist_table>tbody>tr.row-selected")


get_selected_data_ids = ->
  get_selected_data_rows().children("td.data-id").map( (i, e) ->
    $(e).text()).get()


setup_delete_data_action_handler = ->
  logg.debug("adding handler to delete action")
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
  return


setup_create_set_from_data_action_handler = ->
  logg.debug("adding handler to create set from data action")
  $("#create_set_from_data_action").click ->
    ids = get_selected_data_ids()
    logg.info("selected ids", ids)
    if not ids
      logg.debug("nothing selected, doing nothing")
      return
    $("#create_set_for_data_modal input[name=data_ids]").val(ids)
    $("#create_set_for_data_modal p.data-ids").text("Data # to add: " + ids).show()
    return
  return


setup_data_click_handler = ->
  logg.debug("setup_data_click_handler")
  #: Save current data sort order as session cookie,
  #: used for previous / next buttons on server side.
  $(".data-link").click ->
    dtable_f = $.fn.dataTable.settings.filter (s) -> s.nTable.id == "datalist_table"
    dtable = dtable_f[0].oInstance
    data_order = dtable.$(".data-id").map( (i, e) ->
      $(e).text()).get()
    $.cookie("data_order", data_order, path: "/")
    $.cookie("from_set", that.from_set, path: "/")
    logg.debug("saved cookie data:", $.cookie("data_order"), $.cookie("from_set"))
    return
  return


setup_datalist = ->
  logg.debug("setup_datalist")
  #: Misc setup needed for the datalist.
  yamoda.entry.sparkline_setup($("td.valuecolumn>.sparkline"))
  $table = $("#datalist_table")
  dtable = yamoda.utils.setup_datatable($table,
    bStateSave: true
  )
  logg.info("setting up 2d preview")
  yamoda.entry.fetch_2D_preview_images($("#datalist_table td.2d-preview"), "100%")
  $("#datalist_table_wrapper .datatables-bottom-right-bar").append($("#data_action").remove())
  yamoda.utils.setup_column_filter_boxes($("#datalist_table th.footer input.filter-input"), dtable)
  yamoda.utils.setup_datatable_selection($table)
  #$('a[rel=tooltip]').tooltip()
  return

###-- READY --###

$ ->
  # module def
  that = yamoda.datalist = yamoda.make_module(MODULE_NAME,
    {}
  )
  # other stuff to do
  logg = that.logg
  setup_datalist()
  setup_delete_data_action_handler()
  setup_create_set_from_data_action_handler()
  setup_data_click_handler()
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
