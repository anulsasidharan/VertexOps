/** Realistic mock data for platform pages. Replace with real API calls when backend endpoints are ready. */

export const MOCK_METRICS = {
  resourcesMonitored: 847,
  incidentsAutoResolved: 23,
  monthlySavings: 47324,
  complianceScore: 98.7,
  activeIncidents: 1,
  uptimePct: 99.94,
};

export const MOCK_ACTIVITY = [
  { id: "1", type: "resolved",  message: "CPU spike auto-resolved on GKE prod",   time: "2m ago",  cloud: "GCP" },
  { id: "2", type: "alert",     message: "RDS memory at 87% — threshold breached", time: "5m ago",  cloud: "AWS" },
  { id: "3", type: "deploy",    message: "api-gateway v2.4 deployed successfully",  time: "12m ago", cloud: "GCP" },
  { id: "4", type: "cost",      message: "Cost rec: $1,200 idle RDS identified",    time: "1h ago",  cloud: "AWS" },
  { id: "5", type: "security",  message: "Cloud Armor WAF rule updated",            time: "2h ago",  cloud: "GCP" },
  { id: "6", type: "resolved",  message: "Network latency spike resolved on AKS",  time: "3h ago",  cloud: "Azure" },
];

export type Resource = {
  id: string; name: string; type: string; cloud: "GCP"|"AWS"|"Azure"; region: string;
  status: "healthy"|"warning"|"critical"; cpu: number; memory: number;
  x: number; y: number;
};

export const MOCK_RESOURCES: Resource[] = [
  { id:"r1", name:"GKE Cluster (prod)", type:"Kubernetes",  cloud:"GCP",   region:"us-central1",  status:"healthy",  cpu:42, memory:31, x:14, y:18 },
  { id:"r2", name:"Cloud SQL PG",       type:"Database",    cloud:"GCP",   region:"us-east1",     status:"healthy",  cpu:28, memory:18, x:22, y:62 },
  { id:"r3", name:"Memorystore Redis",  type:"Cache",       cloud:"GCP",   region:"us-central1",  status:"healthy",  cpu:15, memory:44, x:10, y:42 },
  { id:"r4", name:"EC2 Fleet",          type:"Compute",     cloud:"AWS",   region:"us-east-1",    status:"healthy",  cpu:55, memory:40, x:42, y:44 },
  { id:"r5", name:"RDS PostgreSQL",     type:"Database",    cloud:"AWS",   region:"us-east-1",    status:"warning",  cpu:87, memory:92, x:52, y:70 },
  { id:"r6", name:"Lambda Functions",   type:"Serverless",  cloud:"AWS",   region:"global",       status:"healthy",  cpu:12, memory:5,  x:64, y:22 },
  { id:"r7", name:"AKS Cluster",        type:"Kubernetes",  cloud:"Azure", region:"eastus",       status:"healthy",  cpu:38, memory:27, x:74, y:18 },
  { id:"r8", name:"Azure VM Scale Set", type:"Compute",     cloud:"Azure", region:"eastus2",      status:"healthy",  cpu:61, memory:48, x:80, y:56 },
  { id:"r9", name:"Azure SQL DB",       type:"Database",    cloud:"Azure", region:"westus",       status:"healthy",  cpu:22, memory:30, x:70, y:70 },
];

export const RESOURCE_EDGES = [
  ["r1","r2"],["r1","r3"],["r1","r4"],["r4","r5"],["r4","r6"],["r6","r7"],["r7","r8"],["r8","r9"],
];

export type Incident = {
  id: string; title: string; severity: "critical"|"high"|"medium"|"low";
  status: "open"|"resolving"|"resolved"; cloud: "GCP"|"AWS"|"Azure";
  resource: string; detectedAt: string; resolvedAt?: string;
  confidence: number; rootCause: string;
  timeline: { time: string; event: string; type: "info"|"warning"|"success"|"ai" }[];
  actions: { label: string; status: "applied"|"pending"|"manual" }[];
};

