###
# search.coffee
# search related stuff
# 
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

YM_MODULE_NAME = "search"
logg = undefined
query_results_shown = false
query_history_html = ""
query_results_html = "<h3>No results yet.</h3>"


###-- module functions --###

change_to_query_history = () ->
  logg.info("change_to_query_history")
  query_results_html = $("#bottom-content").html()
  $("#bottom-content").html(query_history_html)
  $("#query_results_btn").show()
  $("#query_history_btn").hide()
  $("#bottom-headline").text("Query History")
  yamoda.queryhistory.initialize_if_needed()
  query_results_shown = false
  return


change_to_query_results = () ->
  logg.info("change_to_query_results")
  query_history_html = $("#bottom-content").html()
  $("#bottom-content").html(query_results_html)
  $("#query_history_btn").show()
  $("#query_results_btn").hide()
  query_results_shown = true
  $("#bottom-headline").text("Query Results")
  return


intercept_query_submit = () ->
  # unused
  show_results = $("input[name='show_results']:checked").val()
  logg.info("where to show results:", show_results)
  if show_results == "newpage"
    return true
  else
    send_query_request()
    return false


send_query_history_request = () ->
  # AJAX update query history
  $.get(yamoda.search.query_history_url, (history_content) ->
    logg.info("got history content")
    query_history_html = history_content
    if not query_results_shown
      $("#bottom-content").html(query_history_html)
      yamoda.queryhistory.initialize_if_needed()
  )
  return


send_query_request = () ->
  # send query to server and display results below the query box
  logg.info("send query request")
  show_results = $("input[name='show_results']:checked").val()
  logg.info("where to show results:", show_results)
  if show_results == "newpage"
    $("#query_form").submit()
    return

  $("#bottom-headline").text("Processing...")
  save_query = $("#save_query_checkbox").attr("checked")
  $.ajax(
    type: 'POST',
    url: yamoda.search.search_url
    data:
      query: $("#query_input").val()
      name:  $("#query_name_input").val()
      save_query: save_query
    success: (data) ->
      logg.info("received query request answer")
      query_results_html = data
      change_to_query_results()
      # refresh history in background
      send_query_history_request()
      return
    error: () ->
      $("#bottom_headline").text("Error!")
      return
  )


send_query_save_request = () ->
  # don't run query, just save it and refresh the history
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

$(document).ready(() ->
  if yamoda[YM_MODULE_NAME]
    yamoda.logg.warn(YM_MODULE_NAME, "already defined, skipping!")
    return
  # module init
  logg = yamoda.get_logger("yamoda.search")
  yamoda.run_before_init(YM_MODULE_NAME)

  # hide switch buttons
  # XXX: not very clever...
  $("#query_history_btn").hide()
  $("#query_results_btn").hide()

  # module def
  module = yamoda.search = {
    YM_MODULE_NAME: YM_MODULE_NAME
    request_help_content: (url) ->
      # request content for a tab in the query help box
      # :param url: GET URL for needed helptext 
      $.get(url, (helptext) ->
        logg.info("got helptext for", url)
        $("#help-content").html(helptext)
      )
    change_to_query_history: change_to_query_history
    change_to_query_results: change_to_query_results
    send_query_request: send_query_request
    send_query_save_request: send_query_save_request
  }
  
  yamoda.apply_module_constants(module)

  #ok, all done
  yamoda.logg.info("yamoda.search loaded")
  return
)



