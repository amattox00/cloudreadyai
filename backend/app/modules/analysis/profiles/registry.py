# backend/app/modules/analysis/profiles/registry.py

ANALYSIS_PROFILES = {
    "migration_readiness": {
        "display_name": "Migration Readiness",
        "weights": {
            "utilization": 0.10,
            "dependencies": 0.30,
            "data_quality": 0.20,
            "risk": 0.30,
            "modernization": 0.10,
        },
        "required_slices": [
            "servers",
            "storage",
            "network",
            "dependencies",
        ],
        "flags_enabled": [
            "missing_data",
            "high_risk",
            "unclear_dependencies",
        ],
        "recommendations_enabled": [
            "migration_strategy",
            "risk_mitigation",
            "modernization",
        ],
    },

    "cost_optimization": {
        "display_name": "Cost Optimization",
        "weights": {
            "utilization": 0.40,
            "dependencies": 0.05,
            "data_quality": 0.10,
            "risk": 0.10,
            "modernization": 0.05,
            "cost_impact": 0.30,
        },
        "required_slices": ["servers", "utilization"],
        "flags_enabled": ["oversized", "low_utilization"],
        "recommendations_enabled": ["right_size"],
    },

    "modernization": {
        "display_name": "Modernization Potential",
        "weights": {
            "modernization": 0.40,
            "risk": 0.20,
            "dependencies": 0.15,
            "utilization": 0.10,
            "data_quality": 0.15,
        },
        "required_slices": ["servers", "applications", "databases"],
        "flags_enabled": ["legacy_os", "legacy_db"],
        "recommendations_enabled": ["modernization"],
    },

    "operational_risk": {
        "display_name": "Operational Risk",
        "weights": {
            "risk": 0.50,
            "dependencies": 0.20,
            "data_quality": 0.15,
            "utilization": 0.05,
            "modernization": 0.10,
        },
        "required_slices": ["servers", "storage", "network"],
        "flags_enabled": ["eol_os", "no_redundancy", "no_backups"],
        "recommendations_enabled": ["risk_mitigation"],
    },

    "cloud_fit": {
        "display_name": "Cloud Fit Score",
        "weights": {
            "cloud_fit": 0.40,
            "dependencies": 0.20,
            "risk": 0.10,
            "modernization": 0.20,
            "data_quality": 0.10,
        },
        "required_slices": ["servers", "network", "storage"],
        "flags_enabled": ["latency_sensitive", "specialized_hardware"],
        "recommendations_enabled": ["architecture"],
    },
}


def get_profile_config(profile_name: str):
    """Return the profile config, fallback to migration_readiness."""
    return ANALYSIS_PROFILES.get(profile_name, ANALYSIS_PROFILES["migration_readiness"])
