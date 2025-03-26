import os
import json
import requests
import boto3


# force deploy 002


def lambda_handler(event, context):
    # Step 1: Weather API setup
    city = "Auburn,GA,US"
    api_key = os.environ['WEATHER_API_KEY']
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid={api_key}"

    # Step 2: Make API request
    response = requests.get(url)
    if response.status_code != 200:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to fetch weather: {response.text}")
        }

    # Step 3: Parse weather data
    weather_data = response.json()
    temp = weather_data['main']['temp']
    condition = weather_data['weather'][0]['description']
    humidity = weather_data['main']['humidity']

    # Step 4: Format email message
    message = (
        f"Good morning!\n\n"
        f"Here's your weather update for Auburn, GA:\n"
        f"🌡️ Temperature: {temp}°F\n"
        f"🌤️ Conditions: {condition.title()}\n"
        f"💧 Humidity: {humidity}%\n\n"
        f"Have a great day!"
    )

    # Step 5: Send the email via SES
    ses = boto3.client('ses', region_name='us-east-1')

    response = ses.send_email(
        Source="tycrusher@gmail.com",
        Destination={
            'ToAddresses': ["tycrusher@gmail.com"]
        },
        Message={
            'Subject': {
                'Data': "Daily Weather Report - Auburn, GA"
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        }
    )

    print("Email sent! Message ID:", response['MessageId'])

    return {
        'statusCode': 200,
        'body': json.dumps('Weather fetched and emailed successfully')
    }
