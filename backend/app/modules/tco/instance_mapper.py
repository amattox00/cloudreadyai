def map_to_instance_type(vcpu: int, ram_gb: float) -> str:
    """
    Simple vCPU + RAM → AWS instance type mapper.
    Expand later for multi-family support.
    """

    # General-purpose - M5 family (MVP baseline)
    if vcpu <= 2 and ram_gb <= 8:
        return "m5.large"
    if vcpu <= 4 and ram_gb <= 16:
        return "m5.xlarge"
    if vcpu <= 8 and ram_gb <= 32:
        return "m5.2xlarge"
    if vcpu <= 16 and ram_gb <= 64:
        return "m5.4xlarge"
    if vcpu <= 32 and ram_gb <= 128:
        return "m5.8xlarge"

    # Fallback
    return "m5.large"
