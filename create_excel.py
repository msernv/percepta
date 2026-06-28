import pandas as pd

# Читаем CSV
df = pd.read_csv('static/sample_data.csv')

# Сохраняем как Excel
df.to_excel('static/sample_data.xlsx', index=False)
print("✅ Excel-файл создан: static/sample_data.xlsx")