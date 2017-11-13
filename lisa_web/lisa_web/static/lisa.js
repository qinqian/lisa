// The table generation function
function tabulate(cl, data, columns, interact) {
  var table = d3.select("." + cl).append("table")
        .attr("class", "table tab" + cl),
      thead = table.append("thead"),
      tbody = table.append("tbody").attr("class", "tbody");

  // append the header row
  thead.append("tr")
    .selectAll("th")
    .data(columns)
    .enter()
    .append("th")
    .text(function(column) { return column; });
  // create a row for each object in the data
  var rows = tbody.selectAll("tr")
        .data(data)
        .enter()
        .append("tr");

  // create a cell in each row for each column
  var cells = rows.selectAll("td")
        .data(function(row) {
          return columns.map(function(column) {
            return {column: column, value: row[column]};
          });
        })
        .enter()
        .append("td")
        .html(function(d) {
          if (d.column == 'ID') {
            if (interact){
              a = d.value.split("|").slice(0, 5);
              s = "";
              // <button type="button" class="btn btn-primary" data-toggle="modal" data-target=".bd-example-modal-lg" data-id="222">222</button>
              for (i = 0; i < a.length; i++) {
                s += '<button type="button" class="btn btn-outline-info" data-toggle="modal" data-target=".bd-example-modal-lg" data-id="' + a[i] + '">' + a[i] + '</button>';
              }
              return s;
            } else {
              return d.value;
            }
          }
          return d.value; // '<a href="'+d.value+'"'+'</a>';
        });

  if (cl != "tf0" && cl != "tfl") {
    $('.tab' + cl).ready(function() {
      $('.tab'+ cl).DataTable({"order": [[ 2, "asc" ]]});
    });
  }
  return table;
}

function update_progress(status_url, status_div) {
  // send GET request to status URL
  $.getJSON(status_url, function(data) {
    // update UI
    $(status_div.childNodes[0]).css("width", data['status']);
    $(status_div.childNodes[0]).text(data['status']+ " " + data['state']);

    if (data['state'] == 'Taskcompleted') {
      // show result
      $(status_div.childNodes[0]).text('100% done');

      $(".result").show(2000);
      $('.nav-tabs a[href="#tf"]').click(function(e){
        $('.active').removeClass("active");
        if ($('.tabtf').length == 0) {
         $(".tf").html($('<div class="col"><a href="' + data['result'] +'">download lisa beta results</a></div>'));
         d3.csv(data['result'], function(error, d) {
           tabulate('tf', d, ['TF', "ID", "p"], true, 'tf');
         });
        }
        $(this).tab('show');
      });

      $('.nav-tabs a[href="#tf0"]').click(function(e) {
        $('.active').removeClass("active");
        if ($('.tabtf0').length == 0) {
         $(".tf0").html($('<div class="col"><a href="' + data['result0'] +'">download epigenome sample coefficients</a></div>'));
         d3.csv(data['result0'], function(error, d) {
           tabulate('tf0', d,  ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue'], false, 'tf0');
         });
        }
         $(this).tab('show');
      });

      $('.nav-tabs a[href="#tf2"]').click(function(e){
        $('.active').removeClass("active");
        if ($('.tabtf2').length == 0) {
         $(".tf2").html($('<div class="col"><a href="' + data['result2'] +'">download motif ranking of TF result</a></div>'));
         d3.csv(data['result2'], function(error, d) {
           tabulate('tf2', d, ['TF', "ID", "p"], false, 'tf2');
         });
        }
        $(this).tab('show');
      });

      $('.nav-tabs a[href="#tf1"]').click(function(e) {
        $('.active').removeClass("active");
        if ($('.tabtf1').length == 0) {
         $(".tf1").html($('<div class="col"><a href="' + data['result1'] +'">download chip-seq ranking of TF result</a></div>'));
         d3.csv(data['result1'], function(error, d) {
           tabulate('tf1', d, ['TF', "ID", "p"], true, 'tf1');
         });
        }
        $(this).tab('show');
      });

      $('.nav-tabs a[href="#tfl"]').click(function(){
        $('.active').removeClass("active");
        if ($('iframe').length == 0) {
          $(".tfl").html($('<iframe width="1000" height="500" src="' + data['resultl'] + '"></iframe>'));
        }
        $(this).tab('show');
      });

      $('.bd-example-modal-lg').on('show.bs.modal', function (e) {
        var bookId = $(e.relatedTarget).data('id'); // this works
        $.getJSON('http://dc2.cistrome.org/api/inspector?id='+bookId, function(d) {
          modelc = $('<table class="table">' +
          '<thead><tr><th>Cell Line</th><th>Cell Type</th><th>Tissue</th><th>Paper</th></tr></thead>' +
          '<tbody><tr><td>' + d.treats[0].cell_line__name + '</td><td>' + d.treats[0].cell_type__name + '</td><td>' + d.treats[0].tissue_type__name + '</td><td>' + d.treats[0].paper__reference + '</td></tr></tbody>' +
                     '</table>');
          $(".modal-content").html( modelc );
          modelc = $('<table class="table">' +
          '<thead><tr><th>Mappable Reads</th><th>Mappable ratio</th><th>PBC</th><th>Peak number</th><th>FRiP</th><th>DHS ratio</th></tr></thead>' +
          '<tbody><tr><td>' + d.qc.table.map_number[0] + '</td><td>' + d.qc.table.map[0] + '</td><td>' + d.qc.table.pbc[0] + '</td><td>' + d.qc.table.peaks[0] + '</td><td>' + d.qc.table.frip[0] + '</td><td>' + d.qc.table.dhs + '</td></tr></tbody>' +
                     '</table>');
          $(".modal-content").append( modelc );
        });
      });
    } else {
      setTimeout(function() {
        update_progress(status_url, status_div);
      }, 1000);
    }
  });
}

function start_lisa_task(id) {
  $(".result").hide();
  // add task status elements
  div = $('<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div></div><hr>');

  $('.lisa_progress').append(div);

  $.ajax({
    type: 'POST',
    url: id,
    success: function(data, status, request) {
      update_progress(id, div[0]);
    },
    error: function() {
      alert('Unexpected error');
    }
  });
  // search interface
  // http://dc2.cistrome.org/api/main_filter_ng?cellinfos=all&completed=false&curated=false&factors=all&keyword=34330&page=1&run=false&species=all
  // http://dc2.cistrome.org/api/main_filter_ng?cellinfos=all&completed=false&curated=false&factors=all&keyword=&page=1&run=false&species=Homo%20sapiens&factors=AR
  // conservation interface
  // http://dc2.cistrome.org/api/conserv?id=2816
  // information interface
  // http://dc2.cistrome.org/api/inspector?id=2816
  // genome browser
  // http://dc2.cistrome.org/api/batchview/h/1792_8448/w/
}
