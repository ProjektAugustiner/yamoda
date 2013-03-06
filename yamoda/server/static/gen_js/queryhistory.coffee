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
query_rename_template = undefined


###-- module functions --###

setup_query_history_table = ->
  # Initialize jquery.dataTables and some helpers for the filter boxes.
  logg.info("setup_query_history_table called")
  # register handlers for selecting

  yamoda.utils.setup_datatable_selection($("#query_history_table"))

  # actions for selection menu

  $("#delete_query_action").click ->
    yamoda.queryhistory.del_queries()
    return
    
  $("#toggle_favorite_query_action").click ->
    yamoda.queryhistory.toggle_favorite_queries()
    return

  $("#rename_query_action").click ->
    create_rename_queries_dialog()
    return
  $table = $("#query_history_table")
  dtable = yamoda.utils.setup_datatable($table,
    aoColumnDefs: [
      {asSorting: [], aTargets: [5, 6]}
    ]
  )

  $("#query_rename_save").click ->
    query_id_to_name = {}
    query_ids = []
    query_names = []
    $("#query_rename_form .query-name-input").each (i, e) ->
      $input = $(e)
      query_id_to_name[$input.data("query_id")] = $input.val()
      query_ids.push($input.data("query_id"))
      query_names.push($input.val())
    logg.info("renaming queries", query_id_to_name)
    $.ajax(
      type: 'POST',
      url: yamoda.queryhistory.rename_queries_url
      data:
        query_id_to_name: JSON.stringify(query_id_to_name)
        query_ids: query_ids
        query_names: query_names
      success: ->
        logg.info("renaming queries finished")
        send_query_history_request()
        $("#query_rename_modal").modal("hide")
        return
    )
    return

  # move action button to right table toolbar
  $("#query_history_table_wrapper .datatables-bottom-right-bar").append($("#query_action").remove())

  yamoda.utils.setup_column_filter_boxes($("#query_history_table tfoot input"), dtable)

  # setup popovers which show the query string in formatted form (newlines).
  query_texts = $(".query-text")
  query_texts.each((index, query) ->
    text = $(query).text().replace(/,/g, "<br>")
    $("#query_" + index).popover {
      content: text
      title: "Query #" + (index + 1) + " (click to run)"
      html: true
      trigger: "hover"
      placement: "top"
    }
  )

  return # end of setup_query_history_table, sorry for the long function (TODO refactor) ;)


insert_query = (row) ->
  # Insert query from history into query box.
  # :param row: table row from which the query is taken.
  query_string = $("#query_" + row).text().replace(/,/g, "\n")
  query_name = $("#query_name_" + row).text()
  $("#query_input").val(query_string)
  $("#query_name_input").val(query_name)
  return


run_query = (row) ->
  # insert query from history into query box and run it.
  # :param row: table row from which the query is taken.
  logg.debug("called run_query")
  that.insert_query(row)
  # kill remaining popovers
  $(".popover").remove()
  yamoda.search.send_query_request(false)
  return


get_selected_query_rows = ->
  $("#query_history_table>tbody>tr.row-selected")


get_selected_query_ids = ->
  get_selected_query_rows().children("td.query-id").map( (i, e) ->
    $(e).text()).get()


get_selected_query_names = ->
  get_selected_query_rows().children("td.query-name").map( (i, e) ->
    $(e).text()).get()


create_rename_queries_dialog = ->
  $selected_rows = get_selected_query_rows()
  ids = get_selected_query_ids()
  names = get_selected_query_names()
  logg.info("ids to rename: ", ids)
  logg.info("old names: ", names)
  zipped = _.zip(ids, names)
  console.log(zipped)
  lines = (query_rename_template({id: p[0], query_name: p[1]}) for p in zipped)
  console.log(lines)
  for line in lines
    console.log("lines", line)
  html = lines.join(" ")
  $("#query_rename_form").html(html)


del_queries = ->
  # Get checked queries from table and delete them from query history
  # TODO: remove reloading whole page.
  logg.info("called del_queries")
  ids = get_selected_query_ids()
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


_send_toggle_favorite_queries_request = (ids) ->
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


toggle_favorite_queries = ->
  # Get checked queries from table and toggle favorite status for each
  # TODO: remove reloading whole page
  logg.info("called toggle_favorite_queries")
  ids = get_selected_query_ids()
  if not ids?
    return
  names = get_selected_query_names()
  ids_without_name = []
  for id, name of _.object(ids, names)
    if name == ""
      ids_without_name.push(id)

  logg.info("ids to toggle favorite state for: ", ids)
  logg.info("ids without names: ", ids_without_name)

  # do it if all names are available. If not, display an alert and do nothin.
  if ids_without_name.length == 0
    _send_toggle_favorite_queries_request(ids)
  else
    alert("Name missing for some queries: ##{ids_without_name}!\nFavorite queries need a name. Please set them before changing favorite status.")
  return


send_query_history_request = ->
  # AJAX update query history
  $.get(yamoda.search.query_history_url, (history_content) ->
    logg.info("got history content")
    $("#query_history_content").html(history_content)
    yamoda.queryhistory.setup_query_history_table()
  )
  return

###-- READY --###

$ ->
  # module def
  that = yamoda.queryhistory = yamoda.make_module(MODULE_NAME,
    insert_query: insert_query
    run_query: run_query
    del_queries: del_queries
    toggle_favorite_queries: toggle_favorite_queries
    setup_query_history_table: setup_query_history_table
    send_query_history_request: send_query_history_request
  )
  # other stuff to do
  logg = that.logg
  query_rename_template = _.template(
    '<div class="control-group">' +
    '<label class="control-label" for="query_rename_<%=id%>">Old: "<%=query_name%>"</label>' +
    '<div class="controls">' +
    '<input class="query-name-input input-large" type="text" value="<%=query_name%>" data-query_id="<%=id%>"> #<%=id%>' +
    '</div>' +
    '</div>'
  )
  setup_query_history_table()

  $('a[rel=tooltip]').tooltip()
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #



