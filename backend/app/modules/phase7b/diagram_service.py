# backend/app/modules/phase7b/diagram_service.py

from .exporters.drawio_exporter import (
    generate_basic_drawio_xml,
    generate_from_template,
)
from .diagram_templates.aws import aws_landing_zone_template, aws_dr_topology_template
from .diagram_templates.azure import azure_hub_spoke_template, azure_dr_topology_template
from .diagram_templates.gcp import gcp_project_network_template, gcp_dr_topology_template

def generate_basic_drawio() -> str:
    """
    Original minimal endpoint for health/testing.
    """
    return generate_basic_drawio_xml()


def generate_cloud_diagram(
    cloud: str,
    diagram_type: str,
    overrides: dict | None = None,
) -> str:
    """
    Simple dispatcher:
      - aws   + landing_zone -> AWS landing zone diagram
      - azure + hub_spoke    -> Azure hub-spoke network
      - gcp   + shared_vpc   -> GCP Shared VPC layout
      - everything else      -> generic single-node diagram for now

    overrides:
      - org_name: str (e.g., client org name)
      - environment: str (e.g., Prod, Non-Prod)
      - workload_name: str (optional)
    """
    key = (cloud.lower(), diagram_type.lower())

    # 1) Pick base template by cloud/type
    if key == ("aws", "landing_zone"):
        template = aws_landing_zone_template()
    elif key == ("azure", "hub_spoke"):
        template = azure_hub_spoke_template()
    elif key == ("gcp", "shared_vpc"):
        template = gcp_project_network_template()
    elif key == ("aws", "dr_topology"):
        template = aws_dr_topology_template()
    elif key == ("azure", "dr_topology"):
        template = azure_dr_topology_template()
    elif key == ("gcp", "dr_topology"):
        template = gcp_dr_topology_template()
    else:
        # Fallback generic diagram
        name = f"{cloud.upper()} – {diagram_type}"
        template = {
            "name": name,
            "nodes": [
                {
                    "id": "n1",
                    "label": name,
                    "x": 80,
                    "y": 80,
                    "width": 260,
                    "height": 80,
                    "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;",
                }
            ],
            "edges": [],
        }

    # 2) Apply optional overrides to node labels
    if overrides:
        org = overrides.get("org_name")
        env = overrides.get("environment")
        workload = overrides.get("workload_name")

        for node in template.get("nodes", []):
            label = node.get("label", "")

            # --- AWS tweaks ---
            # Management account label
            if org and "Organizations" in label:
                node["label"] = f"{org}\n(Management Account)"

            # Workload OU / accounts label
            if env and "Workload OU" in label:
                node["label"] = f"Workload OU – {env}\n(Accounts)"

            # --- Azure tweaks ---
            # Hub VNet includes environment
            if env and "Hub VNet" in label:
                node["label"] = f"Hub VNet – {env}\n(Security / Shared Services)"

            # --- GCP tweaks ---
            # Org/folder
            if org and "GCP Organization" in label:
                node["label"] = f"{org} / Folder"

            # Optional workload name hook (generic)
            if workload and "Workloads" in label:
                node["label"] = f"{workload}\n(Workloads)"

    return generate_from_template(template)
