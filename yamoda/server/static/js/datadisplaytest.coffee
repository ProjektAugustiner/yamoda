logg = yamoda.get_logger("yamoda.datadisplaytest")

$(document).ready( () ->
  logg.info("document.ready")
  $("#datatable").dataTable(
    bStateSave: true
  )

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
  )
)
