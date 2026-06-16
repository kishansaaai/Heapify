import io
import json

import requests

from heapify.config import config, INDEX_LTM_BUGS

DASHBOARD_ID = "heapify-dashboard"
DATA_VIEW_ID = "heapify-ltm-bugs-dataview"

# ── helpers ──────────────────────────────────────────────────────────────

def _data_view():
    return {
        "type": "index-pattern",
        "id": DATA_VIEW_ID,
        "attributes": {
            "title": INDEX_LTM_BUGS,
            "timeFieldName": "timestamp",
            "name": "Heapify Bugs",
        },
        "references": [],
    }


def _lens(obj_id, title, vis_type, layer_id, columns, column_order, vis_config, filters=None):
    ref_name = f"indexpattern-datasource-layer-{layer_id}"
    state = {
        "datasourceStates": {
            "formBased": {
                "layers": {
                    layer_id: {
                        "columnOrder": column_order,
                        "columns": columns,
                    }
                }
            }
        },
        "visualization": vis_config,
        "filters": filters or [],
        "query": {"language": "kuery", "query": ""},
    }
    return {
        "type": "lens",
        "id": obj_id,
        "typeMigrationVersion": "8.9.0",
        "attributes": {
            "title": title,
            "visualizationType": vis_type,
            "state": state,
        },
        "references": [
            {"type": "index-pattern", "id": DATA_VIEW_ID, "name": ref_name},
        ],
    }


def _count_col(label="Count"):
    return {
        "operationType": "count",
        "dataType": "number",
        "isBucketed": False,
        "label": label,
        "sourceField": "___records___",
    }


def _terms_col(field, label=None, size=10, order_col="col-count"):
    return {
        "operationType": "terms",
        "sourceField": field,
        "dataType": "string",
        "isBucketed": True,
        "label": label or field,
        "params": {
            "size": size,
            "orderBy": {"type": "column", "columnId": order_col},
            "orderDirection": "desc",
        },
    }


# ── metric panels ───────────────────────────────────────────────────────

def _metric_viz(obj_id, label, severity_filter=None):
    layer_id = f"layer-{obj_id.split('-')[-1]}"
    columns = {"col-count": _count_col(label)}
    vis_config = {
        "layerId": layer_id,
        "layerType": "data",
        "metricAccessor": "col-count",
    }
    kql = f'severity: "{severity_filter}"' if severity_filter else ""
    ref_name = f"indexpattern-datasource-layer-{layer_id}"
    state = {
        "datasourceStates": {
            "formBased": {
                "layers": {
                    layer_id: {
                        "columnOrder": ["col-count"],
                        "columns": columns,
                    }
                }
            }
        },
        "visualization": vis_config,
        "filters": [],
        "query": {"language": "kuery", "query": kql},
    }
    return {
        "type": "lens",
        "id": obj_id,
        "typeMigrationVersion": "8.9.0",
        "attributes": {
            "title": label,
            "visualizationType": "lnsMetric",
            "state": state,
        },
        "references": [
            {"type": "index-pattern", "id": DATA_VIEW_ID, "name": ref_name},
        ],
    }


# ── chart panels ─────────────────────────────────────────────────────────

def _bugs_over_time():
    layer_id = "layer-time"
    columns = {
        "col-x": {
            "operationType": "date_histogram",
            "sourceField": "timestamp",
            "dataType": "date",
            "isBucketed": True,
            "label": "Timestamp",
            "params": {"interval": "auto"},
        },
        "col-breakdown": _terms_col("severity", "Severity", size=5, order_col="col-count"),
        "col-count": _count_col("Bugs"),
    }
    vis_config = {
        "preferredSeriesType": "bar_stacked",
        "layers": [
            {
                "layerId": layer_id,
                "layerType": "data",
                "seriesType": "bar_stacked",
                "xAccessor": "col-x",
                "accessors": ["col-count"],
                "splitAccessor": "col-breakdown",
            }
        ],
        "legend": {"isVisible": True, "position": "right"},
        "valueLabels": "hide",
    }
    return _lens(
        "heapify-viz-bugs-over-time",
        "Bug Discovery Over Time",
        "lnsXY",
        layer_id,
        columns,
        ["col-x", "col-breakdown", "col-count"],
        vis_config,
    )


