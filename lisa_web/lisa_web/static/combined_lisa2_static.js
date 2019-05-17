// The table generation function
function tabulate(cl, data, columns, interact) {
  var table = d3.select("." + cl).append("div");
  if (cl == 'tfcoef0' || cl == 'tfcoef') {
      table.attr("class", "col-sm-7");
  } else {
      table.attr("class", "col-sm-10");
  }

  var table = table.append("table")
        .attr("class", "table compact hover row-border tab" + cl),
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
        .data(data);

  var enter = rows.enter().append("tr");
  var update = rows.merge(enter);

  update.attr('data_id',
              function(d) {
                if (d.hasOwnProperty('coefficient')) {
                  return d.coefficient.split('|')[0];
                } else {
                  return "row";
                }
              });

  // create a cell in each row for each column
  var cells = enter.selectAll("td")
        .data(function(row) {
          return columns.map(function(column) {
            return {column: column, value: row[column]};
          });
        });

  var enterc = cells.enter().append("td");
  var updatec = cells.merge(enterc);

  enterc.html(function(d) {
    if (d.column != 'Transcription Factor') {
      if (interact){
        a = d.value;
        a = a.split(';');
        if (a.length == 2) {
          return a[1];
        } else {
          return d.value;
        } 
      } else {
        if (d.value.indexOf("http") !== -1) {
          aaa = d.value.split(".");
          return '<a href="' + d.value + '">' + aaa[aaa.length-2] + '</a>';
        }

        if (cl == "tf2" || cl == "tf2_1" || cl == "tf1_1") {
          if (d.value.split(';').length==2) {
            return d.value.split(';')[1] + "<img class='img-fluid' style='vertical-align:middle' height='36' width='60' src='http://lisa.cistrome.org/static/" + d.value.split(';')[0] + ".pwm.jpg'>";
          } else {
            return "";
          }
        } // for motifs 
        else {
          a = d.value.split('|');
          if (a.length == 2) {
            return a[1];
          } else {
            return d.value;
          }
        }
      }
    }
    return d.value;
  });

  updatec.attr("data_id",
               function(d) {
                 return d.value.split(';')[0].split('|')[0];
               });
  updatec.style({
    "vertical-align": "middle"
  });

  if (cl != "tfl") {
    if (cl != "tf2") {
       $('.tab' + cl).ready(function() {
         $('.tab'+ cl).DataTable({
           retrieve: true,
           // destroy: true,
           paging: true,
           "order": [],
           dom: 'Bfrtip',
           buttons: [
               'csv', 'excel', 'pdf'
           ]
         });
       });
    } else {
       $('.tab' + cl).ready(function() {
         $('.tab'+ cl).DataTable({
           "order": [],
           retrieve: true,
           // destroy: true,
           paging: true,
           dom: 'Bfrtip',
           buttons: [
               'csv', 'excel', 'pdf'
           ]
         });
       });
    }
  }
  return table;
}

function auc_curve(root, dom) {
  var margin = {top: 22, right: 30, bottom: 22, left: 30},
      width = 450 - margin.left - margin.right,
      height = 420 - margin.top - margin.bottom;

  var x = d3.scaleLinear().range([0, width]),
      y2 = d3.scaleLinear().range([height, 0]);
  x.domain([0,1]);
  y2.domain([0,1]);
  var data = new Array();
  
  for (var i = 0; i < root.fpr.length; i++) {
    var obj = {"fpr": root.fpr[i], "tpr": root.tpr[i]};
    data.push(obj);
  }

  var svg = d3.select(dom)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  var valueline = d3.line()
        .curve(d3.curveBasis)
        .x(function(d, i) { return x(d.fpr); })
        .y(function(d, i) { return y2(d.tpr); });

  var xAxis = d3.axisBottom(x).ticks(5);
  var yAxis = d3.axisLeft(y2).ticks(5);

  svg.append("path")
    .style("stroke", "steelblue")
    .style("stroke-width", "2.5px")
    .style("fill", "none")
    .attr("d", valueline(data));

  svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
  svg.append("g")
    .attr("class", "x axis")
    .call(yAxis);

  var legend = svg.append("g")
        .attr("transform", "translate(" + width/10 + "," + height/10 + ")");
  var formatNum = d3.format(".3");

  legend.append("rect")
    .attr("x", x(0)-margin.left+5)
    .attr("y", y2(1)-margin.top+5)
    .attr("fill", "steelblue")
    .attr("width", width/25)
    .attr("height", height/25);

  legend.append("text")
    .attr("x", x(0)- margin.left+25)
    .attr("y", y2(1)-margin.top+23)
    .attr("dy", "-0.51em")
    .attr("dx", "0.58em")
    .text("AUC:" + formatNum(root.performance));
}

