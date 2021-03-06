/**
* Created by td6301 on 26/05/2017.
*/
var seriesOptions = [];
var streamChart;
var data;
var chartData;
var timestamps;
var heatmapData;  // different format to other charts
var chartType;
var chartZoom;
var numVariables;  // for multivariate data, how many variables
var categories;    // categories for multivariate data

var availableRanges = {
    '1h': {
        type: 'hour',
        count: 1,
        text: '1h'
    },
    '6h': {
        type: 'hour',
        count: 6,
        text: '6h'
    },
    '12h': {
        type: 'hour',
        count: 12,
        text: '12h'
    },
    '1D': {
        type: 'day',
        count: 1,
        text: '1D'
    },
    '7D': {
        type: 'week',
        count: 1,
        text: '7D'
    },
    '1M': {
        type: 'month',
        count: 1,
        text: '1M'
    },
    'All': {
        type: 'all',
        count: 1,
        text: 'All'
    }
};


// default chart type for multivariate and univariate charts
if (typeof(window.defaultChartType) === 'undefined') {
    window.defaultChartType = {
        'true': 'line',
        'false': 'line'
    };
}

// default zoom level for multivariate and univariate charts
if (typeof(window.defaultChartZoom) === 'undefined') {
    window.defaultChartZoom = {
        'true': '1D',
        'false': '1D'
    };
}

function isNumeric(n) {
    'use strict'; return !isNaN(parseFloat(n)) && isFinite(n);
}

var globalSeriesOptions = {
    'line': {
        type: 'line',
        tooltip: {
            // headerFormat: 'Value<br/>',
            // pointFormat: '{point.x:%e %b, %Y %H:%M} {point.y}: <b>{point.value}</b>',
            pointFormatter: function() {
                'use strict'; var point = this;
                return '<span style="color:' + point.color + '">\u25CF</span> ' + point.series.name + ': <b>' + point.y + '</b><br/>';
            },
            followPointer: true,
            snap: 1
        }
    },
    'column': {
        type: 'column',
        tooltip: {valueDecimals: 2}
    },
    'bar': {
        type: 'bar',
        tooltip: {valueDecimals: 2}
    },
    'heatmap': {
        type: 'heatmap',
        boostThreshold: 100,
        borderWidth: 0,
        nullColor: '#EFEFEF',
        colsize: 24 * 36e5, // one day
        tooltip: {
            headerFormat: '{point.x}<br/>',
            pointFormat: '{point.y}: <b>{point.value}</b>',
            followPointer: true,
            snap: 1,
            xDateFormat: '%e %b, %Y %H:%M}<br/>'
        }
    }
};

function createSeries(data, type, multivariate, i, name) {
    'use strict'; if (multivariate) {
        if (type === 'heatmap') {
            // set multivariate to false since it's a single series for heatmap
            createSeries(heatmapData, 'heatmap', false);
        } else {
            var timestamps = _.pluck(data, 0);
            var values = _.pluck(data, 1);
            var unzipped = _.unzip(values);

            if (unzipped.length === 0) {
                // The values may be in a dict
                var keys = _.uniq(_.flatten(_.map(values, _.keys)));

                _.each(keys, function(key, i) {
                    var column = _.pluck(values, key);
                    createSeries(_.zip(timestamps, column), type, false, i, key);
                });
            }

            // Create series for multi-line plots
            _.each(unzipped, function(column, i) {
                // recursive call to create each series
                createSeries(_.zip(timestamps, column), type, false, i);
            });
        }
    } else {
        // Make a deep copy of the series definition
        var series = jQuery.extend(true, {}, globalSeriesOptions[type]);
        series.data = data;
        i = (typeof i === 'undefined') ? 1 : i;
        name = (typeof name === 'undefined') ? i : name;
        series.name = name;
        seriesOptions[i - 1] = series;
    }
}

function createRangeSelector(chartZoom) {
    'use strict';

    return {
        buttons: _.values(availableRanges),
        selected: _.indexOf(_.keys(availableRanges), chartZoom),
        inputEnabled: false
    };
}

function createChart(chartType, chartZoom, seriesOptions, streamId, name, metaData) {'use strict';
    var chartDefinition = {
        title: {
            text: name
        },
        chart: {
            type: chartType
        },
        boost: {
            useGPUTranslations: true
        },
        subtitle: {
            text: metaData
        },
        xAxis: {
            type: 'datetime',
            format: '%e %b, %Y'
        },
        yAxis: {
            title: {
                text: null
            }
        },
        series: seriesOptions,
        credits: {
            enabled: false
        },
        rangeSelector: createRangeSelector(chartZoom)
    };

    if (chartType !== 'heatmap') {
    } else {
        chartDefinition.xAxis.categories = timestamps;
        chartDefinition.xAxis.gapGridLineWidth = 0;
        chartDefinition.yAxis = {
            categories: categories,
            title: {text: null},
            min: 0,
            max: numVariables,
            labels: {style: {color: 'white', fontSize: '14px'}}
        };
        chartDefinition.yAxis.max = numVariables;
        chartDefinition.legend = {
            'enabled': true,
            'align': 'right',
            'layout': 'vertical',
            'verticalAlign': 'middle',
            'symbolHeight': 320
        };
        chartDefinition.colorAxis = {
            minColor: '#3060cf',
            maxColor: '#c4463a'
        };
    }

    streamChart = Highcharts.stockChart('chart-' + streamId, chartDefinition);
}

var allChartTypes = ['line', 'column', 'bar', 'heatmap'];

function getLabel(c, streamId) {
    'use strict'; return $('#label-' + c + streamId);
}

function show(availableChartTypes, active, streamId) {
    // Show the available chart types, and set the active one
    _.each(availableChartTypes, function(c) {
        var label = getLabel(c, streamId);
        label.show();
        if (c === active) {
            label.addClass('active');
        } else {
            label.removeClass('active');
        }
    });

    // Hide all the other chart types
    _.each(_.difference(allChartTypes, availableChartTypes), function(c) {
        var label = getLabel(c, streamId);
        label.hide();
        label.removeClass('active');
    });
}
