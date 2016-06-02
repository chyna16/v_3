// this is called by chooseColumn() when the user selects data for y-axis
function createGraph(data) {
    if (analysis_type == "hotspots") {
        createBubbleChart(data);
    }
    else if (analysis_type == "coupling") {
        d3.select("#wrapper").html('<p><p>Choose an enitity to view degree of coupling.</p></p>');
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
    var padding = 1;
    var color = d3.scale.ordinal().range(["#98abc5", "#8a89a6"]);  
    
    if (data.length > 50) { w = data.length * 20; }
    else if (data.length < 10) { w = data.length * 100; }
    else { w = 1000; }
    width = w - margin.left - margin.right;

    if (chosen_key == 'default') {
        // if no column was specified, the data from all value columns is used
        var labels = d3.keys(data[0]).filter(function(key) 
        { return key !== keys[0] && key !== 'values' && key !== 'coupled'; });
    }
    else {
        // if a column was specified, only the data from that column is used
        var labels = d3.keys(data[0]).filter(function(key) 
        { return key == chosen_key; });
    }

    data.forEach(function(d, i) {
        delete d.values;
        d.values = labels.map(function(label) {
            return {type: label, value: +d[label]};
        });
    });

    var x0Scale = d3.scale.ordinal().rangeBands([0, width], .05);
    var x1Scale = d3.scale.ordinal();
    var yScale = d3.scale.linear().range([height, 0]);
    yScale.domain([0, d3.max(data, function(d) { 
        return d3.max(d.values, function(d) { return d.value; }); 
    })]);

    var xAxis = d3.svg.axis()
            .scale(x0Scale)
            .orient("bottom");
    var yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left");

    if (keys[1] == 'coupled') { var domain_key = keys[1]; }
    else { var domain_key = keys[0]; }

    x0Scale.domain(data.map(function(d) { return d[domain_key]; }));
    x1Scale.domain(labels).rangeBands([0, x0Scale.rangeBand()]);

    var canvas = d3.select("#wrapper")
        .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var category = canvas.selectAll(".category")
            .data(data)
            .enter()
        .append("g")
            .attr("class", "category")
            .attr("transform", function(d) { return "translate(" + x0Scale(d[domain_key]) + ",0)"; });

    var bar = category.selectAll("rect")
            .data(function(d) { if (typeof d.values != 'undefined') return d.values; })
            .enter()
        .append("rect")
            .attr("height", function(d) { return height - yScale(d.value); })
            .attr("width", x1Scale.rangeBand())
            .attr("x", function(d) { return x1Scale(d.type); })
            .attr("y", function(d) { return yScale(d.value); })
            .style("fill", function(d) { return color(d.type); })
        .append("svg:title")
            .text(function(d) { return d.value; });
        
     // var text = category.selectAll("text")
     //        .data(function(d) { if (typeof d.values != 'undefined') return d.values; })
     //        .enter()
     //    .append('text')
     //        .attr("x", function(d) { return x1Scale(d.type); })
     //        .attr("y", function(d) { return yScale(d.value); })
     //        .text(function(d){ return d.value })
     //        .style("display", "block");
        
        //feature to display numerical values on mouse enter broken
        // text.on("mouseenter", function(d){
        //     word = d3.select(this);
        //     word.select("text")
        //     .style("display", "block")
            // // .style("fill", "black") 
            // .style("font-size", "12px"); 
        // });

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
            .attr("fill", "steelblue");

    canvas.append("g")
            .attr('class', 'axis')
            .attr('transform', 'translate(0, 0)')
            .call(yAxis)
            .selectAll("text")  
            .style("text-anchor", "end")
            .attr("dx", "-1em")
            .attr("dy", ".15em")
            .style("font-size", ".8em")
            .attr("fill", "steelblue");

    var hScale = d3.scale.linear()
        .domain([0, labels.length - 1])
        .range([0, 225]);

    var legend = d3.select("#header").html('')
        .append("svg")
            .attr('height', 25)
            .attr('width', 300)
        .selectAll("legend")
            .data(labels)
            .enter();

    legend.append("circle")
            .attr('r', 10)
            .attr('transform', function(d, i) { return 'translate(' + (hScale(i) + 10) + ',10)'; })
            .style('fill', function(d) { return color(d); });

    legend.append("text")
            .attr("x", function(d, i) { return hScale(i) + 20; })
            .attr("y", function(d) { return 10; })
            .attr("text-anchor", "right")
        .text(function(d) { return d; })
            .style("fill", "black") 
            .style("font-size", "12px");
}


function createBubbleChart(data) {
    d3.select("#wrapper").html('');

    var diameter = 700;

    var color = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return +d['n-revs']; })])
        .range(["#ffb3b3", "#e60000"]);

    var chart = d3.layout.pack()
        .sort(null)
        .size([diameter, diameter])
        .padding(1.5);

    data.forEach(function(d) { d.value = +d['lines']; })

    var nodes = chart.nodes({children: data}).filter(function(d) { return !d.children; });

    var canvas = d3.select("#wrapper")
        .append("svg")
            .attr("width", diameter)
            .attr("height", diameter)
            .attr("class", "bubble");

    var bubbles = canvas.append("g")
            .attr("transform", "translate(0,0)")
        .selectAll(".bubble")
            .data(nodes)
            .enter();

    bubbles.append("circle")
            .attr("r", function(d) { return d.r; })
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; })
            .style("fill", function(d) { return color(+d['n-revs']); })
        .append("svg:title")
            .text(function(d) { return d['entity']; });

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

    var r = 75,
        w = data.length * 200;

    var xScale = d3.scale.linear()
        .domain([0, data.length-1])
        .range([r, w-r]);

    var arc = d3.svg.arc()
        .startAngle(Math.PI)
        .innerRadius(r-30)
        .outerRadius(r);

    d3.select("#header").html('')
        .append("text")
            .attr('text-anchor', 'middle')
            .text('Coupled with: ' + module);

    var svg = d3.select("#wrapper")
        .append("svg")
            .attr('width', w)
            .attr('height', 250)
            .attr('class', 'percentage')
        .append("g");

    var meter = svg.selectAll("meters")
        .data(data).enter()
        .append("g")
            .attr('transform', function(d, i) { 
                return 'translate(' + xScale(i) + ',130)';
            });

    meter.append("path")
        .attr('d', arc.endAngle(3 * Math.PI))
        .style('fill', '#c5c2bd');

    meter.append("path")
        .attr('d', arc.endAngle(function(d) { 
            return (d.degree / 100) * (2 * Math.PI) + Math.PI;
        }))
        .attr('fill', '#a57103');

    meter.append("text")
        .attr('text-anchor', 'middle')
        .text(function(d) { return d.degree + "%"; });

    meter.append("text")
        .attr('text-anchor', 'middle')
        .attr('y', '95')
        .style('font-size', '13px')
        .text(function(d) { return d.coupled.split('/').pop(); });
}