export const MOCK_INCIDENTS: Incident[] = [
  {
    id:"INC-2847", title:"High Memory Usage — Production GKE Cluster",
    severity:"critical", status:"resolving", cloud:"GCP", resource:"GKE Cluster (prod)",
    detectedAt:"10:15 AM", confidence:94, rootCause:"Memory leak in app-v2.3 deployment",
    timeline:[
      { time:"10:15 AM", event:"Memory usage increased to 85%",    type:"info"    },
      { time:"10:17 AM", event:"Threshold breached (90%)",          type:"warning" },
      { time:"10:18 AM", event:"AI analysis initiated",             type:"ai"      },
      { time:"10:19 AM", event:"Root cause identified (94%)",       type:"success" },
      { time:"10:20 AM", event:"Auto-remediation proposed",         type:"ai"      },
    ],
    actions:[
      { label:"Scale down app-v2.3 deployment",  status:"applied"  },
      { label:"Restart high-memory pods (3)",    status:"pending"  },
      { label:"Enable memory profiling",         status:"manual"   },
    ],
  },
  {
    id:"INC-2841", title:"RDS Connection Pool Exhausted",
    severity:"high", status:"resolved", cloud:"AWS", resource:"RDS PostgreSQL",
    detectedAt:"Yesterday 3:40 PM", resolvedAt:"Yesterday 4:12 PM", confidence:91,
    rootCause:"Missing connection limit in ORM pool config",
    timeline:[
      { time:"3:40 PM", event:"Connection errors spiked >500/min",  type:"warning" },
      { time:"3:42 PM", event:"AI analysis — pool exhaustion",       type:"ai"      },
      { time:"3:55 PM", event:"Config patch deployed",               type:"success" },
    ],
    actions:[
      { label:"Update ORM pool max_connections=20", status:"applied" },
      { label:"Restart app containers",             status:"applied" },
    ],
  },
  {
    id:"INC-2835", title:"SSL Certificate Expiry — api.acme.com",
    severity:"medium", status:"resolved", cloud:"GCP", resource:"Cloud Run API Gateway",
    detectedAt:"2 days ago", resolvedAt:"2 days ago", confidence:99,
    rootCause:"Certificate not enrolled in auto-renewal",
    timeline:[
      { time:"Day -7", event:"Expiry warning triggered (7d)", type:"warning" },
      { time:"Day 0",  event:"Certificate renewed via Let's Encrypt", type:"success" },
    ],
    actions:[
      { label:"Renew certificate", status:"applied" },
      { label:"Enable auto-renewal", status:"applied" },
    ],
  },
];

export type CostRecommendation = {
  id: string; resource: string; cloud: "GCP"|"AWS"|"Azure"; issue: string;
  saving: number; action: string; status: "pending"|"approved";
};

export const MOCK_COST_RECS: CostRecommendation[] = [
  { id:"c1", resource:"GCE instance us-east1-b",   cloud:"GCP",   issue:"Idle 14 days",         saving:456,  action:"Terminate",           status:"pending" },
  { id:"c2", resource:"RDS db.m5.2xlarge",          cloud:"AWS",   issue:"Over-provisioned 60%", saving:1200, action:"Rightsize → t3.large", status:"pending" },
  { id:"c3", resource:"EBS Volumes (5 unattached)", cloud:"AWS",   issue:"Unattached volumes",   saving:340,  action:"Delete",              status:"pending" },
  { id:"c4", resource:"Azure VM Standard_D8s",      cloud:"Azure", issue:"<5% CPU avg 30 days",  saving:680,  action:"Rightsize → D2s",     status:"pending" },
  { id:"c5", resource:"CloudFront dist (legacy)",   cloud:"AWS",   issue:"0 requests 60 days",   saving:120,  action:"Disable",             status:"pending" },
];

export const MOCK_COST_BREAKDOWN = [
  { label:"Compute",    pct:45, color:"#0A66C2" },
  { label:"Storage",    pct:25, color:"#f5922e" },
  { label:"Networking", pct:15, color:"#00A4BD" },
  { label:"Databases",  pct:10, color:"#57A639" },
  { label:"Other",      pct:5,  color:"#475569" },
];

export const MOCK_COMPLIANCE_FRAMEWORKS = {
  soc2: {
    name:"SOC 2", score:98, controls:[
      { name:"Access Controls",    pct:100, status:"pass" },
      { name:"Encryption at Rest", pct:100, status:"pass" },
      { name:"Log Retention",      pct:85,  status:"warn", issue:"3 buckets with 60d retention (policy: 90d)" },
      { name:"Network Security",   pct:100, status:"pass" },
      { name:"Change Management",  pct:100, status:"pass" },
    ],
  },
  iso27001: {
    name:"ISO 27001", score:96, controls:[
      { name:"Asset Management",   pct:100, status:"pass" },
      { name:"Access Control",     pct:100, status:"pass" },
      { name:"Cryptography",       pct:92,  status:"warn", issue:"2 services using deprecated TLS 1.1" },
      { name:"Operations Security",pct:100, status:"pass" },
      { name:"Incident Management",pct:96,  status:"warn", issue:"SLA breach on 1 incident" },
    ],
  },
  gdpr: {
    name:"GDPR", score:100, controls:[
      { name:"Data Minimisation",  pct:100, status:"pass" },
      { name:"Right to Erasure",   pct:100, status:"pass" },
      { name:"Data Portability",   pct:100, status:"pass" },
      { name:"Privacy by Design",  pct:100, status:"pass" },
    ],
  },
  hipaa: {
    name:"HIPAA", score:97, controls:[
      { name:"PHI Access Controls",  pct:100, status:"pass" },
      { name:"Audit Controls",       pct:100, status:"pass" },
      { name:"Transmission Security",pct:100, status:"pass" },
      { name:"Risk Analysis",        pct:92,  status:"warn", issue:"Annual risk assessment due in 14 days" },
    ],
  },
};

