###
# entrydisplay.coffee
# backing code for entrydisplay.html
#
# @author dpausp (Tobias Stenzel)
#
###

###-- private module vars --###

MODULE_NAME = "yamoda.entrydisplay"
logg = undefined
that = undefined

# displayed entry

###-- module functions --###

set_plot_area_height = ->
  # some hack, maybe this can be improved...
  height = $(window).height() * 0.45
  yamoda.logg.info("new height of plot", height)
  $("#plot>.plot-area").height(height)
  return


## 1D functions

init_1D = ->
  plot_and_show = (entry) ->
    yamoda.logg.info("plot_and_show")
    set_plot_area_height()
    yamoda.entry.show_values(entry, $("#values_display"))
    yamoda.entry.plot_1D(entry, $("#plot"))
    return

  yamoda.entry.add(that.ENTRY_URL, that.ENTRY_ID,that.PARAMETER_NAME, that.ENTRY_VALUE)
  yamoda.entry.get(that.ENTRY_URL, plot_and_show)
  $(window).resize ->
    set_plot_area_height()
    return
  return


## common functions

hide_values = ->
  yamoda.logg.debug("Hide values")
  $("#values_display").text("Values hidden")
  $("#values_toggle_btn").text("Show values")
  return


show_values = ->
  yamoda.logg.debug("Show values")
  $("#values_display").text("Wait...")
  yamoda.entry.get(that.ENTRY_URL, (entry) ->
    yamoda.entry.show_values(entry, $("#values_display"))
    $("#values_toggle_btn").text("Hide values")
  )
  return


## 1D ondemand functions

init_1D_ondemand = ->
  show_plot = ->
    yamoda.logg.debug("Show plot")
    $("#plot_toggle_btn").text("Wait...")
    set_plot_area_height()
    yamoda.entry.show_plot($("#plot"))
    $("#plot_toggle_btn").text("Hide plot")
    return

  hide_plot = ->
    yamoda.logg.debug("Hide plot")
    yamoda.entry.hide_plot($("#plot"))
    $("#plot>.plot-area").height("auto")
    $("#plot_toggle_btn").text("Show plot")
    return

  initial_cb_plot = ->
    $("#plot_toggle_btn").text("Wait...")
    yamoda.entry.get(that.ENTRY_URL, (entry) ->
      # callback: plot entry
      set_plot_area_height()
      yamoda.entry.plot_1D(entry, $('#plot'))
      $("#plot_toggle_btn").off("click").toggle(hide_plot, show_plot).text("Hide plot").removeClass("initial")
      $(window).resize ->
        yamoda.logg.info("resize!")
        if not $("#plot>.plot-area").hasClass("placeholder")
          set_plot_area_height()
        return
      values_btn = $("#values_toggle_btn")
      if values_btn.hasClass("initial")
        # other button is still in initial state, change it
        values_btn.text("Show values").removeClass("initial")
    )
    return

  initial_cb_values = ->
    $("#values_toggle_btn").text("Wait...")
    yamoda.entry.get(that.ENTRY_URL, (entry) ->
      yamoda.entry.show_values(entry, $("#values_display"))
      $("#values_toggle_btn").off("click").toggle(hide_values, show_values).text("Hide values").removeClass("initial")
      plot_btn = $("#plot_toggle_btn")
      if plot_btn.hasClass("initial")
        # other button is still in initial state, change it
        plot_btn.text("Show plot").removeClass("initial")
    )
    return

  $("#plot_toggle_btn").click(initial_cb_plot).text("Request values and plot...")
  $("#values_toggle_btn").click(initial_cb_values)
  return


## 2D functions

init_2D_ondemand = ->
  initial_cb_values = ->
    $("#values_toggle_btn").text("Wait...")
    yamoda.entry.get(that.ENTRY_URL, (entry) ->
      yamoda.entry.show_values(entry, $("#values_display"))
      $("#values_toggle_btn").off("click").toggle(hide_values, show_values).text("Hide values").removeClass("initial")
    )
    return

  show_image = ->
      $("#plot>.plot-area").html('<img src="' + that.ENTRY_URL + '" alt="Plot image cannot be displayed">').removeClass("placeholder")
      $("#plot_toggle_btn").text("Hide Image")
      return

  hide_image = ->
      $("#plot>.plot-area").text("Image hidden").addClass("placeholder")
      $("#plot_toggle_btn").text("Show Image")
      return

  $("#static-download-btn").text("Download image")
  $("#plot_toggle_btn").text("Show image").toggle(show_image, hide_image)
  $("#values_toggle_btn").click(initial_cb_values)
  return

###-- READY --###

$ ->
  # module def
  that = yamoda.entrydisplay = yamoda.make_module(MODULE_NAME,
      e1D:
        init: init_1D
      e1D_ondemand:
        init: init_1D_ondemand
      e2D_ondemand:
        init: init_2D_ondemand
  )
  # other stuff to do
  logg = that.logg
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
