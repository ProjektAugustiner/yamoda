logg = yamoda.get_logger("yamoda.queryhistory")

asInitVals = []

$(document).ready(() ->
    logg.debug("activating dataTable for queryhistory_table")
    oTable = $("#queryhistory_table").dataTable(
        bStateSave: true
        sDom: "zflrtpi"
        oLanguage:
            sSearch: "Search all columns"
    )
    $("tfoot input").keyup((i) ->
        logg.debug("input keyup")
        oTable.fnFilter(this.value, $("tfoot input").index(this))
        return
    )
    $("tfoot input").each((i) ->
        asInitVals[i] = this.value
        return
    )
    $("tfoot input").focus((i) ->
        logg.debug("input focus")
        if this.className == "search_init"
            this.className = ""
            this.value = ""
        return
    )
    logg.info("before keyup")
    $("tfoot input").blur((i) ->
        logg.debug("input blur")
        if this.value == ""
            this.className = "search_init"
            this.value = asInitVals[$("tfoot input").index(this)]
        return
    )
    return
)


query_links = $(".query_popover")
query_links.each((index, link) ->
  text = link.text.replace(/,/g, "<br>")
  $("#query_" + index).popover {
    content: text
    title: "Query #" + (index + 1)
    html: true
    trigger: "hover"
    placement: "top"
  }
)

that = yamoda.queryhistory = {
  insert_query: (row, target$) ->
    newtext = $("#query_" + row).text().replace(/,/g, "\n")
    target$.val(newtext)
    return

  run_query: (row, target$, form$) ->
    logg.debug("called run_query")
    that.insert_query(row, target$)
    form$.trigger("submit")
    return

  toggle_all_checkboxes: (master_checkbox, slave_checkboxes$) ->
    logg.debug("called toggle_all_checkboxes")
    if master_checkbox.checked
      slave_checkboxes$.attr("checked", "checked")
    else
      slave_checkboxes$.removeAttr("checked")
    return

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

yamoda.logg.info("yamoda.queryhistory loaded")

