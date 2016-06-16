// called by filterData
// checks to see if the passed in value falls within the range of the filter
// returns true if filter should be applied on said value, false if not
function applyFilter(filter_value) {
    if (filter_value == undefined) { return false; }

    // parseInt changes user-entered number from string to int
    if (parseInt(filter_value) < filter_start || parseInt(filter_value) > filter_end) 
        { return true; }

    return false;
}


// called by setFilter
// reassigns filtered_data to new set of data meeting filter requirements
function filterData() {
    filtered_data = []; // filtered_data is emptied, and updated below

    json_data.forEach(function(d) {
        // if the current value of the filter column chosen by the user
        // falls within the filter range, then the loop skips the following
        if (applyFilter(+d[filter_key]) != true) {
            filtered_data.push(d);
        }
    });

    createTable(filtered_data);
}


// called when user selects a column to filter by, and selects range
// reads user entries and sets variables accordingly
// if one of start/end is left empty, assigns default value
function setFilter() {
    filter_obj = [];

    keys.forEach(function(d, i) { 
        if (d != keys[0] && d != 'coupled') {
            // from_value = document.forms["filter"][d]["from"].value;
            // to_value = document.forms["filter"][d]["to"].value;

            var from_value = document.getElementById(d).children[1].value;
            var to_value = document.getElementById(d).children[2].value;

            var filter_key = d;
            filter_obj.push({filter_key:{"from": from_value, "to": to_value}})
            // filter_obj[d]["from_value"] = from_value;
            // filter_obj[d]["to_value"] = to_value;
        }
    });

    console.log(filter_obj);

    // filter_key = document.forms["filter"]["key"].value;
    // filter_start = parseInt(document.forms["filter"]["start"].value);
    //     if (filter_start == null || filter_start == "") { filter_start = 0; }
    // filter_end = parseInt(document.forms["filter"]["end"].value);
    //     if (filter_end == null || filter_end == "") { filter_end = 100000; }

    // for (i = 0; i < keys.length; i++) { if (filter_key == keys[i]) { filterData(); } }
}


// called when user selects an entity in coupling analysis
// parses data for every object in which that entity is present
// creates new data with those objects
function chooseModule(elem) {
    var chosen_module = elem.getAttribute('value');

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

    if (chosen_key == "average-revs") { createPie(coupled_data, chosen_module); }
    else { createMeter(coupled_data, chosen_module); } // meter chart is created
}


// called when user clicks on column header
// specifies the y-axis values for the graphs to whichever column the user selects
// calls function to create graph using the selected data
function chooseColumn(elem) {
    chosen_key = elem.getAttribute('value'); // chosen_key is reassigned
    createGraph(filtered_data); 
}


// NOTE: currently not in use
// changes the display of corresponding graph to show or hide
function toggleGraph(elem) {
    var display_status = document.getElementById(elem.getAttribute('name')).style.display;

    if (display_status == "none") 
        { document.getElementById(elem.getAttribute('name')).style.display = "block"; }
    else { document.getElementById(elem.getAttribute('name')).style.display = "none"; }
}