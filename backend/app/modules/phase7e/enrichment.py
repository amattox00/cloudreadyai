from typing import List
from .models import DiagramMetadata, DiagramRecommendation


def _aws_base_recommendations(meta: DiagramMetadata) -> List[DiagramRecommendation]:
    recs: List[DiagramRecommendation] = []

    recs.append(
        DiagramRecommendation(
            category="network",
            title="Add AWS Transit Gateway for multi-account connectivity",
            description=(
                "For multi-account landing zones, use AWS Transit Gateway to centralize "
                "VPC connectivity and simplify routing between security, shared services, "
                "and workload accounts."
            ),
            severity="info",
            tags=["aws", "networking", "transit-gateway"],
        )
    )

    recs.append(
        DiagramRecommendation(
            category="security",
            title="Front-end public applications with AWS WAF + CloudFront",
            description=(
                "Place internet-facing workloads behind CloudFront and AWS WAF to improve "
                "security posture, performance, and DDoS mitigation."
            ),
            severity="warning",
            tags=["aws", "waf", "cloudfront", "zero-trust"],
        )
    )

    if (meta.compliance or "").lower() in {"dod", "fedramp"}:
        recs.append(
            DiagramRecommendation(
                category="compliance",
                title="Use AWS Config and Security Hub for FedRAMP / DoD control visibility",
                description=(
                    "Enable AWS Config and AWS Security Hub across accounts to continuously "
                    "monitor configuration drifts and map findings to frameworks like "
                    "FedRAMP and NIST 800-53."
                ),
                severity="info",
                tags=["aws", "fedramp", "config", "security-hub"],
            )
        )

    return recs


def _azure_base_recommendations(meta: DiagramMetadata) -> List[DiagramRecommendation]:
    recs: List[DiagramRecommendation] = []

    recs.append(
        DiagramRecommendation(
            category="network",
            title="Use hub-and-spoke with Azure Firewall or NVA",
            description=(
                "Adopt a hub-and-spoke network topology with Azure Firewall or a "
                "network virtual appliance in the hub VNet for centralized security and routing."
            ),
            severity="info",
            tags=["azure", "networking", "hub-spoke"],
        )
    )

    recs.append(
        DiagramRecommendation(
            category="identity",
            title="Enable Conditional Access and PIM via Entra ID",
            description=(
                "Apply Conditional Access and Privileged Identity Management in Entra ID "
                "for strong Zero Trust enforcement, particularly for admin roles."
            ),
            severity="warning",
            tags=["azure", "identity", "zero-trust"],
        )
    )

    return recs


def _gcp_base_recommendations(meta: DiagramMetadata) -> List[DiagramRecommendation]:
    recs: List[DiagramRecommendation] = []

    recs.append(
        DiagramRecommendation(
            category="network",
            title="Use Shared VPC for centralized control",
            description=(
                "Use Shared VPC to centralize network management and delegate service "
                "projects for workloads while keeping security enforcement in the host project."
            ),
            severity="info",
            tags=["gcp", "networking", "shared-vpc"],
        )
    )

    recs.append(
        DiagramRecommendation(
            category="security",
            title="Leverage Cloud Armor and Security Command Center",
            description=(
                "Use Cloud Armor for WAF and DDoS protection in front of external "
                "applications, and Security Command Center for centralized security posture management."
            ),
            severity="warning",
            tags=["gcp", "cloud-armor", "scc"],
        )
    )

    return recs


def build_recommendations(metadata: DiagramMetadata) -> List[DiagramRecommendation]:
    cloud = (metadata.cloud or "").lower()
    recs: List[DiagramRecommendation] = []

    if cloud == "aws":
        recs.extend(_aws_base_recommendations(metadata))
    elif cloud == "azure":
        recs.extend(_azure_base_recommendations(metadata))
    elif cloud == "gcp":
        recs.extend(_gcp_base_recommendations(metadata))
    else:
        recs.append(
            DiagramRecommendation(
                category="security",
                title="Ensure centralized logging and monitoring",
                description=(
                    "Enable centralized logging, metrics, and alerting across all workloads "
                    "to detect anomalies and enforce Zero Trust policies."
                ),
                severity="info",
                tags=["observability", "logging"],
            )
        )

    recs.append(
        DiagramRecommendation(
            category="dr",
            title="Regularly test failover and recovery paths",
            description=(
                "Document and rehearse DR runbooks. Validate RPO/RTO using automated "
                "failover drills where possible."
            ),
            severity="info",
            tags=["dr", "testing"],
        )
    )

    return recs
