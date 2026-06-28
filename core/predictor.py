import pandas as pd
import numpy as np
from datetime import datetime

def calculate_churn_probability(df):
    """
    Рассчитывает вероятность оттока для каждого активного клиента.
    Возвращает DataFrame с колонками: user_id, churn_probability, risk_factors
    """
    if df.empty:
        return pd.DataFrame()
    
    # Работаем только с активными клиентами
    active_df = df[df['status'] == 'active'].copy()
    if active_df.empty:
        return pd.DataFrame()
    
    today = df['date'].max()
    this_month = today.replace(day=1)
    last_month = this_month - pd.offsets.MonthBegin(1)
    
    results = []
    
    for user_id in active_df['user_id'].unique():
        user_data = df[df['user_id'] == user_id]
        
        # 1. Риск на основе недавней активности (40% веса)
        inactivity_risk = 0
        if 'last_activity_date' in df.columns:
            last_activity = user_data['last_activity_date'].max()
            days_inactive = (today - last_activity).days
            if days_inactive > 30:
                inactivity_risk = 40
            elif days_inactive > 14:
                inactivity_risk = 25
            elif days_inactive > 7:
                inactivity_risk = 10
        
        # 2. Риск на основе негативных отзывов в поддержку (30% веса)
        sentiment_risk = 0
        if 'support_ticket_text' in df.columns:
            negative_words = ['дорого', 'дороговато', 'отказ', 'альтернатив', 'не подошел', 
                            'не устроил', 'проблем', 'ошибк', 'сломал', 'медленн']
            all_text = ' '.join(user_data['support_ticket_text'].astype(str))
            negative_count = sum(1 for word in negative_words if word in all_text.lower())
            if negative_count > 2:
                sentiment_risk = 30
            elif negative_count > 0:
                sentiment_risk = 15
        
        # 3. Риск на основе пропусков платежей (30% веса)
        payment_risk = 0
        # Проверяем, был ли платеж в этом месяце
        has_payment_this_month = any(
            (user_data['date'] >= this_month) & 
            (user_data['status'] == 'active')
        )
        if not has_payment_this_month:
            payment_risk = 30
        else:
            # Проверяем, не снизился ли чек
            current_revenue = user_data[user_data['date'] >= this_month]['revenue'].sum()
            past_revenue = user_data[(user_data['date'] >= last_month) & (user_data['date'] < this_month)]['revenue'].sum()
            if past_revenue > 0 and current_revenue < past_revenue * 0.7:
                payment_risk = 15
        
        # Итоговая вероятность (сумма рисков, но не более 100%)
        total_risk = inactivity_risk + sentiment_risk + payment_risk
        churn_probability = min(total_risk, 100)
        
        # Собираем факторы риска для пояснения
        risk_factors = []
        if inactivity_risk > 0:
            risk_factors.append(f"Не активен {days_inactive} дней")
        if sentiment_risk > 0:
            risk_factors.append(f"Негативные отзывы ({negative_count} шт)")
        if payment_risk == 30:
            risk_factors.append("Нет платежа в текущем месяце")
        elif payment_risk == 15:
            risk_factors.append("Снижение чека")
        
        if not risk_factors:
            risk_factors = ["Низкий риск"]
        
        # Получаем последнюю выручку клиента
        last_revenue = user_data[user_data['date'] == user_data['date'].max()]['revenue'].sum()
        
        results.append({
            'user_id': int(user_id),
            'churn_probability': float(churn_probability),
            'risk_factors': risk_factors,
            'last_revenue': float(last_revenue),
            'days_inactive': days_inactive if 'last_activity_date' in df.columns else 0
        })
    
    # Сортируем по убыванию вероятности
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values('churn_probability', ascending=False)
    
    return results_df

def get_top_risky_clients(df, top_n=5):
    """
    Возвращает топ-N клиентов с наибольшей вероятностью оттока
    """
    predictions = calculate_churn_probability(df)
    if predictions.empty:
        return []
    
    # Берем топ-N
    top = predictions.head(top_n)
    
    return top.to_dict('records')