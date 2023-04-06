import requests
import argparse
import subprocess
import random
import os
import json


OPNSENSE_API_KEY = 'your_api_key'
OPNSENSE_API_SECRET = 'your_api_secret'
OPNSENSE_API_URL = 'https://your_opnsense_firewall/api'

def get_existing_endpoints():
    url = f'{OPNSENSE_API_URL}/wireguard/endpoint'
    response = requests.get(url, auth=(OPNSENSE_API_KEY, OPNSENSE_API_SECRET))
    return response.json()

def generate_unique_ip(existing_endpoints):
    existing_ips = [endpoint['address'] for endpoint in existing_endpoints]
    while True:
        new_ip = f'10.10.116.{random.randint(2, 254)}'
        if new_ip not in existing_ips:
            return new_ip

def generate_key_pair():
    private_key = subprocess.check_output(['wg', 'genkey']).strip().decode()
    public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key.encode()).strip().decode()
    return private_key, public_key

def add_endpoint_to_local_interface(endpoint_data):
    url = f'{OPNSENSE_API_URL}/wireguard/endpoint'
    response = requests.post(url, json=endpoint_data, auth=(OPNSENSE_API_KEY, OPNSENSE_API_SECRET))
    return response.json()

def refresh_wireguard():
    url = f'{OPNSENSE_API_URL}/wireguard/service/reconfigure'
    response = requests.post(url, auth=(OPNSENSE_API_KEY, OPNSENSE_API_SECRET))
    return response.json()

def generate_client_config(client_data, output_dir):
    config_template = f"""[Interface]
        PrivateKey = {client_data['private_key']}
        Address = {client_data['address']}/24
        DNS = <dns>, <dns>

        [Peer]
        PublicKey = {client_data['public_key']}
        AllowedIPs = <ips>
        Endpoint = <public ip>:<port>
        """
    file_path = os.path.join(output_dir, f"{client_data['name']}.conf")
    with open(file_path, 'w') as f:
        f.write(config_template)

def main(name):
    existing_endpoints = get_existing_endpoints()

    unique_ip = generate_unique_ip(existing_endpoints)

    private_key, public_key = generate_key_pair()

    new_endpoint = {
        "enabled": "1",
        "name": name,
        "publickey": public_key,
        "address": unique_ip,
    }

    add_endpoint_to_local_interface(new_endpoint)

    refresh_wireguard()

    client_data = {
        "name": new_endpoint["name"],
        "private_key": private_key,
        "public_key": public_key,
        "address": new_endpoint["address"],
    }

    output_dir = "client_configs"
    os.makedirs(output_dir, exist_ok=True)
    generate_client_config(client_data, output_dir)

    print(f"Client configuration saved in {os.path.join(output_dir, client_data['name'] + '.conf')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automate WireGuard VPN client setup on OPNsense firewall.')
    parser.add_argument('name', type=str, help='Name for the new endpoint and configuration file.')
    args = parser.parse_args()
    main(args.name)
