"""
ECharts Widget - Wrapper for Apache ECharts in PyQt5
Uses QWebEngineView to render interactive charts
"""

import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel

from .pyqt_theme import ECHARTS_THEME, C


class EChartsWidget(QWidget):
    """
    A reusable widget that embeds Apache ECharts.

    Usage:
        chart = EChartsWidget()
        layout.addWidget(chart)
        chart.set_option({
            'title': {'text': 'My Chart'},
            'xAxis': {'type': 'category', 'data': ['A', 'B', 'C']},
            'yAxis': {'type': 'value'},
            'series': [{'type': 'bar', 'data': [10, 20, 30]}]
        })
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._ready = False
        self._pending_option = None

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Load ECharts
        self._init_echarts()

    def _init_echarts(self):
        """Initialize ECharts with embedded JS"""

        # Read echarts.min.js (works in both dev and PyInstaller bundle)
        from core.paths import resource_path
        echarts_path = resource_path('gui/assets/echarts.min.js')

        try:
            with open(echarts_path, 'r', encoding='utf-8') as f:
                echarts_js = f.read()
        except FileNotFoundError:
            echarts_js = ""
            print(f"Warning: echarts.min.js not found at {echarts_path}")

        # Theme JSON
        theme_json = json.dumps(ECHARTS_THEME)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{
            width: 100%;
            height: 100%;
            background-color: transparent;
            overflow: hidden;
        }}
        #chart {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>{echarts_js}</script>
    <script>
        // Register dark theme
        echarts.registerTheme('dark', {theme_json});

        // Initialize chart with dark theme
        var chart = echarts.init(document.getElementById('chart'), 'dark');

        // Handle resize
        window.addEventListener('resize', function() {{
            chart.resize();
        }});

        // Function to set chart option from Python
        function setOption(optionJson) {{
            try {{
                var option = JSON.parse(optionJson);
                chart.setOption(option, true);  // true = notMerge
            }} catch(e) {{
                console.error('ECharts setOption error:', e);
            }}
        }}

        // Function to clear chart
        function clearChart() {{
            chart.clear();
        }}

        // Signal ready
        window.chartReady = true;
    </script>
</body>
</html>
"""

        # Connect to load finished
        self.web_view.loadFinished.connect(self._on_load_finished)

        # Load HTML
        self.web_view.setHtml(html)

    def _on_load_finished(self, ok):
        """Called when page finishes loading"""
        if ok:
            self._ready = True
            # If there's a pending option, apply it now
            if self._pending_option:
                self._apply_option(self._pending_option)
                self._pending_option = None

    def set_option(self, option: dict):
        """
        Set the ECharts option.

        Args:
            option: A dict containing ECharts configuration
        """
        if self._ready:
            self._apply_option(option)
        else:
            # Store for later when page is ready
            self._pending_option = option

    def _apply_option(self, option: dict):
        """Actually apply the option to the chart"""
        # Serialize to JSON
        option_json = json.dumps(option)
        # Escape for JS string
        option_json = option_json.replace('\\', '\\\\').replace("'", "\\'")

        # Execute JS
        js = f"setOption('{option_json}');"
        self.web_view.page().runJavaScript(js)

    def clear(self):
        """Clear the chart"""
        if self._ready:
            self.web_view.page().runJavaScript("clearChart();")

    def resizeEvent(self, event):
        """Handle resize to trigger chart resize"""
        super().resizeEvent(event)
        if self._ready:
            self.web_view.page().runJavaScript("chart.resize();")


def create_line_chart_option(title, x_data, series_data, y_axis_name="Value"):
    """
    Helper to create a basic line chart option.

    Args:
        title: Chart title
        x_data: List of x-axis labels
        series_data: List of dicts with 'name' and 'data' keys
        y_axis_name: Y-axis label

    Returns:
        ECharts option dict
    """
    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'cross'}
        },
        'legend': {
            'data': [s['name'] for s in series_data],
            'top': 30
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '3%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'category',
            'boundaryGap': False,
            'data': x_data
        },
        'yAxis': {
            'type': 'value',
            'name': y_axis_name
        },
        'dataZoom': [
            {'type': 'inside', 'start': 0, 'end': 100},
            {'type': 'slider', 'start': 0, 'end': 100}
        ],
        'series': [
            {
                'name': s['name'],
                'type': 'line',
                'data': s['data'],
                'smooth': True
            }
            for s in series_data
        ]
    }


def create_bar_chart_option(title, x_data, series_data, y_axis_name="Value"):
    """
    Helper to create a basic bar chart option.
    """
    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'shadow'}
        },
        'legend': {
            'data': [s['name'] for s in series_data],
            'top': 30
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '3%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'category',
            'data': x_data
        },
        'yAxis': {
            'type': 'value',
            'name': y_axis_name
        },
        'series': [
            {
                'name': s['name'],
                'type': 'bar',
                'data': s['data']
            }
            for s in series_data
        ]
    }


