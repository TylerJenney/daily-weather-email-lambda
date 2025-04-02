import os
import json
import urllib.request
import boto3

def lambda_handler(event, context):
    city = "Auburn,GA,US"
    api_key = os.environ['WEATHER_API_KEY']
    print("API KEY FROM ENV:", repr(api_key))

    # Step 1: Get coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    with urllib.request.urlopen(geo_url) as geo_response:
        geo_data = json.loads(geo_response.read().decode())

    if not geo_data:
        return {
            'statusCode': 500,
            'body': json.dumps("Failed to get coordinates")
        }

    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']

    # Step 2: Get forecast
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    with urllib.request.urlopen(weather_url) as weather_response:
        weather_data = json.loads(weather_response.read().decode())

    high = round(weather_data['main']['temp_max'])
    low = round(weather_data['main']['temp_min'])
    condition = weather_data['weather'][0]['description'].capitalize()
    humidity = weather_data['main']['humidity']

    message = (
        f"Good morning!\n\n"
        f"Here's your weather update for Auburn, GA:\n"
        f"🌡️ High: {high}°F\n"
        f"❄️ Low: {low}°F\n"
        f"💧 Humidity: {humidity}%\n"
        f"🌤️ Conditions: {condition}\n\n"
        f"Have a great day!"
    )

    # Send email
    ses = boto3.client('ses', region_name='us-east-1')
    response = ses.send_email(
        Source="tycrusher@gmail.com",
        Destination={'ToAddresses': ["tycrusher@gmail.com"]},
        Message={
            'Subject': {'Data': "Daily Weather Report - Auburn, GA"},
            'Body': {'Text': {'Data': message}}
        }
    )

    print("Email sent! Message ID:", response['MessageId'])

    return {
        'statusCode': 200,
        'body': json.dumps('Weather fetched and emailed successfully')
    }
