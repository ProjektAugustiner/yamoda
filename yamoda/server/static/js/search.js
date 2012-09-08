// Generated by CoffeeScript 1.3.3
(function() {
  var change_to_query_history, change_to_query_results, intercept_query_submit, logg, query_history_html, query_results_html, query_results_shown, send_query_history_request, send_query_request, send_query_save_request;

  logg = yamoda.get_logger("yamoda.search");

  query_results_shown = false;

  query_history_html = "";

  query_results_html = "<h3>No results yet.</h3>";

  change_to_query_history = function() {
    logg.info("change_to_query_history");
    query_results_html = $("#bottom-content").html();
    $("#bottom-content").html(query_history_html);
    $("#query_results_btn").show();
    $("#query_history_btn").hide();
    $("#bottom-headline").text("Query History");
    yamoda.queryhistory.initialize_if_needed();
    return query_results_shown = false;
  };

  change_to_query_results = function() {
    logg.info("change_to_query_results");
    query_history_html = $("#bottom-content").html();
    $("#bottom-content").html(query_results_html);
    $("#query_history_btn").show();
    $("#query_results_btn").hide();
    query_results_shown = true;
    return $("#bottom-headline").text("Query Results");
  };

  intercept_query_submit = function() {
    var show_results;
    show_results = $("input[name='show_results']:checked").val();
    logg.info("where to show results:", show_results);
    if (show_results === "newpage") {
      return true;
    } else {
      send_query_request();
      return false;
    }
  };

  send_query_history_request = function() {
    return $.get(yamoda.search.query_history_url, function(history_content) {
      logg.info("got history content");
      query_history_html = history_content;
      if (!query_results_shown) {
        $("#bottom-content").html(query_history_html);
        return yamoda.queryhistory.initialize_if_needed();
      }
    });
  };

  send_query_request = function() {
    var save_query, show_results;
    logg.info("send query request");
    show_results = $("input[name='show_results']:checked").val();
    logg.info("where to show results:", show_results);
    if (show_results === "newpage") {
      $("#query_form").submit();
      return;
    }
    $("#bottom-headline").text("Processing...");
    save_query = $("#save_query_checkbox").attr("checked");
    return $.ajax({
      type: 'POST',
      url: yamoda.search.search_url,
      data: {
        query: $("#query_input").val(),
        name: $("#query_name_input").val(),
        save_query: save_query
      },
      success: function(data) {
        logg.info("received query request answer");
        query_results_html = data;
        change_to_query_results();
        send_query_history_request();
        /* XXX: 
        Add submit handler again after request because it seems 
        to get lost somehow. Don't know why this is happening...
        */

      },
      error: function() {
        $("#bottom_headline").text("Error!");
      }
    });
  };

  send_query_save_request = function() {
    logg.info("send query save request");
    return $.ajax({
      type: 'POST',
      url: yamoda.search.save_query_url,
      data: {
        query: $("#query_input").val(),
        name: $("#query_name_input").val()
      },
      success: function(msg) {
        logg.info("received query save request answer");
        $("#main_msg_area").html(msg);
        return send_query_history_request();
      }
    });
  };

  $(document).ready(function() {
    logg.info("document.ready here");
    $("#query_history_btn").hide();
    $("#query_results_btn").hide();
  });

  yamoda.search = {
    request_help_content: function(url) {
      return $.get(url, function(helptext) {
        logg.info("got helptext for", url);
        return $("#help-content").html(helptext);
      });
    },
    change_to_query_history: change_to_query_history,
    change_to_query_results: change_to_query_results,
    send_query_request: send_query_request,
    send_query_save_request: send_query_save_request
  };

  yamoda.logg.info("yamoda.search loaded");

}).call(this);
