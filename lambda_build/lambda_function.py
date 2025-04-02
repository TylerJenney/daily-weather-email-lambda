import os
import json
import requests
import boto3


def lambda_handler(event, context):
    # Weather API setup
    city = "Auburn,GA,US"
    api_key = os.environ['WEATHER_API_KEY']

    # Step 1: Get coordinates using Geocoding API
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    geo_response = requests.get(geo_url)
    if geo_response.status_code != 200 or not geo_response.json():
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to get coordinates: {geo_response.text}")
        }

    geo_data = geo_response.json()[0]
    lat = geo_data['lat']
    lon = geo_data['lon']

    # Step 2: Get daily forecast using One Call API
    weather_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=imperial&appid={api_key}"
    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to fetch weather: {weather_response.text}")
        }

    weather_data = weather_response.json()
    today = weather_data['daily'][0]
    high = round(today['temp']['max'])
    low = round(today['temp']['min'])
    rain_chance = int(today['pop'] * 100)
    condition = today['weather'][0]['description'].capitalize()

    # Format email message
    message = (
        f"Good morning!\n\n"
        f"Here's your weather update for Auburn, GA:\n"
        f"🌡️ High: {high}°F\n"
        f"❄️ Low: {low}°F\n"
        f"☔ Chance of Rain: {rain_chance}%\n"
        f"🌤️ Conditions: {condition}\n\n"
        f"Have a great day!"
    )

    # Send the email via SES
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
