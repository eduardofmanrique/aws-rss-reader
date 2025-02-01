provider "aws" {
  region = "sa-east-1"
}

terraform {
  backend "s3" {
    bucket         = "aws-alerts-config-bucket"
    key            = "rss_reader/terraform/state/terraform.tfstate"
    region         = "sa-east-1"
    encrypt        = true
  }
}

resource "aws_iam_role" "lambda_role_rss_reader" {
  name               = "lambda-basic-role-rss-reader"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_policy_rss_reader" {
  role       = aws_iam_role.lambda_role_rss_reader.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_full_access_rss_reader" {
  role       = aws_iam_role.lambda_role_rss_reader.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_ssm_read_only_rss_reader" {
  role       = aws_iam_role.lambda_role_rss_reader.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_access_rss_reader" {
  role       = aws_iam_role.lambda_role_rss_reader.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_lambda_layer_version" "dependencies_layer_rss_reader" {
  filename            = "lambda_dependencies.zip"
  layer_name          = "lambda-dependencies-rss-reader"
  compatible_runtimes = ["python3.9"]
}

resource "aws_lambda_function" "lambda_rss_reader" {
  function_name    = "lambda-rss-reader"
  role             = aws_iam_role.lambda_role_rss_reader.arn
  handler          = "main.handler"
  runtime          = "python3.9"
  filename         = "lambda.zip"
  source_code_hash = fileexists("lambda.zip") ? filebase64sha256("lambda.zip") : null
  timeout          = 120
  memory_size      = 300
  layers           = [
    "arn:aws:lambda:sa-east-1:336392948345:layer:AWSSDKPandas-Python39:29",
    aws_lambda_layer_version.dependencies_layer_rss_reader.arn
  ]
}

resource "aws_dynamodb_table" "rss_reader" {
  name           = "rss_reader"
  billing_mode   = "PROVISIONED" # Capacidade fixa
  read_capacity  = 1             # 1 unidade de capacidade de leitura
  write_capacity = 1             # 1 unidade de capacidade de escrita

  hash_key       = "id"

  attribute {
    name = "id"
    type = "S" # String
  }
}

resource "aws_cloudwatch_event_rule" "every_hour_rss_reader" {
  name        = "lambda-trigger-every-hour-rss-reader"
  description = "Trigger Lambda every hour"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda_target_rss_reader" {
  rule      = aws_cloudwatch_event_rule.every_hour_rss_reader.name
  target_id = "lambda-rss-reader-target"
  arn       = aws_lambda_function.lambda_rss_reader.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_invoke_rss_reader" {
  statement_id  = "AllowCloudWatchInvoke"
  action        = "lambda:InvokeFunction"
  principal     = "events.amazonaws.com"
  function_name = aws_lambda_function.lambda_rss_reader.function_name
  source_arn    = aws_cloudwatch_event_rule.every_hour_rss_reader.arn
}
