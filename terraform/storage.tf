terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "export_bucket" {
  type    = string
  default = "teamdocs-exports"
}

variable "export_region" {
  type    = string
  default = "us-east-1"
}

data "aws_caller_identity" "this" {}

resource "aws_s3_bucket" "exports" {
  bucket = "${data.aws_caller_identity.this.account_id}-${var.export_bucket}"
}

resource "aws_s3_bucket_ownership_controls" "exports" {
  bucket = aws_s3_bucket.exports.id
  rule { object_ownership = "ObjectWriter" }
}

resource "aws_s3_bucket_public_access_block" "exports" {
  bucket                  = aws_s3_bucket.exports.id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}
        ]
      }
    ]
  })
}

output "export_bucket_id" {
  value = aws_s3_bucket.exports.id
}

output "export_bucket_name" {
  value = aws_s3_bucket.exports.bucket
}

output "export_bucket_arn" {
  value = aws_s3_bucket.exports.arn
}
