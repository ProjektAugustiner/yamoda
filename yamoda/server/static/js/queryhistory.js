// Generated by CoffeeScript 1.3.3
(function() {
  var asInitVals, logg, query_links, that;

  logg = yamoda.get_logger("yamoda.queryhistory");

  asInitVals = [];

  $(document).ready(function() {
    var oTable;
    logg.debug("activating dataTable for queryhistory_table");
    oTable = $("#queryhistory_table").dataTable({
      bStateSave: true,
      sDom: "zflrtpi",
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
    logg.info("before keyup");
    $("tfoot input").blur(function(i) {
      logg.debug("input blur");
      if (this.value === "") {
        this.className = "search_init";
        this.value = asInitVals[$("tfoot input").index(this)];
      }
    });
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
    insert_query: function(row, target$) {
      var newtext;
      newtext = $("#query_" + row).text().replace(/,/g, "\n");
      target$.val(newtext);
    },
    run_query: function(row, target$, form$) {
      logg.debug("called run_query");
      that.insert_query(row, target$);
      form$.trigger("submit");
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
    }
  };

  yamoda.logg.info("yamoda.queryhistory loaded");

}).call(this);
