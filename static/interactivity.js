// called by filterData
// checks to see if the passed in value falls within the range of the filter
// returns true if filter should be applied on said value, false if not
function applyFilter(filter_value) {
    var bool = false;

    filter_obj.forEach(function(d) {
        if (parseInt(filter_value[d.key]) < d.value.from
        || parseInt(filter_value[d.key]) > d.value.to) {
            bool = true;
        }
    });

    return bool;
}


// called by setFilter
// reassigns filtered_data to new set of data meeting filter requirements
function filterData() {
    if (analysis_type == 'coupling') {
        filtered_entity_list = {}

        for (key in entity_list) {
            console.log(entity_list[key]);
            if (applyFilter(entity_list[key]) != true) {
                filtered_entity_list[key] = entity_list[key];
            }
        }
        console.log(filtered_entity_list);
        createGraph(filtered_entity_list, analysis_type);
    }
    else {
        filtered_data = []; // filtered_data is emptied, and updated below

        json_data.forEach(function(d) {
            // if the current value of the filter column chosen by the user
            // falls within the filter range, then the loop skips the following
            if (applyFilter(d) != true) {
                filtered_data.push(d);
            }
        });

        createGraph(filtered_data, analysis_type);
    }
}


function toggleFilter() {
    var filter = document.getElementById("filter");
    filter.style.display = filter.style.display == 'none' ? 'block' : 'none';
}


// called when user selects a column to filter by, and selects range
// reads user entries and sets variables accordingly
// if one of start/end is left empty, assigns default value
function setFilter() {
    filter_obj = [];

    keys.forEach(function(d, i) {
        if (d != keys[0] && d != 'coupled') {
            var filter_key = d;

            var values = $("#" + d + "-slider-range").slider( "option", "values" );
            var from_value = values[0];
            var to_value = values[1];
            if (from_value > to_value) { return; }
            filter_obj.push({key: filter_key, value: {from: from_value, to: to_value}})
        }
    });

    filterData();
    toggleFilter();
}


function resetFilter() {
    filter_obj = [];

    filterData();
    toggleFilter();
}


// appends all necessary divs needed for filtering slider
// uses jquery plugin to create and adjust slider range
function createSlider() {
    keys.forEach(function(key) {
        if (key != keys[0] && key != 'coupled') {
            var slider = d3.select("#filter");

            var p = slider.append("center").append("p");
            p.append("label")
                .attr('for', key + '-amount')
                .attr('class', 'filter-key')
                .text(key + ':');
            p.append("text")
                .attr('type', 'text')
                .attr('class', 'range')
                .attr('id', key + '-amount');
            slider.append("div")
                .attr('id', key + '-slider-range');

            var max_value = d3.max(json_data, function(d) { return +d[key]; })

            // original version of jquery function retrieved from:
            // http://jqueryui.com/slider/#range
            $(function() {
                $( "#" + key + "-slider-range" ).slider({
                  range: true,
                  min: 0,
                  max: max_value,
                  values: [ 0, max_value ],
                  slide: function( event, ui ) {
                    $( "#" + key + "-amount" )
                        .text( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
                  }
                });
                $( "#" + key + "-amount" ).text( $( "#" + key + "-slider-range" )
                    .slider( "values", 0 ) + " - " + $( "#" + key + "-slider-range" )
                    .slider( "values", 1 ) );
            });
        }
    })

    d3.select("#filter").append("input")
        .attr('type', 'button')
        .attr('value', 'Filter')
        .on('click', function() { setFilter(); });

    d3.select("#filter").append("input")
        .attr('type', 'button')
        .attr('value', 'Reset')
        .on('click', function() { resetFilter(); });
}


// called when user selects an entity in coupling analysis
// parses data for every object in which that entity is present
// creates new data with those objects
function chooseModule(elem) {
    var chosen_module = elem.getAttribute('value');

    elem.style.backgroundColor = '#6d9af6';
    elem.style.color = 'white';
    if (temp_elem) {
        temp_elem.style.backgroundColor = '';
        temp_elem.style.color = '';
    }
    temp_elem = elem;

    coupled_data = [];

    filtered_data.forEach(function(d) {
        if (d[keys[0]] == chosen_module || d[keys[1]] == chosen_module) {
            // if chosen entity is found in either first / second column of row
            var temp_obj = {};
            keys.forEach(function(k, i) {
                // traverse row and create object w/ all data aside from entity
                if (d[k] != chosen_module) {
                    if (k == 'entity') { temp_obj.coupled = d[k]; }
                    else { temp_obj[k] = d[k]; }
                }
            })
            coupled_data.push(temp_obj); // push the object into new data
        }
    });

    if (chosen_key == "average-revs") { createPieChart(coupled_data, chosen_module); }
    else { createMeter(coupled_data, chosen_module); } // meter chart is created
}


// called when user clicks on column header
// specifies the y-axis values for the graphs to whichever column the user selects
// calls function to create graph using the selected data
function chooseColumn(elem) {
    chosen_key = elem.getAttribute('value'); // chosen_key is reassigned
    createGraph(filtered_data, analysis_type);
}



// Called by createGraph
// Custom styling for Coupling visualization
function configureDivCoupling() {
  d3.select("#container")
      .style('display', 'flex');

  d3.select("#wrapper")
      .style('width', '50%')
      .style('height', '400px')
      .style('margin-top', '30px');

  d3.select("#table")
      .style('margin-top', '0');
}
