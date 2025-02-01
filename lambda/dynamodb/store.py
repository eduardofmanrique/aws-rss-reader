import boto3
from botocore.exceptions import ClientError


class StoreDynamoDb:
    def __init__(self, dynamodb_client: boto3.resource, table: str):
        """
        :param dynamodb_client: Instância do cliente DynamoDB.
        :param table: Nome da tabela no DynamoDB.
        """
        self.table = table
        self.dynamodb_client = dynamodb_client
        self.table_obj = self.dynamodb_client.Table(self.table)

    def check_new_items(self, items: list[dict]) -> list[dict]:
        """
        Verifica os dados armazenados no DynamoDB para identificar novos registros e mudanças na coluna especificada.

        :param items: Lista de dicionários com os dados atuais (ex: [{"id": "1", "value": 1000}]).
        :return: Uma tupla contendo duas listas:
            - Novos registros a serem inseridos.
            - Registros com mudanças na coluna especificada a serem atualizados.
        """
        new_items = []

        for item in items:
            try:
                # Busca o registro pelo ID
                response = self.table_obj.get_item(Key={"id": item["id"]}, ReturnConsumedCapacity='TOTAL')
                stored_item = response.get("Item")
                consumed_capacity = response.get('ConsumedCapacity', [])
                print(consumed_capacity)
                if not stored_item:
                    # Novo registro
                    new_items.append(item)
            except ClientError as e:
                print(f"Erro ao consultar item {item['id']}: {e.response['Error']['Message']}")

        return new_items

    def insert_new_items(self, new_items: list[dict]) -> None:
        """
        Insere novos registros na tabela DynamoDB.

        :param new_items: Lista de novos registros para inserir.
        """
        for item in new_items:
            try:
                response = self.table_obj.put_item(Item=item, ReturnConsumedCapacity='TOTAL')
                consumed_capacity = response.get('ConsumedCapacity', [])
                print(consumed_capacity)
                print(f"Novo item inserido: {item}")
            except ClientError as e:
                print(f"Erro ao inserir item {item}: {e.response['Error']['Message']}")

