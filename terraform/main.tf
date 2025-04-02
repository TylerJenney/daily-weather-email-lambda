provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_execution_role_v2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "ses_policy" {
  name   = "AllowSES_v2"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = "ses:SendEmail",
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ses_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.ses_policy.arn
}

resource "aws_lambda_function" "weather_email" {
  function_name = "weather_email_lambda_v2"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_handler"

  filename         = "${path.module}/../lambda.zip"
 source_code_hash = filebase64sha256("${path.module}/../lambda.zip") # force update 010




  environment {
    variables = {
      WEATHER_API_KEY = "6c796dea6f961ebf869a177dbaeea091"

    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "daily-weather-trigger"
  schedule_expression = "cron(0 12 * * ? *)" # 7am EST
}

resource "aws_cloudwatch_event_target" "target_lambda" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "sendWeather"
  arn       = aws_lambda_function.weather_email.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather_email.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}
