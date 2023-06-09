import os
import json
import time
from textwrap import dedent

import requests
from dotenv import load_dotenv


MOLTIN_TOKEN_EXPIRES_TIME = 0
MOLTIN_TOKEN = None


def get_access_token(client_id, client_secret):
    global MOLTIN_TOKEN_EXPIRES_TIME
    global MOLTIN_TOKEN

    if time.time() <= MOLTIN_TOKEN_EXPIRES_TIME:
        return MOLTIN_TOKEN

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    token_details = response.json()
    MOLTIN_TOKEN_EXPIRES_TIME = token_details.get('expires')
    MOLTIN_TOKEN = token_details.get('access_token')
    return MOLTIN_TOKEN


def add_product_to_cart(client_id, client_secret, cart_id, product_id, quantity):
    access_token = get_access_token(client_id, client_secret)
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()


def remove_product_from_cart(client_id, client_secret, cart_id, product_id):
    access_token = get_access_token(client_id, client_secret)
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_products(client_id, client_secret, cart_id):
    access_token = get_access_token(client_id, client_secret)
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_total(client_id, client_secret, cart_id):
    access_token = get_access_token(client_id, client_secret)
    url = f'https://api.moltin.com/v2/carts/{cart_id}/'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['meta']['display_price']['with_tax']['formatted']


def get_all_products(client_id, client_secret):
    access_token = get_access_token(client_id, client_secret)
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers)
    response.raise_for_status()
    return response.json()


def get_product_by_id(client_id, client_secret, product_id):
    access_token = get_access_token(client_id, client_secret)
    url = f'https://api.moltin.com/catalog/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_img_id(client_id, client_secret, prod_id):
    access_token = get_access_token(client_id, client_secret)
    url = f'https://api.moltin.com/pcm/products/{prod_id}/relationships/main_image'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['id']


def get_img_url(client_id, client_secret, prod_id):
    access_token = get_access_token(client_id, client_secret)
    img_id = get_img_id(client_id, client_secret, prod_id)
    url = f'https://api.moltin.com/v2/files/{img_id}'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def create_customer(client_id, client_secret, user_name, user_email):
    access_token = get_access_token(client_id, client_secret)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'data': {
            'type': 'customer',
            'name': user_name,
            'email': user_email,
        },
    }
    response = requests.post(
        'https://api.moltin.com/v2/customers',
        headers=headers,
        json=data
    )
    response.raise_for_status()