function fetch(row, test_type) {
  if (test_type == 'motif') {
    $('td').click(function(e) {
      $(".annotation").html("");
      $(".annotation").append("<div><img class='img-fluid motifs' style='vertical-align:middle' height='240' width='320' src='http://lisa.cistrome.org/static/" + $(this).attr('data_id') + ".pwm.jpg'></div>");
      $(".motifs").ready(function(e) {
        $(".annotation").show(500);
      });
    })
    return false;
  }

  if (!row) {
    selector = "td";
  } else {
    selector = "tr";
  }
  $(selector).click(function(e) {
          var bookId = $(this).attr('data_id'); // this works
          $.getJSON('http://dc2.cistrome.org/api/inspector?id='+bookId, function(d) {

          $("body, html").animate({
            scrollTop: $('.annotation').offset().top - $('.dataTable').offset().top
          }, 600);

            $(".annotation").html("");
            conserv="http://dc2.cistrome.org/api/conserv?id="+bookId;
            color = {true: "green", false: "red", "NA": "gray"};

            if (d.treats[0].species__name == "Homo sapiens") {
               browser_sp = "hg38"
            } else {
               browser_sp = "mm10"
            }

            if (d.treats[0].unique_id.startsWith('GSM')) {
                link = 'https://www.ncbi.nlm.nih.gov/sra?term=' + d.treats[0].unique_id;
            } else {
                link = 'https://www.encodeproject.org/experiments/' + d.treats[0].unique_id.split('_')[0];
            }

            modelc = $('<div class="card"><div class="card-header"><div class="card-title"><h3><b>Inspector</b></h3></div></div><div class="card-body"><div class="row"><div class="col-sm-9"><div class="row inspector_attrib_row"><div class="col"><b>Title:</b></div><div class="col">' + d.treats[0].name + '</div></div>' + 
                       '<div class="row inspector_attrib_row"><div class="col"><b>GEO or ENCODE:</b></div><div class="col"><p class="tight-line">' + '<a href="' + link + '">' + d.treats[0].unique_id + '</a></div></div>' + 
                       '<div class="row inspector_attrib_row"><div class="col"><b>Species:</b></div><div class="col"><p>' + d.treats[0].species__name + '</p></div></div>' + 
                       '<div class="row inspector_attrib_row"><div class="col"><b>Citation:</b></div><div class="col"><p>' + d.treats[0].paper__reference + '</p>' +'PMID:' + '<a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=' + d.treats[0].paper__pmid + '">' + d.treats[0].paper__pmid + '</a></div></div>' + 
                       '<div class="row inspector_attrib_row"><div class="col"><b>Species:</b></div><div class="col"><p>' + d.treats[0].species__name + '</p></div></div>' + 
                       '<div class="row inspector_attrib_row"><div class="col"><b>Factor:</b></div><div class="col"><p>' + d.treats[0].factor__name + '</p></div></div>' +
                       '<div class="row inspector_attrib_row"><div class="col"><b>Biological Source:</b></div><div class="col"><p class="tight-line"><b>Cell Line:</b>' + d.treats[0].cell_line__name + '</p>' +  
                                        '<p class="tight-line"><b>Cell Type:</b>' + d.treats[0].cell_type__name + '</p>' + 
                                        '<p class="tight-line"><b>Tissue:</b>' + d.treats[0].tissue_type__name + '</p>' + 
                                        '<p class="tight-line"><b>Disease:</b>' + d.treats[0].disease_state__name + '</p></div></div></div>' + 
  '<div class="col-sm-3"><div class="row"><div class="col"><b>Quality Control</b></div></div>' + 
  '<div class="row"><div class="col">' + 
     '<div class="circle-col"><div class="circle ' + color[d.qc.judge.fastqc] + '"></div></div>' +
     '<div class="circle-col"><div class="circle ' + color[d.qc.judge.map] + '"></div></div>' +
     '<div class="circle-col"><div class="circle ' + color[d.qc.judge.pbc] + '"></div></div>' +
     '<div class="circle-col"><div class="circle ' + color[d.qc.judge.peaks] + '"></div></div>' +
     '<div class="circle-col"><div class="circle ' + color[d.qc.judge.frip] + '"></div></div>' +
     '<div class="circle-col"><div class="circle ' + color[d.qc.judge.dhs] + '"></div></div>' +
  '</div></div>' + 
  '<div class="row"><div class="col"><b>Visualize</b></div></div>' + 
  '<div class="row"><div class="col"><div class="btn-group">' + '<a target="_blank" id="genomebrowser-bw" type="button" class="btn btn-default button-list" href="http://epigenomegateway.wustl.edu/browser/?genome='+browser_sp+'&amp;datahub=http://dc2.cistrome.org/api/datahub/'+d.id+'&amp;gftk=refGene,full">WashU</a><a target="_blank" id="genomebrowser-bw" type="button" class="btn btn-default button-list" href="http://dc2.cistrome.org/api/hgtext/' + d.id + '/?db=' + browser_sp + '">UCSC</a></div></div></div>' + 
  '</div></div>');
  $(".annotation").append( modelc );
  modelc = $('<div class="card"><div class="card-header">Tool</div><div class="card-body"><table class="table">' +
                       '<thead><tr><th>QC</th><th>Value</th></tr></thead>' +
                       '<tbody><tr><td>Mappable Reads</td>' + '<td>' + d.qc.table.map_number[0] + '</td></tr>' + 
                       '<tr><td>Mappable ratio</td><td>' + d.qc.table.map[0] + '</td></tr>' +
                       '<tr><td>PBC</td><td>' + d.qc.table.pbc[0] + '</td></tr>' +
                       '<tr><td>Peak number</td><td>' + d.qc.table.peaks[0] + '</td></tr>' + 
                       '<tr><td>FRiP</td><td>' + d.qc.table.frip[0] + '</td></tr>' + 
                       '<tr><td>Peaks in promoter/exon/intron/intergenic</td><td>' + d.qc.table.meta + '</td><tr>' +
                       '<tr><td>DHS ratio</td><td>' + d.qc.table.dhs + '</td></tr>' +
                       '<tr><td>Converation plot</td><td><img class="img-fluid" height="400" width="400" src="' + conserv + '">' + '</td></tr></tbody>' +
                       '</table></div></div>');
   $(".annotation").append( modelc );
   if (d.motif) {
      console.log(d.motif_url);
      m = 'http://dc2.cistrome.org/'+d.motif_url;
      modelc = $('<div class="row"><iframe height="800" width="100%" src="' + m + '"></div>');
      $(".annotation").append( modelc );
   }
   $(".annotation").show(500);
   });
   });
   return true;
}

