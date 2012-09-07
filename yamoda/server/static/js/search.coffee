query_links = $(".query_popover")
query_links.each((index, link) ->
  text = link.text.replace(/,/g, "<br>")
  $("#query_" + index).popover {
    content: text
    title: "Click to insert #" + (index + 1)
    html: true
    trigger: "hover"
  }
)
logg = yamoda.get_logger("yamoda.search")

self = yamoda.search = {
  thisorthat: ->
    logg.info("this", this)

  insert_query: (row) ->
    newtext = $("#query_" + row).text().replace(/,/g, "\n")
    $("#query_input").val(newtext)
    return

  run_query: (row) ->
    logg.debug("called run_query")
    self.insert_query(row)
    $("#query_form").trigger("submit")
    return

  toggle_all_checkboxes: (master_checkbox, $slave_checkboxes) ->
    logg.debug("called toggle_all_checkboxes")
    if master_checkbox.checked
      $slave_checkboxes.attr("checked", "checked")
    else
      $slave_checkboxes.removeAttr("checked")
    return

  request_help_content: (url) ->
    $.get(url, (helptext) ->
      logg.info("got helptext for", url)
      $("#help-content").html(helptext)
    )

  del_queries: ->
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
}

yamoda.logg.info("yamoda.search loaded")

