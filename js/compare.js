// data
var timeParse = d3.timeParse('%Y-%m-%d %H');
d3.json('data/hourly.json').then(function(data) {
	var dataset = _.map(data.data, (obj) => {
        obj.dt_string = obj.datetime;
		obj.datetime = d3.timeDay.offset(timeParse(obj.datetime), -1);
		obj.image_url = 'img/' + obj.img;
		return obj;
	});
	init_chart(dataset);
});

// chart
function init_chart (dataset) {
    var body = $('body');
	var margin = {
		top: 50, 
		right: 50, 
		bottom: 50, 
		left: 80,
	};
	var width = body.innerWidth() - margin.left - margin.right;
	var height = 400 - margin.top - margin.bottom;


	var svg = d3.select('#chart')
		.append('svg')
		.attr('width', width + margin.left + margin.right)
		.attr('height', height + margin.top + margin.bottom)
		.append('g')
		.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

	svg.append('defs')
		.append('clipPath')
		.attr('id', 'clip')
		.append('rect')
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', width)
		.attr('height', height);

    // get the daily total rather than by hour
    var groups =_.groupBy(dataset, 'day');
    dataset = _.map(groups, (grp) => {
        var point = grp[0];
        point.total = _.sumBy(grp, 'total'); 
        point.grp = grp;
        return point;
    })
    //dataset = _.filter(dataset, (d) => {
    //    return _.includes([2,3,4,5,6], d.datetime.getDay());
    //});

	// axes
	var x = d3.scaleTime().range([0, width]);
	var y = d3.scaleLinear().range([height, 0]);

	x.domain(d3.extent(_.map(dataset, 'datetime').concat([new Date('2014-12-31'), new Date('2016-01-02')])));
	y.domain([0, d3.max(dataset, function (d) { return d.total; })]).nice();


	var x_axis = d3.axisBottom()
		.scale(x)
		.ticks(10);

	var y_axis = d3.axisLeft()
		.scale(y)
		.ticks(10);

	svg.append('g')
		.attr('class', 'x axis')
		.attr('transform', 'translate(0,' + height + ')')
		.call(x_axis);
	svg.append('g')
		.attr('class', 'y axis')
		.call(y_axis);

	// text label for the y axis
	svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x',0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
	  .style('font-size', '11px')
	  .style('font-family', 'Helvetica Neue, Helvetica')
      .text('metric tons of carbon (tC) emitted per day');      

    //var line = d3.line()
    //    .x(function(d) { return x(d.datetime); })
    //    .y(function(d) { return y(d.total); });

    //svg.append('path')
    //    .datum(dataset)
    //    .attr('class', 'line')
    //    .attr('d', line)
    //    .attr('clip-path', 'url(#clip)')
    //    .attr('opacity', '1')
    //    .attr('stroke', 'rgb(80,80,255)')

    var div = d3.select('body').append('div')   
        .attr('class', 'tooltip')               
        .style('font-size', '11px')
        .style('opacity', 0);



    var pad = 1;
    var bars = svg.selectAll('.bar')
        .data(dataset)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('clip-path', 'url(#clip)');

    function do_bars (bars, x) {
        function bar_width () {
            return x(new Date('2015-01-02')) - x(new Date('2015-01-01')) - 0.8;
        }
        bars.attr('width', bar_width)
        .attr('height', function(d) {
            return height - y(d.total);
        })
        .attr('x', function(d) {
            return x(d.datetime) - (bar_width() / 2);
        })
        .attr('y', function(d) {
            return y(d.total);
        })
        .style('fill', (d) => {
			return d3.interpolateReds((d.total - 3000000) / 3000000);
		})
        .on('mouseover', function(d) {      
			d3.select(this)
				.style('fill', 'rgba(0,0,100,0.3)')

            div.transition().duration(50)      
				.style('opacity', .9);      

			// TODO get rid of magic numbers!!!
			if (x(d.datetime) > (width - 100)) {
				div.html(moment(d.datetime).format(' ddd, MMM Do') + '<br/>'  + d.total.toLocaleString() + ' tC')  
					.style('left', (x(d.datetime) - (bar_width() / 2) + 11) + 'px')
					.style('border-right', '1px solid rgba(0,0,0,0.5)')
					.style('border-left', 'none')
					.style('top', '210px');    
			} else {
				div.html(moment(d.datetime).format(' ddd, MMM Do') + '<br/>'  + d.total.toLocaleString() + ' tC')  
					.style('left', (x(d.datetime) - (bar_width() / 2) + 100) + 'px')
					.style('border-left', '1px solid rgba(0,0,0,0.5)')
					.style('border-right', 'none')
					.style('top', '210px');    
			}
        })                  
        .on('mouseout', function(d) {       
            div.transition().duration(50)      
				.style('opacity', 0);   

			d3.select(this)
				.style('fill', (d) => {
					return d3.interpolateReds((d.total - 3000000) / 3000000);
				})
        });
    }
    do_bars(bars, x)



    ////
    //function zoom(svg) {
    //  const extent = [[margin.left, margin.top], [width - margin.right, height - margin.top]];
    //  
    //  svg.call(d3.zoom()
    //      .scaleExtent([1, 8])
    //      .translateExtent(extent)
    //      .extent(extent)
    //      .on("zoom", zoomed));
    //  
    //  function zoomed() {
    //    x.range([margin.left, width - margin.right].map(d => d3.event.transform.applyX(d)));
    //    svg.selectAll(".bars rect").attr("x", d => x(d.name)).attr("width", x.bandwidth());
    //    svg.selectAll(".x-axis").call(xAxis);
    //  }
    //}


	// handle zooming
	var zoom = d3.zoom()
		.scaleExtent([1, 50])
		//.translateExtent([
		//	[ x.range()[0], y.range()[1] ],
		//	[ x.range()[1], y.range()[0] ],
		//])
		.on('zoom', zoomed);

	d3.select('svg').call(zoom);

	function zoomed () {
        div.style('opacity', 0);
		var t = d3.event.transform;
		t.x = d3.min([t.x, 0]);
		t.y = d3.min([t.y, 0]);
		t.x = d3.max([t.x, (1-t.k) * width]);
		t.y = d3.max([t.y, (1-t.k) * height]);
		let new_x = t.rescaleX(x);
		rescale_x_axis(new_x, 0);
	}
	function rescale_x_axis (new_x, duration) {
		svg.select('.x.axis')
			//.transition().duration(50)
			.call(x_axis.scale(new_x));
        do_bars(svg.selectAll('.bar'), new_x);
	}
	function show_week () {
		bars.transition().duration(500).style('opacity', (d) => {
			return (d.datetime.getDay() == 0 || d.datetime.getDay() == 6) ? 0 : 1;
		});		
	}
	function show_weekend () {
		bars.transition().duration(500).style('opacity', (d) => {
			return (d.datetime.getDay() == 0 || d.datetime.getDay() == 6) ? 1 : 0;
		});		
	}
	function show_all () {
		bars.transition().duration(500).style('opacity', 1);
	}
	$('#show-week').click(show_week);
	$('#show-weekend').click(show_weekend);
	$('#show-all').click(show_all);
}