def create_scatter_chart_option(title, series_data, x_axis_name="X", y_axis_name="Y"):
    """
    Helper to create a scatter chart option.

    Args:
        title: Chart title
        series_data: List of dicts with 'name' and 'data' keys
                     data should be list of [x, y] pairs
    """
    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {
            'trigger': 'item',
            'formatter': '{a}: ({c})'
        },
        'legend': {
            'data': [s['name'] for s in series_data],
            'top': 30
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '3%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'value',
            'name': x_axis_name
        },
        'yAxis': {
            'type': 'value',
            'name': y_axis_name
        },
        'series': [
            {
                'name': s['name'],
                'type': 'scatter',
                'data': s['data'],
                'symbolSize': 10
            }
            for s in series_data
        ]
    }


def create_candlestick_option(title, dates, ohlc_data, volume_data=None):
    """
    Helper to create a candlestick chart option.

    Args:
        title: Chart title
        dates: List of date strings
        ohlc_data: List of [open, close, low, high] values
        volume_data: Optional list of volume values
    """
    grids = [{'left': '10%', 'right': '8%', 'height': '50%'}]
    x_axes = [{'type': 'category', 'data': dates, 'boundaryGap': False}]
    y_axes = [{'type': 'value', 'scale': True}]
    series = [
        {
            'name': 'Price',
            'type': 'candlestick',
            'data': ohlc_data,
            'itemStyle': {
                'color': C['up'],
                'color0': C['down'],
                'borderColor': C['up'],
                'borderColor0': C['down']
            }
        }
    ]

    if volume_data:
        grids.append({'left': '10%', 'right': '8%', 'top': '63%', 'height': '16%'})
        x_axes.append({
            'type': 'category',
            'gridIndex': 1,
            'data': dates,
            'boundaryGap': False,
            'axisTick': {'show': False},
            'axisLabel': {'show': False}
        })
        y_axes.append({
            'type': 'value',
            'gridIndex': 1,
            'splitNumber': 2,
            'axisLabel': {'show': False}
        })
        series.append({
            'name': 'Volume',
            'type': 'bar',
            'xAxisIndex': 1,
            'yAxisIndex': 1,
            'data': volume_data,
            'itemStyle': {'color': C['dim']}
        })

    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'cross'}
        },
        'legend': {'data': ['Price'], 'top': 30},
        'grid': grids,
        'xAxis': x_axes,
        'yAxis': y_axes,
        'dataZoom': [
            {'type': 'inside', 'xAxisIndex': [0, 1] if volume_data else [0]},
            {'type': 'slider', 'xAxisIndex': [0, 1] if volume_data else [0], 'top': '85%'}
        ],
        'series': series
    }


def create_pie_chart_option(title, data, show_legend=True):
    """
    Helper to create a pie chart option.

    Args:
        title: Chart title
        data: List of dicts with 'name' and 'value' keys
    """
    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {
            'trigger': 'item',
            'formatter': '{a} <br/>{b}: {c} ({d}%)'
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left',
            'show': show_legend
        },
        'series': [
            {
                'name': title,
                'type': 'pie',
                'radius': ['40%', '70%'],
                'avoidLabelOverlap': False,
                'itemStyle': {
                    'borderRadius': 10,
                    'borderColor': C['bg'],
                    'borderWidth': 2
                },
                'label': {
                    'show': False,
                    'position': 'center'
                },
                'emphasis': {
                    'label': {
                        'show': True,
                        'fontSize': 20,
                        'fontWeight': 'bold'
                    }
                },
                'labelLine': {'show': False},
                'data': data
            }
        ]
    }


def create_heatmap_option(title, x_data, y_data, values, min_val=None, max_val=None):
    """
    Helper to create a heatmap option.

    Args:
        title: Chart title
        x_data: List of x-axis labels
        y_data: List of y-axis labels
        values: List of [x_index, y_index, value] triples
        min_val: Minimum value for color scale
        max_val: Maximum value for color scale
    """
    if min_val is None:
        min_val = min(v[2] for v in values) if values else 0
    if max_val is None:
        max_val = max(v[2] for v in values) if values else 100

    return {
        'title': {'text': title, 'left': 'center'},
        'tooltip': {
            'position': 'top'
        },
        'grid': {
            'height': '50%',
            'top': '10%'
        },
        'xAxis': {
            'type': 'category',
            'data': x_data,
            'splitArea': {'show': True}
        },
        'yAxis': {
            'type': 'category',
            'data': y_data,
            'splitArea': {'show': True}
        },
        'visualMap': {
            'min': min_val,
            'max': max_val,
            'calculable': True,
            'orient': 'horizontal',
            'left': 'center',
            'bottom': '15%',
            'inRange': {
                'color': [C['down'], C['yellow'], C['up']]
            }
        },
        'series': [{
            'name': title,
            'type': 'heatmap',
            'data': values,
            'label': {'show': True},
            'emphasis': {
                'itemStyle': {
                    'shadowBlur': 10,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    }
