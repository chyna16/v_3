var keys = {{keys|safe}}; // an array of the data type in original order
var json_data = {{data|safe}}; // a dictionary w/ each key (data type) holding an array

var keys_len = keys.length;
var data_len = json_data[keys[0]].length;

// parses data from dictionary using keys and fills each row.col with values
var table = document.getElementById("tbody");
for (i = 0; i < data_len; i++) {
  var row = document.createElement("tr");
  for (j = 0; j < keys_len; j++) {
    var col = document.createElement("td");
    col.appendChild(document.createTextNode(json_data[keys[j]][i]));
    row.appendChild(col);
  }
  table.appendChild(row);
}

// sets the y-axis values for the graphs to whichever column the user selects
// calls function to create graph using the selected data
function chooseColumn(elem) {
  var key = elem.getAttribute('value');
  var y_values = json_data[key];

  createGraph(y_values);
  console.log(y_values);
}

// changes the display of corresponding graph to show or hide
function toggleGraph(elem) {
  var display_status = document.getElementById(elem.getAttribute('name')).style.display;

  if (display_status == "none") {
    document.getElementById(elem.getAttribute('name')).style.display = "block";
  }
  else {
    document.getElementById(elem.getAttribute('name')).style.display = "none";
  }
}

// graph dimensions that don't change
var margin = {top: 20, left: 50, right: 20, bottom: 130};
var height = 450 - margin.top - margin.bottom;
var width = 800 - margin.left - margin.right;
var padding = 1;

// this is called by chooseColumn() when the user selects data for y-axis
// NOTE: currently, only bar graph functions displays; needs to be modified
function createGraph(values) {
  d3.select("#wrapperBar").html("");
  d3.select("#wrapperPie").html("");
  d3.select("#wrapperScatter").html("");
    // .html("") causes the wrapper to be emptied out
    // this prevents copies from being made each time function is called
    // NOTE: this apparently does not work in Safari; fix later

///////////////////////////// B A R  G R A P H ///////////////////////////////
  var type = json_data[keys[0]];
  var vlength = values.length;

  var xScale = d3.scale.ordinal()
        .domain(type).rangePoints([0, width - (width / values.length)]);
  var yScale = d3.scale.linear()
        .domain([0, Math.max.apply(Math, values)]).range([height, 0]);

  var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .ticks(type.length);
  var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left")
        .ticks(values.length);

  var canvas = d3.select("#wrapperBar")
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var bar = canvas.selectAll("rect")
      .data(values)
      .enter()
        .append("rect")
        .attr("height", function(d) { return height - yScale(d); })
        .attr("width", width / vlength - padding)
        .attr("x", function(d, i) { return i * (width / vlength) })
        .attr("y", function(d) { return height - (height-yScale(d)) });

  canvas.selectAll("text")
      .data(values)
      .enter()
        .append("text")
        .attr("fill", "steelblue")
        .style("font-size", ".7em")
        .attr("x", function(d, i) { return i * (width/vlength) + (width/vlength) / 2})
        .attr("y", function(d) { return height - (height-yScale(d)) - 5 })
        .text(function(d) { return d; })
        .style("text-anchor", "middle");

  canvas.append("g")
        .attr('class', 'x axis')
        .attr('transform', 'translate(' + (width/vlength) / 2 + ',' + (height) + ')')
        .call(xAxis)
        .selectAll("text")  
        .style("text-anchor", "end")
        .attr("dx", "-1em")
        .attr("dy", ".15em")
        .attr("transform", function(d) { return "rotate(-65)"; })
        .style("font-size", ".7em")
        .attr("fill", "steelblue");

///////////////////////////// P I E  C H A R T /////////////////////////////// {
  // var arc = d3.svg.arc()
  //   .innerRadius(radius - 40)
  //   .outerRadius(radius);
  // var pie = d3.layout.pie()
  //     .padAngle(.02);
  // var color = d3.scale.category10();
  // var svg = d3.select("#wrapperPie").append("svg")
  //     .attr("width", width)
  //     .attr("height", height)
  //   .append("g")
  //     .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  // pieSVG.selectAll("path")
  //     .data(pie(values))
  //   .enter().append("path")
  //     .style("fill", function(d, i) { return color(i); })
  //     .attr("d", arc);
// }

////////////////////////// S C A T T E R  P L O T //////////////////////////// {
  // FIX: summary.csv shows a skewed range
  // FIX: automated spacing between plot points
  // var plot = d3.select("#wrapperScatter").append('svg')
  //     .attr('id', 'plot')
  //     .attr('height', height + padding * 2)
  //     .attr('width', width + padding * 2)
  //     .style('padding', padding)
  //     .append('g')
  //     .attr('id', 'viz')
  //     .attr('transform', 'translate(' + padding + ',' + padding + ')');

  // var xScale = d3.scale.ordinal().domain(type).rangePoints([0, width]);
  // var yScale = d3.scale.linear().range([height, 10]);
  // var yDomain = [0, d3.max(value)]
  // yScale.domain(yDomain);

  // var xAxis = d3.svg.axis()
  //       .scale(xScale)
  //       .orient("bottom")
  //       .ticks(6);
  // var yAxis = d3.svg.axis()
  //       .scale(yScale)
  //       .orient("left")
  //       .ticks(3);

  // plot.append("g")
  //       .attr('class', 'y axis')
  //       .call(yAxis);
  // plot.append("g")
  //       .attr('class', 'x axis')
  //       .attr('transform', 'translate(0,' + height + ')')
  //       .call(xAxis);

  // var dots = plot.selectAll('circle')
  //       .data(value)
  //       .enter()
  //       .append('circle');

  // dots.attr('r', 5)
  //   .attr('cx', function(d, i) {
  //     return i * 20 })
  //   .attr('cy', function(d) {
  //     return yScale(d) });
// }
}

// called when user clicks "Back" button
function goBack() {
    window.history.back();
}