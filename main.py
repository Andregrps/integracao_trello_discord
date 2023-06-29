from discord_webhook import DiscordWebhook
import time
import json
import requests
from trello import TrelloClient

# Caminho para o arquivo JSON
json_file_path = 'C:\keys.json'

# Função para carregar as chaves e tokens do arquivo JSON
def load_keys_from_file(file_path):
    with open(file_path, 'r') as file:
        keys_data = json.load(file)
    return keys_data

# Carrega as chaves e tokens do arquivo JSON
keys_data = load_keys_from_file(json_file_path)

# Atribui as chaves e tokens às variáveis
TRELLO_API_KEY = keys_data['TRELLO_API_KEY']
TRELLO_TOKEN = keys_data['TRELLO_TOKEN']
DISCORD_WEBHOOK_URL = keys_data['DISCORD_WEBHOOK_URL']
TRELLO_BOARD_ID = keys_data['TRELLO_BOARD_ID']
BUG_URGENTE_ID = keys_data.get('BUG_URGENTE_ID')  # Obtém a ID da lista "BUG URGENTE" do arquivo JSON

# Inicialização do webhook do Discord
webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)

# Lista para armazenar os IDs dos cards iniciais
initial_cards = []

# Inicialização do cliente do Trello
client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=None,
    token=TRELLO_TOKEN,
    token_secret=None
)

# Obtém o nome da lista "BUG URGENTE"
trello_list = client.get_list(BUG_URGENTE_ID)
bug_urgente_list_name = trello_list.name

# Função para enviar uma mensagem no webhook do Discord
def send_discord_message(message):
    webhook.content = message
    webhook.execute()

# Função para obter o nome do usuário pelo ID
def get_member_name(card_id):
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/actions"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN,
        'filter': 'createCard',
        'fields': 'idMemberCreator',
        'idModels': card_id
    }
    response = requests.request("GET", url, params=query)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            name = data[0]["memberCreator"]["fullName"]
            print(name)
        else:
            print("Nenhum dado encontrado.")
    else:
        print("Erro na requisição:", response.status_code)

    return name

# Função para verificar as alterações no Trello
def check_trello():
    url = f'https://api.trello.com/1/lists/{BUG_URGENTE_ID}/cards'
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        cards_data = response.json()
        for card_data in cards_data:
            card_id = card_data['id']
            # Verifica se o card é novo ou se já estava presente inicialmente
            if card_id not in initial_cards:
                member_name = get_member_name(card_id)
                card_name = card_data['name']
                send_discord_message(f'<@&989164790087827498> Novo card criado por {member_name}, em {bug_urgente_list_name}, descrição do card: {card_name}')
                initial_cards.append(card_id)  # Adiciona o ID do card à lista de cards iniciais

# Obtém os cards iniciais
list_ = client.get_list(BUG_URGENTE_ID)
initial_cards = [card.id for card in list_.list_cards()]

# Loop contínuo para verificar o Trello
while True:
    check_trello()
    time.sleep(1)
