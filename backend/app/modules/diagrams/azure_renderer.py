# app/modules/diagrams/azure_renderer.py

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


class AzureDiagramRenderer:
    """
    Normalized TopologyGraph -> CSP-specific DiagramSpec for Azure.

    TopologyGraph = source world (on-prem / existing workloads).
    DiagramSpec   = what we draw, including synthesized Azure target
    (Front Door, App Gateway, VMSS/AKS, Azure SQL, Monitor, etc.).

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

        subscription_id = "azure-subscription-1"
        vnet_id = "azure-vnet-1"

        groups.append(
            DiagramGroup(
                id=subscription_id,
                label="Azure Subscription",
                group_type="azure_subscription",
            )
        )
        groups.append(
            DiagramGroup(
                id=vnet_id,
                label="VNet (Landing Zone)",
                group_type="azure_vnet",
                parent_group_id=subscription_id,
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

            icon_key = self._map_node_to_azure_icon(node.kind, node.db_engine)

            dnode = DiagramNode(
                id=node.id,
                label=node.name,
                icon_key=icon_key,
                parent_group_id=vnet_id,
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
            cloud=CloudProvider.azure,
            diagram_type=self.diagram_type,
            title=f"Azure Landing Zone – Run {self.topology.run_id}",
            groups=groups,
            nodes=nodes,
            edges=edges,
            metadata={},
        )

    # ------------------------------------------------------------------
    # App topology: SOURCE + TARGET Azure pattern
    # ------------------------------------------------------------------

    def _build_app_topology(self) -> DiagramSpec:
        groups: List[DiagramGroup] = []
        nodes: List[DiagramNode] = []
        edges: List[DiagramEdge] = []

        subscription_id = "azure-subscription-1"
        vnet_id = "azure-vnet-1"
        public_web_subnet_id = "azure-subnet-public-web"
        private_app_subnet_id = "azure-subnet-private-app"
        private_db_subnet_id = "azure-subnet-private-db"
        observability_group_id = "azure-observability"
        security_group_id = "azure-security"

        groups.extend(
            [
                DiagramGroup(
                    id=subscription_id,
                    label="Azure Subscription",
                    group_type="azure_subscription",
                ),
                DiagramGroup(
                    id=vnet_id,
                    label="VNet (Target App Environment)",
                    group_type="azure_vnet",
                    parent_group_id=subscription_id,
                ),
                DiagramGroup(
                    id=public_web_subnet_id,
                    label="Subnet (Edge / Web)",
                    group_type="azure_subnet",
                    parent_group_id=vnet_id,
                ),
                DiagramGroup(
                    id=private_app_subnet_id,
                    label="Subnet (App)",
                    group_type="azure_subnet",
                    parent_group_id=vnet_id,
                ),
                DiagramGroup(
                    id=private_db_subnet_id,
                    label="Subnet (DB)",
                    group_type="azure_subnet",
                    parent_group_id=vnet_id,
                ),
                DiagramGroup(
                    id=observability_group_id,
                    label="Operations & Observability",
                    group_type="azure_observability",
                    parent_group_id=subscription_id,
                ),
                DiagramGroup(
                    id=security_group_id,
                    label="Security & IAM",
                    group_type="azure_security",
                    parent_group_id=subscription_id,
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
                icon_key="azure.generic",
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
            icon_key = self._map_node_to_azure_icon(src.kind, src.db_engine)
            parent_group = self._assign_azure_subnet(
                src,
                public_web_subnet_id,
                private_app_subnet_id,
                private_db_subnet_id,
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

        # TARGET Azure PATTERN

        # Edge: Front Door + App Gateway
        frontdoor_id = "azure-frontdoor-main"
        appgw_id = "azure-appgw-main"

        nodes.extend(
            [
                DiagramNode(
                    id=frontdoor_id,
                    label="Azure Front Door",
                    icon_key="azure.front_door",
                    parent_group_id=public_web_subnet_id,
                    is_target=True,
                    layer=DiagramLayer.edge,
                ),
                DiagramNode(
                    id=appgw_id,
                    label="Application Gateway (WAF)",
                    icon_key="azure.app_gateway",
                    parent_group_id=public_web_subnet_id,
                    is_target=True,
                    layer=DiagramLayer.web,
                ),
            ]
        )

        # App tier: VM Scale Set
        vmss_id = "azure-vmss-app"
        nodes.append(
            DiagramNode(
                id=vmss_id,
                label="VM Scale Set (App)",
                icon_key="azure.vmss",
                parent_group_id=private_app_subnet_id,
                is_target=True,
                layer=DiagramLayer.app,
            )
        )

        # Data tier: Azure SQL target
        azure_sql_nodes: List[DiagramNode] = []
        if db_nodes:
            primary_db = db_nodes[0]
            azsql_id = f"azure-sql-target-{primary_db.id}"
            azure_sql_nodes.append(
                DiagramNode(
                    id=azsql_id,
                    label=f"Azure SQL ({primary_db.label})",
                    icon_key="azure.sql_db",
                    parent_group_id=private_db_subnet_id,
                    is_target=True,
                    source_node_id=primary_db.id,
                    layer=DiagramLayer.data,
                )
            )
            nodes.extend(azure_sql_nodes)

        # Observability: Azure Monitor + App Insights + Storage
        mon_id = "azure-monitor"
        ai_id = "azure-appinsights"
        sa_logs_id = "azure-storage-logs"

        nodes.extend(
            [
                DiagramNode(
                    id=mon_id,
                    label="Azure Monitor",
                    icon_key="azure.monitor",
                    parent_group_id=observability_group_id,
                    is_target=True,
                    layer=DiagramLayer.ops,
                ),
                DiagramNode(
                    id=ai_id,
                    label="Application Insights",
                    icon_key="azure.app_insights",
                    parent_group_id=observability_group_id,
                    is_target=True,
                    layer=DiagramLayer.ops,
                ),
                DiagramNode(
                    id=sa_logs_id,
                    label="Storage Account (Logs)",
                    icon_key="azure.storage_account",
                    parent_group_id=observability_group_id,
                    is_target=True,
                    layer=DiagramLayer.ops,
                ),
            ]
        )

        # Security: Azure Firewall + Key Vault
        fw_id = "azure-firewall-main"
        kv_id = "azure-keyvault-main"

        nodes.extend(
            [
                DiagramNode(
                    id=fw_id,
                    label="Azure Firewall",
                    icon_key="azure.firewall",
                    parent_group_id=security_group_id,
                    is_target=True,
                    layer=DiagramLayer.security,
                ),
                DiagramNode(
                    id=kv_id,
                    label="Key Vault",
                    icon_key="azure.key_vault",
                    parent_group_id=security_group_id,
                    is_target=True,
                    layer=DiagramLayer.security,
                ),
            ]
        )

        # EDGES – users → Front Door → App Gateway → VMSS → servers → DB → Azure SQL

        edges.append(
            DiagramEdge(
                id=str(uuid4()),
                source_id=users_node_id,
                target_id=frontdoor_id,
                label="HTTPS",
            )
        )
        edges.append(
            DiagramEdge(
                id=str(uuid4()),
                source_id=frontdoor_id,
                target_id=appgw_id,
                label="HTTP/HTTPS",
            )
        )
        edges.append(
            DiagramEdge(
                id=str(uuid4()),
                source_id=appgw_id,
                target_id=vmss_id,
                label="Backend Pool",
            )
        )

        # VMSS → compute servers
        for server in server_nodes[:3]:
            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=vmss_id,
                    target_id=server.id,
                    label="VM instances",
                )
            )

        # App → DB → Azure SQL
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

            if azure_sql_nodes:
                azsql = azure_sql_nodes[0]
                edges.append(
                    DiagramEdge(
                        id=str(uuid4()),
                        source_id=db_src.id,
                        target_id=azsql.id,
                        label="Migrate to Azure SQL",
                    )
                )

        # Ops edges: send metrics/logs to Monitor + Storage
        for n in app_nodes + server_nodes + db_nodes:
            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=n.id,
                    target_id=mon_id,
                    label="Metrics",
                )
            )
            edges.append(
                DiagramEdge(
                    id=str(uuid4()),
                    source_id=n.id,
                    target_id=sa_logs_id,
                    label="Logs",
                )
            )

        return DiagramSpec(
            cloud=CloudProvider.azure,
            diagram_type=self.diagram_type,
            title=f"Azure App Topology (Source + Target) – Run {self.topology.run_id}",
            groups=groups,
            nodes=nodes,
            edges=edges,
            metadata={"app_id": self.app_id},
        )

    # ------------------------------------------------------------------
    # Network / security = app_topology with new title
    # ------------------------------------------------------------------

    def _build_network_security(self) -> DiagramSpec:
        spec = self._build_app_topology()
        spec.diagram_type = DiagramType.network_security
        spec.title = f"Azure Network & Security – Run {self.topology.run_id}"
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
            cloud=CloudProvider.azure,
            diagram_type=DiagramType.data_db,
            title=f"Azure Data & DB – Run {self.topology.run_id}",
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

    def _map_node_to_azure_icon(self, kind: NodeKind, db_engine: str | None) -> str:
        if kind == NodeKind.compute:
            return "azure.vm"
        if kind == NodeKind.database:
            if db_engine:
                engine = db_engine.lower()
                if "sql" in engine:
                    return "azure.sql_db"
                if "cosmos" in engine:
                    return "azure.cosmos_db"
            return "azure.sql_db"
        if kind == NodeKind.app_service:
            return "azure.app_service"
        return "azure.generic"

    def _assign_azure_subnet(
        self,
        node,
        public_web_subnet_id: str,
        private_app_subnet_id: str,
        private_db_subnet_id: str,
    ) -> str:
        if node.kind == NodeKind.database:
            return private_db_subnet_id
        if node.kind == NodeKind.app_service:
            name_lower = (node.name or "").lower()
            if "web" in name_lower or "frontend" in name_lower:
                return public_web_subnet_id
            return private_app_subnet_id
        if node.kind == NodeKind.compute:
            return private_app_subnet_id
        return private_app_subnet_id

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
