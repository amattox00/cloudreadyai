# app/modules/diagrams/gcp_renderer.py

from typing import List
from uuid import uuid4

from app.modules.diagrams.models import (
    TopologyGraph,
    DiagramSpec,
    DiagramNode,
    DiagramGroup,
    DiagramEdge,
    CloudProvider,
    DiagramType,
    NodeKind,
    EdgeKind,
    DiagramLayer,
    DiagramViewMode,
)


class GcpDiagramRenderer:
    """
    Normalized TopologyGraph -> CSP-specific DiagramSpec for GCP.

    TopologyGraph = source world.
    DiagramSpec   = draw target GCP pattern (HTTP(S) LB, MIG/GKE,
                    Cloud SQL, Cloud Logging/Monitoring, IAM, etc.).

    view_mode controls source vs target visibility.
    """

    def __init__(
        self,
        topology: TopologyGraph,
        diagram_type: DiagramType,
        app_id: str | None = None,
        view_mode: DiagramViewMode = DiagramViewMode.source_and_target,
        show_criticality: bool = True,
        show_licensing: bool = True,
        show_utilization: bool = True,
    ) -> None:
        self.topology = topology
        self.diagram_type = diagram_type
        self.app_id = app_id
        self.view_mode = view_mode
        self.show_criticality = show_criticality
        self.show_licensing = show_licensing
        self.show_utilization = show_utilization

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------

    def build(self) -> DiagramSpec:
        if self.diagram_type == DiagramType.landing_zone:
            spec = self._build_landing_zone()
        elif self.diagram_type == DiagramType.app_topology:
            spec = self._build_app_topology()
        elif self.diagram_type == DiagramType.network_security:
            spec = self._build_network_security()
        elif self.diagram_type == DiagramType.data_db:
            spec = self._build_data_db()
        else:
            spec = self._build_app_topology()

        return self._apply_view_mode(spec)

    # ------------------------------------------------------------------
    # Landing zone
    # ------------------------------------------------------------------

    def _build_landing_zone(self) -> DiagramSpec:
        groups: List[DiagramGroup] = []
        nodes: List[DiagramNode] = []
        edges: List[DiagramEdge] = []

        project_id = "gcp-project-1"
        vpc_id = "gcp-vpc-1"

        groups.append(
            DiagramGroup(
                id=project_id,
                label="GCP Project",
                group_type="gcp_project",
            )
        )
        groups.append(
            DiagramGroup(
                id=vpc_id,
                label="VPC Network (Landing Zone)",
                group_type="gcp_vpc",
                parent_group_id=project_id,
            )
        )

        onprem_group_id = "onprem-1"
        groups.append(
            DiagramGroup(
                id=onprem_group_id,
                label="On-Premises Datacenter",
                group_type="onprem_datacenter",
            )
        )

        for node in self.topology.nodes.values():
            if node.kind not in {NodeKind.compute, NodeKind.database, NodeKind.app_service}:
                continue

            icon_key = self._map_node_to_gcp_icon(node.kind, node.db_engine)

            dnode = DiagramNode(
                id=node.id,
                label=node.name,
                icon_key=icon_key,
                parent_group_id=vpc_id,
                is_critical=(self.show_criticality and node.criticality is not None),
                compliance_tags=node.compliance_tags if self.show_criticality else [],
                utilization_band=node.utilization_band if self.show_utilization else None,
                licensing_badge=node.license_product if self.show_licensing else None,
                is_target=False,
                source_node_id=node.id,
                layer=DiagramLayer.app if node.kind != NodeKind.database else DiagramLayer.data,
            )
            nodes.append(dnode)

        node_ids = {n.id for n in nodes}
        for e in self.topology.edges:
            if e.kind not in {EdgeKind.connects_to, EdgeKind.runs_on}:
                continue
            if e.source_id not in node_ids or e.target_id not in node_ids:
                continue
            edges.append(
                DiagramEdge(
                    id=e.id,
                    source_id=e.source_id,
                    target_id=e.target_id,
                    label=e.description,
                )
            )

        return DiagramSpec(
            cloud=CloudProvider.gcp,
            diagram_type=self.diagram_type,
            title=f"GCP Landing Zone – Run {self.topology.run_id}",
            groups=groups,
            nodes=nodes,
            edges=edges,
            metadata={},
        )

    # ------------------------------------------------------------------
    # App topology: SOURCE + TARGET GCP pattern
    # ------------------------------------------------------------------

    def _build_app_topology(self) -> DiagramSpec:
        groups: List[DiagramGroup] = []
        nodes: List[DiagramNode] = []
        edges: List[DiagramEdge] = []

        project_id = "gcp-project-1"
        vpc_id = "gcp-vpc-1"
        web_subnet_id = "gcp-subnet-web"
        app_subnet_id = "gcp-subnet-app"
        db_subnet_id = "gcp-subnet-db"
        observability_group_id = "gcp-observability"
        security_group_id = "gcp-security"

        groups.extend(
            [
                DiagramGroup(
                    id=project_id,
                    label="GCP Project",
                    group_type="gcp_project",
                ),
                DiagramGroup(
                    id=vpc_id,
                    label="VPC Network (Target App Environment)",
                    group_type="gcp_vpc",
                    parent_group_id=project_id,
                ),
                DiagramGroup(
                    id=web_subnet_id,
                    label="Subnet (Web / Edge)",
                    group_type="gcp_subnet",
                    parent_group_id=vpc_id,
                ),
                DiagramGroup(
                    id=app_subnet_id,
                    label="Subnet (App)",
                    group_type="gcp_subnet",
                    parent_group_id=vpc_id,
                ),
                DiagramGroup(
                    id=db_subnet_id,
                    label="Subnet (DB)",
                    group_type="gcp_subnet",
                    parent_group_id=vpc_id,
                ),
                DiagramGroup(
                    id=observability_group_id,
                    label="Operations & Observability",
                    group_type="gcp_observability",
                    parent_group_id=project_id,
                ),
                DiagramGroup(
                    id=security_group_id,
                    label="Security & IAM",
                    group_type="gcp_security",
                    parent_group_id=project_id,
                ),
            ]
        )

        # Users / Internet
        users_group_id = "users-internet"
        groups.append(
            DiagramGroup(
                id=users_group_id,
                label="Users / Internet",
                group_type="internet_clients",
            )
        )

        users_node_id = "node-users"
        nodes.append(
            DiagramNode(
                id=users_node_id,
                label="Users",
                icon_key="gcp.generic",
                parent_group_id=users_group_id,
                is_target=False,
                layer=DiagramLayer.edge,
            )
        )

        # SOURCE NODES
        app_scope_nodes = self._select_app_scope_nodes()

        app_nodes: List[DiagramNode] = []
        server_nodes: List[DiagramNode] = []
        db_nodes: List[DiagramNode] = []

        for src in app_scope_nodes:
            icon_key = self._map_node_to_gcp_icon(src.kind, src.db_engine)
            parent_group = self._assign_gcp_subnet(
                src,
                web_subnet_id,
                app_subnet_id,
                db_subnet_id,
            )

            if src.kind == NodeKind.app_service:
                layer = DiagramLayer.app
            elif src.kind == NodeKind.compute:
                layer = DiagramLayer.app
            elif src.kind == NodeKind.database:
                layer = DiagramLayer.data
            else:
                layer = None

            dnode = DiagramNode(
                id=src.id,
                label=src.name,
                icon_key=icon_key,
                parent_group_id=parent_group,
                is_critical=(self.show_criticality and src.criticality is not None),
                compliance_tags=src.compliance_tags if self.show_criticality else [],
                utilization_band=src.utilization_band if self.show_utilization else None,
                licensing_badge=src.license_product if self.show_licensing else None,
                is_target=False,
                source_node_id=src.id,
                layer=layer,
            )
            nodes.append(dnode)

            if src.kind == NodeKind.app_service:
                app_nodes.append(dnode)
            elif src.kind == NodeKind.compute:
                server_nodes.append(dnode)
            elif src.kind == NodeKind.database:
                db_nodes.append(dnode)

        # TARGET GCP PATTERN

        # Edge: HTTP(S) Load Balancer + Cloud Armor
        https_lb_id = "gcp-https-lb-main"
        armor_id = "gcp-armor-main"

        nodes.extend(
            [
                DiagramNode(
                    id=https_lb_id,
                    label="HTTP(S) Load Balancer",
                    icon_key="gcp.http_lb",
                    parent_group_id=web_subnet_id,
                    is_target=True,
                    layer=DiagramLayer.edge,
                ),
                DiagramNode(
                    id=armor_id,
                    label="Cloud Armor (WAF)",
                    icon_key="gcp.armor",
                    parent_group_id=web_subnet_id,
                    is_target=True,
                    layer=DiagramLayer.security,
                ),
            ]
        )

        # App tier: Managed Instance Group
        mig_id = "gcp-mig-app"
        nodes.append(
            DiagramNode(
                id=mig_id,
                label="Managed Instance Group (App)",
                icon_key="gcp.managed_instance_group",
                parent_group_id=app_subnet_id,
                is_target=True,
                layer=DiagramLayer.app,
            )
        )

        # Data tier: Cloud SQL for primary DB
        cloudsql_nodes: List[DiagramNode] = []
        if db_nodes:
            primary_db = db_nodes[0]
            cs_id = f"gcp-cloudsql-target-{primary_db.id}"
            cloudsql_nodes.append(
                DiagramNode(
                    id=cs_id,
                    label=f"Cloud SQL ({primary_db.label})",
                    icon_key="gcp.cloud_sql",
                    parent_group_id=db_subnet_id,
                    is_target=True,
                    source_node_id=primary_db.id,
                    layer=DiagramLayer.data,
                )
            )
            nodes.extend(cloudsql_nodes)

        # Observability: Cloud Logging + Monitoring + bucket for logs
        logging_id = "gcp-cloud-logging"
        monitoring_id = "gcp-cloud-monitoring"
        bucket_id = "gcp-storage-logs"

        nodes.extend(
            [
                DiagramNode(
                    id=logging_id,
                    label="Cloud Logging",
                    icon_key="gcp.cloud_logging",
                    parent_group_id=observability_group_id,
                    is_target=True,
                    layer=DiagramLayer.ops,
                ),
                DiagramNode(
                    id=monitoring_id,
                    label="Cloud Monitoring",
                    icon_key="gcp.cloud_monitoring",
                    parent_group_id=observability_group_id,
                    is_target=True,
                    layer=DiagramLayer.ops,
                ),
                DiagramNode(
                    id=bucket_id,
                    label="Cloud Storage (Logs & Backups)",
                    icon_key="gcp.storage",
                    parent_group_id=observability_group_id,
                    is_target=True,
                    layer=DiagramLayer.ops,
                ),
            ]
        )

        # Security: IAM + firewall rules (conceptual)
        iam_id = "gcp-iam-main"
        fw_id = "gcp-firewall-main"

        nodes.extend(
            [
                DiagramNode(
                    id=iam_id,
                    label="IAM Policies",
                    icon_key="gcp.generic",
                    parent_group_id=security_group_id,
                    is_target=True,
                    layer=DiagramLayer.security,
                ),
                DiagramNode(
                    id=fw_id,
                    label="VPC Firewall Rules",
                    icon_key="gcp.firewall",
                    parent_group_id=security_group_id,
                    is_target=True,
                    layer=DiagramLayer.security,
                ),
            ]
        )

        # EDGES – users → LB → MIG → servers → DB → Cloud SQL

        edges.append(
            DiagramEdge(
                id=str(uuid4()),
                source_id=users_node_id,
                target_id=https_lb_id,
                label="HTTPS",
            )
        )
        edges.append(
            DiagramEdge(
                id=str(uuid4()),
                source_id=https_lb_id,
                target_id=armor_id,
                label="Protected traffic",
            )
        )
        edges.append(
            DiagramEdge(
                id=str(uuid4()),
                source_id=armor_id,
                target_id=mig_id,
                label="Backend service",
            )
        )

        # MIG → compute servers
        for server in server_nodes[:3]:
            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=mig_id,
                    target_id=server.id,
                    label="VM instances",
                )
            )

        # App → DB → Cloud SQL
        if app_nodes and db_nodes:
            app_src = app_nodes[0]
            db_src = db_nodes[0]

            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=app_src.id,
                    target_id=db_src.id,
                    label="App → DB",
                )
            )

            if cloudsql_nodes:
                cs_node = cloudsql_nodes[0]
                edges.append(
                    DiagramEdge(
                        id=str(uuid4()),
                        source_id=db_src.id,
                        target_id=cs_node.id,
                        label="Migrate to Cloud SQL",
                    )
                )

        # Ops edges: logs / metrics to Logging and Storage
        for n in app_nodes + server_nodes + db_nodes:
            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=n.id,
                    target_id=logging_id,
                    label="Logs",
                )
            )
            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=n.id,
                    target_id=bucket_id,
                    label="Backups / Archives",
                )
            )

        return DiagramSpec(
            cloud=CloudProvider.gcp,
            diagram_type=self.diagram_type,
            title=f"GCP App Topology (Source + Target) – Run {self.topology.run_id}",
            groups=groups,
            nodes=nodes,
            edges=edges,
            metadata={"app_id": self.app_id},
        )

    # ------------------------------------------------------------------
    # Network / security view
    # ------------------------------------------------------------------

    def _build_network_security(self) -> DiagramSpec:
        spec = self._build_app_topology()
        spec.diagram_type = DiagramType.network_security
        spec.title = f"GCP Network & Security – Run {self.topology.run_id}"
        return spec

    # ------------------------------------------------------------------
    # Data / DB view
    # ------------------------------------------------------------------

    def _build_data_db(self) -> DiagramSpec:
        base_spec = self._build_app_topology()

        data_nodes = [
            n for n in base_spec.nodes if n.layer in {DiagramLayer.data, DiagramLayer.app}
        ]
        data_ids = {n.id for n in data_nodes}

        data_edges = [
            e for e in base_spec.edges if e.source_id in data_ids and e.target_id in data_ids
        ]

        return DiagramSpec(
            cloud=CloudProvider.gcp,
            diagram_type=DiagramType.data_db,
            title=f"GCP Data & DB – Run {self.topology.run_id}",
            groups=base_spec.groups,
            nodes=data_nodes,
            edges=data_edges,
            metadata=base_spec.metadata,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _apply_view_mode(self, spec: DiagramSpec) -> DiagramSpec:
        if self.view_mode == DiagramViewMode.source_and_target:
            return spec

        if self.view_mode == DiagramViewMode.source_only:
            keep_nodes = [n for n in spec.nodes if not n.is_target]
        elif self.view_mode == DiagramViewMode.target_only:
            keep_nodes = [n for n in spec.nodes if n.is_target]
        else:
            keep_nodes = spec.nodes

        keep_ids = {n.id for n in keep_nodes}
        keep_edges = [
            e for e in spec.edges if e.source_id in keep_ids and e.target_id in keep_ids
        ]

        return DiagramSpec(
            cloud=spec.cloud,
            diagram_type=spec.diagram_type,
            title=spec.title,
            groups=spec.groups,
            nodes=keep_nodes,
            edges=keep_edges,
            metadata=spec.metadata,
        )

    def _map_node_to_gcp_icon(self, kind: NodeKind, db_engine: str | None) -> str:
        if kind == NodeKind.compute:
            return "gcp.compute_engine"
        if kind == NodeKind.database:
            if db_engine:
                engine = db_engine.lower()
                if "sql" in engine:
                    return "gcp.cloud_sql"
                if "spanner" in engine:
                    return "gcp.spanner"
            return "gcp.cloud_sql"
        if kind == NodeKind.app_service:
            return "gcp.generic"
        return "gcp.generic"

    def _assign_gcp_subnet(
        self,
        node,
        web_subnet_id: str,
        app_subnet_id: str,
        db_subnet_id: str,
    ) -> str:
        if node.kind == NodeKind.database:
            return db_subnet_id
        if node.kind == NodeKind.app_service:
            name_lower = (node.name or "").lower()
            if "web" in name_lower or "frontend" in name_lower:
                return web_subnet_id
            return app_subnet_id
        if node.kind == NodeKind.compute:
            return app_subnet_id
        return app_subnet_id

    def _select_app_scope_nodes(self):
        if not self.app_id:
            return [
                n
                for n in self.topology.nodes.values()
                if n.kind in {NodeKind.app_service, NodeKind.compute, NodeKind.database}
            ]
        return [
            n
            for n in self.topology.nodes.values()
            if n.app_id == self.app_id
            or (
                n.kind in {NodeKind.compute, NodeKind.database}
                and n.attributes.get("primary_app_id") == self.app_id
            )
        ]
