// this is called by chooseColumn when the user selects data for y-axis
// also called by createTable after table has been created / updated
function createGraph(data) {
    if (analysis_type == "hotspots") {
        createBubbleChart(data);
    }
    else if (analysis_type == "coupling") {
        // if coupling, graph is not create until chooseModule is called
        var color = d3.scale.category20();
        createHeader(color);
        d3.select("#wrapper")
            .html('<p><p>Choose an enitity to view degree of coupling.</p></p>');
    }
    else if (analysis_type == "cloud") {
        createWordcloud(data);
    }
    else {
        createBarGraph(data);
    }
}


function createBarGraph(data) {
    d3.select("#wrapper").html('');
        // .html("") causes the wrapper to be emptied out
        // this prevents copies from being made each time function is called
        // NOTE: this apparently does not work in Safari; fix later

    var w;
    var width;
    var margin = {top: 20, left: 70, right: 20, bottom: 130};
    var height = 450 - margin.top - margin.bottom;
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
            return {type: label, value: +d[label]};
        });
    });

    // the scale for each category of bars (each row)
    var x0Scale = d3.scale.ordinal()
        .domain(data.map(function(d) { return d[keys[0]]; })) // array of entities
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
        .orient("bottom");
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");

    var tip = d3.tip()
      .attr('class', 'd3-tip')
      .offset([-10, 0])
      .html(function(d) {
        return "<strong>" + d.type + ":</strong> <span style='color:red'>" + d.value + "</span>";
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
            .attr("transform", function(d) { 
                return "translate(" + x0Scale(d[keys[0]]) + ",0)"; 
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
            .attr("y", function(d) { return yScale(d.value); })
        //labels dont display with this + transition enabled
        // .append("svg:title")
            .text(function(d) { return d.value; });

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


    // var h_width = labels.length * 150; // width for header div

    // // scale for placing legend ticks on header div
    // var hScale = d3.scale.linear()
    //     .domain([0, labels.length - 1])
    //     .range([0, h_width - 75]);

    // // svg is appended to header div
    // var legend = d3.select("#header").html('')
    //     .append("svg")
    //         .attr('height', 25)
    //         .attr('width', h_width)
    //     .selectAll("legend")
    //         .data(labels)
    //         .enter();

    // // circles to represent legend ticks are appended
    // legend.append("circle")
    //     .attr('r', 10)
    //     .attr('transform', function(d, i) { 
    //         return 'translate(' + (hScale(i) + 10) + ',10)'; 
    //     })
    //     .style('fill', function(d) { return color(d); });

    // // text is added to the circles
    // legend.append("text")
    //         .attr("x", function(d, i) { return hScale(i) + 20; })
    //         .attr("y", function(d) { return 10; })
    //         .attr("text-anchor", "right")
    //     .text(function(d) { return d; })
    //         .style("fill", "black") 
    //         .style("font-size", "12px");
    createHeader(color);
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

function toggleFilter() {
    var filter = document.getElementById("filter");
    filter.style.display = filter.style.display == 'none' ? 'block' : 'none';
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
    d3.select("#wrapper")
        .append("text")
            // .style('position', 'fixed')
            .attr('text-anchor', 'middle')
            .text('Coupled with: ' + module);
            // .attr('transform', 'translate(0, 0)');

    // svg and g div appended
    var svg = d3.select("#wrapper")
        // .attr('class', 'mCustomScrollbar')
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

    // createHeader(color);
}

function createPieChart(data, module) {
    d3.select("#wrapper").html('');

    d3.select("#header").html('')
        .append("text")
            .attr('text-anchor', 'middle')
            .text('Coupled with: ' + module);

    var r = 200,
        w = 400;

    var color = d3.scale.category20();

    var arc = d3.svg.arc()
        .outerRadius(r);

    var textArc = d3.svg.arc()
        .innerRadius(r - 50)
        .outerRadius(r - 50);

    var pie = d3.layout.pie()
        .sort(null)
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
        .attr('fill', function(d) { return color(d.data.coupled); });

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
        .style('font-size', '10px')
        .text(function(d) { return d.data['average-revs']; });

    slice.append("title")
        .text(function(d) { return d.data.coupled; });

}

function createWordcloud(data) {
    var commit_words = data;
    var padding = 30;
    var height = window.innerHeight - 2*padding,
        width = window.innerWidth - 2*padding;

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
        d3.select("#wrapper").append("svg")
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
                    d3.select(this).style("fill", function(d, i) { return color(i); });
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