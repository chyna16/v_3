alert("hello");


document.getElementById("test").innerHTML = "Hello";

var data = [];
  {% for v in dataValue %} data.push({{v}}); {% endfor %};

var labels = [];
  {% for t in dataType %} labels.push("{{t}}"); {% endfor %};

var height = 300, width = 500;
var padding = 50;


function scatterPlot() {    
  var plot = d3.select("#wrapper").append('svg')
      .attr('id', 'plot')
      .attr('height', height + padding * 2)
      .attr('width', width + padding * 2)
      .style('padding', padding)
      .append('g')
      .attr('id', 'viz')
      .attr('transform', 'translate(' + padding + ',' + padding + ')');

  var yScale = d3.scale.linear().range([height, 10]);
  var xScale = d3.scale.ordinal().domain(labels).rangePoints([0, width]);

  var yDomain = [0, d3.max(data)]
  yScale.domain(yDomain);

  var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .ticks(6);
  var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left")
        .ticks(3);

  plot.append("g")
        .attr('class', 'y axis')
        .call(yAxis);
  plot.append("g")
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

  var dots = plot.selectAll('circle')
        .data(data)
        .enter()
        .append('circle');

  dots.attr('r', 5)
    .attr('cx', function(d, i) {
      return i * ((width/6) + 15) })
    .attr('cy', function(d) {
      return yScale(d) });
}

function barGraph() {
  var x = d3.scale.linear()
    .domain([0, d3.max(data)])
    .range([0, 420]);

  d3.select("#wrapper")
    .selectAll("div")
      .data(data)
    .enter().append("div")
      .style("width", function(d) { return x(d) + "px"; })
      .text(function(d) { return d; });
}