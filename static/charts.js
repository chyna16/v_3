"use strict";

// Function that handles setup and drawing of each type of analysis
function createGraph(data, analysis) {
  var color = d3.scale.category20();
  //d3.select('#wrapper').html('')

  switch (analysis){
    case 'cloud':
      createWordcloud(data);
      break;
    case 'coupling':
      // if coupling, graph is not created until chooseModule is called
      json_data.forEach(function(d) {
        if (!entity_list[d.entity]) {
          entity_list[d.entity] = {degree: d.degree, 'average-revs': d['average-revs']};
        }
        if (!entity_list[d.coupled]) {
          entity_list[d.coupled] = {degree: d.degree, 'average-revs': d['average-revs']};
        }
      })

      configureDivCoupling()
      createHeader(color);
      createTable(entity_list)
      d3.select("#wrapper")
        .html('<p>Choose an enitity to view degree of coupling.</p>');
      break;
    case 'complexity':
      createHeader(color);
      createLineGraph(data);
      createTable(data)
      break;
    case 'churn':
      createScatterPlot(data);
      createTable(data)
      break;
    case 'hotspots':
      createHeader(color);
      createBubblePack(data);
      createTable(data)
      break;
    case 'metrics':
      createBarGraph(data);
      createTable(data)
      break;
    default:
      createBarGraph(data);
      createTable(data)
      break;
  }
}

function createHeader(color) {
    var header = d3.select("#header").html('').append("p");

    if (analysis_type !== "churn" && analysis_type !== "hotspots"){
      header
        .selectAll("button")
            .data(keys.filter(function(key) {
                if (analysis_type == "complexity")
                    { return key != keys[0] && key != keys[1]
                        && key != keys[6] && key != 'coupled'}
                else { return key != keys[0] && key != 'coupled' };}))
            .enter()
        .append("button")
        .attr('class', 'btn')
        .text(function(d) { return d; })
        .style('background-color', function(d) { return color(d); })
        .style('color', 'white')
        .style('margin', '10px')
        .attr('value', function(d) { return d; })
        .on('click', function() { chooseColumn(this); });

      if (analysis_type != 'coupling' && analysis_type != 'complexity') {
          header.append("button")
              .attr('class', 'btn')
              .text('all')
              .style('background-color', 'black')
              .style('color', 'white')
              .style('margin', '10px')
              .attr('value', 'default')
              .on('click', function() { chooseColumn(this); });
      }
  }
  if (analysis_type != 'complexity' && analysis_type != 'coupling') {
    header.append("button")
      .attr('class', 'btn')
      .text('add filter')
      .style('background-color', 'grey')
      .style('color', 'white')
      .style('margin', '10px')
      .on('click', function() { toggleFilter(); });
    }


}


function createLineGraph(data){
    d3.select("#wrapper").html('Select a module from the dropdown list above.');
    var stage = []
    var arr = []
    data.map(function(d) {
        if (stage.indexOf(d[keys[0]]) == -1){
          stage.push(d[keys[0]])
        }
        else if (arr.indexOf(d[keys[0]]) == -1){
          arr.push(d[keys[0]])
        }
      })

    var w;
    var width=900;
    var margin = {top: 20, left: 70, right: 20, bottom: 130};
    var height = 450 - margin.top - margin.bottom;
    var color = d3.scale.ordinal().domain(keys).range(["#6d9af6", "#52465f"]);

    if (chosen_key == 'default') {
        var labels = keys.filter(function(key) {
            return key !== keys[0] && key !== 'values' && key !== 'coupled'
            && key !== 'rev' && key !== 'date';
            // keys that would not make appropriate columns are filtered out
        });
    }
    else {
        var labels = keys.filter(function(key) { return key == chosen_key; });
    }

    var formatDate = d3.time.format("%Y-%m-%d %X %Z");

    var x = d3.time.scale()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0])
        .domain([0, d3.max(filtered_data, function(d) { return d.value; })]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .innerTickSize(-height)
        .outerTickSize(10)
        .tickPadding(10)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .innerTickSize(-width)
        .outerTickSize(10)
        .orient("left");

function updateData(data, name, button){
    d3.select("#wrapper").html('');
    var filtered_data = (data.filter(function(d) { return d.name == name;}))
    var line = d3.svg.line()
        // .interpolate("basis")
        .x(function(d) { return x(formatDate.parse(d.date)); })
        .y(function(d) { return y(d[button]); });

    var svg = d3.select("#wrapper")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      x.domain(d3.extent(filtered_data, function(d) { return formatDate.parse(d.date); }));
      y.domain(d3.extent(filtered_data, function(d) { return +d[button]; }));

      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .style("font-size", "14px")
          .text("'" + button + "'");

      svg.append("path")
          .datum(filtered_data)
          .attr("class", "line")
          .attr("d", line);

        if (chosen_key == 'default') {
            var labels = keys.filter(function(key) {
                return key !== keys[0] && key !== 'values' && key !== 'coupled'
                && key !== 'rev' && key !== 'date';
                // keys that would not make appropriate columns are filtered out
            });
        }
        else {
            // if a column was specified, only the data from that column is used
            var labels = keys.filter(function(key) { return key == chosen_key; });
        }

        // a values object is appended to each object (row) in the data
        // values itself has an object for each column in labels
        filtered_data.forEach(function(d, i) {
            delete d.values; // delete data from previous renditions of the graph
            d.values = labels.map(function(label) {
                return {entity: d.name, type: label, value: +d[label]};
            });
        });

      x.domain(d3.extent(filtered_data, function(d) { return formatDate.parse(d.date); }));
      y.domain(d3.extent(filtered_data, function(d) { return +d[button]; }));
    }
        d3.select("#header")
        .append("select")
        .selectAll("option")
        .data(arr)
        .enter()
        .append("option")
        .text(function(d) { return d; });

     var buttonValue = 'n'
     var nameof;
        d3.select('select')
            .on("change", function(){
                var key = this.selectedIndex
                nameof = (arr[key])
                updateData(data, nameof, buttonValue)
            })

        d3.select("#header")
        .selectAll(".btn")
        .on('click', function() {
            buttonValue = this.value
            updateData(data, nameof, buttonValue);
        });

  updateData(data, arr[0], buttonValue)
}


function createBarGraph(data) {
    d3.select("#wrapper").html('');
        // .html("") causes the wrapper to be emptied out
        // this prevents copies from being made each time function is called
    var w;
    var width;
    var margin = {top: 20, left: 70, right: 20, bottom: 150};
    var height = 480 - margin.top - margin.bottom;
    var color = d3.scale.ordinal().domain(keys).range(["#6d9af6", "#52465f"]);

    if (data.length > 50) { w = data.length * 20; }
    else if (data.length < 10) { w = data.length * 100; }
    else { w = 1000; }
    width = w - margin.left - margin.right;

    if (chosen_key == 'default') {
        // if no column was specified, the data from all value columns is used
        var labels = keys.filter(function(key) {
            return key !== keys[0] && key !== 'values' && key !== 'coupled';
            // keys that would not make appropriate columns are filtered out
        });
    }
    else {
        // if a column was specified, only the data from that column is used
        var labels = keys.filter(function(key) { return key == chosen_key; });
    }

    // a values object is appended to each object (row) in the data
    // values itself has an object for each column in labels
    data.forEach(function(d, i) {
        delete d.values; // delete data from previous renditions of the graph
        d.values = labels.map(function(label) {
            return {entity: d.entity, type: label, value: +d[label]};
        });
    });

    // the scale for each category of bars (each row)
    var x0Scale = d3.scale.ordinal()
        // .domain(data.map(function(d) { return d.entity.split('/').pop(); }))
            // array of entities
        .domain(d3.range(0, data.length))
        .rangeBands([0, width], .05);

    // the scale for individual bars within each category
    var x1Scale = d3.scale.ordinal()
        .domain(labels) // array of columns being used
        .rangeBands([0, x0Scale.rangeBand()]); // from 0 to category size

    // the proportional scale for the height of the bars
    var yScale = d3.scale.linear()
        .range([height, 0])
        .domain([0, d3.max(data, function(d) {
            return d3.max(d.values, function(d) { return d.value; });
        })]); // max int from out of all columns being displayed

    // axes decleration using d3 axis() method
    var xAxis = d3.svg.axis()
        .scale(x0Scale)
        .tickFormat(function(d, i) { return data[i].entity.split('/').pop(); })
        .orient("bottom");
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");

    var tip = d3.tip()
      .attr('class', 'd3-tip')
      .offset([-10, 0])
      .html(function(d) {
        return "<center>" + "<strong>"
            + d.entity + "<br>"
            + d.type + ":</strong> <span style='color:red'>"
            + d.value + "</span>" + "</center>";
      });

    // appending the general svg as well as the div for the graph itself
    var canvas = d3.select("#wrapper")
        .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    // category represents each module/row; one category per object in the data
    var category = canvas.selectAll(".category")
            .data(data)
            .enter()
        .append("g")
            .attr("class", "category")
            .attr("transform", function(d, i) {
                return "translate(" + x0Scale(i) + ",0)";
            });

    // bars appended to each category depending on how many columns are being displayed
    var bar = category.selectAll("rect")
            .data(function(d) { if (typeof d.values != 'undefined') return d.values; })
            .enter()
        .append("rect")
            .attr("class", "bar")
            .style("fill", function(d) { return color(d.type); })
            .call(tip)
            .on('mouseover', function(d){
                tip.show(d);
                d3.select(this)
                    .style("fill", "red");
                })
            .on('mouseout', function(d){
                tip.hide(d);
                d3.select(this)
                    .style("fill", function(d) { return color(d.type); });
                })
            .attr("height", 0)
            .attr("width", x1Scale.rangeBand())
            .attr("x", function(d) { return x1Scale(d.type); })
            .attr("y", height);

    bar.transition().duration(900)
            .attr("height", function(d) { return height - yScale(d.value); })
            .attr("y", function(d) { return yScale(d.value); });
        //labels dont display with this + transition enabled
        // .append("svg:title")
            // .text(function(d) { return d.value; });

        /*labels hide all text
        d3.select("button").on("click", function(d) {
            var current_display = d3.select("text").style("display");
            if (current_display == "block") {
                d3.select(this).text("Show Labels")
                d3.selectAll("text").style("display", "none");
            } else {
                d3.select(this).text("Hide Labels");
            d3.selectAll("text").style("display","block");
        }
        });
        */

    // appending and styling of x-axis to graph
    canvas.append("g")
        .attr('class', 'axis')
        .attr('transform', 'translate(0,' + (height) + ')')
        .call(xAxis)
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-1em")
            .attr("dy", ".05em")
            .attr("transform", function(d) { return "rotate(-55)" })
            .style("font-size", ".7em")
            .attr("fill", "#325a7e");

    // appending and styling of y-axis to graph
    canvas.append("g")
        .attr('class', 'axis')
        .attr('transform', 'translate(0, 0)')
        .call(yAxis)
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-1em")
            .attr("dy", ".15em")
            .style("font-size", ".8em")
            .attr("fill", "#325a7e");

    createHeader(color);
}

function createScatterPlot(data){
  d3.select("#wrapper").html('');

  var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 900 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom,
    duration_time = 700;

  var x_scale = d3.scale.linear().range([0,width]);
  var y_scale = d3.scale.linear().range([height,0]);

  var color = "#1ab7ea"

  var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d) {
      return "<p>File: " + d.id +
        "</p><p>Lines Added: " + d.added +
        "</p><p>Lines Removed: " + d.deleted + "</p>";
    })

  var x_axis = d3.svg.axis()
    .scale(x_scale)
    .innerTickSize(-height)
    .outerTickSize(10)
    .orient("bottom");

  var y_axis = d3.svg.axis()
    .scale(y_scale)
    .innerTickSize(-width)
    .outerTickSize(10)
    .orient("left");

  var svg = d3.select("#wrapper").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .call(tip)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("g")
    .attr("transform", "translate(0,"+ height +")")
    .attr("class", "axis")
    .attr("id", "x_axis")
    .append("text")
      .attr("class", "label")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("Added");

  svg.append("g")
    .attr("class", "axis")
    .attr("id", "y_axis")
    .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Removed");

  function update(arr_data) {
    //Format Data
    data = {};
    arr_data.forEach(function(d) {
      data[d.entity] = { id: d.entity };
      data[d.entity]["added"] = d["added"];
      data[d.entity]["deleted"] = d["deleted"];
    });

    var cAddMax = d3.max(d3.values(data), function(d) { return parseInt(d.added); });
    var cDelMax = d3.max(d3.values(data), function(d) { return parseInt(d.deleted); });
    function scaleColor(point) {
      var add = parseInt(point.added) / cAddMax;
      var del = parseInt(point.deleted) / cDelMax;
      return add + del;
    }

    color = d3.scale.linear().domain([0,1]).range(["#1ab7ea", "red"]);

    //Calc X and Y scale
    x_scale.domain([0,d3.max(d3.values(data), function(d) {
      return d["added"]*1.1;
    })]);
    y_scale.domain([0,d3.max(d3.values(data), function(d) {
      return d["deleted"]*1.1;
    })]);

    // update axis accordingly
    d3.select("g#x_axis")
      .transition()
      .duration(duration_time)
      .call(x_axis);

    d3.select("g#y_axis")
      .transition()
      .duration(duration_time)
      .call(y_axis);

    //enter new nodes
    var data_to_draw = d3.values(data).filter(function(d) {
      return true;
    });
    var node_g = svg.selectAll("g.node")
      .data(d3.values(data_to_draw));

    //enter our groups
    var node_g_enter = node_g.enter()
      .append("g")
      .attr("class", "node");

    // Enter circles nested within our group
    node_g_enter.append("circle");

    // update currently existing nodes
    var count = d3.values(data_to_draw).length;
    node_g
        .select("circle")
        .transition()
        .duration(duration_time)
        .delay(function(d,i) {
          return i / count * duration_time;
        })
        .attr("cx", function(d) { return x_scale(d["added"]); })
        .attr("cy", function(d) {
          if (d["deleted"]){
            return y_scale(d["deleted"]);
          }
          return y_scale.range()[0];
        });
    node_g. select("circle")
        .attr("r", 5)
        .attr("fill", function(d) {
            return color(scaleColor(d));
        })
        .on("mouseover", tip.show)
        .on("mouseout", tip.hide);

        //Exit old nodes
        var exit_node_gs = node_g.exit();

        exit_node_gs.transition().delay(duration_time * 3).remove();

        exit_node_gs.select("circle")
          .transition()
          .delay(duration_time * 2)
          .ease("bounce")
          .duration(duration_time)
          .attr("cy", y_scale.range()[0]);

  }
  update(data);
  createHeader(color);
}

function createBubblePack(inputData) {
    // Clear wrapper html
    d3.select("#wrapper").html('');

    // Create deep copy of inputData
    var data = inputData.slice(0);

    var margin = 20,
        diameter = 610,
        // Variable k is needed as a global scaling factor for textfit
        k=1;

    // Establish color scales
    var color = d3.scale.linear()
        .domain([0, 5])
        .range(["#1ab7ea", "#0B108C"])

    var colorHotspot = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return +d['n-revs']; })])
        .range(["#ffb3b3", "#e60000"]);

    // Create Tooltip
    var tip = d3.tip()
        .attr('class', "d3-tip")
        .direction('e')
        .offset([0, 10])
        .html(function(d) {
            return "<p>File: <text style='color:red'>" + d.data["entity"]
                + "</p>" + "<p>Revisions: " + d.data["n-revs"] + "</p>"
                + "<p>Lines: " + d.data["lines"] + "</p>";
        });

    // Set Pack settings
    var pack = d3.layout.pack()
        .padding(2)
        .size([diameter - margin, diameter - margin])

    var svg = d3.select("#wrapper").append("svg")
        .attr("width", diameter)
        .attr("height", diameter)
        .append("g")
        .attr("transform", "translate(" + diameter/2 + "," + diameter/2 + ")");

    // Process data in order to create tree structure out of file structure
    data.forEach(function(d){
        // Add repo name to path to create parent node
        d["full-path"] = repo + "/" + d["entity"];
        // Split off file name and create internal nodes
        var splitItem =  d["full-path"].substring(0, d["full-path"].lastIndexOf("/"));
        if (data.filter(function(a){ return a["full-path"] == splitItem })[0] == undefined) {
            var pieces = splitItem.split('/');
            var insertion = '';
            for (var i=0; i<pieces.length; i=i+1){
                insertion += pieces[i]
                if(data.filter(function(a){ return a["full-path"] == insertion })[0] == undefined) {
                    data.push({"full-path": insertion});
                }
                insertion += "/";
            }
        }
    });

    var stratify = d3.stratify()
        .id(function(d) { return d["full-path"]; })
        .parentId(function(d) {
            var splitItem =  d["full-path"].substring(0, d["full-path"].lastIndexOf("/"));
            return splitItem;
        });

    data.sort(function(a,b){
        var nameA=a["full-path"], nameB=b["full-path"];
        //sort string ascending
        if (nameA < nameB)
            return -1;
        if (nameA > nameB)
            return 1;
        //default return value (no sort)
        return 0;
    });

    // Create tree structure
    var root = stratify(data)
        .sum(function(d) { return d.lines; })
        .sort(function(a, b) { return b.lines - a.lines; });

    // Create visualization
    var focus = root,
    nodes = pack.nodes(root),
    view;

    var circle = svg.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("class", function(d) { return d.parent ? d.children ? "node node--middle" : "node node--leaf" : "node node--root"; })
        .style("fill", function(d) { return d.children ? color(d.depth) : colorHotspot(d.data["n-revs"]); })
        .on("click", function(d) {
            if (focus !== d) zoom(d), d3.event.stopPropagation();
        });

    var text = svg.selectAll("text")
        .data(nodes)
        .enter().append("text")
        .attr("class", "label")
        .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
        .text(function(d) { return d.id.substring(d.id.lastIndexOf("/") + 1).split(/(?=[A-Z][^A-Z])/g); })
        .style("visibility", function(d) { return (d.parent === root && labelFit(d,this)) ? "visible" : "hidden"; });

    var node = svg.selectAll("circle,text");

    d3.select("#wrapper")
        //.style("background", color(-1))
        .on("click", function() { zoom(root); });

    svg.selectAll("circle.node--leaf")
        .call(tip)
        .on("mouseover", tip.show)
        .on("mouseout", tip.hide);

    zoomTo([root.x, root.y, root.r * 2 + margin]);

    function zoom(d) {
        var focus0 = focus;
        focus = d;

        // Auto-skip folders with one child
        while(focus.children !== undefined && focus.children[0].children !== undefined && focus.children.length == 1) {
            focus = focus.children[0];
        }

        if (d.children !== undefined) {
            var transition = d3.transition()
                .duration(d3.event.altKey ? 7500 : 750)
                .tween("zoom", function(d) {
                  var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
                  return function(t) { zoomTo(i(t)); };
            });

            transition.selectAll("text")
                .filter(function(d) {
                    if(d == undefined) return false;
                    return (d.parent === focus || this.style.visibility === "visible");
                })
                .style("fill-opacity", function(d) { return (d.parent === focus) ? 1 : 0; })
                .each("end", function(a) {
                    if (a.parent === focus && labelFit(a,this)) this.style.visibility = "visible";
                    if (a.parent !== focus || !labelFit(a,this)) this.style.visibility = "hidden"; });
        }
    }

    function zoomTo(v) {
        k = diameter / v[2]; view = v;
        node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
        circle.attr("r", function(d) { return d.r * k; })
            .style("pointer-events", function(d) { return (d.parent === focus) ? "auto" : "none"; });
    }

    function labelFit(nodeElement, textElement) {
        //TODO Firefox Compatibility
            var widthBBox = textElement.getBBox().width;
            var widthNodeE = nodeElement.r*2*k
            return (widthBBox <= widthNodeE);

    }

    d3.select(self.frameElement).style("height", diameter + "px");
}

