import os
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials():
    """Загружает credentials из service_account.json"""
    if os.path.exists('service_account.json'):
        creds = service_account.Credentials.from_service_account_file(
            'service_account.json', scopes=SCOPES
        )
        return creds
    return None

def get_sheet_data(spreadsheet_id, range_name='Лист1'):
    """Получает данные из Google Sheets"""
    creds = get_credentials()
    if not creds:
        return None
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    values = result.get('values', [])
    
    if not values:
        return None
    
    headers = values[0]
    rows = values[1:]
    
    data = []
    for row in rows:
        while len(row) < len(headers):
            row.append('')
        data.append(dict(zip(headers, row)))
    
    return pd.DataFrame(data)

def process_sheet_data(df):
    """Преобразует данные в формат Percepta"""
    if df.empty:
        return pd.DataFrame()
    
    required = ['user_id', 'date', 'revenue', 'status']
    missing = [r for r in required if r not in df.columns]
    if missing:
        raise ValueError(f'Отсутствуют колонки: {", ".join(missing)}')
    
    df['user_id'] = df['user_id'].astype(str).str.replace('"', '').str.replace("'", '')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
    df['status'] = df['status'].str.lower().str.strip()
    df['status'] = df['status'].apply(lambda x: 'active' if x in ['active', 'true', '1'] else 'churned')
    
    if 'last_activity_date' not in df.columns:
        df['last_activity_date'] = df['date']
    if 'support_ticket_text' not in df.columns:
        df['support_ticket_text'] = ''
    
    return df