// called by createTable
// takes a row element, a column id, and a row of data
// fills row element w/ a column for each item in the row of data
// returns a completed row
function setTableRows(row, elem_id, data) {
    for (i = 0; i < keys.length; i++) {
        var col = document.createElement(elem_id); // a th / td element

        if (i == 0) { col.style.width = "65%"; } // first column width
        else { col.style.width = (35 / (keys.length - 1)) + "%"; } 
            // remaining column widths

        // column styling
        // col.style.overflow = "hidden";
        // col.style.fontSize = "15px";
        // col.onmouseover = function() { this.style.overflow = "visible"; }
        // col.onmouseout = function() { this.style.overflow = "hidden"; }
        // col.style.backgroundColor = "white"; // INTERFERES W/ OVERFLOW

        if (data == keys) {
            // if table head is being created
            col.setAttribute('value', data[i]);
            col.appendChild(document.createTextNode(data[i])); 
        } 
        else {
            // if table body is being created
            col.setAttribute('value', data[keys[i]]);
            col.appendChild(document.createTextNode(data[keys[i]])); 
        }

        row.appendChild(col); // each column created is added to passed in row
    }
    return row;
}

function setListRows(row, elem_id, data) {
    var col = document.createElement(elem_id);
    if (elem_id == 'td') { 
        col.onclick = function() { chooseModule(this); }
        col.setAttribute('value', data);
        col.style.cursor = 'pointer';
        col.style.width = '100%';
        col.setAttribute('class', 'list-column')
    }
    col.appendChild(document.createTextNode(data));
    row.appendChild(col);
    return row;
}

// called upon document load & by filterData
// parses data from dictionary using keys and fills each row.col with values
function createTable(data) {
    d3.select("#table").style("display","block");
    d3.select("#thead").html("");
    d3.select("#tbody").html("");
        // table is emptied before being filled


    var table_head = document.getElementById("thead");
    var table_body = document.getElementById("tbody");
    var h_row = document.createElement("tr");
    if (analysis_type == 'coupling') {
        table_head.appendChild(setListRows(h_row, "th", "Choose a module:"));
        for (var key in data) {
            var b_row = document.createElement("tr");
            table_body.appendChild(setListRows(b_row, "td", key));
        }
    }
    else {
        // h_row.style.width = '1000px';
        // h_row.style.float = 'none';
        table_head.appendChild(setTableRows(h_row, "th", keys)) 
            // adds a completed row to table head
        data.forEach(function(d) { 
            // for each row within the data, a row is created and added to body
            var b_row = document.createElement("tr");
            table_body.appendChild(setTableRows(b_row, "td", d));
        })
    }
    
    createGraph(data);
}