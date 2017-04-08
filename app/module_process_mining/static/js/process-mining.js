$(document).ready(function(){
    namespace = '/test';

    displayLoadingModal(true)

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace, {
        transports: ['polling']
    });

    //Draw graph
     function initGraph(message) {
         //Math.seedrandom("Bluestone");
        config.layout = true;
        config.get_graph = message.graph_position;
        myDiagram = init();
        drawGraph(myDiagram);
    }

    function drawGraph (myDiagram, min, max) {
        var tokens = get_demo_tokens(min, max);
        initTokens(myDiagram, tokens);
    }

    var componentBase = {
                        chart:{
                            backgroundColor: 'rgba(255, 255, 255, 0)'
                        },
                        title:{
                            text: ''
                        },
                        series: [{
                                color: 'rgb(255,255,255)'
                        }],
                        legend:{
                            itemStyle: {
                                color: '#fff'
                        }},
                        credits : {
                            enabled: false
                        },
                        plotOptions: {
                            series: {
                                animation: {
                                    duration: 20
                        }}}
                    }

    var barChartBase = {
                        chart:{
                            events: {
                                selection: function(event) {
                                    if (event.xAxis) {
                                        socket.emit(
                                            "addFilter",
                                            {
                                                filterType: "timeRange",
                                                lower: Math.floor(event.xAxis[0].min),
                                                upper: Math.ceil(event.xAxis[0].max)
                                            }
                                        )
                                        return false;
                                    }
                                }
                            },
                            zoomType: 'x',
                            renderTo: "chartNbEventsPerDay",
                            type: "column"
                        },
                        xAxis:{
                            type: "datetime",
                            dateTimeLabelFormats: { // don't display the dummy year
                                month: '%e. %b',
                                year: '%b'
                            },
                            title: {
                                color: '#fff',
                                text: "Date"
                            },
                            labels: {
                                style: {
                                    fontSize: '11px',
                                    fontFamily: 'Verdana, sans-serif',
                                    color: '#fff'
                                }
                            }
                        },
                        yAxis: [{
                                title: {
                                    text: 'Number of triggered actions'
                                },
                                labels: {
                                    style: {
                                        fontSize: '11px',
                                        fontFamily: 'Verdana, sans-serif',
                                        color: '#fff'
                                    }}
                        }],
                        series: [{
                                data: [],
                                name:"#events by day",
                                yAxis: 0,
                        }],
                        legend:{
                            enabled: true,
                        },
                        plotOptions: {
                            column: {
                                cursor: 'zoom-in',
                                point: {
                                    events: {
                                        click: function (event) {
                                            displayLoadingModal(true)

                                            // http://jsfiddle.net/7xEhW/31/
                                            socket.emit(
                                                "addFilter",
                                                {
                                                    filterType: "daily",
                                                    date: this.x
                                                }
                                            )

                                        }
                                    }
                                }
                            }
                        }
                    }

    var pieChartBase = {
                        chart: {
                            type: "pie",
                        },
                        series: [{
                                data: [],
                                name:"#events by day",
                                yAxis: 0
                        }],
                        legend:{
                            enabled: true,
                        },
                        plotOptions: {
                            column: {
                                cursor: 'zoom-in'
                                }
                            }
                        }

    var eventtypePieChartBase = {
                        series: [{
                                data: [],
                                name:"#events by type",
                                point:{
                                    events:{
                                        click: function (event) {
                                            displayLoadingModal(true)

                                            // http://jsfiddle.net/7xEhW/31/
                                            console.log(this)
                                            socket.emit(
                                                "addFilter",
                                                {
                                                    filterType: "list",
                                                    filterBy: "event",
                                                    filterList: [this.name]
                                                }
                                            )
                                        }
                                    }
                                }
                        }]
                        }

    var userPieChartBase = {
                        series: [{
                                data: [],
                                name:"#events by user",
                                point:{
                                    events:{
                                        click: function (event) {
                                            displayLoadingModal(true)

                                            // http://jsfiddle.net/7xEhW/31/
                                            socket.emit(
                                                "addFilter",
                                                {
                                                    filterType: "list",
                                                    filterBy: "user",
                                                    filterList: [this.name]
                                                }
                                            )
                                        }
                                    }
                                }
                        }]
                        }

    var barChart = new Highcharts.Chart($.extend(true, {}, componentBase, barChartBase ))
    var eventtypePieChart = new Highcharts.Chart($.extend(true, {}, componentBase, pieChartBase, eventtypePieChartBase, {chart: {renderTo: "chartNbEventsPerEventtype"}} ))
    var eventtypePieChartModal = new Highcharts.Chart($.extend(true, {}, componentBase, pieChartBase, eventtypePieChartBase, {chart: {renderTo: "chartNbEventsPerEventtypeModal"}} ))
    var userPieChart = new Highcharts.Chart($.extend(true, {}, componentBase, pieChartBase, userPieChartBase, {chart: {renderTo: "chartNbEventsPerUser"}}))
    var userPieChartModal = new Highcharts.Chart($.extend(true, {}, componentBase, pieChartBase, userPieChartBase, {chart: {renderTo: "chartNbEventsPerUserModal"}} ))

    socket.on('highchartsData', function(message) {
        initGraph(message.graph);
        // TODO check data shape
        updateFilterList(message.filterList)
        barChart.series[0].setData(message.barChartData)
        eventtypePieChart.series[0].setData(message.eventtypePieChartData)
        eventtypePieChartModal.series[0].setData(message.eventtypePieChartData)
        userPieChart.series[0].setData(message.userPieChartData)
        userPieChartModal.series[0].setData(message.userPieChartData)
        displayLoadingModal(false)
    });

    updateFilterList = function(filterList) {
        var stats = '<p class="btn btn-default">Case IDs: ' + nFormatter(filterList.filtered_case_id_amount, 1) + ' / ' + nFormatter(filterList.total_case_id_amount, 1) + '</p>'
        var content = filterList.filter_list.map(x => formatFilter(x.id, x.text)).join('')
        $('#breadcrumb').html(stats + content)
        $('span.remove-filter').click(function(event){
            displayLoadingModal(true)
            socket.emit("removeFilter", {filterIdx:parseInt($(this).attr('name').split('-')[2])})
        })
    }
})

displayLoadingModal = function(bool) {
    $('.cssload').css('display', bool ? 'flex' : 'none')
}

formatFilter = function(filterId, filterText) {
    return '<p class="btn btn-default">' + filterText +
    '<span name="remove-filter-' + filterId + '" class="remove-filter fa-stack"><i class="fa fa-circle fa-stack-2x text-danger"></i><i class="fa fa-trash-o fa-stack-1x fa-inverse"></i></span></p>'
}

function nFormatter(num, digits) {
  var si = [
    { value: 1E18, symbol: "E" },
    { value: 1E15, symbol: "P" },
    { value: 1E12, symbol: "T" },
    { value: 1E9,  symbol: "G" },
    { value: 1E6,  symbol: "M" },
    { value: 1E3,  symbol: "k" }
  ], rx = /\.0+$|(\.[0-9]*[1-9])0+$/, i;
  for (i = 0; i < si.length; i++) {
    if (num >= si[i].value) {
      return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
    }
  }
  return num.toFixed(digits).replace(rx, "$1");
}