import os
import json

import requests
from dotenv import load_dotenv


def get_access_token(client_id, client_secret):
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    return response.json().get('access_token')


def get_cart_items(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get('https://api.moltin.com/v2/carts/zxcvbnma/items', headers=headers)
    print(response.json())


def add_product_to_cart(access_token, id):
    url = 'https://api.moltin.com/v2/carts/zxcvbnma/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'data': {
            'id': id,
            'type': 'cart_item',
            'quantity': 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        print('Продукт успешно добавлен в корзину!')
    else:
        print(f'Ошибка при добавлении продукта в корзину: {response.text}')


def get_all_products(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers)
    return response.json()


def get_product_by_id(access_token, product_id):
    url = f'https://api.moltin.com/catalog/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_img_id(access_token, prod_id):
    url = f'https://api.moltin.com/pcm/products/{prod_id}/relationships/main_image'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['id']


def get_img_url(access_token, prod_id):
    img_id = get_img_id(access_token, prod_id)
    url = f'https://api.moltin.com/v2/files/{img_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


if __name__ == '__main__':
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    get_access_token(client_id, client_secret)
    moltin_token = get_access_token(client_id, client_secret)
    img_id = get_img_id(moltin_token, 'ec4f7d90-793d-430f-9bc4-2e1fdd3adeba')
    print(get_img_url(moltin_token, img_id))
