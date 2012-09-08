// Generated by CoffeeScript 1.3.3
(function() {
  var asInitVals, initialized, logg, query_links, setup_datatable, that;

  logg = yamoda.get_logger("yamoda.queryhistory");

  asInitVals = [];

  initialized = false;

  setup_datatable = function() {
    var oTable;
    if (initialized || $("#queryhistory_table").dataTable()) {
      logg.info("table already initialized, doing nothing", "initialized var is", initialized);
      return;
    }
    logg.debug("activating dataTable for queryhistory_table");
    oTable = $("#queryhistory_table").dataTable({
      bStateSave: true,
      sDom: "zrltpi",
      oLanguage: {
        sSearch: "Search all columns"
      }
    });
    $("tfoot input").keyup(function(i) {
      logg.debug("input keyup");
      oTable.fnFilter(this.value, $("tfoot input").index(this));
    });
    $("tfoot input").each(function(i) {
      asInitVals[i] = this.value;
    });
    $("tfoot input").focus(function(i) {
      logg.debug("input focus");
      if (this.className === "search_init") {
        this.className = "";
        this.value = "";
      }
    });
    $("tfoot input").blur(function(i) {
      logg.debug("input blur");
      if (this.value === "") {
        this.className = "search_init";
        this.value = asInitVals[$("tfoot input").index(this)];
      }
    });
    return initialized = true;
  };

  $(document).ready(function() {
    logg.info("document.ready here");
    return setup_datatable();
  });

  query_links = $(".query_popover");

  query_links.each(function(index, link) {
    var text;
    text = link.text.replace(/,/g, "<br>");
    return $("#query_" + index).popover({
      content: text,
      title: "Query #" + (index + 1),
      html: true,
      trigger: "hover",
      placement: "top"
    });
  });

  that = yamoda.queryhistory = {
    insert_query: function(row) {
      var query_name, query_string;
      query_string = $("#query_" + row).text().replace(/,/g, "\n");
      query_name = $("#query_name_" + row).text();
      $("#query_input").val(query_string);
      $("#query_name_input").val(query_name);
    },
    run_query: function(row) {
      logg.debug("called run_query");
      that.insert_query(row);
      $("#save_query_checkbox").removeAttr("checked");
      $("#query_form").submit();
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
    initialize_if_needed: function() {
      logg.info("called initialize_if_needed");
      return setup_datatable();
    }
  };

  yamoda.logg.info("yamoda.queryhistory loaded");

}).call(this);
