# backend/app/modules/phase7b/diagram_templates/gcp.py

def gcp_project_network_template():
    """
    Simple GCP Shared VPC layout:
    - Organization / Folder
    - Shared VPC host project
    - Two service projects attached to the shared VPC
    """
    return {
        "name": "GCP Shared VPC Layout",
        "nodes": [
            {
                "id": "n1",
                "label": "GCP Organization / Folder",
                "x": 80,
                "y": 40,
                "width": 260,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f0f5ff;strokeColor=#1a73e8;",
            },
            {
                "id": "n2",
                "label": "Shared VPC Host Project",
                "x": 80,
                "y": 150,
                "width": 260,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f0fe;strokeColor=#174ea6;",
            },
            {
                "id": "n3",
                "label": "Service Project 1\n(Workloads)",
                "x": 40,
                "y": 260,
                "width": 200,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e6fffa;strokeColor=#0f766e;",
            },
            {
                "id": "n4",
                "label": "Service Project 2\n(Data / Analytics)",
                "x": 260,
                "y": 260,
                "width": 220,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff7e6;strokeColor=#b25a00;",
            },
        ],
        "edges": [
            {
                "id": "e1",
                "source": "n1",
                "target": "n2",
                "style": "endArrow=block;strokeColor=#1a73e8;",
            },
            {
                "id": "e2",
                "source": "n2",
                "target": "n3",
                "style": "endArrow=block;strokeColor=#1a73e8;",
            },
            {
                "id": "e3",
                "source": "n2",
                "target": "n4",
                "style": "endArrow=block;strokeColor=#1a73e8;",
            },
        ],
    }

def gcp_dr_topology_template():
    """
    Simple GCP DR topology:
    - Primary project / region
    - DR project / region
    """
    return {
        "name": "GCP DR Topology",
        "nodes": [
            {
                "id": "n10",
                "label": "Primary Project\n(us-central1)",
                "x": 40,
                "y": 80,
                "width": 240,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f0fe;strokeColor=#174ea6;",
            },
            {
                "id": "n11",
                "label": "DR Project\n(europe-west1)",
                "x": 320,
                "y": 80,
                "width": 240,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff7e6;strokeColor=#b25a00;",
            },
        ],
        "edges": [
            {
                "id": "e10",
                "source": "n10",
                "target": "n11",
                "style": "endArrow=block;dashed=1;strokeColor=#1a73e8;",
            },
        ],
    }
