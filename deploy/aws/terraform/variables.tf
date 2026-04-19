variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as a prefix for all resource names"
  type        = string
  default     = "vertexops"
}

variable "environment" {
  description = "Deployment environment: staging or production"
  type        = string
  default     = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production."
  }
}

variable "image_tag" {
  description = "Docker image tag to deploy (e.g. git short SHA)"
  type        = string
  default     = "latest"
}

# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of AZs for subnet placement (must be >= 2)"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ---------------------------------------------------------------------------
# ALB / TLS
# ---------------------------------------------------------------------------

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate for the HTTPS listener (leave empty to use HTTP only)"
  type        = string
  default     = ""
}

# ---------------------------------------------------------------------------
# ECS
# ---------------------------------------------------------------------------

variable "api_cpu" {
  description = "Fargate vCPU units for the API task (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "api_memory" {
  description = "Fargate memory (MiB) for the API task"
  type        = number
  default     = 2048
}

variable "api_desired_count" {
  description = "Desired number of API task instances"
  type        = number
  default     = 1
}

variable "worker_cpu" {
  description = "Fargate vCPU units for the Worker task"
  type        = number
  default     = 2048
}

variable "worker_memory" {
  description = "Fargate memory (MiB) for the Worker task"
  type        = number
  default     = 4096
}

variable "worker_desired_count" {
  description = "Desired number of Worker task instances"
  type        = number
  default     = 1
}

# ---------------------------------------------------------------------------
# RDS
# ---------------------------------------------------------------------------

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.small"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "vertexops"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "vertexops"
}

# ---------------------------------------------------------------------------
# ElastiCache
# ---------------------------------------------------------------------------

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t4g.small"
}
