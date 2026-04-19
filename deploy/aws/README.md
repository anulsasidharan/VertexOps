# VertexOps — AWS Deployment (Optional Parity)

> **GCP is the primary and tested deployment target for VertexOps.**
> This directory provides an optional AWS parity pack for teams that need to
> run on AWS. It is explicitly out-of-scope for CI gate checks.
> No core platform code depends on AWS-specific services.

---

## Architecture on AWS

```
[ALB]  ──  [ECS Fargate — API Task]  ──  [RDS PostgreSQL]
                │                              │
       [ECS Fargate — Worker Task]  ──  [ElastiCache Redis]
                │
         [ECR — Container Images]
                │
         [Secrets Manager — secrets]
                │
         [S3 — document storage]
```

## Service Mapping (GCP → AWS)

| GCP | AWS Equivalent |
|-----|---------------|
| Cloud Run (API) | ECS Fargate Service |
| Cloud Run (Worker) | ECS Fargate Service |
| Cloud SQL PostgreSQL | RDS PostgreSQL |
| Memorystore Redis | ElastiCache Redis |
| Artifact Registry | ECR |
| Secret Manager | Secrets Manager |
| GCS Bucket | S3 Bucket |
| Cloud Build | GitHub Actions (already shared CI) |
| Cloud Logging | CloudWatch Logs |

---

## Prerequisites

- AWS CLI configured (`aws configure`)
- Terraform >= 1.6
- Docker

---

## Quick Start

### 1. Initialise Terraform

```bash
cd deploy/aws/terraform
terraform init
```

### 2. Configure variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS account, region, and settings
```

### 3. Create infrastructure

```bash
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Terraform creates:
- VPC with public and private subnets across 2 AZs
- ECS Cluster (Fargate)
- RDS PostgreSQL instance (private subnet)
- ElastiCache Redis cluster (private subnet)
- ECR repositories for API and Worker
- ALB with HTTPS listener (requires ACM certificate ARN)
- Secrets Manager entries for required secrets
- IAM roles and task execution policies

### 4. Build and push images to ECR

```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=$(terraform output -raw aws_region)

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$REGION.amazonaws.com

./scripts/docker-build.sh \
  IMAGE_REPO="$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/vertexops" \
  IMAGE_TAG=latest \
  --push
```

### 5. Run database migrations

```bash
# One-off ECS task
aws ecs run-task \
  --cluster vertexops \
  --task-definition vertexops-migrate \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$(terraform output -raw private_subnet_ids)],securityGroups=[$(terraform output -raw ecs_security_group_id)],assignPublicIp=DISABLED}"
```

### 6. Deploy services

ECS services are managed by Terraform. After pushing new images, update the service:

```bash
aws ecs update-service \
  --cluster vertexops \
  --service vertexops-api \
  --force-new-deployment
```

---

## Secrets

Secrets are stored in AWS Secrets Manager and injected into ECS tasks via `secrets` in the task definition. Required secrets:

| Secret Name | Description |
|-------------|-------------|
| `vertexops/jwt-secret-key` | JWT signing key |
| `vertexops/api-key-pepper` | API key HMAC pepper |
| `vertexops/database-url` | PostgreSQL connection string |
| `vertexops/redis-url` | Redis connection string |

Create secrets:

```bash
aws secretsmanager create-secret \
  --name vertexops/jwt-secret-key \
  --secret-string "$(openssl rand -hex 32)"

aws secretsmanager create-secret \
  --name vertexops/api-key-pepper \
  --secret-string "$(openssl rand -hex 16)"
```

---

## Differences from GCP Baseline

| Aspect | GCP (baseline) | AWS (parity) |
|--------|---------------|-------------|
| Container platform | Cloud Run | ECS Fargate |
| Image registry | Artifact Registry | ECR |
| Secrets | Secret Manager | Secrets Manager |
| Storage | GCS | S3 |
| Observability | Cloud Logging / Cloud Trace | CloudWatch |
| IAM auth | Workload Identity | IAM roles for tasks |
| CI/CD | Cloud Build + GitHub Actions | GitHub Actions only |

---

## Notes

- The AWS pack does not enable or disable any backend feature. All feature flags
  (`METRICS_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`, etc.) work identically.
- Terraform state should be stored in an S3 backend with DynamoDB locking for
  team use. Update `terraform/main.tf` backend block accordingly.
- ECS task definitions reference the same Docker images built from the project
  `Dockerfile` — no AWS-specific code changes are needed.
