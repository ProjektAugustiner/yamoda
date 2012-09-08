logg = yamoda.get_logger("yamoda.search")

query_results_shown = false
query_history_html = ""
query_results_html = "<h3>No results yet.</h3>"


change_to_query_history = () ->
  logg.info("change_to_query_history")
  if not query_results_shown
    return
  query_results_html = $("#bottom-content").html()
  $("#bottom-content").html(query_history_html)
  $("#query_results_btn").show()
  $("#query_history_btn").hide()
  $("#bottom-headline").text("Query History")
  query_results_shown = false


change_to_query_results = () ->
  logg.info("change_to_query_results")
  if query_results_shown or query_results_html == ""
    return
  query_history_html = $("#bottom-content").html()
  $("#bottom-content").html(query_results_html)
  $("#query_history_btn").show()
  $("#query_results_btn").hide()
  query_results_shown = true
  $("#bottom-headline").text("Query Results")


send_query_request = () ->
  logg.info("send query request")
  old_headline = $("#bottom-headline").text()
  $("#bottom-headline").text("Processing...")
  $.ajax(
    type: 'POST',
    url: yamoda.search.search_url
    data:
      query: $("#query_input").val()
      name:  $("#query_name_input").val()
      save_query: $("#save_query_checkbox").attr("checked")
    success: (data) ->
      logg.info("received query request answer")
      query_results_html = data
      $("#bottom-headline").text(old_headline)
      change_to_query_results()
  )


$(document).ready(() ->
  $("#query_history_btn").hide()
  $("#query_results_btn").hide()
  $('#query_form').submit(() ->
    show_results = $("input[name='show_results']:checked").val()
    if show_results == "newpage"
      return true
    else
      send_query_request()
      return false
  )
  return
)


yamoda.search = {
  request_help_content: (url) ->
    $.get(url, (helptext) ->
      logg.info("got helptext for", url)
      $("#help-content").html(helptext)
    )
  change_to_query_history: change_to_query_history
  change_to_query_results: change_to_query_results
}

yamoda.logg.info("yamoda.search loaded")

