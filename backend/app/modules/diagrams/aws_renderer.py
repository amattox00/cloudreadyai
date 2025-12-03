from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# Centralized AWS icon + color definitions for draw.io (mxGraph AWS4 library)


@dataclass(frozen=True)
class AwsIconStyle:
    """Represents a single AWS icon tile style."""
    res_icon: str | None = None  # for resourceIcon
    pr_icon: str | None = None  # for productIcon
    fill_color: str = "#232F3E"  # default dark navy
    font_color: str = "#232F3E"


# Base style fragments ---------------------------------------------------------

BASE_TILE_STYLE = (
    "sketch=0;outlineConnect=0;html=1;dashed=0;"
    "fontStyle=0;fontSize=12;"
    "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
    "strokeColor=#FFFFFF;"
)

RESOURCE_SHAPE = "shape=mxgraph.aws4.resourceIcon;"
PRODUCT_SHAPE = "shape=mxgraph.aws4.productIcon;"


AWS_ICON_STYLES: Dict[str, AwsIconStyle] = {
    # Edge / entry
    "users": AwsIconStyle(res_icon="mxgraph.aws4.user", fill_color="#FFFFFF"),
    "route53": AwsIconStyle(res_icon="mxgraph.aws4.route_53", fill_color="#232F3E"),
    "cloudfront": AwsIconStyle(res_icon="mxgraph.aws4.cloudfront", fill_color="#945DF2"),

    # Networking & compute
    "alb": AwsIconStyle(
        res_icon="mxgraph.aws4.application_load_balancer",
        fill_color="#945DF2",
    ),
    "ec2_asg": AwsIconStyle(
        res_icon="mxgraph.aws4.ec2",
        fill_color="#ED7100",
    ),
    "fargate": AwsIconStyle(
        res_icon="mxgraph.aws4.fargate",
        fill_color="#ED7100",
    ),

    # Data
    "rds": AwsIconStyle(
        res_icon="mxgraph.aws4.rds_instance",
        fill_color="#007DBC",
    ),
    "dynamodb": AwsIconStyle(
        res_icon="mxgraph.aws4.dynamodb",
        fill_color="#C925D1",
    ),
    "s3": AwsIconStyle(
        pr_icon="mxgraph.aws4.s3",
        fill_color="#2E77D0",
    ),

    # Observability / security
    "cloudwatch": AwsIconStyle(
        res_icon="mxgraph.aws4.cloudwatch",
        fill_color="#945DF2",
    ),
    "guardduty": AwsIconStyle(
        res_icon="mxgraph.aws4.guardduty",
        fill_color="#F34482",
    ),

    # Serverless / integration (for later use)
    "lambda": AwsIconStyle(
        res_icon="mxgraph.aws4.lambda",
        fill_color="#ED7100",
    ),
    "step_functions": AwsIconStyle(
        res_icon="mxgraph.aws4.step_functions",
        fill_color="#FF4F8B",
    ),
    "cloudformation": AwsIconStyle(
        res_icon="mxgraph.aws4.cloudformation",
        fill_color="#FF4F8B",
    ),
}


def build_aws_tile_style(logical_type: str) -> str:
    """
    Given a logical service key ('cloudfront', 'rds', etc.) return
    a full mxGraph style string for a 2023 AWS tile.
    """
    meta = AWS_ICON_STYLES.get(logical_type)
    if meta is None:
        # Fallback: generic dark tile
        return (
            BASE_TILE_STYLE
            + "fillColor=#232F3E;fontColor=#FFFFFF;"
            + RESOURCE_SHAPE
            + "resIcon=mxgraph.aws4.generic;"
        )

    if meta.pr_icon:
        icon_part = PRODUCT_SHAPE + f"prIcon={meta.pr_icon};"
    else:
        icon_part = RESOURCE_SHAPE + f"resIcon={meta.res_icon};"

    return (
        BASE_TILE_STYLE
        + f"fillColor={meta.fill_color};fontColor={meta.font_color};"
        + icon_part
        + "aspect=fixed;"
    )


# Container and group styles ---------------------------------------------------


AWS_CLOUD_CONTAINER_STYLE = (
    "sketch=0;html=1;rounded=0;"
    "strokeColor=#232F3E;strokeWidth=2;"
    "fillColor=#FFFFFF;fontColor=#232F3E;"
    "align=left;verticalAlign=top;labelPosition=left;verticalLabelPosition=top;"
    "spacingLeft=16;spacingTop=8;"
)

AWS_ACCOUNT_CONTAINER_STYLE = (
    "sketch=0;html=1;rounded=0;"
    "strokeColor=#AAB7B8;strokeWidth=1;"
    "fillColor=#F7F7F7;fontColor=#232F3E;"
    "align=left;verticalAlign=top;labelPosition=left;verticalLabelPosition=top;"
    "spacingLeft=12;spacingTop=6;"
)

AWS_GROUP_DOTTED_STYLE = (
    "sketch=0;html=1;rounded=1;"
    "dashed=1;dashPattern=4 4;"
    "strokeColor=#AAB7B8;strokeWidth=1;"
    "fillColor=none;fontColor=#232F3E;"
    "align=left;verticalAlign=top;labelPosition=left;verticalLabelPosition=top;"
    "spacingLeft=8;spacingTop=4;"
)

STEP_BADGE_STYLE = (
    "shape=ellipse;sketch=0;html=1;"
    "fontSize=12;fontStyle=1;"
    "align=center;verticalAlign=middle;"
    "strokeColor=#232F3E;strokeWidth=1.2;"
    "fillColor=#FFFFFF;fontColor=#232F3E;"
)


def get_container_style(kind: str) -> str:
    if kind == "aws_cloud":
        return AWS_CLOUD_CONTAINER_STYLE
    if kind == "account":
        return AWS_ACCOUNT_CONTAINER_STYLE
    if kind == "group":
        return AWS_GROUP_DOTTED_STYLE
    return AWS_ACCOUNT_CONTAINER_STYLE


def get_step_badge_style() -> str:
    return STEP_BADGE_STYLE
