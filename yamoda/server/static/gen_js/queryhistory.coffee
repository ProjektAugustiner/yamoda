###
# queryhistory.coffee
# query history related stuff
#
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

MODULE_NAME = "yamoda.queryhistory"
logg = undefined
asInitVals = []
that = undefined


###-- module functions --###

setup_query_history_table = ->
  # Initialize jquery.dataTables and some helpers for the filter boxes.
  $table = $("#query_history_table")
  dtable = yamoda.utils.setup_datatable($table,
    aoColumnDefs: [
      {asSorting: [], aTargets: [5, 6]}
    ]
  )
  yamoda.utils.setup_column_filter_boxes($("#query_history_table tfoot input"), dtable)

  # setup popovers which show the query string in formatted form (newlines).
  query_links = $(".query_popover")
  query_links.each((index, link) ->
    text = link.text.replace(/,/g, "<br>")
    $("#query_" + index).popover {
      content: text
      title: "Query #" + (index + 1) + " (click to run)"
      html: true
      trigger: "hover"
      placement: "top"
    }
  )
  return


insert_query = (row) ->
  # Insert query from history into query box.
  # :param row: table row from which the query is taken.
  query_string = $("#query_" + row).text().replace(/,/g, "\n")
  query_name = $("#query_name_" + row).text()
  $("#query_input").val(query_string)
  $("#query_name_input").val(query_name)
  $("#favorite_checkbox").removeAttr("checked")
  return


run_query = (row) ->
  # insert query from history into query box and run it.
  # :param row: table row from which the query is taken.
  logg.debug("called run_query")
  that.insert_query(row)
  # kill remaining popovers
  $(".popover").remove()
  $("#save_query_checkbox").removeAttr("checked")
  yamoda.search.send_query_request(false)
  return


toggle_all_checkboxes = (master_checkbox, slave_checkboxes$) ->
  # toggle some "slave" checkboxes depending on the state of another
  # "master" checkbox.
  # :param master_checkbox: box which determines the toggle state.
  # :param slave_checkboxes: list of boxes to toggle.
  logg.debug("called toggle_all_checkboxes")
  if master_checkbox.checked
    slave_checkboxes$.attr("checked", "checked")
  else
    slave_checkboxes$.removeAttr("checked")
  return


del_queries = ->
  # Get checked queries from table and delete them from query history
  # TODO: remove reloading whole page.
  logg.info("called del_queries")
  ids = $.map($(".querycheck:checked"), (el) ->
    el.id.substring(6)
  )
  logg.info("ids to delete: ", ids)
  if not ids?
    return
  $("actionbutton button").button("loading")
  logg.info("sending request to", that.del_queries_url)
  $.ajax(
    type: "POST"
    url: that.del_queries_url
    data:
      ids: ids
    success: (data, st, xhr) ->
      window.location.reload()
      $("checkbox_all").removeAttr("checked")
    error: (xhr, st, err) ->
      logg.error("error in delete callback: ", err)
      $("actionbutton button").button("reset")
      $("actionerror").text(err).show()
  )
  return


toggle_favorite_queries = ->
  # Get checked queries from table and toggle favorite status for each
  # TODO: remove reloading whole page
  logg.info("called toggle_favorite_queries")
  ids = $.map($(".querycheck:checked"), (el) ->
    el.id.substring(6)
  )
  logg.info("ids to toggle favorite state for: ", ids)
  if not ids?
    return
  $("actionbutton button").button("loading")
  logg.info("sending request to", that.toggle_favorite_queries_url)
  $.ajax(
    type: "POST"
    url: that.toggle_favorite_queries_url
    data:
      ids: ids
    success: (data, st, xhr) ->
      window.location.reload()
      $("checkbox_all").removeAttr("checked")
    error: (xhr, st, err) ->
      logg.error("error in favorite callback: ", err)
      $("actionbutton button").button("reset")
      $("actionerror").text(err).show()
  )
  return


###-- READY --###

$ ->
  # module def
  that = yamoda.queryhistory = yamoda.make_module(MODULE_NAME,
    insert_query: insert_query
    run_query: run_query
    toggle_all_checkboxes: toggle_all_checkboxes
    del_queries: del_queries
    toggle_favorite_queries: toggle_favorite_queries
    setup_query_history_table: setup_query_history_table
  )
  # other stuff to do
  logg = that.logg
  setup_query_history_table()
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #

