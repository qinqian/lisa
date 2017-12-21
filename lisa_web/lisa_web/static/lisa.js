// The table generation function
function tabulate(cl, data, columns, interact) {
  var table = d3.select("." + cl).append("table")
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
        .style({
          "vertical-align": "middle"
        })
        .attr({
          data_id: function(d) { return d.value.split(';')[0].split('|')[0]; }
        })
        .html(function(d) {
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
              if (cl == "tf2") {
                if (d.value.split(';').length==2) {
                    return d.value.split(';')[1] + "<img class='img-fluid' style='vertical-align:middle' height='39' src='http://lisa.cistrome.org/static/" + d.value.split(';')[0] + ".pwm.jpg'>";
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

  if (cl != "tfl") {
  
    if (cl != "tf2") {
       $('.tab' + cl).ready(function() {
         $('.tab'+ cl).DataTable({
           "order": [],
         });
       });
    } else {
       $('.tab' + cl).ready(function() {
         $('.tab'+ cl).DataTable({
           "order": [],
           "columnDefs": [
              { "width": "20%", "targets": 0 }
           ]
         });
       });
    }
  }
  return table;
}

function update_progress(status_url, status_div, div_heatmap_data) {
  // send GET request to status URL
  $.getJSON(status_url, function(data) {
    // update UI
    $(status_div.childNodes[0]).css("width", data['status']);
    $(status_div.childNodes[0]).text(data['status']+ " " + data['state']);

    if (data['state'] == 'Taskcompleted') {
      // show result
      // $(status_div.childNodes[0]).text('100% done');
      $('.progress').hide();
      $(".result").show(2000);

      $('.nav-tabs a[href="#tfheat"]').click(function(e){
        $(".annotation").html("");
        $('.active').removeClass("active");
        var hzome = ini_hzome();
        make_clust(div_heatmap_data); // 'mult_view.json'

        var about_string = 'Zoom, scroll, and click buttons'; //  to interact with the clustergram. <a href="http://amp.pharm.mssm.edu/clustergrammer/help"> <i class="fa fa-question-circle" aria-hidden="true"></i> </a>';

        function make_clust(inst_network){

          d3.json(inst_network, function(network_data){

            // define arguments object
            var args = {
              root: '#container-id-1',
              'network_data': network_data,
              'about':about_string,
              'row_tip_callback':hzome.gene_info,
              'col_tip_callback':test_col_callback,
              'tile_tip_callback':test_tile_callback,
              'dendro_callback':dendro_callback,
              'matrix_update_callback':matrix_update_callback,
              'cat_update_callback': cat_update_callback,
              'sidebar_width':150,
              // 'ini_view':{'N_row_var':20}
              // 'ini_expand':true
            };

            resize_container(args);

            d3.select(window).on('resize',function(){
              resize_container(args);
              cgm.resize_viz();
            });

            cgm = Clustergrammer(args);

            check_setup_enrichr(cgm);

            d3.select(cgm.params.root + ' .wait_message').remove();
          });

        }

        function matrix_update_callback(){

          if (genes_were_found[this.root]){
            enr_obj[this.root].clear_enrichr_results(false);
          }
        }

        function cat_update_callback(){
          console.log('callback to run after cats are updated');
        }

        function test_tile_callback(tile_data){
          var row_name = tile_data.row_name;
          var col_name = tile_data.col_name;

        }

        function test_col_callback(col_data){
          var col_name = col_data.name;
        }

        function dendro_callback(inst_selection){

          var inst_rc;
          var inst_data = inst_selection.__data__;

          // toggle enrichr export section
          if (inst_data.inst_rc === 'row'){
            d3.select('.enrichr_export_section')
              .style('display', 'block');
          } else {
            d3.select('.enrichr_export_section')
              .style('display', 'none');
          }

        }

        function resize_container(args){

          var screen_width = window.innerWidth;
          var screen_height = window.innerHeight - 20;

          d3.select(args.root)
            .style('width', screen_width+'px')
            .style('height', screen_height+'px');
        }

        $(this).tab('show');
      });


      $('.nav-tabs a[href="#tf"]').click(function(e){
        $('.active').removeClass("active");
        $(".annotation").hide();
        $(".annotation").html("");
        if ($('.tabtf').length == 0) {
         $(".tf").html($('<div class="col"><a href="' + data['result'] +'">download lisa beta results</a></div>'));
         d3.csv(data['result'], function(error, d) {
           tabulate('tf', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, 'tf');
           fetch();
         });
        }
        $(this).tab('show');
      });

      $('.nav-tabs a[href="#tf0"]').click(function(e) {
        $('.active').removeClass("active");
        $(".annotation").hide();
        $(".annotation").html("");

        if ($('.tabtf0').length == 0) {
         $(".tf0").html($('<div class="col"><a href="' + data['result0'] +'">download epigenome sample coefficients</a></div>'));
         d3.csv(data['result0'], function(error, d) {
           tabulate('tf0', d,  ['coefficient', 'cell_type', 'cell_line', 'tissue'], false, 'tf0');
           fetch();
         });
        }
        $(this).tab('show');
      });

      var fetch = function() {
        $("td").click(function(e) {
          var bookId = $(this).attr('data_id'); // this works
          $.getJSON('http://dc2.cistrome.org/api/inspector?id='+bookId, function(d) {
            $(".annotation").html("");
            conserv="http://dc2.cistrome.org/api/conserv?id="+bookId;
            color = {true: "green", false: "red", "NA": "gray"}

            modelc = $('<div class="card"><div class="card-header"><div class="card-title"><h3><b>Inspector</b></h3></div></div><div class="card-body"><div class="row"><div class="col-sm-9"><div class="row inspector_attrib_row"><div class="col"><b>Title:</b></div><div class="col">' + d.treats[0].name + '</div></div>' + 
                       '<div class="row inspector_attrib_row"><div class="col"><b>GEO:</b></div><div class="col"><p class="tight-line">' + '<a href="https://www.ncbi.nlm.nih.gov/sra?term=' + d.treats[0].unique_id + '">' + d.treats[0].unique_id + '</a></div></div>' + 
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
  '<div class="row"><div class="col"><div class="btn-group">' + '<a target="_blank" id="genomebrowser-bw" type="button" class="btn btn-default button-list" href="http://epigenomegateway.wustl.edu/browser/?genome=hg38&amp;datahub=http://dc2.cistrome.org/api/datahub/'+d.id+'&amp;gftk=refGene,full">WashU Browser</a><a target="_blank" id="genomebrowser-bw" type="button" class="btn btn-default button-list" href="http://dc2.cistrome.org/api/hgtext/' + d.id + '/?db=hg38">UCSC Browser</a></div></div></div>' + 
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
      };

      $('.nav-tabs a[href="#tf2"]').click(function(e){
        $('.active').removeClass("active");
        $(".annotation").html("");

        if ($('.tabtf2').length == 0) {
         $(".tf2").html($('<div class="col"><a href="' + data['result2'] +'">download motif ranking of TF result</a></div>'));
         d3.csv(data['result2'], function(error, d) {
           tabulate('tf2', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value"], false, 'tf2'); // "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"
         });
        }
        $(this).tab('show');
      });

     $(".tf1").ready(function() {
        $(".tf1").html($('<div class="col"><a href="' + data['result1'] +'">download chip-seq ranking of TF result</a></div>'));
        d3.csv(data['result1'], function(error, d) {
          tabulate('tf1', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, 'tf1');
          fetch();
        });
     })

     $('.nav-tabs a[href="#tf1"]').click(function(e) {

      $('.active').removeClass("active");
      $(".annotation").hide();
        $(".annotation").html("");
      if ($('.tabtf1').length == 0) {
        $(".tf1").html($('<div class="col"><a href="' + data['result1'] +'">download chip-seq ranking of TF result</a></div>'));
        d3.csv(data['result1'], function(error, d) {
          tabulate('tf1', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], true, 'tf1');
          fetch();
        });
      }
      $(this).tab('show');
    });

    $('.nav-tabs a[href="#tfl"]').click(function(){
        $('.active').removeClass("active");
        $(".annotation").hide();
        $(".annotation").html("");
        if ($('iframe').length == 0) {
          $(".tfl").html($('<iframe width="100%" height="800" src="' + data['resultl'] + '"></iframe>'));
        }
        $(this).tab('show');
      });
      // $('.bd-example-modal-lg').on('show.bs.modal', function (e) {
      //   $(".modal-content").html("");
      //   var bookId = $(e.relatedTarget).data('id'); // this works
      //   $.getJSON('http://dc2.cistrome.org/api/inspector?id='+bookId, function(d) {
      //     modelc = $("<h1>" + d.treats[0].name + "</h1>");
      //     $(".modal-content").html(modelc)
      //     modelc = $('<table class="table">' +
      //     '<thead><tr><th>Factor</th><th>Cell Line</th><th>Disease</th><th>Cell Type</th><th>Tissue</th><th>Paper</th><th>GEO ID</th><th>PMID</th></tr></thead>' +
      //     '<tbody><tr><td>' + d.treats[0].factor__name + '</td><td>' + d.treats[0].cell_line__name + '</td><td>' + d.treats[0].disease_state__name + '</td><td>' + d.treats[0].cell_type__name + '</td><td>' + d.treats[0].tissue_type__name + '</td><td>' + d.treats[0].paper__reference + '</td><td>' + d.treats[0].unique_id + '</td><td>' + d.treats[0].paper__pmid + '</td></tr></tbody>' +
      //                '</table>');
      //     $(".modal-content").append( modelc );
      //     modelc = $('<table class="table">' +
      //     '<thead><tr><th>Mappable Reads</th><th>Mappable ratio</th><th>PBC</th><th>Peak number</th><th>FRiP</th><th>Peaks in promoter/exon/intron/intergenic</th><th>DHS ratio</th></tr></thead>' +
      //     '<tbody><tr><td>' + d.qc.table.map_number[0] + '</td><td>' + d.qc.table.map[0] + '</td><td>' + d.qc.table.pbc[0] + '</td><td>' + d.qc.table.peaks[0] + '</td><td>' + d.qc.table.frip[0] + '</td><td>' + d.qc.table.meta + '</td><td>' + d.qc.table.dhs + '</td></tr></tbody>' +
      //                '</table>');
      //     $(".modal-content").append( modelc );
      //     conserv="http://dc2.cistrome.org/api/conserv?id="+bookId;
      //     modelc = $('<img src="' + conserv + '">');
      //     $(".modal-content").append( modelc );
      //     if (d.motif) {
      //       console.log(d.motif_url);
      //       m = 'http://dc2.cistrome.org/'+d.motif_url;
      //       modelc = $('<iframe src="' + m + '">');
      //       $(".modal-content").append( modelc );
      //     }
      //   });
      // });
    } else {
      setTimeout(function() {
        update_progress(status_url, status_div, div_heatmap_data);
      }, 2000);
    }
  });
}

function start_lisa_task(id, div_heatmap_data) {
  // $(".result").hide();
  // add task status elements
  div = $('<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div></div><hr>');

  $('.lisa_progress').append(div);

  $.ajax({
    type: 'POST',
    url: id,
    success: function(data, status, request) {
      update_progress(id, div[0], div_heatmap_data);
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
