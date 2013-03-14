###
# entry.coffee
# common functions for displaying / plotting entries
#
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

MODULE_NAME = "yamoda.entry"
logg = undefined
# entry cache
entries = {}

used_plot_ids = []

default_flot_options =
  series:
    lines:
      show: true
    points:
      show: true
      radius: 0.4
  grid:
    clickable: true
    hoverable: true
    autoHighlight: true
  selection:
    mode: "xy"
  zoom:
    interactive: true
  pan:
    interactive: true


###-- module functions --###

add = (entry_url, entry_id, parameter_name, entry_value) ->
  # Manually add an entry to the entry cache.
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


entry_request = (entry_url, success_cb) ->
  $.ajax(
    type: "GET"
    url: entry_url
    dataType: "json"
    success: success_cb
  )


get = (entry_url, success_fn) ->
  # Get an entry (maybe from cache) and call a function.
  # :param entry_url: like entries/220
  # :param success_fn: callback which gets the entry as first argument

  if entry_url not of entries
    logg.debug(entry_url, "unknown, requesting it from server...")
    logg.debug("current entries", entries)
    entry_request(entry_url, (entry) ->
        entries[entry_url] = entry
        success_fn(entry)
        return
    )
  else
    logg.debug(entry_url, "already known")
    success_fn(entries[entry_url])
  return
        

get_two = (entry_x_url, entry_y_url, success_fn) ->
  # Get two entries (maybe from cache) and call a function.
  # :param entry_x_url: like entries/220
  # :param entry_y_url: like entries/220
  # :param success_fn: callback which gets entry_x and entry_x as args
  entry_x = null
  entry_y = null
  check_success = (entry_url, entry) ->
    if entry_url == entry_x_url
      entry_x = entry
    else
      entry_y = entry
    if entry_x and entry_y
      success_fn(entry_x, entry_y)

  get(entry_x_url, (entry) -> check_success(entry_x_url, entry))
  get(entry_y_url, (entry) -> check_success(entry_y_url, entry))
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


_find_next_free_plot_id = ->
  ii = 0
  while true
    if ii not in used_plot_ids
      used_plot_ids.push(ii)
      return ii
    ii += 1


_remove_plot_id = (plot_id) ->
  index = _.indexOf(used_plot_ids, plot_id)
  used_plot_ids.splice(index, 1)


_remove_series = (plot_data, series_to_remove) ->
  index = 0
  for series in plot_data
    if series.yamoda_plot_id == series_to_remove.yamoda_plot_id
      plot_data.splice(index, 1)
      _remove_plot_id(series.yamoda_plot_id)
      return plot_data
    index += 1


plot_series = (series, $target) ->
  # plot a series with flot
  # :param entry: series to plot
  # :param $taget: JQuery selector for the node that will display the plot

  # get old plot and its data if there is one
  $plot_area = $target.find(".plot-area")
  $sidebar = $target.find(".plot-sidebar")
  prev_plot = $target.data("plot")
  series.yamoda_plot_id = series.color = _find_next_free_plot_id()
  if prev_plot
    logg.debug("previous plot exists")
    plot_data = prev_plot.getData()
    plot_data.push(series)
  else
    # new plot
    logg.debug("first series to plot")
    plot_data = [series]
  
  # plot area changes
  if $plot_area.hasClass("placeholder")
    $plot_area.removeClass("placeholder").text("")
  logg.debug("color", series.color)
  plot = $.plot($plot_area, plot_data, default_flot_options)
  $target.data("plot", plot)
  logg.debug("color ", series.color)
  # sidebar changes
  # find legend / plot color
  # depends on flot internals, may change in later versions
  label = $(series.label).text()
  selector = ".legendLabel:contains('#{label}')"
  $color_marker = $plot_area.find(selector).parent().children(".legendColorBox").children().children()
  $legend = $sidebar.children(".sidebar-legend")
  color = $color_marker.css("border-left-color")
  # create new legend entry
  $list_elem = $("<li data-label='#{label}'>")
  $color_span = $("<span>&nbsp;&nbsp;&nbsp;</span>").css("background-color", color)
  $list_elem.append($color_span)
  $button = $('<a class="btn btn-mini" href="#">Delete Plot</a>').css("border-color", color)
  $button.click ->
    logg.debug("delete clicked for ", label)
    $list_elem.remove()
    plot_data = $target.data("plot").getData()
    console.log("plot_data", plot_data)
    console.log("series", series)
    remaining_series = _remove_series(plot_data, series)
    if remaining_series.length == 0
      logg.debug("no remaining series")
      $plot_area.addClass("placeholder").text("No content to display")
    else
      logg.debug(remaining_series.length, " series remain")
      plot = $.plot($plot_area, remaining_series, default_flot_options)
      $target.data("plot", plot)
    return

  $list_elem.append("&nbsp;&nbsp;" + series.label + '&nbsp;&nbsp;').append($button)
  $legend.append($list_elem)
  return


