// Generated by CoffeeScript 1.3.3

/*
# entry.coffee
# displaying / plotting entries
# #
# @author dpausp (Tobias Stenzel)
*/


/*-- private module vars --
*/


(function() {
  var YM_MODULE_NAME, add, entries, fetch_2D_preview_images, flot_setup, get, hide_plot, logg, plot, setup_2D_preview_images_ondemand, show_plot, show_values, sparkline_setup, _do_ajax_2D_preview_images, _show_plot_tooltip;

  YM_MODULE_NAME = "entry";

  logg = void 0;

  entries = {};

  /*-- module functions --
  */


  add = function(entry_url, entry_id, parameter_name, entry_value) {
    var entry;
    entry = {
      id: entry_id,
      parameter_name: parameter_name,
      values: entry_value
    };
    logg.debug("adding entry", entry);
    entries[entry_url] = entry;
  };

  get = function(entry_url, success_fn) {
    if (!(entry_url in entries)) {
      logg.debug(entry_url, "unknown, requesting it from server...");
      logg.debug("current entries", entries);
      $.ajax({
        type: "GET",
        url: entry_url,
        dataType: "json",
        success: function(entry) {
          entries[entry_url] = entry;
          success_fn(entry);
        }
      });
    } else {
      logg.debug(entry_url, "already known");
      success_fn(entries[entry_url]);
    }
  };

  _do_ajax_2D_preview_images = function($target, height) {
    var image_url;
    image_url = $target.children("a").attr("imageUrl");
    $target.children("a").replaceWith("Loading...");
    return $.getJSON(image_url, function(json) {
      $target.html('<img width="' + height + '" src="' + json.img_url + '"></img>');
    });
  };

  fetch_2D_preview_images = function($target, height) {
    $target.each(function() {
      return _do_ajax_2D_preview_images($(this), height);
    });
  };

  setup_2D_preview_images_ondemand = function($target, height) {
    $target.each(function() {
      return $(this).children("a").click(function() {
        _do_ajax_2D_preview_images($(this), height);
      });
    });
  };

  plot = function(entry, $target) {
    var $plot_area, i, options, plot_data, prev_plot, series, value;
    logg.info("plotting entry", entry.id, "...");
    series = {
      data: (function() {
        var _i, _len, _ref, _results;
        _ref = entry.value;
        _results = [];
        for (i = _i = 0, _len = _ref.length; _i < _len; i = ++_i) {
          value = _ref[i];
          _results.push([i, value]);
        }
        return _results;
      })(),
      label: "<strong>" + entry.parameter_name + "</strong>",
      clickable: true,
      hoverable: true
    };
    options = {
      series: {
        lines: {
          show: true
        },
        points: {
          show: true,
          radius: 0.4
        }
      },
      xaxis: {
        zoomRange: [2, 100],
        panRange: [0, 100]
      },
      yaxis: {
        zoomRange: [0.01, 1],
        panRange: [0, 1]
      },
      grid: {
        clickable: true,
        hoverable: true,
        autoHighlight: true
      },
      selection: {
        mode: "xy"
      }
    };
    $plot_area = $target.children(".plot-area");
    prev_plot = $target.data("plot");
    if (prev_plot) {
      logg.debug("previous plot exists");
      plot_data = prev_plot.getData();
      plot_data.push(series);
    } else {
      plot_data = [series];
    }
    plot = $.plot($plot_area, plot_data, options);
    $target.data("plot", plot);
    $plot_area.removeClass("placeholder");
  };

  show_plot = function($target) {
    var $plot_area, prev_plot;
    $plot_area = $target.children(".plot-area");
    prev_plot = $target.data("plot");
    plot = $.plot($plot_area, prev_plot.getData(), prev_plot.getOptions());
    $plot_area.data("plot", plot).removeClass("placeholder");
  };

  hide_plot = function($target) {
    var $plot_area;
    $plot_area = $target.children(".plot-area");
    $plot_area.replaceWith('<div class="plot-area placeholder">Plot hidden</div>');
  };

  show_values = function(entry, $values_div) {
    logg.info("showing values of entry #", entry.id, "...");
    $values_div.text(JSON.stringify(entry.value).replace(/,/g, ", "));
  };

  _show_plot_tooltip = function(x, y, contents, $plot_div) {
    $('<div class="plot-tooltip">' + contents + '</div>').css({
      position: "absolute",
      display: "none",
      top: y + 5,
      left: x + 5,
      border: "1px solid #fdd",
      padding: "2px",
      "background-color": "#fee",
      opacity: 0.80
    }).appendTo($plot_div).fadeIn(200);
  };

  flot_setup = function($plot_div) {
    var $plot_area, $plot_clickmessage, $plot_enable_tooltip, $plot_message;
    logg.debug("flot setup for", $plot_div.length);
    $plot_area = $plot_div.children(".plot-area");
    $plot_message = $plot_div.children(".plot-message");
    $plot_clickmessage = $plot_div.children(".plot-clickmessage");
    $plot_enable_tooltip = $plot_div.children(".plot-enable-tooltip");
    $plot_area.on("plotclick", function(ev, pos, item) {
      var y;
      if (item) {
        y = item.datapoint[1].toFixed(4);
        $plot_clickmessage.html("<strong>" + item.series.label + "</strong> #" + item.dataIndex + ": " + y);
      }
    });
    $plot_area.on("plothover", function(ev, pos, item) {
      var $plot_tooltip, x, y;
      if ($plot_enable_tooltip.attr("checked") === "checked") {
        $plot_tooltip = $plot_div.children(".plot-tooltip");
        if (item) {
          if ($plot_area.data("previous_hover_point") !== item.dataIndex) {
            $plot_area.data("previous_hover_point", item.dataIndex);
            $plot_tooltip.remove();
            x = item.dataIndex;
            y = item.datapoint[1].toFixed(4);
            _show_plot_tooltip(item.pageX, item.pageY, item.series.label + " at " + x + ": " + y, $plot_div);
          }
        } else {
          $plot_tooltip.remove();
          $plot_area.removeData("previous_hover_point");
        }
      }
    });
    return $plot_area.on("plotzoom", function(ev, plot) {
      var axes;
      axes = plot.getAxes();
      $plot_message.html("Zooming to x: " + axes.xaxis.min.toFixed(2) + " &ndash; " + axes.xaxis.max.toFixed(2) + " and y; " + axes.yaxis.min.toFixed(2) + " &ndash; " + axes.yaxis.max.toFixed(2));
    });
  };

  sparkline_setup = function($target) {
    var cell_width, pixel_per_value, value_count;
    logg.info("sparkline for target", $target.selector);
    value_count = $target.attr("count");
    cell_width = $target.width();
    pixel_per_value = Math.max(Math.floor(cell_width / value_count), 1);
    logg.debug("cell width", cell_width, "pixel_per_value", pixel_per_value);
    $target.sparkline("html", {
      type: "line",
      height: "60",
      tooltipFormat: '<span style="color: {{color}}">&#9679;</span> {{prefix}}{{x}} | {{y}}{{suffix}}',
      defaultPixelsPerValue: pixel_per_value,
      normalRangeMin: $target.attr("normalMin"),
      normalRangeMax: $target.attr("normalMax"),
      fillColor: false
    });
  };

  /*-- READY --
  */


  $(function() {
    var module;
    if (yamoda[YM_MODULE_NAME]) {
      yamoda.logg.warn(YM_MODULE_NAME, "already defined, skipping!");
      return;
    }
    logg = yamoda.get_logger("yamoda." + YM_MODULE_NAME);
    yamoda.run_before_init(YM_MODULE_NAME);
    module = yamoda.entry = {
      YM_MODULE_NAME: YM_MODULE_NAME,
      add: add,
      get: get,
      plot: plot,
      hide_plot: hide_plot,
      show_plot: show_plot,
      flot_setup: flot_setup,
      show_values: show_values,
      sparkline_setup: sparkline_setup,
      setup_2D_preview_images_ondemand: setup_2D_preview_images_ondemand,
      fetch_2D_preview_images: fetch_2D_preview_images
    };
    yamoda.apply_module_constants(module);
    logg.info("yamoda." + YM_MODULE_NAME, "loaded");
  });

}).call(this);
