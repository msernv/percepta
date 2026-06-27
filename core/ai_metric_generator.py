import re

KEYWORD_MAPPING = {
    'выручка': 'revenue', 'доход': 'revenue', 'платеж': 'revenue', 'сумма': 'revenue',
    'клиент': 'user_id', 'пользователь': 'user_id', 'юзер': 'user_id',
    'активный': 'status_active', 'активность': 'last_activity_date', 'статус': 'status',
    'отток': 'churn', 'ушел': 'churned', 'уход': 'churn',
    'чек': 'revenue', 'заказ': 'revenue', 'транзакция': 'revenue',
    'подписка': 'subscription', 'тариф': 'plan_type',
    'реклама': 'acquisition_channel', 'канал': 'acquisition_channel', 'источник': 'acquisition_channel',
    'дата': 'date', 'месяц': 'date', 'год': 'date',
    'регион': 'region', 'город': 'region',
    'категория': 'category', 'товар': 'product_name', 'продукт': 'product_name'
}

AGGREGATION_PATTERNS = {
    'сумма': 'sum', 'всего': 'sum', 'общая': 'sum', 'общий': 'sum',
    'средний': 'mean', 'средняя': 'mean', 'среднее': 'mean',
    'количество': 'count', 'сколько': 'count', 'кол-во': 'count',
    'максимальный': 'max', 'максимальная': 'max', 'самый большой': 'max',
    'минимальный': 'min', 'минимальная': 'min', 'самый маленький': 'min',
    'процент': 'percentage', '%': 'percentage', 'доля': 'percentage'
}

FILTER_PATTERNS = {
    'активный': ('status', 'active'), 'активные': ('status', 'active'),
    'платящий': ('status', 'active'), 'платящие': ('status', 'active'),
    'ушел': ('status', 'churned'), 'ушедшие': ('status', 'churned'), 'ушедших': ('status', 'churned'),
    'отписался': ('status', 'churned'), 'отписавшиеся': ('status', 'churned'),
    'новый': ('status', 'new'), 'новые': ('status', 'new'),
    'триал': ('status', 'trial'), 'пробный': ('status', 'trial'), 'бесплатный': ('status', 'trial')
}

def create_metric_from_query(query):
    query_lower = query.lower()
    # Определяем агрегацию
    aggregation = 'sum'
    for keyword, agg_type in AGGREGATION_PATTERNS.items():
        if keyword in query_lower:
            aggregation = agg_type
            break
    # Определяем целевую колонку
    target_column = 'revenue'
    for keyword, column in KEYWORD_MAPPING.items():
        if keyword in query_lower:
            target_column = column
            break
    # Определяем фильтры
    filters = []
    for keyword, (column, value) in FILTER_PATTERNS.items():
        if keyword in query_lower:
            filters.append({'column': column, 'operator': '==', 'value': value})
    # Определяем группировку
    group_by = None
    group_keywords = ['по', 'в разрезе', 'группировка', 'каждый', 'каждому']
    for kw in group_keywords:
        if kw in query_lower:
            for keyword, column in KEYWORD_MAPPING.items():
                if keyword in query_lower and column not in ['revenue', 'user_id']:
                    group_by = column
                    break
            if not group_by:
                group_by = 'user_id'
            break
    # Генерируем описание
    agg_names = {'sum': 'сумма', 'mean': 'среднее значение', 'count': 'количество', 'max': 'максимальное значение', 'min': 'минимальное значение', 'percentage': 'процент'}
    col_names = {'revenue': 'выручки', 'user_id': 'пользователей', 'status': 'статус', 'last_activity_date': 'даты активности'}
    agg_name = agg_names.get(aggregation, aggregation)
    col_name = col_names.get(target_column, target_column)
    desc = f"Расчет {agg_name} {col_name}"
    if filters:
        filter_desc = ", ".join([f"{f['column']} = {f['value']}" for f in filters])
        desc += f" с условием: {filter_desc}"
    if group_by:
        desc += f", сгруппировано по {group_by}"
    # Генерируем название
    words = query.split()[:5]
    name = ' '.join(words)
    if len(name) > 30:
        name = name[:30] + '...'
    name = name.capitalize()
    # Генерируем код
    code_lines = []
    code_lines.append("def custom_metric(df):")
    code_lines.append("    \"\"\"")
    code_lines.append(f"    {desc}")
    code_lines.append("    \"\"\"")
    filter_str = ""
    for f in filters:
        if f['operator'] == '==':
            filter_str += f"df['{f['column']}'] == '{f['value']}'"
    if filter_str:
        code_lines.append(f"    filtered_df = df[{filter_str}]")
    else:
        code_lines.append("    filtered_df = df")
    if aggregation == 'sum':
        code_lines.append(f"    result = filtered_df['{target_column}'].sum()")
    elif aggregation == 'mean':
        code_lines.append(f"    result = filtered_df['{target_column}'].mean()")
    elif aggregation == 'count':
        code_lines.append(f"    result = len(filtered_df['{target_column}'])")
    elif aggregation == 'max':
        code_lines.append(f"    result = filtered_df['{target_column}'].max()")
    elif aggregation == 'min':
        code_lines.append(f"    result = filtered_df['{target_column}'].min()")
    elif aggregation == 'percentage':
        code_lines.append("    total = df['{target_column}'].sum()")
        code_lines.append("    if total == 0:")
        code_lines.append("        return 0.0")
        code_lines.append(f"    result = (filtered_df['{target_column}'].sum() / total) * 100")
    else:
        code_lines.append(f"    result = filtered_df['{target_column}'].{aggregation}()")
    code_lines.append("    return float(result)")
    code = '\n'.join(code_lines)
    parsed = {'query': query, 'aggregation': aggregation, 'target_column': target_column, 'filters': filters, 'group_by': group_by, 'description': desc, 'name': name}
    return parsed, code