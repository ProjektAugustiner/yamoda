###
# search.coffee
# search related stuff
#
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

MODULE_NAME = "yamoda.search"
logg = undefined
query_results_shown = false


###-- module functions --###

request_help_content = (url) ->
  # Request content for a tab in the query help box
  # :param url: GET URL for needed helptext
  $.get(url, (helptext) ->
    logg.info("got helptext for", url)
    $("#help_content").html(helptext)
    return
  )
  return

change_to_query_history = ->
  logg.info("change_to_query_history")
  $("#query_results_content").hide()
  $("#query_history_content").show()
  $("#query_results_btn").show()
  $("#query_history_btn").hide()
  $("#action_dropdown").dropdown()
  $("#bottom_headline").text("Query History")
  query_results_shown = false
  return


change_to_query_results = ->
  logg.info("change_to_query_results")
  $("#query_results_content").show()
  $("#query_history_content").hide()
  $("#query_history_btn").show()
  $("#query_results_btn").hide()
  query_results_shown = true
  $("#bottom_headline").text("Query Results")
  return


send_query_history_request = ->
  # AJAX update query history
  $.get(yamoda.search.query_history_url, (history_content) ->
    logg.info("got history content")
    $("#query_history_content").html(history_content)
    yamoda.queryhistory.setup_query_history_table()
  )
  return


send_query_request = (save_query=true) ->
  # Send query to server and display results below the query box.
  logg.info("send query request")
  show_results = $("input[name='show_results']:checked").val()
  logg.info("where to show results:", show_results)
  $("#bottom_headline").text("Processing...")
  $.ajax(
    type: 'POST',
    url: yamoda.search.search_url
    data:
      query: $("#query_input").val()
      name:  $("#query_name_input").val()
      save_query: save_query
    success: (query_result) ->
      logg.info("received query request answer")
      $("#query_results_content").html(query_result)
      change_to_query_results()
      # refresh history in background
      send_query_history_request()
      return
    error: () ->
      $("#bottom_headline").text("Server Error! Please try again.")
      return
  )


send_query_save_request = ->
  # Don't run query, just save it and refresh the history
  logg.info("send query save request")
  $.ajax(
    type: 'POST',
    url: yamoda.search.save_query_url
    data:
      query: $("#query_input").val()
      name:  $("#query_name_input").val()
    success: (msg) ->
      logg.info("received query save request answer")
      $("#main_msg_area").html(msg)
      # refresh history
      send_query_history_request()
  )
  return


###-- READY --###

$ ->
  # module def
  that = yamoda.search = yamoda.make_module(MODULE_NAME,
    request_help_content: request_help_content
    change_to_query_history: change_to_query_history
    change_to_query_results: change_to_query_results
    send_query_request: send_query_request
    send_query_save_request: send_query_save_request
  )
  # other stuff to do
  logg = that.logg
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #


