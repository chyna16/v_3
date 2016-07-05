// this is called by chooseColumn when the user selects data for y-axis
// also called by createTable after table has been created / updated
function createGraph(data) {
    if (analysis_type == "hotspots") {
        createBubblePack(data);
    }
    else if (analysis_type == "coupling") {
        // if coupling, graph is not create until chooseModule is called
        var color = d3.scale.category20();
        createHeader(color);
        d3.select("#graph")
            .html('<p><p>Choose an enitity to view degree of coupling.</p></p>');
    }
    else if (analysis_type == "cloud") {
        createWordcloud(data);
    }
    else {
        createBarGraph(data);
    }
}

function createHeader(color) {
    var header = d3.select("#header").html('').append("p");

    header
        .selectAll("button")
            .data(keys.filter(function(key) { 
                return key != keys[0] && key != 'coupled'; }))
            .enter()
        .append("button")
        .attr('class', 'btn')
        .text(function(d) { return d; })
        .style('background-color', function(d) { return color(d); })
        .style('color', 'white')
        .style('margin', '10px')
        .attr('value', function(d) { return d; })
        .on('click', function() { chooseColumn(this); });

    if (analysis_type != 'coupling') {
        header.append("button")
            .attr('class', 'btn')
            .text('all')
            .style('background-color', 'black')
            .style('color', 'white')
            .style('margin', '10px')
            .attr('value', 'default')
            .on('click', function() { chooseColumn(this); });
    }

    header.append("button")
        .attr('class', 'btn')
        .text('add filter')
        .style('background-color', 'grey')
        .style('color', 'white')
        .style('margin', '10px')
        .on('click', function() { toggleFilter(); });
}


function createBarGraph(data) {
    d3.select("#graph").html('');
        // .html("") causes the wrapper to be emptied out
        // this prevents copies from being made each time function is called
        // NOTE: this apparently does not work in Safari; fix later

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
    var canvas = d3.select("#graph")
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
            .attr("width", 0)
            .transition()
            .duration(900)
            .attr("height", function(d) { return height - yScale(d.value); })
            .attr("width", x1Scale.rangeBand())
            .attr("x", function(d) { return x1Scale(d.type); })
            .attr("y", function(d) { return yScale(d.value); });
        //labels dont display with this + transition enabled
        // .append("svg:title")
            // .text(function(d) { return d.value; });

        //labels hide all text
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

function createBubblePack(inputData) {
    d3.select("#wrapper").html('');

    var data = inputData.slice(0);

    var margin = 20,
        diameter = 610,
        k=1;

    var color = d3.scale.linear()
        .domain([-1, 5])
        .range(["hsl(152,80%,80%)", "hsl(228,30%,40%)"])
        .interpolate(d3.interpolateHcl);

    var colorHotspot = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return +d['n-revs']; })])
        .range(["#ffb3b3", "#e60000"]);

    var tip = d3.tip()
        .attr('class', "d3-tip")
        .direction('e')
        .offset([0, 10])
        .html(function(d) {
            return "<p>File: <text style='color:red'>" + d.data["entity"]+ "</p>"
                +"<p>Revisions: " + d.data["n-revs"] + "</p>"
                +"<p>Lines: " + d.data["lines"] + "</p>";
        });

    var pack = d3.layout.pack()
        .padding(2)
        .size([diameter - margin, diameter - margin])

    var svg = d3.select("#wrapper").append("svg")
        .attr("width", diameter)
        .attr("height", diameter)
        .append("g")
        .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
    
    data.forEach(function(d){
        d["full-path"] = repo + "/" + d["entity"];
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
        if (nameA < nameB) //sort string ascending
            return -1;
        if (nameA > nameB)
            return 1;
        return 0; //default return value (no sorting)
    });

    var root = stratify(data)
        .sum(function(d) { return d.lines; })
        .sort(function(a, b) { return b.lines - a.lines; });


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
        .style("display", function(d) { return (d.parent === root && labelFit(d,this)) ? "inline" : "none"; });

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
        var focus0 = focus; focus = d;

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
                    return (d.parent === focus || this.style.display === "inline"); 
                })
                .style("fill-opacity", function(d) { return (d.parent === focus) ? 1 : 0; })
                .each("end", function(a) { 
                    if (a.parent === focus && labelFit(a,this)) this.style.display = "inline";
                    if (a.parent !== focus || !labelFit(a,this)) this.style.display = "none"; });
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
        try {
            return textElement.getBBox().width <= nodeElement.r*2*k;
        } catch(err) {
            console.log('error');
        }

    }

    d3.select(self.frameElement).style("height", diameter + "px");
}

function createBubbleChart(data) {
    d3.select("#graph").html('');

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
    var canvas = d3.select("#graph")
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
    d3.select("#graph").html('');

    var r = 75, // meter outer radius
        h = data.length * 200; // width of svg

    var width = parseInt(d3.select("#graph").style("width"));

    var color = d3.scale.category20();

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
    var svg = d3.select("#graph")
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
            });

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
    d3.select("#graph").html('');

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
            return "<strong>" + d.data.coupled + "<br>" + "degree: </strong> " 
                + "<span style='color:red'>" + d.data['degree'] + "% </span>";
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

    var svg = d3.select("#graph")
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
                // + 'rotate(' + angle(d) + ')';
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
        width = d3.select("#content-div").node().getBoundingClientRect().width - 2*padding;
    console.log(d3.select("#content-div").node().getBoundingClientRect().width);
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
            /* Posotion aware corner tip
            if (d3.event.clientY > height/2) {
                result = 'n';
            } else {
                result = 's';
            }
            if (d3.event.pageX > width/2) {
                result += 'w';
            } else {
                result += 'e';
            }
            */
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
                    // rotates random words 90 degrees
                    // .rotate(function(d) { return Math.floor(Math.random() * 2) * 90; })
                    .rotate(function (d) {return 0})
                    //not all words are being displayed if font size is too large
                    .text(function(d) {return d.text;})
                    .fontSize(function(d) {return font(d['freq'])})
                    .spiral("rectangular")
                    .on("end", draw)
                    .start();

    function draw(words) {
        d3.select("#graph").append("svg")
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