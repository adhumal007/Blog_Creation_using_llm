import boto3
import botocore.config
import json
from datetime import datetime

def generate_blog(topic:str)-> str:
    prompt=f"""<s>[INST]User:Write a 200 words blog on the topic {topic}
    Assistant:[/INST]
    """
    
    body={
        "prompt":prompt,
        "max_gen_len":256,
        "temperature":0.5,
        "top_p":0.9
        }
    
    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-2",
                             config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3})
                             )
        response = bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-3-70b-instruct-v1:0")
        
        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error Generatiung the Blog:{e}")
        
def save_blog_to_s3(s3_key, s3_bucket, data):
    s3=boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=data)
        print(f"File {s3_key} saved to s3")
    except Exception as e:
        print(f"S3 Error: {e}")
        
def lambda_handler(event,context):
    events=json.loads(events['body'])
    topic=event['blog_topic']
    
    data=generate_blog(topic)
    
    if data:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"blog-output/{current_time}.txt"
        s3_bucket= 'aws_bedrock_blog'
        save_blog_to_s3(s3_key,s3_bucket,data)
    else:
        print('Blog not generated')
        
    return {
        'statusCode': 200,
        'body': json.dumps('Blog Generated!')
    }
    