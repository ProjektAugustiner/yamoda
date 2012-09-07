logg = yamoda.get_logger("yamoda.search")

$(document).ready(() ->
  $("#query_history_btn").hide()
  #    $("#query_results_btn").hide()
  return
)

query_results_shown = false
query_history_html = ""
query_results_html = "<b>here be dragons...</b>"

that = yamoda.search = {
  thisorthat: ->
    logg.info("this", this)

  request_help_content: (url) ->
    $.get(url, (helptext) ->
      logg.info("got helptext for", url)
      $("#help-content").html(helptext)
    )

  change_to_query_history: () ->
    logg.info("change_to_query_history")
    if not query_results_shown
      return
    query_results_html = $("#bottom-content").html()
    $("#bottom-content").html(query_history_html)
    $("#query_results_btn").show()
    $("#query_history_btn").hide()
    $("#bottom-headline").text("Query History")
    query_results_shown = false

  change_to_query_results: () ->
    logg.info("change_to_query_results")
    if query_results_shown or query_results_html == ""
      return
    query_history_html = $("#bottom-content").html()
    $("#bottom-content").html(query_results_html)
    $("#query_history_btn").show()
    $("#query_results_btn").hide()
    query_results_shown = true
    $("#bottom-headline").text("Query Results")

}

yamoda.logg.info("yamoda.search loaded")

