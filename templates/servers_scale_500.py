import csv

output_path = "../templates/servers_scale_500.csv"

header = [
    "hostname",
    "environment",
    "os",
    "platform",
    "vm_id",
    "ip_address",
    "subnet",
    "datacenter",
    "cluster_name",
    "role",
    "app_name",
    "owner",
    "criticality",
    "cpu_cores",
    "memory_gb",
    "storage_gb",
    "is_virtual",
    "is_cloud",
    "tags",
]

envs = ["prod", "dev", "qa", "stage"]
oss = ["Windows", "RHEL", "Ubuntu", "SLES"]
roles = ["app", "db", "web", "batch", "file"]
criticalities = ["low", "medium", "high", "critical"]

with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for i in range(1, 501):
        env = envs[i % len(envs)]
        os_name = oss[i % len(oss)]
        role = roles[i % len(roles)]
        crit = criticalities[i % len(criticalities)]

        hostname = f"server{i:04d}"
        platform = "vmware"
        vm_id = f"vm-{1000 + i}"
        ip_address = f"10.{i // 256}.{(i % 256)}.{10 + (i % 10)}"
        subnet = f"10.{i // 256}.{(i % 256)}.0/24"
        datacenter = f"DC{i % 3 + 1}"
        cluster_name = f"Cluster{i % 4 + 1}"
        app_name = f"App{i % 50 + 1}"
        owner = f"user{i % 20 + 1}"

        cpu_cores = (i % 8) + 1      # 1–9
        memory_gb = ((i % 16) + 1) * 2
        storage_gb = ((i % 20) + 1) * 50

        is_virtual = "true"
        is_cloud = "false"
        tags = f"env:{env};role:{role};dc:{datacenter}"

        writer.writerow([
            hostname,
            env,
            os_name,
            platform,
            vm_id,
            ip_address,
            subnet,
            datacenter,
            cluster_name,
            role,
            app_name,
            owner,
            crit,
            cpu_cores,
            memory_gb,
            storage_gb,
            is_virtual,
            is_cloud,
            tags,
        ])

print(f"Wrote {output_path}")
