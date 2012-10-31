### 
# datadisplaytest.coffee
# test module for data displays
# 
# @author dpausp (Tobias Stenzel)
###

###-- private module vars --###

YM_MODULE_NAME = "datadisplaytest"
logg = undefined
plot_data = []
plot = undefined


###-- module functions --###

_request_fakeentry_data = (yid) ->
  $.ajax(
    type: "GET"
    url: yamoda.base_url + "testentry/" + yid
    dataType: "json"
    success: (json) ->
      logg.info("got data for", yid, "plotting...")
      series = {
        data: json.data
        label: "<strong>" + json.parameter_x + ":" + json.parameter_y + "</strong>"
        clickable: true
        hoverable: true
      }

      plot_data.push(series)

      if plot_data
        options = {
          series:
            lines:
              show: true
            points:
              show: true
          grid:
            clickable: true
            hoverable: true
            autoHighlight: true
        }
        plot = $.plot($("#plotdisplay"), plot_data, options)
      return
  )


###-- READY --###

$(document).ready( () ->
  if yamoda[YM_MODULE_NAME]
    yamoda.logg.warn(YM_MODULE_NAME, "already defined, skipping!")
    return
  # module init
  logg = yamoda.get_logger("yamoda.datadisplaytest")
  yamoda.run_before_init(YM_MODULE_NAME)

  # datatables setup
  $("#datatable").dataTable(
    bStateSave: false
    aaSorting: [[6, "desc"], [3, "asc"], [1, "asc"]]
    aoColumns: [
        null,
        null,
        null,
        null,
        #sType:
        #    "dimension"
        null,
        null,
        null
    ]
  )
  # define sort function:
  #jQuery.fn.dataTableExt.oSort["dimension-asc"] = sort_by_dimension_asc

  # sparkline setup
  $("td.valuecolumn").each( (i, elem) ->
    el$ = $(elem)
    logg.info("sparkline for elem", i, el$.attr("normalMax"))
    value_count = el$.attr("count")
    cell_width = el$.width()
    pixel_per_value = cell_width / value_count
    $(elem).sparkline(
      "html",
      type: "line"
      height: "60"
      tooltipFormat: '<span style="color: {{color}}">&#9679;</span> {{prefix}}{{x}} | {{y}}{{suffix}}'
      defaultPixelsPerValue: pixel_per_value
      normalRangeMin: el$.attr("normalMin")
      normalRangeMax: el$.attr("normalMax")
      fillColor: false
    )
    return
  )

  # flot setup
  $("#plotdisplay").bind("plotclick", (ev, pos, item) ->
    if item
      $("#plot_clicktext").html("Point #" + item.dataIndex + " in plot <strong>" + item.series.label+ "</strong>")
    return
  )
  _request_fakeentry_data(0)
  _request_fakeentry_data(1)

  # module def
  module = yamoda.datadisplaytest = {
    YM_MODULE_NAME: YM_MODULE_NAME
    request_entry: request_entry
    setup_sparkline: setup_sparkline
  }

  yamoda.apply_module_constants(module)

  # ok, all ready
  logg.info("yamoda.datadisplaytest loaded")
  return
)
