// Generated by CoffeeScript 1.3.3

/*
# queryhistory.coffee
# query history related stuff
#
# @author dpausp (Tobias Stenzel)
*/


/*-- private module vars --
*/


(function() {
  var YM_MODULE_NAME, asInitVals, logg, setup_datatable;

  YM_MODULE_NAME = "queryhistory";

  logg = void 0;

  asInitVals = [];

  /*-- module functions --
  */


  setup_datatable = function() {
    var dtable, query_links, table;
    table = $("#queryhistory_table");
    if (table.hasClass("initialized")) {
      logg.info("table already initialized, doing nothing");
      return;
    }
    logg.debug("activating dataTable for queryhistory_table");
    dtable = table.addClass("initialized").dataTable({
      bStateSave: true,
      sDom: "zrltpi",
      sPaginationType: "full_numbers",
      oLanguage: {
        sSearch: "Search all columns"
      }
    });
    $("tfoot input").keyup(function(i) {
      logg.debug("input keyup");
      dtable.fnFilter(this.value, $("tfoot input").index(this));
    });
    $("tfoot input").each(function(i) {
      asInitVals[i] = this.value;
    });
    $("tfoot input").focus(function(i) {
      var t$;
      logg.debug("input focus");
      t$ = $(this);
      if (t$.hasClass("search_init")) {
        t$.removeClass("search_init");
        this.value = "";
      }
    });
    $("tfoot input").blur(function(i) {
      var t$;
      logg.debug("input blur");
      if (this.value === "") {
        t$ = $(this);
        t$.addClass("search_init");
        this.value = asInitVals[$("tfoot input").index(this)];
      }
    });
    query_links = $(".query_popover");
    query_links.each(function(index, link) {
      var text;
      text = link.text.replace(/,/g, "<br>");
      return $("#query_" + index).popover({
        content: text,
        title: "Query #" + (index + 1) + " (click to run)",
        html: true,
        trigger: "hover",
        placement: "top"
      });
    });
  };

  /*-- READY --
  */


  $(function() {
    var module, that;
    if (yamoda[YM_MODULE_NAME]) {
      yamoda.logg.warn(YM_MODULE_NAME, "already defined, skipping!");
      return;
    }
    logg = yamoda.get_logger("yamoda.queryhistory");
    yamoda.run_before_init(YM_MODULE_NAME);
    setup_datatable();
    that = module = yamoda.queryhistory = {
      YM_MODULE_NAME: YM_MODULE_NAME,
      insert_query: function(row) {
        var query_name, query_string;
        query_string = $("#query_" + row).text().replace(/,/g, "\n");
        query_name = $("#query_name_" + row).text();
        $("#query_input").val(query_string);
        $("#query_name_input").val(query_name);
        $("#favorite_checkbox").removeAttr("checked");
      },
      run_query: function(row) {
        logg.debug("called run_query");
        that.insert_query(row);
        $(".popover").remove();
        $("#save_query_checkbox").removeAttr("checked");
        yamoda.search.send_query_request();
      },
      toggle_all_checkboxes: function(master_checkbox, slave_checkboxes$) {
        logg.debug("called toggle_all_checkboxes");
        if (master_checkbox.checked) {
          slave_checkboxes$.attr("checked", "checked");
        } else {
          slave_checkboxes$.removeAttr("checked");
        }
      },
      del_queries: function() {
        var ids;
        logg.info("called del_queries");
        ids = $.map($(".querycheck:checked"), function(el) {
          return el.id.substring(6);
        });
        logg.info("ids to delete: ", ids);
        if (!(ids != null)) {
          return;
        }
        $("actionbutton button").button("loading");
        logg.info("sending request to", that.del_queries_url);
        $.ajax({
          type: "POST",
          url: that.del_queries_url,
          data: {
            ids: ids
          },
          success: function(data, st, xhr) {
            window.location.reload();
            return $("checkbox_all").removeAttr("checked");
          },
          error: function(xhr, st, err) {
            logg.error("error in delete callback: ", err);
            $("actionbutton button").button("reset");
            return $("actionerror").text(err).show();
          }
        });
      },
      toggle_favorite_queries: function() {
        var ids;
        logg.info("called toggle_favorite_queries");
        ids = $.map($(".querycheck:checked"), function(el) {
          return el.id.substring(6);
        });
        logg.info("ids to toggle favorite state for: ", ids);
        if (!(ids != null)) {
          return;
        }
        $("actionbutton button").button("loading");
        logg.info("sending request to", that.toggle_favorite_queries_url);
        $.ajax({
          type: "POST",
          url: that.toggle_favorite_queries_url,
          data: {
            ids: ids
          },
          success: function(data, st, xhr) {
            window.location.reload();
            return $("checkbox_all").removeAttr("checked");
          },
          error: function(xhr, st, err) {
            logg.error("error in favorite callback: ", err);
            $("actionbutton button").button("reset");
            return $("actionerror").text(err).show();
          }
        });
      },
      initialize_if_needed: function() {
        logg.info("called initialize_if_needed");
        return setup_datatable();
      }
    };
    yamoda.apply_module_constants(module);
    logg.info("yamoda.queryhistory loaded");
  });

}).call(this);
