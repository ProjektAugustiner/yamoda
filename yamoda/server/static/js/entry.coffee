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


add = (entry_url, entry_id, parameter_name, entry_values) ->
  entry = {
    id: entry_id
    parameter_name: parameter_name
    values: entry_values
  }
  logg.debug("adding entry", entry)
  entries[entry_url] = entry
  return


get = (entry_url, success_fn) ->
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
        

plot = (entry, $target) ->
  logg.info("plotting entry", entry.id, "...")
  series = {
    data: ([i, value] for value,i in entry.values)
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
  prev_plot = $plot_area.data("plot")
  if prev_plot
      logg.debug("previous plot exists")
      plot_data = prev_plot.getData()
      plot_data.push(series)
  else
      # new plot
      plot_data = [series]
      
  plot = $.plot($plot_area, plot_data, options)
  $plot_area.data("plot", plot).removeClass("placeholder")
  return


show_plot = ($target) ->
  $plot_area = $target.children(".plot-area")
  prev_plot = $plot_area.data("plot")
  plot = $.plot($plot_area, prev_plot.getData(), prev_plot.getOptions())
  $plot_area.data("plot", plot).removeClass("placeholder")
  return


hide_plot = ($target) ->
  $plot_area = $target.children(".plot-area")
  $plot_area.text("Plot hidden").addClass("placeholder")
  return


show_values = (entry, $values_div) ->
  logg.info("showing values of entry #", entry.id, "...")
  $values_div.text(JSON.stringify(entry.values).replace(/,/g, ", "))
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

  $plot_area.bind("plotclick", (ev, pos, item) ->
    if item
      y = item.datapoint[1].toFixed(4)
      $plot_clickmessage.html("<strong>" + item.series.label + "</strong> #" + item.dataIndex + ": " + y)
    return
  )
  # click support (display value and parameter name in a hovering tooltip)
  $plot_area.bind("plothover", (ev, pos, item) ->
    if $plot_enable_tooltip.attr("checked") == "checked"
      $plot_tooltip = $plot_div.children(".plot-tooltip")
      if item
        if $plot_area.data("previous_hover_point") != item.dataIndex
          $plot_area.data("previous_hover_point", item.dataIndex)
          $plot_tooltip.remove()
          x = item.dataIndex
          y = item.datapoint[1].toFixed(4)
          logg.info("show_tooltip", x, y)
          _show_plot_tooltip(item.pageX, item.pageY, item.series.label + " at " + x + ": " + y, $plot_div)
      else
        $plot_tooltip.remove()
        $plot_area.removeData("previous_hover_point")
  )

  # zooming with navigation plugin and mousewheel doesn't work with JQuery 1.7(NaN!!)
  # deactivated zooming for now
  $plot_area.bind("plotzoom", (ev, plot) ->
    axes = plot.getAxes()
    $plot_message.html("Zooming to x: " + axes.xaxis.min.toFixed(2) + " &ndash; " + axes.xaxis.max.toFixed(2) +
                            " and y; " + axes.yaxis.min.toFixed(2) + " &ndash; " + axes.yaxis.max.toFixed(2)
    )
  )


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
  }

  yamoda.apply_module_constants(module)

  # ok, all ready
  logg.info("yamoda." + YM_MODULE_NAME, "loaded")
  return
)
