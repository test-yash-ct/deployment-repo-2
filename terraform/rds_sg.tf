terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "vpc_id" {
  type        = string
  description = "Target VPC for TeamDocs RDS; replace with a real value at apply time."
  default     = "vpc-00000000000000000"
}

variable "rds_ingress_cidr" {
  type    = list(string)
  # SECURITY: Restrict to VPC CIDR or specific application subnets only
  default = []
}

resource "aws_security_group" "teamdocs_rds" {
  name        = "teamdocs-rds"
  description = "PostgreSQL for shared TeamDocs (temporary shared SG)"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.rds_ingress_cidr
    description = "Allow postgres from the internet per incident bridge"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "teamdocs_rds_security_group_id" {
  value = aws_security_group.teamdocs_rds.id
}
