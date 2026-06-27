# ==========================================
# ВСЕ МЕТРИКИ ДЛЯ PERCEPTA (ПОЛНЫЙ СПИСОК)
# ==========================================

METRICS_REGISTRY = {
    # ========== ФИНАНСОВЫЕ МЕТРИКИ ==========
    'revenue': {'name': 'Общая выручка', 'description': 'Суммарная выручка за период', 'category': 'Финансы', 'icon': 'bi-cash', 'unit': '$'},
    'mrr': {'name': 'MRR', 'description': 'Ежемесячная регулярная выручка', 'category': 'Финансы', 'icon': 'bi-graph-up', 'unit': '$'},
    'arr': {'name': 'ARR', 'description': 'Годовая регулярная выручка (MRR × 12)', 'category': 'Финансы', 'icon': 'bi-calendar3', 'unit': '$'},
    'nrr': {'name': 'NRR', 'description': 'Удержание дохода ( > 100% — супер)', 'category': 'Финансы', 'icon': 'bi-arrow-repeat', 'unit': '%'},
    'grr': {'name': 'GRR', 'description': 'Валовое удержание дохода (без апсейлов)', 'category': 'Финансы', 'icon': 'bi-arrow-repeat', 'unit': '%'},
    'ltv': {'name': 'LTV', 'description': 'Средняя прибыль от клиента за всё время', 'category': 'Финансы', 'icon': 'bi-clock-history', 'unit': '$'},
    'cac': {'name': 'CAC', 'description': 'Стоимость привлечения одного клиента', 'category': 'Финансы', 'icon': 'bi-cash-stack', 'unit': '$'},
    'ltv_cac_ratio': {'name': 'LTV/CAC Ratio', 'description': 'Соотношение LTV к CAC ( > 3 — здорово)', 'category': 'Финансы', 'icon': 'bi-arrow-left-right', 'unit': ''},
    'payback_period': {'name': 'Payback Period', 'description': 'Срок окупаемости CAC в месяцах', 'category': 'Финансы', 'icon': 'bi-calendar-check', 'unit': 'мес.'},
    'expansion_revenue': {'name': 'Expansion Revenue', 'description': 'Доход от апсейлов и кросс-сейлов', 'category': 'Финансы', 'icon': 'bi-arrow-up-circle', 'unit': '$'},
    'downgrade_revenue': {'name': 'Downgrade Revenue', 'description': 'Потеря дохода от перехода на дешёвые тарифы', 'category': 'Финансы', 'icon': 'bi-arrow-down-circle', 'unit': '$'},
    'churned_revenue': {'name': 'Churned Revenue', 'description': 'Потеря дохода от ушедших клиентов', 'category': 'Финансы', 'icon': 'bi-exclamation-triangle', 'unit': '$'},
    'average_revenue_per_user': {'name': 'ARPU', 'description': 'Средняя выручка на активного пользователя', 'category': 'Финансы', 'icon': 'bi-person-badge', 'unit': '$'},
    'average_revenue_per_paying_user': {'name': 'ARPPU', 'description': 'Средняя выручка на платящего пользователя', 'category': 'Финансы', 'icon': 'bi-person-check', 'unit': '$'},
    'monthly_growth_rate': {'name': 'Monthly Growth Rate', 'description': 'Темп роста MRR по месяцам', 'category': 'Финансы', 'icon': 'bi-graph-up-arrow', 'unit': '%'},
    
    # ========== ОТТОК И УДЕРЖАНИЕ ==========
    'customer_churn_rate': {'name': 'Customer Churn Rate', 'description': 'Процент ушедших клиентов', 'category': 'Отток и удержание', 'icon': 'bi-person-x', 'unit': '%'},
    'revenue_churn_rate': {'name': 'Revenue Churn Rate', 'description': 'Процент потерянной выручки', 'category': 'Отток и удержание', 'icon': 'bi-cash-x', 'unit': '%'},
    'net_churn_rate': {'name': 'Net Churn Rate', 'description': 'Revenue Churn минус Expansion', 'category': 'Отток и удержание', 'icon': 'bi-arrow-left-right', 'unit': '%'},
    'retention_rate': {'name': 'Retention Rate', 'description': 'Процент оставшихся клиентов', 'category': 'Отток и удержание', 'icon': 'bi-heart', 'unit': '%'},
    'downgrade_rate': {'name': 'Downgrade Rate', 'description': 'Процент перехода на дешёвый тариф', 'category': 'Отток и удержание', 'icon': 'bi-arrow-down-circle', 'unit': '%'},
    'upgrade_rate': {'name': 'Upgrade Rate', 'description': 'Процент перехода на дорогой тариф', 'category': 'Отток и удержание', 'icon': 'bi-arrow-up-circle', 'unit': '%'},
    'reactivation_rate': {'name': 'Reactivation Rate', 'description': 'Процент вернувшихся клиентов', 'category': 'Отток и удержание', 'icon': 'bi-arrow-counterclockwise', 'unit': '%'},
    
    # ========== АКТИВНОСТЬ ==========
    'active_users': {'name': 'Активные пользователи', 'description': 'Количество активных пользователей', 'category': 'Активность', 'icon': 'bi-people', 'unit': ''},
    'churned_users': {'name': 'Ушедшие пользователи', 'description': 'Количество ушедших пользователей', 'category': 'Активность', 'icon': 'bi-person-x', 'unit': ''},
    'trial_users': {'name': 'Пользователи на триале', 'description': 'Количество в пробном периоде', 'category': 'Активность', 'icon': 'bi-clock', 'unit': ''},
    'new_users': {'name': 'Новые пользователи', 'description': 'Зарегистрировались за период', 'category': 'Активность', 'icon': 'bi-person-plus', 'unit': ''},
    'daily_active_users': {'name': 'DAU', 'description': 'Уникальных пользователей в день', 'category': 'Активность', 'icon': 'bi-calendar-day', 'unit': ''},
    'weekly_active_users': {'name': 'WAU', 'description': 'Уникальных пользователей в неделю', 'category': 'Активность', 'icon': 'bi-calendar-week', 'unit': ''},
    'monthly_active_users': {'name': 'MAU', 'description': 'Уникальных пользователей в месяц', 'category': 'Активность', 'icon': 'bi-calendar-month', 'unit': ''},
    'stickiness_ratio': {'name': 'Stickiness Ratio', 'description': 'DAU / MAU (чем выше, тем лучше)', 'category': 'Активность', 'icon': 'bi-heart', 'unit': '%'},
    
    # ========== ВОРОНКА ==========
    'trial_conversion_rate': {'name': 'Trial Conversion', 'description': 'Конверсия из триала в платный', 'category': 'Воронка', 'icon': 'bi-arrow-right-circle', 'unit': '%'},
    'lead_to_mql_conversion': {'name': 'Lead → MQL', 'description': 'Процент лидов, ставших MQL', 'category': 'Воронка', 'icon': 'bi-arrow-right-circle', 'unit': '%'},
    'mql_to_sql_conversion': {'name': 'MQL → SQL', 'description': 'Процент MQL, ставших SQL', 'category': 'Воронка', 'icon': 'bi-arrow-right-circle', 'unit': '%'},
    'sql_to_closed_won': {'name': 'SQL → Closed-Won', 'description': 'Процент SQL, ставших сделками', 'category': 'Воронка', 'icon': 'bi-arrow-right-circle', 'unit': '%'},
    'time_to_value': {'name': 'Time to Value', 'description': 'Время от регистрации до пользы', 'category': 'Воронка', 'icon': 'bi-clock', 'unit': 'дней'},
    
    # ========== ПРОДУКТ ==========
    'feature_adoption_rate': {'name': 'Feature Adoption', 'description': 'Процент использования ключевой функции', 'category': 'Продукт', 'icon': 'bi-grid-3x3-gap', 'unit': '%'},
    'average_session_duration': {'name': 'Ср. длительность сессии', 'description': 'Средняя продолжительность сессии', 'category': 'Продукт', 'icon': 'bi-clock', 'unit': 'мин'},
    'sessions_per_user': {'name': 'Sessions per User', 'description': 'Среднее количество сессий на пользователя', 'category': 'Продукт', 'icon': 'bi-arrow-repeat', 'unit': ''},
    'bounce_rate': {'name': 'Bounce Rate', 'description': 'Процент ухода после 1 страницы', 'category': 'Продукт', 'icon': 'bi-door-open', 'unit': '%'},
    
    # ========== E-COMMERCE ==========
    'average_order_value': {'name': 'Средний чек (AOV)', 'description': 'Средняя стоимость заказа', 'category': 'E-commerce', 'icon': 'bi-cart-check', 'unit': '$'},
    'conversion_rate': {'name': 'Conversion Rate', 'description': 'Процент посетителей, совершивших покупку', 'category': 'E-commerce', 'icon': 'bi-percent', 'unit': '%'},
    'cart_abandonment_rate': {'name': 'Cart Abandonment', 'description': 'Процент брошенных корзин', 'category': 'E-commerce', 'icon': 'bi-cart-x', 'unit': '%'},
    'return_rate': {'name': 'Return Rate', 'description': 'Процент возвратов товаров', 'category': 'E-commerce', 'icon': 'bi-arrow-counterclockwise', 'unit': '%'},
    'customer_lifetime_value': {'name': 'CLV', 'description': 'Общая прибыль от клиента', 'category': 'E-commerce', 'icon': 'bi-clock-history', 'unit': '$'},
    'repurchase_rate': {'name': 'Repurchase Rate', 'description': 'Процент повторных покупок', 'category': 'E-commerce', 'icon': 'bi-arrow-repeat', 'unit': '%'},
    
    # ========== FINTECH ==========
    'transaction_volume': {'name': 'Объем транзакций', 'description': 'Общий объем всех транзакций', 'category': 'FinTech', 'icon': 'bi-credit-card', 'unit': '$'},
    'average_transaction_value': {'name': 'Средняя транзакция', 'description': 'Средняя сумма транзакции', 'category': 'FinTech', 'icon': 'bi-piggy-bank', 'unit': '$'},
    'fraud_rate': {'name': 'Fraud Rate', 'description': 'Процент мошеннических транзакций', 'category': 'FinTech', 'icon': 'bi-shield-exclamation', 'unit': '%'},
    'net_interest_margin': {'name': 'Net Interest Margin', 'description': 'Чистая процентная маржа', 'category': 'FinTech', 'icon': 'bi-graph-up-arrow', 'unit': '%'},
    'transaction_success_rate': {'name': 'Transaction Success', 'description': 'Процент успешных транзакций', 'category': 'FinTech', 'icon': 'bi-check-circle', 'unit': '%'},
    
    # ========== ПОДПИСКИ ==========
    'average_subscription_length': {'name': 'Ср. длина подписки', 'description': 'Среднее количество месяцев', 'category': 'Подписки', 'icon': 'bi-clock', 'unit': 'мес.'},
    'payment_failure_rate': {'name': 'Payment Failure', 'description': 'Процент неудачных списаний', 'category': 'Подписки', 'icon': 'bi-exclamation-octagon', 'unit': '%'},
    'dunning_success_rate': {'name': 'Dunning Success', 'description': 'Процент успешных повторных списаний', 'category': 'Подписки', 'icon': 'bi-arrow-clockwise', 'unit': '%'},
    
    # ========== ОПЕРАЦИОННЫЕ ==========
    'inventory_turnover': {'name': 'Оборачиваемость запасов', 'description': 'Скорость оборота товаров', 'category': 'Операционные', 'icon': 'bi-arrow-left-right', 'unit': 'раз'},
    'staff_efficiency': {'name': 'Эффективность персонала', 'description': 'Выручка на одного сотрудника', 'category': 'Операционные', 'icon': 'bi-person-gear', 'unit': '$'},
    'footfall': {'name': 'Посещаемость', 'description': 'Количество посетителей', 'category': 'Операционные', 'icon': 'bi-people', 'unit': ''},
    'average_check': {'name': 'Средний чек', 'description': 'Средняя сумма покупки', 'category': 'Операционные', 'icon': 'bi-receipt', 'unit': '$'},
    'loyalty_rate': {'name': 'Loyalty Rate', 'description': 'Процент повторных покупок', 'category': 'Операционные', 'icon': 'bi-heart', 'unit': '%'},
    'net_promoter_score': {'name': 'NPS', 'description': 'Оценка лояльности (-100 до +100)', 'category': 'Операционные', 'icon': 'bi-emoji-smile', 'unit': ''},
    
    # ========== КАЧЕСТВО СЕРВИСА ==========
    'support_ticket_volume': {'name': 'Обращения в поддержку', 'description': 'Количество обращений', 'category': 'Качество сервиса', 'icon': 'bi-ticket', 'unit': ''},
    'average_response_time': {'name': 'Ср. время ответа', 'description': 'Среднее время ответа (часы)', 'category': 'Качество сервиса', 'icon': 'bi-clock', 'unit': 'ч'},
    'average_resolution_time': {'name': 'Ср. время решения', 'description': 'Среднее время решения (часы)', 'category': 'Качество сервиса', 'icon': 'bi-clock-history', 'unit': 'ч'},
    'csat': {'name': 'CSAT', 'description': 'Удовлетворённость клиентов (1-5)', 'category': 'Качество сервиса', 'icon': 'bi-star', 'unit': ''},
    
    # ========== МАРКЕТИНГ ==========
    'marketing_roi': {'name': 'Marketing ROI', 'description': 'Возврат на маркетинг', 'category': 'Маркетинг', 'icon': 'bi-graph-up-arrow', 'unit': '%'},
    'lead_velocity_rate': {'name': 'Lead Velocity Rate', 'description': 'Темп роста лидов', 'category': 'Маркетинг', 'icon': 'bi-speedometer2', 'unit': '%'},
    'cost_per_lead': {'name': 'CPL', 'description': 'Стоимость одного лида', 'category': 'Маркетинг', 'icon': 'bi-cash', 'unit': '$'},
    'cost_per_acquisition': {'name': 'CPA', 'description': 'Стоимость привлечения клиента', 'category': 'Маркетинг', 'icon': 'bi-cash-stack', 'unit': '$'}
}

def get_metric_metadata(metric_id):
    return METRICS_REGISTRY.get(metric_id)

def get_all_metric_categories():
    categories = set()
    for metric in METRICS_REGISTRY.values():
        categories.add(metric['category'])
    return sorted(list(categories))

def get_metrics_by_category(category):
    result = []
    for metric_id, metric in METRICS_REGISTRY.items():
        if metric['category'] == category:
            result.append({'id': metric_id, **metric})
    return result