plot_1D = (entry, $target) ->
  # use flot to a create a plot of an 1D entry
  # :param entry: entry to plot
  # :param $taget: JQuery selector for the node that will display the plot

  logg.info("plotting 1D entry", entry.id, "...")
  series = {
    data: ([i, value] for value,i in entry.value)
    label: "<strong>" + entry.parameter_name + "</strong>"
    clickable: true
    hoverable: true
  }
  plot_series(series, $target)
  return


plot_1D_1D = (entry_x, entry_y, $target) ->
  # use flot to a create a plot of an 1D entry against another entry
  # :param entry: entry to plot
  # :param $taget: JQuery selector for the node that will display the plot

  logg.info("plotting 1D entry", entry_x.id, "against", entry_y.id, "...")
  series = {
    data: _.zip(entry_x.value, entry_y.value)
    label: "<strong>" + entry_x.parameter_name + "</strong>:<strong>" + entry_y.parameter_name + "</strong>"
    clickable: true
    hoverable: true
  }
  plot_series(series, $target)
  return


show_plot = ($target) ->
  # Show plot which was hidden previously. 
  # To draw a plot for the first time, use plot function.
  $plot_area = $target.find(".plot-area")
  prev_plot = $target.find("plot")
  plot = $.plot($plot_area, prev_plot.getData(), prev_plot.getOptions())
  $plot_area.data("plot", plot).removeClass("placeholder")
  return


hide_plot = ($target) ->
  $plot_area = $target.find(".plot-area")
  $plot_area.addClass("placeholder").text("Plot hidden")
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
  $plot_area = $plot_div.find(".plot-area")
  $plot_message = $plot_div.find(".plot-message")
  $plot_clickmessage = $plot_div.find(".plot-clickmessage")
  $plot_enable_tooltip = $plot_div.find(".plot-enable-tooltip")

  $plot_area.on("plotclick", (ev, pos, item) ->
    if item
      y = item.datapoint[1].toFixed(4)
      $plot_clickmessage.html("<strong>" + item.series.label + "</strong> #" + item.dataIndex + ": " + y)
    return
  )
  # click support (display value and parameter name in a hovering tooltip)
  $plot_area.on("plothover", (ev, pos, item) ->
    if $plot_enable_tooltip.attr("checked") == "checked"
      $plot_tooltip = $plot_div.find(".plot-tooltip")
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
    logg.info("plotzoom")
    axes = plot.getAxes()
    $plot_message.html("Zooming to x: " + axes.xaxis.min.toFixed(2) + " &ndash; " + axes.xaxis.max.toFixed(2) +
                            " and y; " + axes.yaxis.min.toFixed(2) + " &ndash; " + axes.yaxis.max.toFixed(2)
    )
    return
  )
  return


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

$ ->
  # module def
  that = yamoda.entry = yamoda.make_module(MODULE_NAME,
    add: add
    get: get
    get_two: get_two
    plot_1D: plot_1D
    plot_1D_1D: plot_1D_1D
    hide_plot: hide_plot
    show_plot: show_plot
    flot_setup: flot_setup
    show_values: show_values
    sparkline_setup: sparkline_setup
    setup_2D_preview_images_ondemand: setup_2D_preview_images_ondemand
    fetch_2D_preview_images: fetch_2D_preview_images
  )
  # other stuff to do
  logg = that.logg
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
