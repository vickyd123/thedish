# File: backend/generate_daily_digest.py

import requests
from datetime import datetime, timedelta
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-1')
S3_BUCKET = os.environ['S3_BUCKET']

def summarize_yesterdays_games():
    prompt = "summarize yesterday's MLB games for a daily digest"
    gemini_url = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    response = requests.post(
        gemini_url,
        json={
            "contents": [{"parts": [{"text": prompt}]}]
        }
    )
    response.raise_for_status()
    summary = response.json()['candidates'][0]['content']['parts'][0]['text']
    return summary

def upload_to_s3(content, filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=content, ContentType='text/plain')
    print(f"Uploaded digest to s3://{S3_BUCKET}/{filename}")

def main():
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    #print(f"Digest date: {yesterday_date}")   <-- Add this line
    summary = summarize_yesterdays_games()
    filename = f"{yesterday_date}.txt"
    upload_to_s3(summary, filename)

if __name__ == "__main__":
    main()
