import pandas as pd
import db

data = db.load_sales()

##DATA CLEANING
data["sale_date"] = pd.to_datetime(data["sale_date"])
latest_date = data["sale_date"].max()

current_week_start = latest_date - pd.Timedelta(days=6)

current_week = data[
    (data["sale_date"] >= current_week_start) &
    (data["sale_date"] <= latest_date)
]

previous_week_end = current_week_start - pd.Timedelta(days=1)
previous_week_start = previous_week_end - pd.Timedelta(days=6)

previous_week = data[
    (data["sale_date"] >= previous_week_start) &
    (data["sale_date"] <= previous_week_end)
]


##DATA PROCESSING
total_revenue = data["revenue"].sum()
total_units = data["quantity"].sum()
total_transactions = len(data)

revenue_by_category = data.groupby("category")["revenue"].sum()
revenue_by_country = data.groupby("country")["revenue"].sum()
revenue_by_product = data.groupby("product")["revenue"].sum()

best_category = revenue_by_category.idxmax()
best_country = revenue_by_country.idxmax()
best_product = revenue_by_product.idxmax()


current_week_revenue = current_week["revenue"].sum()
previous_week_revenue = previous_week["revenue"].sum()
if previous_week_revenue != 0:
    weekly_revenue_change = ((current_week_revenue - previous_week_revenue) / previous_week_revenue) * 100
else:
    weekly_revenue_change = None

current_week_units = current_week["quantity"].sum()
previous_week_units = previous_week["quantity"].sum()

current_week_transactions = len(current_week)
previous_week_transactions = len(previous_week)

current_week_category_revenue = current_week.groupby("category")["revenue"].sum()

best_weekly_category = current_week_category_revenue.idxmax()
best_weekly_category_revenue = current_week_category_revenue.max()

current_week_country_revenue = current_week.groupby("country")["revenue"].sum()

best_weekly_country = current_week_country_revenue.idxmax()
best_weekly_country_revenue = current_week_country_revenue.max()


##DATA VISUALIZATION
kpis = {
    "total_revenue": round(float(total_revenue), 2),
    "total_units": int(total_units),
    "total_transactions": int(total_transactions),
    "best_category": best_category,
    "best_country": best_country,
    "best_product": best_product
}

weekly_kpis = {
    "period_start": current_week_start.strftime("%Y-%m-%d"),
    "period_end": latest_date.strftime("%Y-%m-%d"),

    "current_revenue": round(float(current_week_revenue), 2),
    "previous_revenue": round(float(previous_week_revenue), 2),

    "revenue_change_percent": (
        round(float(weekly_revenue_change), 2)
        if weekly_revenue_change is not None
        else None
    ),

    "current_units": int(current_week_units),
    "previous_units": int(previous_week_units),

    "current_transactions": int(current_week_transactions),
    "previous_transactions": int(previous_week_transactions),

    "best_category": best_weekly_category,
    "best_category_revenue": round(float(best_weekly_category_revenue), 2),

    "best_country": best_weekly_country,
    "best_country_revenue": round(float(best_weekly_country_revenue), 2)
}

print("KPIs")
print(kpis)
print("Weekly KPIs")
print(weekly_kpis)