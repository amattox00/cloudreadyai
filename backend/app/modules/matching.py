from typing import Dict, Any

# Simplified rule-based matcher. Real logic can evolve to ML.
# Input example:
#   {"vcpus": 8, "memory_gb": 32, "os": "linux", "storage_gb": 500}

def match_services(payload: Dict[str, Any]) -> Dict[str, Any]:
    v = payload
    vcpus = int(v.get('vcpus', 2))
    mem = float(v.get('memory_gb', 8))
    osname = (v.get('os') or 'linux').lower()

    def pick_aws():
        # naive mapping
        if vcpus <= 2 and mem <= 8:
            inst = 't3.small'
        elif vcpus <= 4 and mem <= 16:
            inst = 'm6i.large'
        elif vcpus <= 8 and mem <= 32:
            inst = 'm6i.2xlarge'
        else:
            inst = 'm6i.4xlarge'
        return {"compute": inst, "storage": {"type": "gp3", "iops": "auto"}}

    def pick_azure():
        if vcpus <= 2 and mem <= 8:
            inst = 'B2s'
        elif vcpus <= 4 and mem <= 16:
            inst = 'D4s_v5'
        elif vcpus <= 8 and mem <= 32:
            inst = 'D8s_v5'
        else:
            inst = 'D16s_v5'
        disk = 'Premium SSD' if osname == 'windows' else 'Premium SSD v2'
        return {"compute": inst, "storage": {"type": disk}}

    def pick_gcp():
        if vcpus <= 2 and mem <= 8:
            inst = 'e2-standard-2'
        elif vcpus <= 4 and mem <= 16:
            inst = 'n2-standard-4'
        elif vcpus <= 8 and mem <= 32:
            inst = 'n2-standard-8'
        else:
            inst = 'n2-standard-16'
        return {"compute": inst, "storage": {"type": "pd-balanced"}}

    return {
        "AWS": pick_aws(),
        "Azure": pick_azure(),
        "GCP": pick_gcp(),
    }
