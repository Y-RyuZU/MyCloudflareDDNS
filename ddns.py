import os
import requests
import re
import json

# Cloudflareの設定を環境変数から取得
auth_email = os.getenv('AUTH_EMAIL')
api_token = os.getenv('API_TOKEN')
domains = json.loads(os.getenv('DOMAINS'))

# CloudflareのAPIエンドポイント
cloudflare_endpoint = "https://api.cloudflare.com/client/v4"

headers = {
    'X-Auth-Email': auth_email,
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

# Zone IDを取得する関数
def get_zone_id(domain):
    try:
        response = requests.get(f"{cloudflare_endpoint}/zones", headers=headers, params={"name": domain})
        response.raise_for_status()
        data = response.json()
        return data['result'][0]['id']
    except Exception as e:
        print(f"Error getting zone ID for {domain}: {e}")
        return None

# Record IDを取得する関数
def get_record_id(zone_id, domain):
    try:
        response = requests.get(f"{cloudflare_endpoint}/zones/{zone_id}/dns_records", headers=headers, params={"name": domain})
        response.raise_for_status()
        data = response.json()
        return data['result'][0]['id']
    except Exception as e:
        print(f"Error getting record ID for {domain}: {e}")
        return None

# IPアドレス取得サービスのリスト
services = [
    "https://api.ipify.org/",
    "https://checkip.amazonaws.com/",
    "https://ipv4.icanhazip.com/",
    "https://4.icanhazip.com/"
]

# IPアドレスの正規表現パターン
ip_pattern = r"^([0-9]{1,3}\.){3}[0-9]{1,3}$"

# IPアドレスを取得する関数
def get_ip_address(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        return None

# 正規表現でIPアドレスが検証できるかチェックする関数
def is_valid_ip(ip_address):
    return re.match(ip_pattern, ip_address) is not None

# DNSレコードを更新する関数
def update_dns_record(domain, zone_id, record_id, ip_address):
    try:
        # Cloudflare APIを使ってDNSレコードを更新
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        data = {'type': 'A', 'name': domain, 'content': ip_address}
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()

        print(f"DNS record updated for {domain}: {ip_address}")

    except Exception as e:
        print(f"Error updating DNS for {domain}: {e}")

# IPアドレス取得のループ
current_ip = None
for service in services:
    current_ip = get_ip_address(service)
    if current_ip and is_valid_ip(current_ip):
        break

# 取得したIPアドレスを使って各ドメインのDNSレコードを更新
if current_ip:
    for domain in domains:
        zone_id = get_zone_id(domain)
        if zone_id:
            record_id = get_record_id(zone_id, domain)
            if record_id:
                update_dns_record(domain, zone_id, record_id, current_ip)
else:
    print("Failed to get IP address")