function createBubbleChart(data) {
    d3.select("#wrapper").html('');

    var diameter = 700;

    // scale for assigning color to bubbles
    var color = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return +d['n-revs']; })])
        .range(["#ffb3b3", "#e60000"]); // from light red to bright red

    // layout.pack organizes elements together while avoiding overlap
    var chart = d3.layout.pack()
        .sort(null)
        .size([diameter, diameter])
        .padding(1.5);

    data.forEach(function(d) { d.value = +d['lines']; })
        // the 'value' key is used to determine radius ('r') attribute
        // each object of the data is assigned a 'value' key paired w/ num lines

    var nodes = chart.nodes({children: data}).filter(function(d) { return !d.children; });
        // layout.pack nodes are created using objects from the data
        // d3 assigns each node with r, x, & y values

    // svg is appended
    var canvas = d3.select("#wrapper")
        .append("svg")
            .attr("width", diameter)
            .attr("height", diameter)
            .attr("class", "bubble");

    // div to contain all bubbles is appended
    var bubbles = canvas.append("g")
            .attr("transform", "translate(0,0)")
        .selectAll(".bubble")
            .data(nodes)
            .enter();

    // circles are appended to the group for each object in the data
    // the radius and coordinates assigned to each object is used
    bubbles.append("circle")
            .attr("r", function(d) { return d.r; })
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; })
            .style("fill", function(d) { return color(+d['n-revs']); })
        .append("svg:title")
            .text(function(d) { return d['entity']; });

    // name of entity is shown on bubble only if it fits within the bubble
    bubbles.append("text")
            .attr("x", function(d) { return d.x; })
            .attr("y", function(d) { return d.y + 5; })
            .attr("text-anchor", "middle")
        .text(function(d) { if(d['entity'].length*6 <= d.r*2) return d['entity']; })
            .style("fill", "black")
            .style("font-size", "12px");
}


function createMeter(data, module) {
    d3.select("#wrapper").html('');

    var r = 75, // meter outer radius
        h = data.length * 200; // width of svg

    var width = parseInt(d3.select("#wrapper").style("width"));

    var color = d3.scale.category20();

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
            return "<center>" + "<strong>" + d.coupled
                + "<br>" + "avg revisions: </strong> " + "<span style='color:red'>"
                + d['average-revs'] + "</span>" + "</center>";
            });

    // scale for location of meter
    // var xScale = d3.scale.linear()
    //     .domain([0, data.length - 1])
    //     .range([r, w-r]);

    // d3's arc creates settings for a circular path w/ radii & angles
    var arc = d3.svg.arc()
        .startAngle(Math.PI) // meter begins at 6 o'clock
        .innerRadius(r - 30)
        .outerRadius(r);
        // endAngle determined from data

    // the header is appended with name of selected module
    d3.select("#title")
        .style('margin-bottom', '15px')
        .attr('text-anchor', 'middle')
        .text('Coupled with: ' + module);

    // svg and g div appended
    var svg = d3.select("#wrapper")
        .append("svg")
            .attr('width', width - 20) // scroll bar if w exceeds width of wrapper
            .attr('height', h)
            .attr('class', 'percentage')
        .append("g");

    // maters are appended for each coupled module
    var meter = svg.selectAll("meter")
        .data(data)
        .enter()
        .append("g")
            .attr('transform', function(d, i) {
                return 'translate(' + (width / 2) + ',' +  (20 + (i * 200 + r)) + ')';
            })
        .call(tip)
        .on('mouseover', function(d) { tip.show(d); })
        .on('mouseout', function(d) { tip.hide(d); });

    // an svg path is appended to each meter div
    // path settings determined by arc & applied using 'd' attribute
    // this is the background meter which is a full circle
    meter.append("path")
        .attr('d', arc.endAngle(3 * Math.PI))
        .style('fill', '#c5c2bd');

    // this is the foreground meter which shows percentage
    meter.append("path")
        .attr('d', arc.endAngle(function(d) {
            return (d.degree / 100) * (2 * Math.PI) + Math.PI;
        })) // endAngle represents progress compared to startAngle
        .attr('fill', '#a57103');

    // percentage text appended
    meter.append("text")
        .attr('text-anchor', 'middle')
        .text(function(d) { return d.degree + "%"; });

    // name of module appended below each meter
    meter.append("text")
        .attr('text-anchor', 'middle')
        .attr('y', '95')
        .style('font-size', '13px')
        .text(function(d) { return d.coupled.split('/').pop(); });
}

