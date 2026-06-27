class Vertical:
    def __init__(self, id, name, icon, description, metrics):
        self.id = id
        self.name = name
        self.icon = icon
        self.description = description
        self.metrics = metrics

# Все метрики из METRICS_REGISTRY (полный список)
ALL_METRICS = [
    # Финансы
    'revenue', 'mrr', 'arr', 'nrr', 'grr', 'ltv', 'cac', 'ltv_cac_ratio',
    'payback_period', 'expansion_revenue', 'downgrade_revenue', 'churned_revenue',
    'average_revenue_per_user', 'average_revenue_per_paying_user', 'monthly_growth_rate',
    # Отток и удержание
    'customer_churn_rate', 'revenue_churn_rate', 'net_churn_rate', 'retention_rate',
    'downgrade_rate', 'upgrade_rate', 'reactivation_rate',
    # Активность
    'active_users', 'churned_users', 'trial_users', 'new_users',
    'daily_active_users', 'weekly_active_users', 'monthly_active_users', 'stickiness_ratio',
    # Воронка
    'trial_conversion_rate', 'lead_to_mql_conversion', 'mql_to_sql_conversion',
    'sql_to_closed_won', 'time_to_value',
    # Продукт
    'feature_adoption_rate', 'average_session_duration', 'sessions_per_user', 'bounce_rate',
    # E-commerce
    'average_order_value', 'conversion_rate', 'cart_abandonment_rate',
    'return_rate', 'customer_lifetime_value', 'repurchase_rate',
    # FinTech
    'transaction_volume', 'average_transaction_value', 'fraud_rate',
    'net_interest_margin', 'transaction_success_rate',
    # Подписки
    'average_subscription_length', 'payment_failure_rate', 'dunning_success_rate',
    # Операционные
    'inventory_turnover', 'staff_efficiency', 'footfall', 'average_check',
    'loyalty_rate', 'net_promoter_score',
    # Качество сервиса
    'support_ticket_volume', 'average_response_time', 'average_resolution_time', 'csat',
    # Маркетинг
    'marketing_roi', 'lead_velocity_rate', 'cost_per_lead', 'cost_per_acquisition'
]

VERTICALS = [
    Vertical(
        id='saas',
        name='SaaS / Подписки',
        icon='bi-cloud',
        description='Подписочные сервисы, B2B SaaS, платформы с ежемесячной оплатой',
        metrics=ALL_METRICS
    ),
    Vertical(
        id='ecommerce',
        name='E-commerce',
        icon='bi-cart',
        description='Интернет-магазины, розничная торговля, D2C бренды',
        metrics=ALL_METRICS
    ),
    Vertical(
        id='fintech',
        name='FinTech',
        icon='bi-bank',
        description='Финансовые сервисы, банки, платежные системы',
        metrics=ALL_METRICS
    ),
    Vertical(
        id='subscription',
        name='Подписки (общие)',
        icon='bi-arrow-repeat',
        description='Подписки на медиа, контент, коробки, сервисы',
        metrics=ALL_METRICS
    ),
    Vertical(
        id='retail',
        name='Ритейл / Офлайн',
        icon='bi-shop',
        description='Сети магазинов, офлайн-продажи, франшизы',
        metrics=ALL_METRICS
    ),
    Vertical(
        id='custom',
        name='Прочее (Custom)',
        icon='bi-tools',
        description='Полный доступ ко всем метрикам. Настройте дашборд под себя.',
        metrics='all'
    )
]

VERTICALS_DICT = {v.id: v for v in VERTICALS}

def get_vertical(vertical_id):
    return VERTICALS_DICT.get(vertical_id)

def get_all_verticals():
    return VERTICALS

def get_metrics_for_vertical(vertical_id):
    from core.metrics_engine import METRICS_REGISTRY
    vertical = get_vertical(vertical_id)
    if not vertical:
        return []
    if vertical.metrics == 'all':
        return list(METRICS_REGISTRY.keys())
    # Возвращаем только те метрики, которые есть в регистре
    return [m for m in vertical.metrics if m in METRICS_REGISTRY]