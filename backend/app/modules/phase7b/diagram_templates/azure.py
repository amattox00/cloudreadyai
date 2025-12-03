# backend/app/modules/phase7b/diagram_templates/azure.py

def azure_hub_spoke_template():
    """
    Simple Azure hub-and-spoke network:
    - Hub VNet with shared services/security
    - Two spoke VNets for workloads
    """
    return {
        "name": "Azure Hub-Spoke Network",
        "nodes": [
            {
                "id": "n1",
                "label": "Hub VNet\n(Security / Shared Services)",
                "x": 80,
                "y": 60,
                "width": 260,
                "height": 90,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d6e4ff;strokeColor=#0050b3;",
            },
            {
                "id": "n2",
                "label": "Spoke VNet 1\n(App Tier / AKS)",
                "x": 40,
                "y": 200,
                "width": 200,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e6fffb;strokeColor=#006d75;",
            },
            {
                "id": "n3",
                "label": "Spoke VNet 2\n(Data Tier)",
                "x": 260,
                "y": 200,
                "width": 200,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff1b8;strokeColor=#d48806;",
            },
        ],
        "edges": [
            {
                "id": "e1",
                "source": "n1",
                "target": "n2",
                "style": "endArrow=block;strokeColor=#0050b3;",
            },
            {
                "id": "e2",
                "source": "n1",
                "target": "n3",
                "style": "endArrow=block;strokeColor=#0050b3;",
            },
        ],
    }

def azure_dr_topology_template():
    """
    Simple Azure DR topology:
    - Primary region VNet
    - DR region VNet
    - Replication between them
    """
    return {
        "name": "Azure DR Topology",
        "nodes": [
            {
                "id": "n10",
                "label": "Primary Region VNet\n(e.g., East US)",
                "x": 40,
                "y": 80,
                "width": 240,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d6e4ff;strokeColor=#0050b3;",
            },
            {
                "id": "n11",
                "label": "DR Region VNet\n(e.g., West Europe)",
                "x": 320,
                "y": 80,
                "width": 240,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff1b8;strokeColor=#d48806;",
            },
        ],
        "edges": [
            {
                "id": "e10",
                "source": "n10",
                "target": "n11",
                "style": "endArrow=block;dashed=1;strokeColor=#0050b3;",
            },
        ],
    }
