import hashlib
import requests
from config import Config
from urllib.parse import urlencode

def generate_signature(merchant_login, amount, inv_id, password):
    """Генерирует MD5-подпись для Robokassa"""
    signature_string = f"{merchant_login}:{amount}:{inv_id}:{password}"
    return hashlib.md5(signature_string.encode()).hexdigest()

def get_payment_url(amount, description, user_email, inv_id):
    """Возвращает полный URL для редиректа на Robokassa"""
    merchant_login = Config.ROBOKASSA_MERCHANT_LOGIN
    password = Config.ROBOKASSA_PASSWORD_1
    
    signature = generate_signature(merchant_login, amount, inv_id, password)
    
    params = {
        'MerchantLogin': merchant_login,
        'OutSum': amount,
        'InvId': inv_id,
        'Description': description,
        'Email': user_email,
        'SignatureValue': signature
    }
    
    url = "https://auth.robokassa.ru/Merchant/Index.aspx?" + urlencode(params)
    return url

def check_payment(inv_id, out_sum):
    """Проверяет статус оплаты через Result URL (использует Password #2)"""
    merchant_login = Config.ROBOKASSA_MERCHANT_LOGIN
    password = Config.ROBOKASSA_PASSWORD_2
    
    signature = generate_signature(merchant_login, out_sum, inv_id, password)
    
    # Это URL, который Robokassa вызывает для подтверждения
    confirm_url = f"https://auth.robokassa.ru/Merchant/Confirm.aspx?MerchantLogin={merchant_login}&InvId={inv_id}&OutSum={out_sum}&SignatureValue={signature}"
    
    try:
        response = requests.get(confirm_url, timeout=10)
        return response.text == 'OK'
    except Exception as e:
        print(f"Ошибка проверки платежа: {e}")
        return False