function createPieChart(data, module) {
    d3.select("#wrapper").html('');

    d3.select("#title")
        .style('margin-bottom', '15px')
        .attr('text-anchor', 'middle')
        .text('Coupled with: ' + module);

    var r = 200,
        w = 400;

    var color = d3.scale.category20();

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
            return "<center>" + "<strong>" + d.data.coupled
                + "<br>" + "degree: </strong> " + "<span style='color:red'>"
                + d.data['degree'] + "% </span>" + "</center>";
            });

    var arc = d3.svg.arc()
        .innerRadius(50)
        .outerRadius(r);

    var textArc = d3.svg.arc()
        .innerRadius(r - 50)
        .outerRadius(r - 50);

    var pie = d3.layout.pie()
        .sort(null)
        .padAngle(.02)
        .value(function(d) { return d['average-revs']; });

    var svg = d3.select("#wrapper")
        .append("svg")
            .attr('width', w)
            .attr('height', w)
        .append("g")
            .attr('transform', 'translate(200, 200)');

    var slice = svg.selectAll("slice")
        .data(pie(data))
        .enter()
        .append("g");

    slice.append("path")
        .attr('d', arc)
        .attr('fill', function(d) { return color(d.data.coupled); })
        .call(tip)
        .on('mouseover', function(d) { tip.show(d); })
        .on('mouseout', function(d) { tip.hide(d); });

    // following function retrieved from:
    // http://stackoverflow.com/questions/26127849/d3-aligning-text-to-centroid-angle
    function angle(d) {
        var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
        return a > 90 ? a - 180 : a;
    }

    slice.append("text")
        .attr('transform', function(d) {
            return 'translate(' + textArc.centroid(d) + ')';
        })
        .attr('dy', '.35em')
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .style('font-size', '30px')
        .text(function(d) { return d.data['average-revs']; });
}

function createWordcloud(data) {
    var commit_words = data;
    var padding = 30;
    var height = window.innerHeight - 2*padding - 20 - 70,
        width = d3.select('#wrapper').node().getBoundingClientRect().width - 2*padding;
    var font = d3.scale.linear()
                    .range([20, 150])
                    .domain(d3.extent(commit_words, function(d) {
                        return +d['freq'];
                    }));
    var color = d3.scale.linear()
            .domain([0, d3.max(commit_words, function(d) { return +d['freq']; })])
            .range(["#c63939", "#130505"]);

    var tip = d3.tip()
        .attr('class', "d3-tip")
        .direction(function(d) {
            var result = 's';
            return result;
        })
        .html(function(d) {
            return "<strong>Frequency:</strong> <span style='color:red'>" + d['freq'] + "</span>";
        });


    var cloud_layout = d3.layout.cloud()
                    .size([width, height])
                    .words(commit_words)
                    .padding(10)
                    .font('monospace')
                    .rotate(function (d) {return 0})
                    .text(function(d) {return d.text;})
                    .fontSize(function(d) {return font(d['freq'])})
                    .spiral("rectangular")
                    .on("end", draw)
                    .start();

    function draw(words) {
        d3.select('#wrapper').append("svg")
                .attr("width", width + padding)
                .attr("height", height + padding)
                .style("display", "block")
                .attr("class", "wordcloud")
                .append("g")
                .attr("transform", "translate("+width/2+","+height/2+")")
                .selectAll("text")
                .data(words)
                .enter().append("text")
                .style("font-size", function(d) { return d.size + "px"; })
                .style("fill", function(d, i) { return color(i); })
                .call(tip)
                .on('mouseover', function(d) {
                    tip.show(d);
                    d3.select(this)
                        .style("fill", "blue");
                })
                .on('mouseout', function(d,i) {
                    tip.hide(d);
                    d3.select(this).style("fill", color(i));
                })
                .transition()
                .duration(1000)
                .attr("text-anchor", "middle")

                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .text(function(d) { return d.text; });
    }
}

