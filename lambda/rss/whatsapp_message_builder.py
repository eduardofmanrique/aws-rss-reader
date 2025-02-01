import datetime


def caption(info: dict):
    default_params = ['Data', 'Título', 'Link', 'image']
    date = (info.get('Data', datetime.datetime.now()) - datetime.timedelta(hours=3)).strftime('%d/%m/%Y %H:%M:%S')
    title = f"*{info.get('Título', 'Sem Título')}*"
    other_params = '\n'.join([field for field_name, field in info.items() if not field_name in default_params])
    return f"{title}\n{date}\n{other_params}\n{info.get('Link', '')}"


if __name__ == '__main__':
    teste = {'id': 'eeed9dc5e51b22ac095499b75db1bcb8', 'info': {'Data': datetime.datetime(2025, 2, 1, 6, 30), 'Título': None, 'Link': 'https://news.google.com/rss/articles/CBMiZEFVX3lxTE1aaHE2MTN1VUFWcG1hNURlb2I3WGZzRHZ2ZkxmcGVtLWNBSWs5Uk5leTZLUUM5b09aS0tmQXMzQk9sTXo3a1hIR1BTaUR4MVFmdHZtODJrTWliTFI3MlNYbHlJdXI?oc=5', 'image': None}}

    print(caption(teste['info']))


