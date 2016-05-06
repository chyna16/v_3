// called when user selects a column to filter by, and selects range
// reads user entries and sets variables accordingly
// if one of start/end is left empty, assigns default value
// calls createTable
function setFilter() {
    filter_key = document.forms["filter"]["key"].value;
    filter_start = parseInt(document.forms["filter"]["start"].value);
        if (filter_start == null || filter_start == "") { filter_start = 0; }
    filter_end = parseInt(document.forms["filter"]["end"].value);
        if (filter_end == null || filter_end == "") { filter_end = 100000; }

    for (i=0; i<keys_len; i++) { if (filter_key == keys[i]) { filterData(); } }
}


// called by createTable
// checks to see if the passed in value falls within the range of the filter
// returns true if filter should be applied on said value, false if not
function applyFilter(filter_value) {
    if (filter_value == undefined) { return false; }

    // parseInt changes user-entered number from string to int
    if (parseInt(filter_value) < filter_start || parseInt(filter_value) > filter_end) 
        { return true; }

    return false;
}


function chooseModule(elem) {
    var chosen_module = elem.getAttribute('value');

    coupled_data = [];

    filtered_json.forEach(function(d) {
        if (d[keys[0]] == chosen_module) {
            var temp_obj = {};
            keys.forEach(function(k, i) {
                if (i != 0) { temp_obj[k] = d[k]; }
            })
            console.log(temp_obj);
            coupled_data.push(temp_obj);
        }
    });

    createGraph(coupled_data);
}


function filterData() {
    filtered_json = [];

    json_data.forEach(function (d) {
        // if the current value of the filter column chosen by theuser
        // falls within the filter range, then the loop skips the following
        if (applyFilter(+d[filter_key]) != true) {
            filtered_json.push(d);
        }
    });

    createTable(filtered_json);
}


// specifies the y-axis values for the graphs to whichever column the user selects
// calls function to create graph using the selected data
function chooseColumn(elem) {
    chosen_key = elem.getAttribute('value');
    createGraph(filtered_json); 
}


// changes the display of corresponding graph to show or hide
function toggleGraph(elem) {
    var display_status = document.getElementById(elem.getAttribute('name')).style.display;

    if (display_status == "none") 
        { document.getElementById(elem.getAttribute('name')).style.display = "block"; }
    else { document.getElementById(elem.getAttribute('name')).style.display = "none"; }
}