def _bugs_by_pattern():
    layer_id = "layer-pattern"
    columns = {
        "col-slice": _terms_col("bug_pattern", "Bug Pattern", size=20, order_col="col-count"),
        "col-count": _count_col("Count"),
    }
    vis_config = {
        "shape": "donut",
        "layers": [
            {
                "layerId": layer_id,
                "layerType": "data",
                "primaryGroups": ["col-slice"],
                "metrics": ["col-count"],
                "numberDisplay": "percent",
                "categoryDisplay": "default",
                "legendDisplay": "default",
            }
        ],
    }
    return _lens(
        "heapify-viz-bugs-by-pattern",
        "Bugs by Pattern",
        "lnsPie",
        layer_id,
        columns,
        ["col-slice", "col-count"],
        vis_config,
    )


def _bugs_by_severity():
    layer_id = "layer-severity"
    columns = {
        "col-bucket": _terms_col("severity", "Severity", size=10, order_col="col-count"),
        "col-count": _count_col("Bugs"),
    }
    vis_config = {
        "preferredSeriesType": "bar_horizontal",
        "layers": [
            {
                "layerId": layer_id,
                "layerType": "data",
                "seriesType": "bar_horizontal",
                "xAccessor": "col-bucket",
                "accessors": ["col-count"],
            }
        ],
        "legend": {"isVisible": False},
        "valueLabels": "show",
    }
    return _lens(
        "heapify-viz-bugs-by-severity",
        "Bugs by Severity",
        "lnsXY",
        layer_id,
        columns,
        ["col-bucket", "col-count"],
        vis_config,
    )


def _pattern_tools_heatmap():
    layer_id = "layer-heatmap"
    columns = {
        "col-y": _terms_col("bug_pattern", "Bug Pattern", size=20, order_col="col-value"),
        "col-x": _terms_col("tools_involved", "Tool", size=20, order_col="col-value"),
        "col-value": _count_col("Count"),
    }
    vis_config = {
        "layerId": layer_id,
        "layerType": "data",
        "xAccessor": "col-x",
        "yAccessor": "col-y",
        "valueAccessor": "col-value",
        "shape": "heatmap",
        "legend": {"isVisible": True, "position": "right"},
    }
    return _lens(
        "heapify-viz-pattern-tools-heatmap",
        "Bug Pattern × Tools Involved",
        "lnsHeatmap",
        layer_id,
        columns,
        ["col-y", "col-x", "col-value"],
        vis_config,
    )


def _bugs_by_run():
    layer_id = "layer-run"
    columns = {
        "col-x": _terms_col("run_id", "Run", size=50, order_col="col-count"),
        "col-count": _count_col("Bugs"),
    }
    vis_config = {
        "preferredSeriesType": "bar",
        "layers": [
            {
                "layerId": layer_id,
                "layerType": "data",
                "seriesType": "bar",
                "xAccessor": "col-x",
                "accessors": ["col-count"],
            }
        ],
        "legend": {"isVisible": False},
        "valueLabels": "show",
    }
    return _lens(
        "heapify-viz-bugs-by-run",
        "Bugs by Run",
        "lnsXY",
        layer_id,
        columns,
        ["col-x", "col-count"],
        vis_config,
    )


def _bug_detail_table():
    layer_id = "layer-table"
    columns = {
        "col-ts": {
            "operationType": "date_histogram",
            "sourceField": "timestamp",
            "dataType": "date",
            "isBucketed": True,
            "label": "Time",
            "params": {"interval": "1h"},
        },
        "col-severity": _terms_col("severity", "Severity", size=100, order_col="col-count"),
        "col-pattern": _terms_col("bug_pattern", "Pattern", size=100, order_col="col-count"),
        "col-tools": _terms_col("tools_involved", "Tools", size=100, order_col="col-count"),
        "col-desc": _terms_col("bug_description", "Description", size=100, order_col="col-count"),
        "col-run": _terms_col("run_id", "Run ID", size=100, order_col="col-count"),
        "col-count": _count_col("Count"),
    }
    col_order = ["col-ts", "col-severity", "col-pattern", "col-tools", "col-desc", "col-run", "col-count"]
    vis_config = {
        "layerId": layer_id,
        "layerType": "data",
        "columns": [
            {"columnId": "col-ts"},
            {"columnId": "col-severity"},
            {"columnId": "col-pattern"},
            {"columnId": "col-tools"},
            {"columnId": "col-desc"},
            {"columnId": "col-run"},
            {"columnId": "col-count", "hidden": True},
        ],
        "paging": {"size": 50, "enabled": True},
    }
    return _lens(
        "heapify-viz-bug-detail-table",
        "Bug Detail Table",
        "lnsDatatable",
        layer_id,
        columns,
        col_order,
        vis_config,
    )


