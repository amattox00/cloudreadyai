// src/types/runSummaryV2.ts

export interface ServersTotals {
  server_count: number;
  total_cpu_cores: number;
  total_ram_gb: number;
}

export interface ServersByEnvironment {
  environment: string;
  count: number;
}

export interface StorageTotals {
  volume_count: number;
  total_size_gb: number;
}

export interface StorageByType {
  storage_type: string;
  count: number;
  total_size_gb: number;
}

export interface NetworkSummary {
  device_count: number;
}

export interface DatabasesTotals {
  db_count: number;
  total_db_size_gb: number;
}

export interface DatabasesByType {
  db_type: string;
  count: number;
  total_size_gb: number;
}

export interface ApplicationsTotals {
  app_count: number;
}

export interface GroupCount {
  [key: string]: any;
  business_unit?: string;
  criticality?: string;
  count: number;
}

export interface BusinessSummary {
  by_sla_tier: { sla_tier: string; count: number }[];
  by_criticality: { criticality: string; count: number }[];
}

export interface DependenciesSummary {
  dependency_count: number;
  apps_with_dependencies: number;
}

export interface OsByFamily {
  os_family: string;
  count: number;
}

export interface OsByName {
  os_name: string;
  count: number;
}

export interface OsSummary {
  by_family: OsByFamily[];
  by_name: OsByName[];
}

export interface LicensingByVendor {
  vendor: string;
  license_records: number;
  total_licenses: number;
}

export interface LicensingByProduct {
  product_name: string;
  license_records: number;
  total_licenses: number;
}

export interface LicensingSummary {
  by_vendor: LicensingByVendor[];
  by_product: LicensingByProduct[];
}

export interface UtilizationSummary {
  servers_with_metrics: number;
  avg_cpu_avg: number;
  avg_cpu_peak: number;
  avg_ram_avg_gb: number;
  avg_ram_peak_gb: number;
}

export interface RunSummaryV2 {
  run_id: string;
  servers: {
    totals: ServersTotals;
    by_environment: ServersByEnvironment[];
  };
  storage: {
    totals: StorageTotals;
    by_type: StorageByType[];
  };
  network: NetworkSummary;
  databases: {
    totals: DatabasesTotals;
    by_type: DatabasesByType[];
  };
  applications: {
    totals: ApplicationsTotals;
    by_business_unit: GroupCount[];
    by_criticality: GroupCount[];
  };
  business: BusinessSummary;
  dependencies: DependenciesSummary;
  os: OsSummary;
  licensing: LicensingSummary;
  utilization: UtilizationSummary;
}
