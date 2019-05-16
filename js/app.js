function img_number () {
    return parseInt(window.location.hash.substring(1)); 
}
function img_src () {
    var padded = img_number().toString().padStart(6, '0');
    return `http://127.0.0.1:8080/img/${padded}.png`;
}
function show_img () {
    // show png of carbon emissions
    canvas=document.getElementById('canvas');
    var context=canvas.getContext('2d');
    var image=new Image();
    image.onload=function(){
        context.drawImage(image,0,0,canvas.width,canvas.height);
    };
    image.src=img_src();
}
function show_chart () {
    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 60};
    var width = 1920 - margin.left - margin.right;
    var height = 200 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    $('#chart').empty();
    var svg = d3.select("#chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    d3.json('hourly.json', function (json_data) {
        console.log('showing chart'); 
        var data = json_data.data;
        var slice_idx = img_number() - 240;
        data.forEach((x) => {
            x.datetime = d3.timeParse("%Y-%m-%d %H")(x.datetime);
        });

        slice_idx = slice_idx <=0 ? 1 : slice_idx;
        slice_data = data.slice(slice_idx, slice_idx + 480);

        // Add X axis --> it is a date format
        var x = d3.scaleTime()
        .domain(d3.extent(slice_data, function(d) { return d.datetime; }))
        .range([ 0, width ]);

        xAxis = svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

        // Add Y axis
        var y = d3.scaleLinear()
        .domain([0, d3.max(data, function(d) { return d.total; })])
        .range([ height, 0 ]);

        yAxis = svg.append("g")
        .call(d3.axisLeft(y));

        // Add a clipPath: everything out of this area won't be drawn.
        var clip = svg.append("defs")
        .append("svg:clipPath")
        .attr("id", "clip")
        .append("svg:rect")
        .attr("width", width )
        .attr("height", height )
        .attr("x", 0)
        .attr("y", 0);

        // Create the line variable: where both the line and the brush take place
        var line = svg.append('g')
        .attr("clip-path", "url(#clip)");

        // Add the line
        line.append("path")
        .datum(slice_data)
        .attr("class", "line")  // I add the class line to be able to modify this line later on.
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr(
            "d", 
            d3.line()
            .x(function(d) { return x(d.datetime) })
            .y(function(d) { return y(d.total) })
        );
    });
}

$('#back').click(() => {
    window.location.hash = parseInt(window.location.hash.substring(1)) - 1;
});
$('#next').click(() => {
    window.location.hash = parseInt(window.location.hash.substring(1)) + 1;
});

window.onhashchange = () => {
    show_img();
    show_chart();
};

if (!window.location.hash) {
    window.location.hash='1';
} else {
    $(window).trigger('hashchange');
}
