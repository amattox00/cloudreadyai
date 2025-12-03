# backend/app/modules/phase7c/templates/aws_app_tier.py

def aws_app_tier_template(overrides: dict) -> dict:
    """
    Simple AWS 3-tier app layout:
      - VPC box
      - Public subnet (ALB)
      - Private subnet (App)
      - DB subnet (RDS/Aurora)
    """

    app_name = overrides.get("app_name", "CloudReadyApp")
    environment = overrides.get("environment", "Prod")

    title = f"{app_name} – {environment} – AWS 3-Tier"

    return {
        "name": title,
        "nodes": [
            # VPC frame
            {
                "id": "vpc",
                "label": f"VPC – {environment}",
                "x": 40,
                "y": 40,
                "width": 420,
                "height": 260,
                "style": (
                    "rounded=1;whiteSpace=wrap;html=1;"
                    "fillColor=#f7f7f7;strokeColor=#232f3e;"
                ),
            },
            # Public subnet (ALB)
            {
                "id": "public_subnet",
                "label": "Public Subnet\n(ALB / Ingress)",
                "x": 60,
                "y": 70,
                "width": 180,
                "height": 80,
                "style": (
                    "rounded=1;whiteSpace=wrap;html=1;"
                    "fillColor=#cce5ff;strokeColor=#004b8d;"
                ),
            },
            # Private subnet (App servers)
            {
                "id": "private_subnet",
                "label": "Private Subnet\n(App Servers / ECS / EKS)",
                "x": 240,
                "y": 70,
                "width": 200,
                "height": 80,
                "style": (
                    "rounded=1;whiteSpace=wrap;html=1;"
                    "fillColor=#e6ffcc;strokeColor=#4c7c2a;"
                ),
            },
            # DB subnet
            {
                "id": "db_subnet",
                "label": "DB Subnet\n(RDS / Aurora)",
                "x": 140,
                "y": 180,
                "width": 220,
                "height": 80,
                "style": (
                    "rounded=1;whiteSpace=wrap;html=1;"
                    "fillColor=#ffe6cc;strokeColor=#b36b00;"
                ),
            },
        ],
        "edges": [
            {
                "id": "edge_public_private",
                "source": "public_subnet",
                "target": "private_subnet",
                "style": "endArrow=block;strokeColor=#232f3e;",
            },
            {
                "id": "edge_private_db",
                "source": "private_subnet",
                "target": "db_subnet",
                "style": "endArrow=block;strokeColor=#232f3e;",
            },
        ],
    }