export const MOCK_AUDIT_LOG = [
  { action:"Scaled down dev-cluster (cost optimization)",  actor:"system@vertexops.ai", time:"5m ago"  },
  { action:"Enabled Cloud Armor WAF (security rec)",        actor:"system@vertexops.ai", time:"1h ago"  },
  { action:"Rotated API credentials (scheduled)",           actor:"system@vertexops.ai", time:"6h ago"  },
  { action:"Terminated idle GCE instance us-east1",         actor:"admin@acme.com",      time:"1d ago"  },
  { action:"Updated log retention policy (90d)",            actor:"admin@acme.com",      time:"2d ago"  },
];

export type AlertRule = {
  id: string; name: string; condition: string; channels: string[];
  escalation: { delay: string; target: string }[]; enabled: boolean;
};

export const MOCK_ALERT_RULES: AlertRule[] = [
  {
    id:"ar1", name:"Critical Incident",
    condition:"incident.severity == CRITICAL",
    channels:["Slack","PagerDuty","In-App"],
    escalation:[
      { delay:"0m",  target:"On-call engineer" },
      { delay:"10m", target:"Engineering Manager" },
      { delay:"30m", target:"VP Engineering" },
    ],
    enabled:true,
  },
  {
    id:"ar2", name:"High Memory Usage",
    condition:"resource.memory_pct > 85 for 5min",
    channels:["Slack","In-App"],
    escalation:[{ delay:"0m", target:"On-call engineer" }],
    enabled:true,
  },
  {
    id:"ar3", name:"Cost Anomaly",
    condition:"daily_spend > budget * 1.2",
    channels:["Email","Slack"],
    escalation:[{ delay:"0m", target:"FinOps team" }],
    enabled:true,
  },
  {
    id:"ar4", name:"SSL Certificate Expiry",
    condition:"certificate.days_until_expiry < 14",
    channels:["Email","PagerDuty"],
    escalation:[{ delay:"0m", target:"Platform team" }],
    enabled:false,
  },
];

export const MOCK_ALERTS_INBOX = [
  { id:"a1", severity:"critical", title:"Memory threshold breached",  channel:"Slack",     time:"2m ago"  },
  { id:"a2", severity:"info",     title:"Cost savings rec available", channel:"Email",     time:"1h ago"  },
  { id:"a3", severity:"warning",  title:"SSL cert expiry in 7 days",  channel:"PagerDuty", time:"3h ago"  },
  { id:"a4", severity:"resolved", title:"CPU spike auto-resolved",    channel:"In-App",    time:"4h ago"  },
];

export type Integration = {
  id: string; name: string; category: string; icon: string;
  status: "connected"|"disconnected"; detail?: string; color: string;
};

export const MOCK_INTEGRATIONS: Integration[] = [
  { id:"i1",  name:"Google Cloud",    category:"Cloud",        icon:"☁️",  status:"connected",    detail:"3 projects · sync 2m ago",     color:"#1a73e8" },
  { id:"i2",  name:"AWS",             category:"Cloud",        icon:"🟠",  status:"connected",    detail:"2 accounts · 289 resources",   color:"#f5922e" },
  { id:"i3",  name:"Microsoft Azure", category:"Cloud",        icon:"🔷",  status:"connected",    detail:"1 subscription · 246 resources",color:"#0078D4" },
  { id:"i4",  name:"Slack",           category:"Comms",        icon:"💬",  status:"connected",    detail:"#alerts, #incidents",          color:"#4a154b" },
  { id:"i5",  name:"PagerDuty",       category:"Comms",        icon:"📟",  status:"connected",    detail:"On-call schedule active",      color:"#06ac38" },
  { id:"i6",  name:"Microsoft Teams", category:"Comms",        icon:"🟦",  status:"disconnected", detail:undefined,                     color:"#6264a7" },
  { id:"i7",  name:"Terraform Cloud", category:"IaC",          icon:"🏗️",  status:"disconnected", detail:undefined,                     color:"#7b42bc" },
  { id:"i8",  name:"Datadog",         category:"Monitoring",   icon:"🐶",  status:"connected",    detail:"Metrics forwarding active",    color:"#632ca6" },
  { id:"i9",  name:"Prometheus",      category:"Monitoring",   icon:"🔥",  status:"connected",    detail:"Self-hosted · port 9090",      color:"#e6522c" },
  { id:"i10", name:"GitHub Actions",  category:"CI/CD",        icon:"🐙",  status:"connected",    detail:"3 repos · deploy workflows",   color:"#24292e" },
  { id:"i11", name:"ArgoCD",          category:"CI/CD",        icon:"🔄",  status:"disconnected", detail:undefined,                     color:"#ef7b4d" },
  { id:"i12", name:"Splunk",          category:"Monitoring",   icon:"📊",  status:"disconnected", detail:undefined,                     color:"#000000" },
];
