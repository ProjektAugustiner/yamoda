###
# queryhistory.coffee
# query history related stuff
#
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

YM_MODULE_NAME = "queryhistory"
logg = undefined
asInitVals = []


###-- module functions --###

setup_datatable = () ->
  # initialize jquery.dataTables and some helpers for the filter boxes.
  table = $("#queryhistory_table")
  if table.hasClass("initialized")
    logg.info("table already initialized, doing nothing")
    return
  logg.debug("activating dataTable for queryhistory_table")
  dtable = table.addClass("initialized").dataTable(
    bStateSave: true
    # z in sDom is for table column resize plugin
    sDom: "zrltpi"
    sPaginationType: "full_numbers"
    oLanguage:
      sSearch: "Search all columns"
  )
  # helper functions adopted from jquery.datatables example
  $("tfoot input").keyup((i) ->
    logg.debug("input keyup")
    dtable.fnFilter(this.value, $("tfoot input").index(this))
    return
  )
  $("tfoot input").each((i) ->
    asInitVals[i] = this.value
    return
  )
  $("tfoot input").focus((i) ->
    logg.debug("input focus")
    t$ = $(this)
    if t$.hasClass("search_init")
      t$.removeClass("search_init")
      this.value = ""
    return
  )
  $("tfoot input").blur((i) ->
    logg.debug("input blur")
    if this.value == ""
      t$ = $(this)
      t$.addClass("search_init")
      this.value = asInitVals[$("tfoot input").index(this)]
    return
  )

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


###-- READY --###

$ ->
  if yamoda[YM_MODULE_NAME]
    yamoda.logg.warn(YM_MODULE_NAME, "already defined, skipping!")
    return
  # module init
  logg = yamoda.get_logger("yamoda.queryhistory")
  yamoda.run_before_init(YM_MODULE_NAME)
  setup_datatable()

  # module def
  that = module = yamoda.queryhistory = {
    YM_MODULE_NAME: YM_MODULE_NAME
    insert_query: (row) ->
      # insert query from history into query box.
      # :param row: table row from which the query is taken.
      query_string = $("#query_" + row).text().replace(/,/g, "\n")
      query_name = $("#query_name_" + row).text()
      $("#query_input").val(query_string)
      $("#query_name_input").val(query_name)
      $("#favorite_checkbox").removeAttr("checked")
      return

    run_query: (row) ->
      # insert query from history into query box and run it.
      # :param row: table row from which the query is taken.
      logg.debug("called run_query")
      that.insert_query(row)
      # kill remaining popovers
      $(".popover").remove()
      $("#save_query_checkbox").removeAttr("checked")
      yamoda.search.send_query_request()
      return

    toggle_all_checkboxes: (master_checkbox, slave_checkboxes$) ->
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

    del_queries: ->
      # delete some rows from query history,
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

    toggle_favorite_queries: ->
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

    initialize_if_needed: () ->
      # XXX: really needed? Check datatable init stuff again.
      logg.info("called initialize_if_needed")
      setup_datatable()
  }

  yamoda.apply_module_constants(module)

  # ok, all ready
  logg.info("yamoda.queryhistory loaded")
  return

