import csv
import random

output_path = "../templates/servers_ugly_200.csv"

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

envs = ["prod", "dev", "qa", "stage", "", "   "]
oss = ["Windows", "RHEL", "Ubuntu", "SLES", "UnknownOS"]
roles = ["app", "db", "web", "batch", "file", ""]
criticalities = ["low", "medium", "high", "critical", ""]

random.seed(42)

with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for i in range(1, 201):
        # 50% of rows intentionally broken
        is_bad = (i % 2 == 0)

        hostname = f"ugly{i:04d}" if not is_bad else ("" if i % 4 == 0 else f"ugly{i:04d}")
        env = envs[i % len(envs)]
        os_name = oss[i % len(oss)]
        platform = "vmware"
        vm_id = f"vm-{2000 + i}"
        ip_address = f"10.200.{(i % 256)}.{10 + (i % 10)}"
        subnet = f"10.200.{(i % 256)}.0/24"
        datacenter = f"DC{i % 3 + 1}"
        cluster_name = f"Cluster{i % 4 + 1}"
        role = roles[i % len(roles)]
        app_name = f"UglyApp{i % 20 + 1}"
        owner = f"user{i % 10 + 1}"
        crit = criticalities[i % len(criticalities)]

        # Good numeric values for "good" rows, garbage for "bad" rows
        if not is_bad:
            cpu_cores = (i % 8) + 1
            memory_gb = ((i % 16) + 1) * 2
            storage_gb = ((i % 20) + 1) * 50
        else:
            bad_tokens = ["not_a_number", "", "   ", "-"]
            cpu_cores = random.choice(bad_tokens)
            memory_gb = random.choice(bad_tokens)
            storage_gb = random.choice(bad_tokens)

        is_virtual = "true" if i % 3 != 0 else "yes"   # some invalid booleans
        is_cloud = "false" if i % 4 != 0 else "maybe"  # some invalid booleans
        tags = f"env:{env};role:{role};ugly:true"

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
