# Daily Weather Email (AWS Lambda + Terraform)

This project sends a daily weather report to my email using AWS Lambda, SES, and Terraform.

## What It Does

- Fetches weather data from the OpenWeatherMap API
- Sends an email with the current weather
- Runs automatically every morning at 7AM EST

## Technologies Used

- AWS Lambda – runs the Python script
- Amazon SES – sends the email