function multiple_request(url, index) {
      console.log(index);
      d3.csv(url, function(error, d) {
        if (error) {
          // this cause multiple dataTable rendering
          // setTimeout(function() {
          //   update_progress(status_url, status_div, div_heatmap_data);
          // }, 2000);
          // use queue instead
          setTimeout(function() {
              multiple_request(url, index);
          }, 3000);
          return null;
        }

        $(".tab-pane.active").ready(function() {
            tabulate(index, d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, index);
            fetch(false);
        });

        if ($('.tab'+index).length == 0) {
            tabulate(index, d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, index);
            fetch(false);
            multiple_request(url, index);
        }
        return true;
      });
      return true;
}

function update_progress(status_url, status_div, div_heatmap_data) {
  // send GET request to status URL
  $.getJSON(status_url, function(data) {
      $('.progress').hide();
      $(".result").show(500);
      $("h4").remove();

      // show figure results by default
      fig = data['result1_fig'];
      if (fig) {
        $(".tf1_fig").append($('<iframe frameBorder="0" width="100%" height="650" src="' + fig + '"></iframe>'));
      }
      fig = data['result2_fig'];
      if (fig) {
        $(".tf1_fig").append($('<iframe frameBorder="0" width="100%" height="650" src="' + fig + '"></iframe>'));
      }
      
      $('.leftpanel a[href="#tf1_fig"]').click(function(e){
        $(".annotation").hide();
      });

      d3.csv(data['result_2'], function(error, d) {
        tabulate('tf2', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, 'tf2'); 
        fetch(false);
        $('.dataTable').on('draw.dt', function() {
          fetch(false);
        });
      });
      $('.leftpanel a[href="#tf2"]').click(function(e) {
        $('.active').removeClass("active");
        $(".annotation").html("");
        $(this).tab('show');
      });

      d3.csv(data['result2_2'], function(error, d) {
        tabulate('tf2_1', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value"], false, 'tf2_1'); // "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"
        fetch(false, 'motif');
        $('.dataTable').on('draw.dt', function() {
          fetch(false, 'motif');
        });
      });
      $('.leftpanel a[href="#tf2_1"]').click(function(e){
        $('.active').removeClass("active");
        $(".annotation").hide();
        $(".annotation").html("");
        $(this).tab('show');
      });

      d3.csv(data['result'], function(error, d) {
        tabulate('tf1', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, 'tf1');
        fetch(false);
        $('.dataTable').on('draw.dt', function() {
          fetch(false);
        });
      });
      $('.leftpanel a[href="#tf1"]').click(function(e) {
       $('.active').removeClass("active");
       $(".annotation").hide();
       $(".annotation").html("");
       $(this).tab('show');
      });

      d3.csv(data['result2'], function(error, d) { 
        tabulate('tf1_1', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value"], false, 'tf1_1');
        fetch(false, 'motif');
        $('.dataTable').on('draw.dt', function() {
          fetch(false, 'motif');
        });
      });
      $('.leftpanel a[href="#tf1_1"]').click(function(e) {
        $('.active').removeClass("active");
        $(".annotation").hide();
        $(".annotation").html("");
        $(this).tab('show');
      });
   })
}

function start_lisa_task(id, div_heatmap_data) {
  // $(".result").hide();
  // add task status elements
  div = $('<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100"></div></div><hr>');

  $('.lisa_progress').append(div);

  $.ajax({
    type: 'GET',
    url: id,
    success: function(data, status, request) {
      update_progress(id, div[0]);
    },
    error: function() {
      alert('Unexpected error');
    }
  });
}