# ── dashboard assembly ──────────────────────────────────────────────────

PANEL_LAYOUT = [
    # Row 0: metrics (h=6)
    {"id": "heapify-viz-metric-total",    "x": 0,  "y": 0,  "w": 10, "h": 6},
    {"id": "heapify-viz-metric-critical", "x": 10, "y": 0,  "w": 10, "h": 6},
    {"id": "heapify-viz-metric-high",     "x": 20, "y": 0,  "w": 10, "h": 6},
    {"id": "heapify-viz-metric-medium",   "x": 30, "y": 0,  "w": 10, "h": 6},
    {"id": "heapify-viz-metric-low",      "x": 40, "y": 0,  "w": 8,  "h": 6},
    # Row 1: time series (h=12)
    {"id": "heapify-viz-bugs-over-time",  "x": 0,  "y": 6,  "w": 48, "h": 12},
    # Row 2: donut + severity bar (h=14)
    {"id": "heapify-viz-bugs-by-pattern",  "x": 0,  "y": 18, "w": 24, "h": 14},
    {"id": "heapify-viz-bugs-by-severity", "x": 24, "y": 18, "w": 24, "h": 14},
    # Row 3: heatmap (h=14)
    {"id": "heapify-viz-pattern-tools-heatmap", "x": 0, "y": 32, "w": 48, "h": 14},
    # Row 4: bugs by run (h=12)
    {"id": "heapify-viz-bugs-by-run",     "x": 0,  "y": 46, "w": 48, "h": 12},
    # Row 5: detail table (h=16)
    {"id": "heapify-viz-bug-detail-table", "x": 0, "y": 58, "w": 48, "h": 16},
]


def _dashboard():
    panels_json = []
    references = []
    for idx, panel in enumerate(PANEL_LAYOUT):
        panel_idx = str(idx)
        panels_json.append({
            "type": "lens",
            "gridData": {
                "x": panel["x"],
                "y": panel["y"],
                "w": panel["w"],
                "h": panel["h"],
                "i": panel_idx,
            },
            "panelIndex": panel_idx,
            "embeddableConfig": {},
            "panelRefName": f"panel_{panel_idx}",
        })
        references.append({
            "name": f"panel_{panel_idx}",
            "type": "lens",
            "id": panel["id"],
        })

    return {
        "type": "dashboard",
        "id": DASHBOARD_ID,
        "attributes": {
            "title": "Heapify Bug Dashboard",
            "description": "Fuzz-testing bug analysis dashboard for the Heapify framework",
            "panelsJSON": json.dumps(panels_json),
            "timeRestore": False,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "query": {"language": "kuery", "query": ""},
                    "filter": [],
                }),
            },
        },
        "references": references,
    }


# ── public API ───────────────────────────────────────────────────────────

def create_dashboard():
    saved_objects = [
        _data_view(),
        _metric_viz("heapify-viz-metric-total", "Total Bugs"),
        _metric_viz("heapify-viz-metric-critical", "Critical Bugs", "critical"),
        _metric_viz("heapify-viz-metric-high", "High Bugs", "high"),
        _metric_viz("heapify-viz-metric-medium", "Medium Bugs", "medium"),
        _metric_viz("heapify-viz-metric-low", "Low Bugs", "low"),
        _bugs_over_time(),
        _bugs_by_pattern(),
        _bugs_by_severity(),
        _pattern_tools_heatmap(),
        _bugs_by_run(),
        _bug_detail_table(),
        _dashboard(),
    ]

    ndjson = "\n".join(json.dumps(obj) for obj in saved_objects) + "\n"

    url = f"{config.KIBANA_URL}/api/saved_objects/_import?overwrite=true"
    headers = {
        "Authorization": f"ApiKey {config.API_KEY}",
        "kbn-xsrf": "true",
        "x-elastic-internal-origin": "Kibana",
    }
    resp = requests.post(
        url,
        headers=headers,
        files={"file": ("export.ndjson", io.BytesIO(ndjson.encode()), "application/ndjson")},
    )

    if resp.status_code == 200:
        result = resp.json()
        if result.get("success"):
            print(f"  Created dashboard: {DASHBOARD_ID}")
        else:
            print(f"  Dashboard import errors: {result.get('errors', [])}")
    else:
        print(f"  Failed to import dashboard: {resp.status_code} {resp.text}")
