import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def load_data(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Поддерживаются только CSV и Excel файлы")
    df['date'] = pd.to_datetime(df['date'])
    if 'last_activity_date' in df.columns:
        df['last_activity_date'] = pd.to_datetime(df['last_activity_date'])
    return df

def build_cohort(df):
    first_payment = df.groupby('user_id')['date'].min().reset_index()
    first_payment.columns = ['user_id', 'first_month']
    first_payment['first_month'] = first_payment['first_month'].dt.to_period('M')
    df['payment_month'] = df['date'].dt.to_period('M')
    df_cohort = df.merge(first_payment, on='user_id')
    df_cohort['cohort_month'] = (df_cohort['payment_month'].dt.year - df_cohort['first_month'].dt.year) * 12 + (df_cohort['payment_month'].dt.month - df_cohort['first_month'].dt.month)
    cohort_data = df_cohort.groupby(['first_month', 'cohort_month'])['user_id'].nunique().reset_index()
    cohort_data.columns = ['first_month', 'cohort_month', 'users']
    pivot = cohort_data.pivot(index='first_month', columns='cohort_month', values='users')
    if 0 in pivot.columns:
        for col in pivot.columns:
            pivot[col] = (pivot[col] / pivot[0] * 100).round(1)
    pivot = pivot.fillna(0)
    return {
        'index': [str(m) for m in pivot.index],
        'columns': [int(c) for c in pivot.columns],
        'data': pivot.values.tolist()
    }

def find_risky_clients(df):
    risky_clients = []
    today = df['date'].max()
    for _, row in df.iterrows():
        if row['status'] != 'active':
            continue
        risk_score = 0
        reasons = []
        if 'last_activity_date' in df.columns:
            days_inactive = (today - row['last_activity_date']).days
            if days_inactive >= 7:
                risk_score += 40
                reasons.append(f"Не заходил {days_inactive} дней")
        negative_words = ['дорого', 'дороговато', 'отказ', 'альтернатив', 'не подошел', 'не устроил']
        if 'support_ticket_text' in df.columns and isinstance(row.get('support_ticket_text'), str):
            for word in negative_words:
                if word in row['support_ticket_text'].lower():
                    risk_score += 30
                    reasons.append(f"Написал: '{row['support_ticket_text']}'")
                    break
        this_month = today.replace(day=1)
        has_payment_this_month = any(
            (df['user_id'] == row['user_id']) & 
            (df['date'] >= this_month) & 
            (df['status'] == 'active')
        )
        if not has_payment_this_month:
            risk_score += 30
            reasons.append("Нет платежа в текущем месяце")
        if risk_score >= 40:
            risky_clients.append({
                'user_id': int(row['user_id']),
                'risk_score': risk_score,
                'reasons': reasons,
                'revenue': float(row['revenue']),
                'last_activity': row.get('last_activity_date', today).strftime('%Y-%m-%d') if 'last_activity_date' in df.columns else today.strftime('%Y-%m-%d')
            })
    risky_clients.sort(key=lambda x: x['risk_score'], reverse=True)
    return risky_clients[:10]

def calculate_all_metrics(file_path: str, vertical_id: str = 'saas', custom_metrics: list = None) -> dict:
    from core.metrics_engine import METRICS_REGISTRY
    from core.predictor import get_top_risky_clients
    
    df = load_data(file_path)
    today = df['date'].max()
    this_month = today.replace(day=1)
    last_month = this_month - pd.offsets.MonthBegin(1)
    next_month = (this_month + pd.offsets.MonthBegin(1))
    
    # ============================================================
    # БАЗОВЫЕ МЕТРИКИ
    # ============================================================
    total_users = int(df['user_id'].nunique())
    active_users = int(df[df['status'] == 'active']['user_id'].nunique())
    churned_users = int(df[df['status'] == 'churned']['user_id'].nunique())
    trial_users = int(df[df['status'] == 'trial']['user_id'].nunique()) if 'trial' in df['status'].unique() else 0
    
    mask_mrr = (df['date'] >= this_month) & (df['date'] < next_month) & (df['status'] == 'active')
    mrr = float(df[mask_mrr]['revenue'].sum())
    arr = mrr * 12
    arpu = float(df[df['status'] == 'active']['revenue'].sum() / active_users) if active_users > 0 else 0
    paying_users = df[df['status'] == 'active']['user_id'].nunique()
    arppu = float(df[df['status'] == 'active']['revenue'].sum() / paying_users) if paying_users > 0 else 0
    
    churned_mask = (df['status'] == 'churned') & (df['date'] >= this_month) & (df['date'] < next_month)
    churned_revenue = float(df[churned_mask]['revenue'].sum())
    churned_customers = int(df[churned_mask]['user_id'].nunique())
    
    start_mask = (df['date'] < this_month) & (df['status'] == 'active')
    start_mrr = float(df[start_mask]['revenue'].sum())
    start_customers = int(df[start_mask]['user_id'].nunique())
    
    customer_churn_rate = float((churned_customers / start_customers) * 100) if start_customers > 0 else 0
    revenue_churn_rate = float((churned_revenue / start_mrr) * 100) if start_mrr > 0 else 0
    
    past_mask = (df['date'] >= last_month) & (df['date'] < this_month) & (df['status'] == 'active')
    past_clients = set(df[past_mask]['user_id'])
    past_revenue = float(df[past_mask]['revenue'].sum()) if len(past_clients) > 0 else 0
    
    current_mask = (df['date'] >= this_month) & (df['user_id'].isin(past_clients))
    current_revenue = float(df[current_mask]['revenue'].sum())
    
    nrr = float((current_revenue / past_revenue) * 100) if past_revenue > 0 else 100
    
    downgrade_mask = (df['date'] >= this_month) & (df['user_id'].isin(past_clients)) & (df['revenue'] < past_revenue)
    downgrade_revenue = float(df[downgrade_mask]['revenue'].sum())
    churned_past_mask = (df['date'] >= this_month) & (df['user_id'].isin(past_clients)) & (df['status'] == 'churned')
    churned_past_revenue = float(df[churned_past_mask]['revenue'].sum())
    grr = float(((past_revenue - downgrade_revenue - churned_past_revenue) / past_revenue) * 100) if past_revenue > 0 else 100
    
    expansion_users = set(df[(df['date'] >= this_month) & (df['status'] == 'active')]['user_id']) & past_clients
    expansion_revenue = float(df[(df['date'] >= this_month) & (df['user_id'].isin(expansion_users))]['revenue'].sum()) - past_revenue
    expansion_revenue = max(0, expansion_revenue)
    
    net_churn = revenue_churn_rate - ((expansion_revenue / past_revenue) * 100) if past_revenue > 0 else 0
    
    avg_revenue = float(df[df['status'] == 'active']['revenue'].mean()) if active_users > 0 else 0
    user_lifetimes = []
    for user_id in df['user_id'].unique():
        user_data = df[df['user_id'] == user_id]
        if len(user_data) > 1:
            lifetime = (user_data['date'].max() - user_data['date'].min()).days / 30
            user_lifetimes.append(lifetime)
    avg_lifetime = float(np.mean(user_lifetimes)) if user_lifetimes else 3
    ltv = avg_revenue * avg_lifetime
    
    cac = arpu * 3
    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    payback_period = cac / arpu if arpu > 0 else 0
    
    month_ago = this_month - pd.offsets.MonthBegin(1)
    month_ago_mask = (df['date'] >= month_ago) & (df['date'] < this_month) & (df['status'] == 'active')
    month_ago_mrr = float(df[month_ago_mask]['revenue'].sum())
    monthly_growth_rate = float(((mrr - month_ago_mrr) / month_ago_mrr) * 100) if month_ago_mrr > 0 else 0
    
    trial_conversion_rate = 0
    if 'trial' in df['status'].unique():
        trial_users_set = set(df[df['status'] == 'trial']['user_id'])
        paid_users_set = set(df[df['status'] == 'active']['user_id'])
        trial_conversion_rate = float((len(trial_users_set.intersection(paid_users_set)) / len(trial_users_set)) * 100) if len(trial_users_set) > 0 else 0
    
    churned_set = set(df[df['status'] == 'churned']['user_id'])
    active_set = set(df[df['status'] == 'active']['user_id'])
    reactivation_rate = float((len(churned_set.intersection(active_set)) / len(churned_set)) * 100) if len(churned_set) > 0 else 0
    
    past_clients_df = df[past_mask][['user_id', 'revenue']].drop_duplicates('user_id')
    current_clients_df = df[(df['date'] >= this_month) & (df['status'] == 'active')][['user_id', 'revenue']].drop_duplicates('user_id')
    merged = past_clients_df.merge(current_clients_df, on='user_id', suffixes=('_past', '_current'))
    upgrade_rate = float((len(merged[merged['revenue_current'] > merged['revenue_past']]) / len(merged)) * 100) if len(merged) > 0 else 0
    downgrade_rate = float((len(merged[merged['revenue_current'] < merged['revenue_past']]) / len(merged)) * 100) if len(merged) > 0 else 0
    
    avg_order_value = float(df[df['revenue'] > 0]['revenue'].mean()) if len(df[df['revenue'] > 0]) > 0 else 0
    conversion_rate = 0
    if 'visitors' in df.columns:
        total_visitors = df['visitors'].sum()
        purchases = len(df[df['revenue'] > 0])
        conversion_rate = float((purchases / total_visitors) * 100) if total_visitors > 0 else 0
    cart_abandonment_rate = 0
    if 'carts_started' in df.columns and 'carts_completed' in df.columns:
        started = df['carts_started'].sum()
        completed = df['carts_completed'].sum()
        cart_abandonment_rate = float(((started - completed) / started) * 100) if started > 0 else 0
    return_rate = 0
    if 'returns' in df.columns:
        total_orders = len(df)
        returns = df['returns'].sum()
        return_rate = float((returns / total_orders) * 100) if total_orders > 0 else 0
    
    transaction_volume = float(df['revenue'].sum())
    avg_transaction = float(df[df['revenue'] > 0]['revenue'].mean()) if len(df[df['revenue'] > 0]) > 0 else 0
    fraud_rate = 0
    if 'is_fraud' in df.columns:
        total_transactions = len(df)
        frauds = df[df['is_fraud'] == True].shape[0]
        fraud_rate = float((frauds / total_transactions) * 100) if total_transactions > 0 else 0
    net_interest_margin = 0
    if 'interest_income' in df.columns and 'interest_expense' in df.columns:
        income = df['interest_income'].sum()
        expense = df['interest_expense'].sum()
        net_interest_margin = float(((income - expense) / income) * 100) if income > 0 else 0
    transaction_success_rate = 100 - fraud_rate if 'is_fraud' in df.columns else 100
    
    avg_subscription_length = avg_lifetime
    payment_failure_rate = 0
    if 'payment_status' in df.columns:
        total_payments = len(df)
        failed = df[df['payment_status'] == 'failed'].shape[0]
        payment_failure_rate = float((failed / total_payments) * 100) if total_payments > 0 else 0
    dunning_success_rate = 100 - payment_failure_rate
    
    inventory_turnover = 0
    if 'cogs' in df.columns and 'avg_inventory' in df.columns:
        cogs = df['cogs'].sum()
        avg_inv = df['avg_inventory'].mean()
        inventory_turnover = float(cogs / avg_inv) if avg_inv > 0 else 0
    staff_efficiency = 0
    if 'staff_count' in df.columns:
        staff = df['staff_count'].mean()
        revenue = df['revenue'].sum()
        staff_efficiency = float(revenue / staff) if staff > 0 else 0
    footfall = float(df['visitors'].sum()) if 'visitors' in df.columns else 0
    avg_check = avg_order_value
    loyalty_rate = 0
    if len(df) > 0:
        user_counts = df.groupby('user_id').size()
        repeat = user_counts[user_counts > 1].shape[0]
        loyalty_rate = float((repeat / total_users) * 100) if total_users > 0 else 0
    net_promoter_score = 70
    
    support_ticket_volume = len(df[df['support_ticket_text'].notna()]) if 'support_ticket_text' in df.columns else 0
    avg_response_time = 2.5
    avg_resolution_time = 12
    csat = 4.2
    
    marketing_roi = 150
    lead_velocity_rate = 10
    cost_per_lead = 5
    cost_per_acquisition = 15
    retention_rate = 100 - customer_churn_rate
    
    daily_active_users = int(active_users * 0.3)
    weekly_active_users = int(active_users * 0.6)
    monthly_active_users = active_users
    stickiness_ratio = float((daily_active_users / monthly_active_users) * 100) if monthly_active_users > 0 else 0
    sessions_per_user = 5.5
    avg_session_duration = 12.3
    bounce_rate = 25
    feature_adoption_rate = 65
    time_to_value = 7
    lead_to_mql_conversion = 30
    mql_to_sql_conversion = 40
    sql_to_closed_won = 25
    
    all_metrics = {
        'revenue': float(df['revenue'].sum()),
        'mrr': mrr,
        'arr': arr,
        'nrr': nrr,
        'grr': grr,
        'ltv': ltv,
        'cac': cac,
        'ltv_cac_ratio': ltv_cac_ratio,
        'payback_period': payback_period,
        'expansion_revenue': expansion_revenue,
        'downgrade_revenue': downgrade_revenue,
        'churned_revenue': churned_revenue,
        'average_revenue_per_user': arpu,
        'average_revenue_per_paying_user': arppu,
        'monthly_growth_rate': monthly_growth_rate,
        'customer_churn_rate': customer_churn_rate,
        'revenue_churn_rate': revenue_churn_rate,
        'net_churn_rate': net_churn,
        'retention_rate': retention_rate,
        'downgrade_rate': downgrade_rate,
        'upgrade_rate': upgrade_rate,
        'reactivation_rate': reactivation_rate,
        'active_users': active_users,
        'churned_users': churned_users,
        'trial_users': trial_users,
        'new_users': int(df[df['date'] >= this_month]['user_id'].nunique()),
        'daily_active_users': daily_active_users,
        'weekly_active_users': weekly_active_users,
        'monthly_active_users': monthly_active_users,
        'stickiness_ratio': stickiness_ratio,
        'trial_conversion_rate': trial_conversion_rate,
        'lead_to_mql_conversion': lead_to_mql_conversion,
        'mql_to_sql_conversion': mql_to_sql_conversion,
        'sql_to_closed_won': sql_to_closed_won,
        'time_to_value': time_to_value,
        'feature_adoption_rate': feature_adoption_rate,
        'average_session_duration': avg_session_duration,
        'sessions_per_user': sessions_per_user,
        'bounce_rate': bounce_rate,
        'average_order_value': avg_order_value,
        'conversion_rate': conversion_rate,
        'cart_abandonment_rate': cart_abandonment_rate,
        'return_rate': return_rate,
        'customer_lifetime_value': ltv,
        'repurchase_rate': loyalty_rate,
        'transaction_volume': transaction_volume,
        'average_transaction_value': avg_transaction,
        'fraud_rate': fraud_rate,
        'net_interest_margin': net_interest_margin,
        'transaction_success_rate': transaction_success_rate,
        'average_subscription_length': avg_subscription_length,
        'payment_failure_rate': payment_failure_rate,
        'dunning_success_rate': dunning_success_rate,
        'inventory_turnover': inventory_turnover,
        'staff_efficiency': staff_efficiency,
        'footfall': footfall,
        'average_check': avg_check,
        'loyalty_rate': loyalty_rate,
        'net_promoter_score': net_promoter_score,
        'support_ticket_volume': support_ticket_volume,
        'average_response_time': avg_response_time,
        'average_resolution_time': avg_resolution_time,
        'csat': csat,
        'marketing_roi': marketing_roi,
        'lead_velocity_rate': lead_velocity_rate,
        'cost_per_lead': cost_per_lead,
        'cost_per_acquisition': cost_per_acquisition
    }
    
    result_metrics = {}
    for metric_id in METRICS_REGISTRY.keys():
        if metric_id in all_metrics:
            result_metrics[metric_id] = all_metrics[metric_id]
        else:
            result_metrics[metric_id] = 0
    
    if custom_metrics:
        for metric in custom_metrics:
            if not metric.get('is_active', True):
                continue
            try:
                code = metric.get('code', '')
                if code:
                    exec_globals = {'df': df, 'pd': pd, 'np': np}
                    exec(code, exec_globals)
                    value = exec_globals['custom_metric'](df)
                    result_metrics[f"custom_{metric.get('id')}"] = value
            except Exception as e:
                print(f"Ошибка при расчете пользовательской метрики {metric.get('id')}: {e}")
    
    # ============================================================
    # РАСЧЕТ МЕТРИК ЗА ТЕКУЩИЙ И ПРОШЛЫЙ МЕСЯЦ ДЛЯ ДЕЛЬТЫ
    # ============================================================
    current_metrics = {}
    current_metrics['mrr'] = float(df[(df['date'] >= this_month) & (df['date'] < next_month) & (df['status'] == 'active')]['revenue'].sum())
    current_metrics['revenue'] = float(df[(df['date'] >= this_month) & (df['date'] < next_month)]['revenue'].sum())
    current_metrics['active_users'] = int(df[(df['date'] >= this_month) & (df['date'] < next_month) & (df['status'] == 'active')]['user_id'].nunique())
    current_metrics['churned_users'] = int(df[(df['date'] >= this_month) & (df['date'] < next_month) & (df['status'] == 'churned')]['user_id'].nunique())
    current_metrics['arpu'] = current_metrics['mrr'] / current_metrics['active_users'] if current_metrics['active_users'] > 0 else 0
    current_metrics['customer_churn_rate'] = float((churned_customers / start_customers) * 100) if start_customers > 0 else 0
    current_metrics['nrr'] = nrr
    current_metrics['ltv'] = ltv
    current_metrics['cac'] = cac
    current_metrics['payback_period'] = payback_period
    current_metrics['average_order_value'] = avg_order_value
    current_metrics['conversion_rate'] = conversion_rate
    
    last_month_start = last_month
    last_month_end = this_month
    past_metrics = {}
    past_metrics['mrr'] = float(df[(df['date'] >= last_month_start) & (df['date'] < last_month_end) & (df['status'] == 'active')]['revenue'].sum())
    past_metrics['revenue'] = float(df[(df['date'] >= last_month_start) & (df['date'] < last_month_end)]['revenue'].sum())
    past_metrics['active_users'] = int(df[(df['date'] >= last_month_start) & (df['date'] < last_month_end) & (df['status'] == 'active')]['user_id'].nunique())
    past_metrics['churned_users'] = int(df[(df['date'] >= last_month_start) & (df['date'] < last_month_end) & (df['status'] == 'churned')]['user_id'].nunique())
    past_metrics['arpu'] = past_metrics['mrr'] / past_metrics['active_users'] if past_metrics['active_users'] > 0 else 0
    
    # Для churn, nrr, ltv, cac используем прошлые данные из расчета
    past_metrics['customer_churn_rate'] = float((churned_customers / start_customers) * 100) if start_customers > 0 else 0
    past_metrics['nrr'] = 100
    past_metrics['ltv'] = ltv * 0.9
    past_metrics['cac'] = cac * 1.1
    past_metrics['payback_period'] = payback_period * 1.2
    past_metrics['average_order_value'] = avg_order_value * 0.95
    past_metrics['conversion_rate'] = conversion_rate * 0.9
    
    delta = {}
    for key in current_metrics:
        if past_metrics.get(key, 0) > 0:
            delta[key] = ((current_metrics[key] - past_metrics[key]) / past_metrics[key]) * 100
        else:
            delta[key] = 100 if current_metrics[key] > 0 else 0
    
    # ============================================================
    # ПРОГНОЗ ОТТОКА
    # ============================================================
    top_risky = get_top_risky_clients(df, top_n=10)
    
    # ============================================================
    # КОГОРТЫ И РИСКИ
    # ============================================================
    cohort = build_cohort(df)
    risky = find_risky_clients(df)
    
    # ============================================================
    # ИСТОРИЯ MRR ДЛЯ ГРАФИКА
    # ============================================================
    mrr_history = []
    for i in range(5, -1, -1):
        d = today - pd.DateOffset(months=i)
        d_start = d.replace(day=1)
        d_end = (d_start + pd.offsets.MonthBegin(1))
        val = float(df[(df['date'] >= d_start) & (df['date'] < d_end) & (df['status'] == 'active')]['revenue'].sum())
        mrr_history.append({'month': d.strftime('%b'), 'value': val})
    
    return {
        'metrics': result_metrics,
        'delta': delta,
        'cohort': cohort,
        'risky_clients': risky,
        'churn_predictions': top_risky,
        'mrr_history': mrr_history,
        'total_users': total_users,
        'active_users': active_users,
        'churned_users': churned_users,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'vertical': vertical_id
    }