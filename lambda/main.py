import boto3
import json

from dynamodb.store import StoreDynamoDb
from rss.reader import RssReader
from rss.whatsapp_message_builder import caption
from config import rss_readers_kwargs

default_image_url = "https://i.pinimg.com/736x/b1/da/e5/b1dae544e9888ba8c72fc80842772898.jpg"

def handler(event, context):
    try:
        sqs_client = boto3.client('sqs', region_name='sa-east-1')
        ssm_client = boto3.client('ssm', region_name='sa-east-1')
        dynamodb_client = boto3.resource("dynamodb", region_name='sa-east-1')

        secrets = json.loads(ssm_client.get_parameter(Name="rss_reader_secrets")['Parameter']['Value'])
        queue_url = secrets['SQS_QUEUE_URL']
        whatsapp_api_id = secrets['WHATSAPP_API_ID']
        whatsapp_api_to = secrets['WHATSAPP_API_TO']

        table_name = "rss_reader"
        dynamodb_handler = StoreDynamoDb(dynamodb_client=dynamodb_client, table=table_name)

        for rss_reader in rss_readers_kwargs:

            rss_reader_obj = RssReader(**rss_reader)
            news = rss_reader_obj.full_parse()

            new_items = dynamodb_handler.check_new_items(
                items=news
            )

            for new_item in new_items:
                try:
                    if 'image' in new_item['info']:
                        if new_item['info']['image']:
                            image = new_item['info']['image']
                        else:
                            image = default_image_url
                    else:
                        image = default_image_url
                    sqs_message = {
                        "resource_name": "messages",
                        "resource_args": {
                            "id": whatsapp_api_id
                        },
                        "resource_function": "send_image_message",
                        "resource_function_args": {
                            "to": whatsapp_api_to,
                            "link": image,
                            "caption": caption(new_item['info'])
                        }
                    }
                    sqs_client.send_message(
                        QueueUrl=queue_url,
                        MessageBody=json.dumps(sqs_message)
                    )
                    item_to_insert = {'id': new_item['id'], 'info': new_item['info']['Link']}
                    dynamodb_handler.insert_new_items([item_to_insert])
                except Exception as e:
                    print(f'Ocorreu um erro ao enviar ou guardar dados de uma casa nova: {e} - {new_item}')


        return {'statusCode': 200}
    except Exception as e:
        return {'statusCode': 400, 'message': f'Error - {e}'}

if __name__ == '__main__':
    print(handler('', ''))