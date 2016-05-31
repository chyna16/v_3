function setTableRows(row, elem_id, data) {
    for (i = 0; i < keys.length; i++) {
        var col = document.createElement(elem_id);

        if (i == 0) { col.style.width = "40%"; }
        else { col.style.width = (60 / (keys_len-1)) + "%"; }

        col.style.overflow = "hidden";
        col.style.fontSize = "15px";
        col.onmouseover = function() { this.style.overflow = "visible"; }
        col.onmouseout = function() { this.style.overflow = "hidden"; }
        // col.style.backgroundColor = "white"; INTERFERES W/ OVERFLOW

        if (data == keys) {
            if (i != 0 && keys[i] != "coupled") { 
                col.onclick = function() { chooseColumn(this); }
                col.style.cursor = 'pointer';
            }
            col.setAttribute('value', data[i]);
            col.appendChild(document.createTextNode(data[i])); 
        } 
        else { 
            if (i == 0 && analysis_type == "coupling") { 
                col.onclick = function() { chooseModule(this); }
                col.style.cursor = 'pointer';
            }
            col.setAttribute('value', data[keys[i]]);
            col.appendChild(document.createTextNode(data[keys[i]])); 
        }

        row.appendChild(col);
    }
    return row;
}


// parses data from dictionary using keys and fills each row.col with values
function createTable(data) {
    d3.select("#thead").html(""); // table is emptied before being filled
    d3.select("#tbody").html(""); // table is emptied before being filled

    var table_head = document.getElementById("thead");
    var h_row = document.createElement("tr");
    table_head.appendChild(setTableRows(h_row, "th", keys))

    var table_body = document.getElementById("tbody");
    data.forEach(function(d) { 
        var b_row = document.createElement("tr");
        table_body.appendChild(setTableRows(b_row, "td", d));
    })

    createGraph(data);
}