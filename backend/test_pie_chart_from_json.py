import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from chat.pie_chart_generator import generate_all_pie_charts

with open("sample_pie_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

charts = generate_all_pie_charts(data)

print("Generated Pie Chart URLs:")
print(json.dumps(charts, indent=2))

print("\nOpen generated files from:")
print("backend/media/pie_charts/")
