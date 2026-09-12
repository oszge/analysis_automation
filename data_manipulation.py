import pandas as pd
import analysis_automation.database as database

data = database.load_sales()

##DATA CLEANING
data["sale_date"] = pd.to_datetime(data["sale_date"])
latest_date = data["sale_date"].max()

#WEEKLY DATA CLEANING
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

## MONTHLY DATA FILTERING

current_month_start = latest_date.replace(day=1)

previous_month_end = current_month_start - pd.Timedelta(days=1)
previous_month_start = previous_month_end.replace(day=1)

current_month = data[
    (data["sale_date"] >= current_month_start) &
    (data["sale_date"] <= latest_date)
]

previous_month = data[
    (data["sale_date"] >= previous_month_start) &
    (data["sale_date"] <= previous_month_end)
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

#WEEKLY KPIS
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

#MONTHLY KPIS
current_month_revenue = current_month["revenue"].sum()
previous_month_revenue = previous_month["revenue"].sum()

if previous_month_revenue != 0:
    monthly_revenue_change = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
else:
    monthly_revenue_change = None

current_month_units = current_month["quantity"].sum()
previous_month_units = previous_month["quantity"].sum()

current_month_transactions = len(current_month)
previous_month_transactions = len(previous_month)

current_month_category_revenue = current_month.groupby("category")["revenue"].sum()

best_monthly_category = current_month_category_revenue.idxmax()
best_monthly_category_revenue = current_month_category_revenue.max()

current_month_country_revenue = current_month.groupby("country")["revenue"].sum()

best_monthly_country = current_month_country_revenue.idxmax()
best_monthly_country_revenue = current_month_country_revenue.max()

## CATEGORY / COUNTRY / PRODUCT MONTHLY TREND COMPARISON

# CATEGORY COMPARISON
current_category_revenue = current_month.groupby("category")["revenue"].sum()
previous_category_revenue = previous_month.groupby("category")["revenue"].sum()

category_comparison = pd.DataFrame({
    "current_revenue": current_category_revenue,
    "previous_revenue": previous_category_revenue
}).fillna(0)

category_comparison["change_percent"] = (
    (category_comparison["current_revenue"] - category_comparison["previous_revenue"])
    / category_comparison["previous_revenue"]
    * 100
)
category_comparison["change_value"] = (
    category_comparison["current_revenue"]
    - category_comparison["previous_revenue"]
)

category_comparison["current_revenue"] = category_comparison["current_revenue"].round(2)
category_comparison["previous_revenue"] = category_comparison["previous_revenue"].round(2)
category_comparison["change_percent"] = category_comparison["change_percent"].round(2)
category_comparison["change_value"] = category_comparison["change_value"].round(2)

category_comparison = category_comparison.sort_values(
    "change_percent",
    ascending=False
)


# COUNTRY COMPARISON
current_country_revenue = current_month.groupby("country")["revenue"].sum()
previous_country_revenue = previous_month.groupby("country")["revenue"].sum()

country_comparison = pd.DataFrame({
    "current_revenue": current_country_revenue,
    "previous_revenue": previous_country_revenue
}).fillna(0)

country_comparison["change_percent"] = (
    (country_comparison["current_revenue"] - country_comparison["previous_revenue"])
    / country_comparison["previous_revenue"]
    * 100
)
country_comparison["change_value"] = (
    country_comparison["current_revenue"]
    - country_comparison["previous_revenue"]
)

country_comparison["current_revenue"] = country_comparison["current_revenue"].round(2)
country_comparison["previous_revenue"] = country_comparison["previous_revenue"].round(2)
country_comparison["change_percent"] = country_comparison["change_percent"].round(2)
country_comparison["change_value"] = country_comparison["change_value"].round(2)

country_comparison = country_comparison.sort_values(
    "change_percent",
    ascending=False
)



# PRODUCT COMPARISON
current_product_revenue = current_month.groupby("product")["revenue"].sum()
previous_product_revenue = previous_month.groupby("product")["revenue"].sum()

product_comparison = pd.DataFrame({
    "current_revenue": current_product_revenue,
    "previous_revenue": previous_product_revenue
}).fillna(0)

product_comparison["change_percent"] = (
    (product_comparison["current_revenue"] - product_comparison["previous_revenue"])
    / product_comparison["previous_revenue"]
    * 100
)
product_comparison["change_value"] = (
    product_comparison["current_revenue"]
    - product_comparison["previous_revenue"]
)

product_comparison["current_revenue"] = product_comparison["current_revenue"].round(2)
product_comparison["previous_revenue"] = product_comparison["previous_revenue"].round(2)
product_comparison["change_percent"] = product_comparison["change_percent"].round(2)
product_comparison["change_value"] = product_comparison["change_value"].round(2)

product_comparison = product_comparison.sort_values(
    "change_percent",
    ascending=False
)

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

monthly_kpis = {
    "period_start": current_month_start.strftime("%Y-%m-%d"),
    "period_end": latest_date.strftime("%Y-%m-%d"),

    "current_revenue": round(float(current_month_revenue), 2),
    "previous_revenue": round(float(previous_month_revenue), 2),

    "revenue_change_percent": (
        round(float(monthly_revenue_change), 2)
        if monthly_revenue_change is not None
        else None
    ),

    "current_units": int(current_month_units),
    "previous_units": int(previous_month_units),

    "current_transactions": int(current_month_transactions),
    "previous_transactions": int(previous_month_transactions),

    "best_category": best_monthly_category,
    "best_category_revenue": round(float(best_monthly_category_revenue), 2),

    "best_country": best_monthly_country,
    "best_country_revenue": round(float(best_monthly_country_revenue), 2)
}


print("KPIs")
print(kpis)
print("Weekly KPIs")
print(weekly_kpis)
print("Monthly KPIs")
print(monthly_kpis)

print("\nCategory Comparison")
print(category_comparison)
print("\nCountry Comparison")
print(country_comparison)
print("\nProduct Comparison")
print(product_comparison)