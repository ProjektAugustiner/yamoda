###
# entry.coffee
# displaying / plotting entries
# #
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

YM_MODULE_NAME = "entry"
logg = undefined
# entry cache
entries = {}


###-- module functions --###


add = (entry_url, entry_id, parameter_name, entry_value) ->
  # manually add an entry to the entry cache
  # :param entry_url: url like entries/220 which is used as key
  # :param entry_id: id of the entry like 220
  # :param parameter_name: name of the corresponding parameter
  # :param entry_value: 1D array of entry values

  entry = {
    id: entry_id
    parameter_name: parameter_name
    value: entry_value
  }
  logg.debug("adding entry", entry)
  entries[entry_url] = entry
  return


get = (entry_url, success_fn) ->
  # get an entry (maybe from cache) and call a function
  # :param entry_url: like entries/220
  # :param success_fn: callback which gets the entry as first argument

  if entry_url not of entries
    logg.debug(entry_url, "unknown, requesting it from server...")
    logg.debug("current entries", entries)
    $.ajax(
      type: "GET"
      url: entry_url
      dataType: "json"
      success: (entry) ->
        entries[entry_url] = entry
        success_fn(entry)
        return
    )
  else
    logg.debug(entry_url, "already known")
    success_fn(entries[entry_url])
  return
        

_do_ajax_2D_preview_images = ($target, height) ->
  image_url = $target.children("a").attr("imageUrl")
  $target.children("a").replaceWith("Loading...")
  $.getJSON(image_url, (json) ->
    $target.html('<img width="' + height + '" src="' + json.img_url + '"></img>')
    return
  )


fetch_2D_preview_images = ($target, height) ->
  $target.each ->
    _do_ajax_2D_preview_images($(this), height)
  return


setup_2D_preview_images_ondemand = ($target, height) ->
  $target.each ->
    $(this).children("a").click ->
      _do_ajax_2D_preview_images($(this), height)
      return
  return


plot = (entry, $target) ->
  # use flot to a create a plot of an entry
  # :param entry: entry to plot
  # :param $taget: JQuery selector for the node that will display the plot

  logg.info("plotting entry", entry.id, "...")
  series = {
    data: ([i, value] for value,i in entry.value)
    label: "<strong>" + entry.parameter_name + "</strong>"
    clickable: true
    hoverable: true
  }
  options = {
    series:
      lines:
        show: true
      points:
        show: true
        radius: 0.4
    xaxis:
      zoomRange: [2, 100]
      panRange: [0, 100]
    yaxis:
      zoomRange: [0.01, 1]
      panRange: [0, 1]
    grid:
      clickable: true
      hoverable: true
      autoHighlight: true
    selection:
      mode: "xy"
  }
  # get old plot and its data if there is one
  $plot_area = $target.children(".plot-area")
  prev_plot = $target.data("plot")
  if prev_plot
    logg.debug("previous plot exists")
    plot_data = prev_plot.getData()
    plot_data.push(series)
  else
    # new plot
    plot_data = [series]
      
  plot = $.plot($plot_area, plot_data, options)
  $target.data("plot", plot)
  $plot_area.removeClass("placeholder")
  return


show_plot = ($target) ->
  # show plot which was hidden previously. To draw a plot for the first time, use plot function
  $plot_area = $target.children(".plot-area")
  prev_plot = $target.data("plot")
  plot = $.plot($plot_area, prev_plot.getData(), prev_plot.getOptions())
  $plot_area.data("plot", plot).removeClass("placeholder")
  return


hide_plot = ($target) ->
  $plot_area = $target.children(".plot-area")
  $plot_area.replaceWith('<div class="plot-area placeholder">Plot hidden</div>')
  return


show_values = (entry, $values_div) ->
  logg.info("showing values of entry #", entry.id, "...")
  as_string = JSON.stringify(entry.value)
  $values_div.text(as_string.replace(/,/g, ", "))
  return