// Dependant on D3 V4
function commitSelector(dates) {
    d3.select("#commitSelector").html('');
    var datum = []
    dates.forEach(function(d){
    datum.push(new Date(d.replace(' ','T')))
    })
    datum.reverse()

    var margin = {top: 10, right: 40, bottom: 40, left: 20},
      width = 900 - margin.left - margin.right,
      height = 140 - margin.top - margin.bottom;

    var x = d3.scaleTime()
      .domain([datum[0], datum[datum.length-1]])
      .rangeRound([0, width]);

    var brush = d3.brushX()
      .extent([[0, 0], [width, height]])
      .on("end", brushended);

    var svg = d3.select("#commitSelector").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

    svg.append("g")
      .attr("class", "axis axis--grid")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x)
          .tickValues(datum)
          .tickSize(-height)
          .tickFormat(function() { return null; }))

    // Assemble an array of values to use as ticks
    var tickVals = [datum[0]]
    var endDate = d3.timeDay(datum[datum.length-1])-5
    if (d3.timeMonth.count(datum[0],datum[datum.length-1]) < 10)
      tickVals = tickVals.concat(d3.timeMonth.range(datum[0],endDate));
    else if (d3.timeMonth.count(datum[0],datum[datum.length-1]) < 30)
      tickVals = tickVals.concat(d3.timeMonth.every(3).range(datum[0],endDate));
    else
      tickVals = tickVals.concat(d3.timeMonth.every(6).range(datum[0],endDate));

    tickVals.push(datum[datum.length-1])

    // Conditional formatting of ticks
    var formatDay = d3.timeFormat("%b %d"),
      formatMonth = d3.timeFormat("%b"),
      formatYear = d3.timeFormat("%Y");
    function multiFormat(date) {
        if (date == datum[0] || date == datum[datum.length-1]){
          return formatDay(date)
        }
        return (d3.timeYear(date) < date ? formatMonth : formatYear)(date);
    }

    svg.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x)
          .tickValues(tickVals)
          .tickFormat(multiFormat)
          .tickPadding(0))
      .attr("text-anchor", null)
    .selectAll("text")
      .style("text-anchor", "start")
      .attr("transform", function(d) {
          return "rotate(45)"
          })
      .attr("x", 6);

    svg.append("g")
      .attr("class", "brush")
      .call(brush);

    var borderPath = svg.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("height", height)
      .attr("width", width)
      .style("stroke", 'black')
      .style("fill", "none")
      .style("stroke-width", '1px');

    // Maps the selected range to snap to commit dates
    function mapDateRange(date1, date2, dates) {
        var returnVal = [dates[0],dates[dates.length-1]]
        var lowerSearch = true

        for (var i=0; i < dates.length; i++){
          var d = dates[i]
          if (lowerSearch) {
            if (d > date1) {
              returnVal[0] = d
              lowerSearch = false
            }
          }
          else {
            if (d > date2) {
              returnVal[1] = dates[i-1]
              break
            }
          }
        }
        return returnVal
    }

    function brushended() {
        if (!d3.event.sourceEvent) return; // Only transition after input.
        if (!d3.event.selection) return; // Ignore empty selections.
        var domain0 = d3.event.selection.map(x.invert),
            domain1 = mapDateRange(domain0[0],domain0[1],datum);
        var formFormat = d3.timeFormat('%Y-%m-%d')
        d3.select('#previousDate').property("value", formFormat(domain1[0]))
        d3.select('#currentDate').property("value", formFormat(domain1[1]))

        $('#currentDate').trigger('change');

        d3.select(this)
          .transition()
            .call(brush.move, domain1.map(x));
    }
}
