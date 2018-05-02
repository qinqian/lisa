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
  // /data5/home/chenfei/JingyuFan/data_collection/MARGE/LISA_figures/human_ebi_random
  $(".gallery").ready({
    d3.csv('/gallery/lisa_results_meta_table_human_with_gene_sets.csv', function(error, d) {
      tabulate('gallery', d, ["Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value"], false, 'gallery');
    });
  });
};
