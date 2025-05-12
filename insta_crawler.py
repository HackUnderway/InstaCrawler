import requests
import json
import re
import urllib3
import csv
from datetime import datetime

urllib3.disable_warnings()

ascii_art = r"""
.___                 __         _________                      .__                
|   | ____   _______/  |______  \_   ___ \____________ __  _  _|  |   ___________ 
|   |/    \ /  ___/\   __\__  \ /    \  \/\_  __ \__  \\ \/ \/ /  | _/ __ \_  __ \
|   |   |  \\___ \  |  |  / __ \\     \____|  | \// __ \\     /|  |_\  ___/|  | \/
|___|___|  /____  > |__| (____  /\______  /|__|  (____  /\/\_/ |____/\___  >__|   
         \/     \/            \/        \/            \/                 \/      
"""

def obtener_info_osint(username, guardar_csv=True):
    url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
    data = {'email_or_username': username}
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Instagram-Ajax': '1',
        'X-Csrftoken': 'DUMMYTOKEN',
        'Referer': 'https://www.instagram.com/accounts/password/reset/',
    }

    response = requests.post(url, headers=headers, data=data, verify=False)
    result = {
        'usuario': username,
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status_code': response.status_code,
        'correo_visible': '',
        'dominio': '',
        'tipo': '',
        'alerta': '',
    }

    if response.status_code == 200:
        try:
            res_json = response.json()
            if 'contact_point' in res_json:
                correo_oculto = res_json['contact_point']
                result['correo_visible'] = correo_oculto

                match = re.search(r'@(\w+\.\w+)', correo_oculto)
                if match:
                    dominio = match.group(1)
                    result['dominio'] = dominio

                    if "gmail.com" in dominio:
                        result['tipo'] = "Gmail"
                    elif "hotmail.com" in dominio:
                        result['tipo'] = "Hotmail"
                    elif "yahoo.com" in dominio:
                        result['tipo'] = "Yahoo"
                    elif "outlook.com" in dominio:
                        result['tipo'] = "Outlook"
                    elif "protonmail.com" in dominio or "proton.me" in dominio:
                        result['tipo'] = "ProtonMail"
                    else:
                        result['tipo'] = "Otro"
                else:
                    result['tipo'] = "Indeterminado"
                result['alerta'] = "Todo OK"
            else:
                result['alerta'] = "No se obtuvo ningún correo."
        except Exception as e:
            result['alerta'] = f"Error JSON: {str(e)}"
    else:
        result['alerta'] = f"Error HTTP: {response.status_code}"

    print(f"\n[INFO OSINT] Usuario: {username}")
    print(f"- Código HTTP: {result['status_code']}")
    print(f"- Correo parcial: {result['correo_visible']}")
    print(f"- Dominio: {result['dominio']}")
    print(f"- Tipo: {result['tipo']}")
    print(f"- Alerta: {result['alerta']}")

    if guardar_csv:
        with open('resultados_osint.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=result.keys())
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(result)

if __name__ == "__main__":
    print(ascii_art)
    usuario = input("🔍 Ingresa el nombre de usuario de Instagram para OSINT: ").strip()
    obtener_info_osint(usuario, guardar_csv=True)
