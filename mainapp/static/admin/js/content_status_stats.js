if (!$) {
    $ = django.jQuery;
}


$(document).ready(function() {
  $('.flex').before('<div id="chart" style="padding: 15px; width: 400px; height: 400px;"></div>');

  google.charts.load('current', {'packages':['corechart']});
  //google.charts.load('current', {'packages':['treemap']});
  google.charts.setOnLoadCallback(drawChart);
  function drawChart() {
    var stauses = ['New', 'Doit', 'Help', 'Good', 'Done'];

    var data_for_chart = [ ['Status', 'counts'] ];
    $.each(stauses, function( index, status_name ) {
      var items = $("td:nth-child(3):contains(" + status_name + ")");
      //console.log(items);
      data_for_chart.push([status_name, items.length]);
    });

    var data = google.visualization.arrayToDataTable(data_for_chart);

    var options = {
      title: 'Content Statuses Activities'
    };

    var chart = new google.visualization.PieChart(document.getElementById('chart'));

/*
        tree= new google.visualization.TreeMap(document.getElementById('chart'));

        tree.draw(data, {
          minColor: '#f00',
          midColor: '#ddd',
          maxColor: '#0d0',
          headerHeight: 15,
          fontColor: 'black',
          showScale: true
        });
*/
    chart.draw(data, options);
  }

});


