import json
import os
from typing import Dict, List
from pathlib import Path

class GrafanaDashboardGenerator:
    """Generate Grafana dashboard configurations for VNF monitoring"""
    
    def __init__(self):
        self.dashboards_dir = Path("grafana/dashboards")
        self.dashboards_dir.mkdir(parents=True, exist_ok=True)
        
    def create_vnf_overview_dashboard(self) -> Dict:
        """Create VNF Overview Dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "VNF Overview Dashboard",
                "tags": ["vnf", "overview", "performance"],
                "style": "dark",
                "timezone": "browser",
                "panels": [
                    # VNF Instance Count Panel
                    {
                        "id": 1,
                        "title": "VNF Instance Count",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "vnf_instances_total",
                                "legendFormat": "{{vnf_type}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "displayMode": "list"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
                    },
                    
                    # CPU Usage Panel
                    {
                        "id": 2,
                        "title": "CPU Usage by VNF",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(vnf_cpu_usage_seconds_total[5m])",
                                "legendFormat": "{{vnf_type}} - {{instance}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "barAlignment": 0,
                                    "lineWidth": 1,
                                    "fillOpacity": 10,
                                    "gradientMode": "none",
                                    "spanNulls": False,
                                    "showPoints": "never",
                                    "pointSize": 5,
                                    "stacking": {
                                        "mode": "none",
                                        "group": "A"
                                    },
                                    "axisLabel": "",
                                    "scaleDistribution": {
                                        "type": "linear"
                                    },
                                    "hideFrom": {
                                        "legend": False,
                                        "tooltip": False,
                                        "vis": False
                                    },
                                    "thresholds": {
                                        "steps": [
                                            {"color": "green", "value": None},
                                            {"color": "red", "value": 80}
                                        ]
                                    }
                                },
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0}
                    },
                    
                    # Memory Usage Panel
                    {
                        "id": 3,
                        "title": "Memory Usage by VNF",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "vnf_memory_usage_bytes / vnf_memory_limit_bytes * 100",
                                "legendFormat": "{{vnf_type}} - {{instance}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 1,
                                    "fillOpacity": 10,
                                    "thresholds": {
                                        "steps": [
                                            {"color": "green", "value": None},
                                            {"color": "yellow", "value": 70},
                                            {"color": "red", "value": 90}
                                        ]
                                    }
                                },
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    
                    # Network Throughput Panel
                    {
                        "id": 4,
                        "title": "Network Throughput",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(vnf_network_bytes_total[5m])",
                                "legendFormat": "{{vnf_type}} - {{instance}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 1,
                                    "fillOpacity": 10
                                },
                                "unit": "Bps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    
                    # VNF Health Status Panel
                    {
                        "id": 5,
                        "title": "VNF Health Status",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "vnf_health_status",
                                "format": "table",
                                "instant": True
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "custom": {
                                    "align": "auto",
                                    "displayMode": "auto"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "timepicker": {},
                "templating": {
                    "list": []
                },
                "annotations": {
                    "list": []
                },
                "refresh": "5s"
            }
        }
        
        return dashboard
    
    def create_latency_improvement_dashboard(self) -> Dict:
        """Create Latency Improvement Overview Dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "uid": "latency-improvement",
                "title": "Latency Improvement Overview",
                "tags": ["latency", "improvement", "sfc"],
                "style": "dark",
                "timezone": "browser",
                "panels": [
                    # Panel 1: End-to-End Latency Trend (Current P95 vs Baseline)
                    {
                        "id": 1,
                        "title": "End-to-End Latency Trend",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(sfc_current_latency_seconds_bucket[5m]))",
                                "legendFormat": "Current P95 Latency"
                            },
                            {
                                "expr": "vector(0.14)",
                                "legendFormat": "Baseline P95 (140 ms)"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "s",
                                "color": {"mode": "palette-classic"},
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2,
                                    "fillOpacity": 10
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                    },
                    
                    # Panel 2: Test Case 1 Improvement % (Stat)
                    {
                        "id": 2,
                        "title": "Test Case 1 Improvement %",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "((0.14 - histogram_quantile(0.95, rate(sfc_current_latency_seconds_bucket[5m]))) / 0.14) * 100",
                                "legendFormat": "Improvement"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"color": "red", "value": None},
                                        {"color": "orange", "value": 15},
                                        {"color": "green", "value": 30}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 8}
                    },
                    
                    # Panel 3: Tail Latency Distribution (P50/P95/P99/P99.9)
                    {
                        "id": 3,
                        "title": "Tail Latency Distribution",
                        "type": "timeseries",
                        "targets": [
                            {"expr": "histogram_quantile(0.50, rate(sfc_current_latency_seconds_bucket[5m]))", "legendFormat": "P50"},
                            {"expr": "histogram_quantile(0.95, rate(sfc_current_latency_seconds_bucket[5m]))", "legendFormat": "P95"},
                            {"expr": "histogram_quantile(0.99, rate(sfc_current_latency_seconds_bucket[5m]))", "legendFormat": "P99"},
                            {"expr": "histogram_quantile(0.999, rate(sfc_current_latency_seconds_bucket[5m]))", "legendFormat": "P99.9"}
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "s",
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineWidth": 2}
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 14}
                    },
                    
                    # Panel 4: P99 Improvement % (Stat)
                    {
                        "id": 4,
                        "title": "P99 Improvement %",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "((0.32 - histogram_quantile(0.99, rate(sfc_current_latency_seconds_bucket[5m]))) / 0.32) * 100",
                                "legendFormat": "P99 Improvement"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"color": "red", "value": None},
                                        {"color": "orange", "value": 15},
                                        {"color": "green", "value": 30}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 8}
                    },
                    
                    # Panel 5: Throughput at 100 ms SLA Trend
                    {
                        "id": 5,
                        "title": "Throughput at 100 ms SLA",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(sfc_requests_processed_total{latency_bucket=\"le_0.1\"}[5m])",
                                "legendFormat": "Throughput under 100 ms SLA"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "req/s",
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineWidth": 2}
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 22}
                    },
                    
                    # Panel 6: Throughput Improvement % (Stat)
                    {
                        "id": 6,
                        "title": "Throughput Improvement %",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "((rate(sfc_requests_processed_total{latency_bucket=\"le_0.1\"}[5m]) - 2100) / 2100) * 100",
                                "legendFormat": "Throughput Improvement"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"color": "red", "value": None},
                                        {"color": "orange", "value": 0},
                                        {"color": "green", "value": 15}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 8}
                    },
                    
                    # Panel 7: Latency Component Breakdown
                    {
                        "id": 7,
                        "title": "Latency Component Breakdown",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(vnf_processing_latency_seconds_sum[5m]) / rate(vnf_processing_latency_seconds_count[5m])",
                                "legendFormat": "Processing"
                            },
                            {
                                "expr": "rate(vnf_queuing_latency_seconds_sum[5m]) / rate(vnf_queuing_latency_seconds_count[5m])",
                                "legendFormat": "Queuing"
                            },
                            {
                                "expr": "rate(sdn_network_latency_seconds_sum[5m]) / rate(sdn_network_latency_seconds_count[5m])",
                                "legendFormat": "Network"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "s",
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineWidth": 2}
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 30}
                    }
                ],
                "time": {"from": "now-6h", "to": "now"},
                "timepicker": {},
                "templating": {"list": []},
                "annotations": {"list": []},
                "refresh": "10s"
            }
        }
        
        return dashboard
    
    def create_drl_agent_dashboard(self) -> Dict:
        """Create DRL Agent Dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "DRL Agent Dashboard",
                "tags": ["drl", "agent", "learning"],
                "style": "dark",
                "timezone": "browser",
                "panels": [
                    # Training Loss Panel
                    {
                        "id": 1,
                        "title": "Training Loss",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "drl_training_loss",
                                "legendFormat": "Loss"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2,
                                    "fillOpacity": 20
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    
                    # Episode Rewards Panel
                    {
                        "id": 2,
                        "title": "Episode Rewards",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "drl_episode_reward",
                                "legendFormat": "Reward"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2,
                                    "fillOpacity": 20
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    
                    # Epsilon Decay Panel
                    {
                        "id": 3,
                        "title": "Epsilon Decay",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "drl_epsilon",
                                "legendFormat": "Epsilon"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2
                                },
                                "min": 0,
                                "max": 1
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    
                    # Action Distribution Panel
                    {
                        "id": 4,
                        "title": "Action Distribution",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum(drl_action_count) by (action_type)",
                                "legendFormat": "{{action_type}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "displayLabels": ["percent", "name"]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    
                    # SFC Satisfaction Rate Panel
                    {
                        "id": 5,
                        "title": "SFC Satisfaction Rate",
                        "type": "gauge",
                        "targets": [
                            {
                                "expr": "drl_sfc_satisfaction_rate",
                                "legendFormat": "Satisfaction Rate"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "thresholds": {
                                        "steps": [
                                            {"color": "red", "value": None},
                                            {"color": "yellow", "value": 0.7},
                                            {"color": "green", "value": 0.9}
                                        ]
                                    }
                                },
                                "min": 0,
                                "max": 1,
                                "unit": "percentunit"
                            }
                        },
                        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 16}
                    },
                    
                    # Resource Efficiency Panel
                    {
                        "id": 6,
                        "title": "Resource Efficiency",
                        "type": "gauge",
                        "targets": [
                            {
                                "expr": "drl_resource_efficiency",
                                "legendFormat": "Efficiency"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "thresholds": {
                                        "steps": [
                                            {"color": "red", "value": None},
                                            {"color": "yellow", "value": 0.6},
                                            {"color": "green", "value": 0.8}
                                        ]
                                    }
                                },
                                "min": 0,
                                "max": 1,
                                "unit": "percentunit"
                            }
                        },
                        "gridPos": {"h": 8, "w": 8, "x": 8, "y": 16}
                    },
                    
                    # Agent Statistics Panel
                    {
                        "id": 7,
                        "title": "Agent Statistics",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "drl_training_steps",
                                "legendFormat": "Training Steps"
                            },
                            {
                                "expr": "drl_replay_buffer_size",
                                "legendFormat": "Replay Buffer Size"
                            },
                            {
                                "expr": "drl_episodes_completed",
                                "legendFormat": "Episodes Completed"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "displayMode": "list"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 8, "x": 16, "y": 16}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "timepicker": {},
                "templating": {
                    "list": []
                },
                "annotations": {
                    "list": []
                },
                "refresh": "5s"
            }
        }
        
        return dashboard
    
    def create_arima_forecasting_dashboard(self) -> Dict:
        """Create ARIMA Forecasting Dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "ARIMA Forecasting Dashboard",
                "tags": ["arima", "forecasting", "prediction"],
                "style": "dark",
                "timezone": "browser",
                "panels": [
                    # Historical Data vs Forecast Panel
                    {
                        "id": 1,
                        "title": "Historical Data vs Forecast",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "arima_historical_data",
                                "legendFormat": "Historical Data"
                            },
                            {
                                "expr": "arima_forecast",
                                "legendFormat": "Forecast"
                            },
                            {
                                "expr": "arima_forecast_upper_ci",
                                "legendFormat": "Upper CI"
                            },
                            {
                                "expr": "arima_forecast_lower_ci",
                                "legendFormat": "Lower CI"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2,
                                    "fillOpacity": 10
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                    },
                    
                    # Forecast Accuracy Metrics Panel
                    {
                        "id": 2,
                        "title": "Forecast Accuracy Metrics",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "arima_mae",
                                "legendFormat": "MAE"
                            },
                            {
                                "expr": "arima_rmse",
                                "legendFormat": "RMSE"
                            },
                            {
                                "expr": "arima_mape",
                                "legendFormat": "MAPE"
                            },
                            {
                                "expr": "arima_r_squared",
                                "legendFormat": "R²"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "displayMode": "list"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    
                    # Model Quality Metrics Panel
                    {
                        "id": 3,
                        "title": "Model Quality Metrics",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "arima_aic",
                                "legendFormat": "AIC"
                            },
                            {
                                "expr": "arima_bic",
                                "legendFormat": "BIC"
                            },
                            {
                                "expr": "arima_ljung_box_pvalue",
                                "legendFormat": "Ljung-Box p-value"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "displayMode": "list"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    
                    # Scaling Recommendations Panel
                    {
                        "id": 4,
                        "title": "Scaling Recommendations",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "arima_scaling_recommendation",
                                "format": "table",
                                "instant": True
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "custom": {
                                    "align": "auto",
                                    "displayMode": "auto"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "timepicker": {},
                "templating": {
                    "list": []
                },
                "annotations": {
                    "list": []
                },
                "refresh": "10s"
            }
        }
        
        return dashboard
    
    def create_sfc_performance_dashboard(self) -> Dict:
        """Create SFC Performance Dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "SFC Performance Dashboard",
                "tags": ["sfc", "performance", "latency"],
                "style": "dark",
                "timezone": "browser",
                "panels": [
                    # End-to-End Latency Panel
                    {
                        "id": 1,
                        "title": "End-to-End Latency",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sfc_e2e_latency_seconds",
                                "legendFormat": "{{chain_id}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2,
                                    "thresholds": {
                                        "steps": [
                                            {"color": "green", "value": None},
                                            {"color": "yellow", "value": 0.5},
                                            {"color": "red", "value": 1.0}
                                        ]
                                    }
                                },
                                "unit": "s"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    
                    # SFC Throughput Panel
                    {
                        "id": 2,
                        "title": "SFC Throughput",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(sfc_packets_processed_total[5m])",
                                "legendFormat": "{{chain_id}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2
                                },
                                "unit": "packets/sec"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    
                    # VNF Chain Status Panel
                    {
                        "id": 3,
                        "title": "VNF Chain Status",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "sfc_chain_status",
                                "format": "table",
                                "instant": True
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "custom": {
                                    "align": "auto",
                                    "displayMode": "auto"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    
                    # SLA Violations Panel
                    {
                        "id": 4,
                        "title": "SLA Violations",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sfc_sla_violations_total",
                                "legendFormat": "{{chain_id}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "bars",
                                    "lineWidth": 1
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    
                    # Resource Utilization by Chain Panel
                    {
                        "id": 5,
                        "title": "Resource Utilization by Chain",
                        "type": "heatmap",
                        "targets": [
                            {
                                "expr": "sfc_resource_utilization",
                                "format": "heatmap",
                                "legendFormat": "{{chain_id}} - {{resource_type}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "thresholds": {
                                        "steps": [
                                            {"color": "green", "value": None},
                                            {"color": "yellow", "value": 0.7},
                                            {"color": "red", "value": 0.9}
                                        ]
                                    }
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "timepicker": {},
                "templating": {
                    "list": []
                },
                "annotations": {
                    "list": []
                },
                "refresh": "5s"
            }
        }
        
        return dashboard
    
    def create_alerting_dashboard(self) -> Dict:
        """Create Alerting Dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "Alerting Dashboard",
                "tags": ["alerts", "notifications", "incidents"],
                "style": "dark",
                "timezone": "browser",
                "panels": [
                    # Active Alerts Panel
                    {
                        "id": 1,
                        "title": "Active Alerts",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "alerts",
                                "format": "table",
                                "instant": True
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "custom": {
                                    "align": "auto",
                                    "displayMode": "auto"
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                    },
                    
                    # Alert History Panel
                    {
                        "id": 2,
                        "title": "Alert History",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "changes(alertmanager_alerts[1h])",
                                "legendFormat": "{{alertname}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "drawStyle": "line",
                                    "lineInterpolation": "linear",
                                    "lineWidth": 2
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    
                    # Alert Severity Distribution Panel
                    {
                        "id": 3,
                        "title": "Alert Severity Distribution",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "count by (severity) (alerts)",
                                "legendFormat": "{{severity}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "palette-classic"
                                },
                                "custom": {
                                    "displayLabels": ["percent", "name"]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "timepicker": {},
                "templating": {
                    "list": []
                },
                "annotations": {
                    "list": []
                },
                "refresh": "10s"
            }
        }
        
        return dashboard
    
    def generate_all_dashboards(self):
        """Generate all dashboard configurations"""
        dashboards = {
            "vnf_overview": self.create_vnf_overview_dashboard(),
            "drl_agent": self.create_drl_agent_dashboard(),
            "arima_forecasting": self.create_arima_forecasting_dashboard(),
            "sfc_performance": self.create_sfc_performance_dashboard(),
            "alerting": self.create_alerting_dashboard(),
            "latency_improvement": self.create_latency_improvement_dashboard()
        }
        
        # Save each dashboard to file
        for name, dashboard in dashboards.items():
            filepath = self.dashboards_dir / f"{name}_dashboard.json"
            with open(filepath, 'w') as f:
                json.dump(dashboard, f, indent=2)
            print(f"Generated {name} dashboard: {filepath}")
        
        # Create dashboard index
        self.create_dashboard_index(dashboards)
        
        return dashboards
    
    def create_dashboard_index(self, dashboards: Dict):
        """Create an index file listing all dashboards"""
        index = {
            "dashboards": [
                {
                    "name": name.replace("_", " ").title(),
                    "file": f"{name}_dashboard.json",
                    "description": self.get_dashboard_description(name)
                }
                for name in dashboards.keys()
            ]
        }
        
        index_file = self.dashboards_dir / "dashboard_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"Generated dashboard index: {index_file}")
    
    def get_dashboard_description(self, name: str) -> str:
        """Get description for dashboard"""
        descriptions = {
            "vnf_overview": "Comprehensive overview of VNF instances, resource usage, and health status",
            "drl_agent": "Deep Reinforcement Learning agent training metrics and performance indicators",
            "arima_forecasting": "ARIMA forecasting results, accuracy metrics, and scaling recommendations",
            "sfc_performance": "Service Function Chain performance metrics including latency and throughput",
            "alerting": "Active alerts, alert history, and severity distribution",
            "latency_improvement": "Real-time latency improvement tracking across test cases with component breakdown"
        }
        return descriptions.get(name, "Dashboard for monitoring and visualization")

def main():
    """Generate all Grafana dashboards"""
    generator = GrafanaDashboardGenerator()
    dashboards = generator.generate_all_dashboards()
    
    print(f"\nGenerated {len(dashboards)} dashboards:")
    for name in dashboards.keys():
        print(f"  - {name.replace('_', ' ').title()}")
    
    print(f"\nDashboard files saved to: {generator.dashboards_dir}")
    print("Import these JSON files into Grafana to set up the monitoring dashboards.")

if __name__ == "__main__":
    main()
