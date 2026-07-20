# ==========================================
# 1. Terraform Settings & AWS Provider Configuration
# ==========================================
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# ==========================================
# 2. Base Networking (VPC & Core Subnets)
# ==========================================
resource "aws_vpc" "nova_shield_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "nova-shield-vpc"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.nova_shield_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "nova-shield-public-subnet"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.nova_shield_vpc.id

  tags = {
    Name = "nova-shield-igw"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.nova_shield_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "nova-shield-public-route"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# ==========================================
# 3. Security Framework (Firewall Configurations)
# ==========================================
resource "aws_security_group" "ecs_sg" {
  name        = "nova-shield-ecs-sg"
  description = "Allows incoming access to dashboard application layout"
  vpc_id      = aws_vpc.nova_shield_vpc.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ==========================================
# 4. Container Image Management Registry (ECR)
# ==========================================
resource "aws_ecr_repository" "nova_shield" {
  name                 = "nova-shield-telemetry"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ==========================================
# 5. ECS Compute Cluster & Logging Framework
# ==========================================
resource "aws_ecs_cluster" "nova_shield_cluster" {
  name = "nova-shield-telemetry-cluster"
}

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/nova-shield-task"
  retention_in_days = 7
}

# ==========================================
# 5.1 ECS Task Execution IAM Role
# ==========================================
resource "aws_iam_role" "ecs_execution_role" {
  name = "nova-shield-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ==========================================
# 6. Multi-Container Task Specifications (Fargate)
# ==========================================
resource "aws_ecs_task_definition" "nova_shield_task" {
  family                   = "nova-shield-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "nova-shield-server"
      image     = image = "${aws_ecr_repository.nova_shield.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        {
          name  = "ENV_MODE"
          value = "PRODUCTION"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "server"
        }
      }
    },
    {
      name      = "nova-shield-simulator"
      image     = image = "${aws_ecr_repository.nova_shield_simulator.repository_url}:latest"
      essential = false
      environment = [
        {
          name  = "API_URL"
          value = "http://localhost:8000/api/v1/telemetry"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "simulator"
        }
      }
    }
  ])
}

# ==========================================
# 7. ECS Fargate Service Handler
# ==========================================
resource "aws_ecs_service" "nova_shield_service" {
  name            = "nova-shield-service"
  cluster         = aws_ecs_cluster.nova_shield_cluster.id
  task_definition = aws_ecs_task_definition.nova_shield_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_subnet.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }
}