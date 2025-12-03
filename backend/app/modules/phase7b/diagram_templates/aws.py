# backend/app/modules/phase7b/diagram_templates/aws.py

def aws_landing_zone_template():
    """
    Simple AWS Landing Zone style diagram:
    - Management account (AWS Organizations)
    - Shared services account
    - Security/logging account
    - Workload OU / accounts
    """
    return {
        "name": "AWS Landing Zone",
        "nodes": [
            {
                "id": "n1",
                "label": "AWS Organizations\n(Management Account)",
                "x": 60,
                "y": 40,
                "width": 260,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f7f7f7;strokeColor=#232f3e;",
            },
            {
                "id": "n2",
                "label": "Shared Services Account",
                "x": 40,
                "y": 160,
                "width": 200,
                "height": 70,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#cce5ff;strokeColor=#004b8d;",
            },
            {
                "id": "n3",
                "label": "Security / Logging Account",
                "x": 280,
                "y": 160,
                "width": 220,
                "height": 70,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#b36b00;",
            },
            {
                "id": "n4",
                "label": "Workload OU\n(Prod / Non-Prod Accounts)",
                "x": 100,
                "y": 270,
                "width": 300,
                "height": 90,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e6ffcc;strokeColor=#4c7c2a;",
            },
        ],
        "edges": [
            {
                "id": "e1",
                "source": "n1",
                "target": "n2",
                "style": "endArrow=block;strokeColor=#232f3e;",
            },
            {
                "id": "e2",
                "source": "n1",
                "target": "n3",
                "style": "endArrow=block;strokeColor=#232f3e;",
            },
            {
                "id": "e3",
                "source": "n1",
                "target": "n4",
                "style": "endArrow=block;strokeColor=#232f3e;",
            },
        ],
    }

def aws_dr_topology_template():
    """
    Simple AWS DR topology:
    - Primary region VPC
    - DR region VPC
    - Replication arrow
    """
    return {
        "name": "AWS DR Topology",
        "nodes": [
            {
                "id": "n10",
                "label": "Primary Region VPC\n(us-east-1)",
                "x": 40,
                "y": 80,
                "width": 220,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#cce5ff;strokeColor=#004b8d;",
            },
            {
                "id": "n11",
                "label": "DR Region VPC\n(us-west-2)",
                "x": 320,
                "y": 80,
                "width": 220,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#b36b00;",
            },
        ],
        "edges": [
            {
                "id": "e10",
                "source": "n10",
                "target": "n11",
                "style": "endArrow=block;dashed=1;strokeColor=#232f3e;",
            },
        ],
    }
