import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from chat.market_chart import generate_market_trend_chart

with open("sample_market_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

chart_url, growth_summary = generate_market_trend_chart(data)

print("Chart URL:", chart_url)
print("Growth Summary:", growth_summary)