_show_plot_tooltip = (x, y, contents, $plot_div) ->
  $('<div class="plot-tooltip">' + contents + '</div>').css(
    position: "absolute"
    display: "none"
    top: y + 5
    left: x + 5
    border: "1px solid #fdd"
    padding: "2px"
    "background-color": "#fee"
    opacity: 0.80
  ).appendTo($plot_div).fadeIn(200)
  return


flot_setup = ($plot_div) ->
  # flot plotting setup
  # click support (display value and parameter name)
  # :param $plot_div: div which contains plotting stuff
  logg.debug("flot setup for", $plot_div.length)
  $plot_area = $plot_div.children(".plot-area")
  $plot_message = $plot_div.children(".plot-message")
  $plot_clickmessage = $plot_div.children(".plot-clickmessage")
  $plot_enable_tooltip = $plot_div.children(".plot-enable-tooltip")

  $plot_area.on("plotclick", (ev, pos, item) ->
    if item
      y = item.datapoint[1].toFixed(4)
      $plot_clickmessage.html("<strong>" + item.series.label + "</strong> #" + item.dataIndex + ": " + y)
    return
  )
  # click support (display value and parameter name in a hovering tooltip)
  $plot_area.on("plothover", (ev, pos, item) ->
    if $plot_enable_tooltip.attr("checked") == "checked"
      $plot_tooltip = $plot_div.children(".plot-tooltip")
      if item
        if $plot_area.data("previous_hover_point") != item.dataIndex
          $plot_area.data("previous_hover_point", item.dataIndex)
          $plot_tooltip.remove()
          x = item.dataIndex
          y = item.datapoint[1].toFixed(4)
          #logg.info("show_tooltip", x, y)
          _show_plot_tooltip(item.pageX, item.pageY, item.series.label + " at " + x + ": " + y, $plot_div)
      else
        $plot_tooltip.remove()
        $plot_area.removeData("previous_hover_point")
    return
  )

  # zooming with navigation plugin and mousewheel doesn't work with JQuery 1.7(NaN!!)
  # deactivated zooming for now
  $plot_area.on("plotzoom", (ev, plot) ->
    axes = plot.getAxes()
    $plot_message.html("Zooming to x: " + axes.xaxis.min.toFixed(2) + " &ndash; " + axes.xaxis.max.toFixed(2) +
                            " and y; " + axes.yaxis.min.toFixed(2) + " &ndash; " + axes.yaxis.max.toFixed(2)
    )
    return
  )


sparkline_setup = ($target) ->
  # sparkline setup for a target containing data which can be plotted
  logg.info("sparkline for target", $target.selector)
  value_count = $target.attr("count")
  cell_width = $target.width()
  pixel_per_value = Math.max(Math.floor(cell_width / value_count), 1)
  logg.debug("cell width", cell_width, "pixel_per_value", pixel_per_value)
  $target.sparkline(
    "html",
    type: "line"
    height: "60"
    tooltipFormat: '<span style="color: {{color}}">&#9679;</span> {{prefix}}{{x}} | {{y}}{{suffix}}'
    defaultPixelsPerValue: pixel_per_value
    normalRangeMin: $target.attr("normalMin")
    normalRangeMax: $target.attr("normalMax")
    fillColor: false
  )
  return


###-- READY --###

$( () ->
  if yamoda[YM_MODULE_NAME]
    yamoda.logg.warn(YM_MODULE_NAME, "already defined, skipping!")
    return
  # module init
  logg = yamoda.get_logger("yamoda." + YM_MODULE_NAME)
  yamoda.run_before_init(YM_MODULE_NAME)


  # module def
  module = yamoda.entry = {
    YM_MODULE_NAME: YM_MODULE_NAME
    add: add
    get: get
    plot: plot
    hide_plot: hide_plot
    show_plot: show_plot
    flot_setup: flot_setup
    show_values: show_values
    sparkline_setup: sparkline_setup
    setup_2D_preview_images_ondemand: setup_2D_preview_images_ondemand
    fetch_2D_preview_images: fetch_2D_preview_images
  }

  yamoda.apply_module_constants(module)

  # ok, all ready
  logg.info("yamoda." + YM_MODULE_NAME, "loaded")
  return
)

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
