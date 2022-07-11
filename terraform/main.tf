terraform {
  required_version = "1.2.3"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.18.0"
    }
  }
}


provider "aws" {
  region = var.region
  profile = var.profile
}

resource "aws_redshift_cluster" "redshift" {
  cluster_identifier = "redshift-cluster-pipeline"
  skip_final_snapshot = true # must be set so we can destroy redshift with terraform destroy
  master_username    = "awsuser"
  master_password    = var.db_password
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  publicly_accessible = "true"
  vpc_security_group_ids = [aws_security_group.sg_redshift.id]

}

resource "aws_security_group" "sg_redshift" {
  name        = "sg_redshift"
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "houses_data" {
  bucket = "${local.data_lake_bucket}-${var.project}"

  force_destroy = true

  tags = {
    Name = "${local.data_lake_bucket}-${var.project}"
    Environment = "DEV"
    Managedby = "Terraform"
  }
}

resource "aws_s3_bucket_acl" "houses_data" {
  bucket = aws_s3_bucket.houses_data.id
  acl = var.acl
}

resource "aws_iam_role" "redshift_role" {
  name = "RedShiftLoadRole"
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "redshift.amazonaws.com"
        }
      },
    ]
  })
}