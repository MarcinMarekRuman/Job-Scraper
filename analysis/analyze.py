import pandas as pd
import plotly.express as px


df = pd.read_csv("data/jobs.csv")
print(f"Wczytano {len(df)} ofert\n")

df["salary_avg"] = (df["salary_from"] + df["salary_to"]) / 2
df["city"] = df["city"].fillna("Remote")
df["seniority"] = df["seniority"].fillna("Nieznany")
df = df.dropna(subset=["salary_from", "salary_to"])

seniority_counts = df["seniority"].value_counts().reset_index()
seniority_counts.columns = ["seniority", "count"]

fig1 = px.bar(
    seniority_counts,
    x="seniority", y="count",
    title="Liczba ofert Python według seniority",
    color="seniority",
    text="count",
)
fig1.write_html("analysis/chart_seniority.html")
print("Zapisano: chart_seniority.html")

salary_by_seniority = df.groupby("seniority")["salary_avg"].mean().reset_index()
salary_by_seniority.columns = ["seniority", "avg_salary"]
salary_by_seniority = salary_by_seniority.sort_values("avg_salary", ascending=False)

fig2 = px.bar(
    salary_by_seniority,
    x="seniority", y="avg_salary",
    title="Średnie wynagrodzenie B2B (PLN/mies.) według seniority",
    color="seniority",
    text=salary_by_seniority["avg_salary"].round(0).astype(int),
)
fig2.write_html("analysis/chart_salary_seniority.html")
print("Zapisano: chart_salary_seniority.html")

city_counts = df["city"].value_counts().head(10).reset_index()
city_counts.columns = ["city", "count"]

fig3 = px.bar(
    city_counts,
    x="count", y="city",
    orientation="h",
    title="Top 10 miast z ofertami Python",
    text="count",
)
fig3.write_html("analysis/chart_cities.html")
print("Zapisano: chart_cities.html")

fig4 = px.box(
    df,
    x="seniority", y="salary_avg",
    title="Rozkład wynagrodzeń Python według seniority",
    color="seniority",
    points="all",
)
fig4.write_html("analysis/chart_salary_box.html")
print("Zapisano: chart_salary_box.html")

print("\n=== PODSUMOWANIE ===")
print(f"Ofert z podanym wynagrodzeniem: {len(df)}")
print(f"\nŚrednie wynagrodzenie B2B: {df['salary_avg'].mean():.0f} PLN/mies.")
print(f"Mediana: {df['salary_avg'].median():.0f} PLN/mies.")
print(f"Min: {df['salary_from'].min():.0f} PLN")
print(f"Max: {df['salary_to'].max():.0f} PLN")
print(f"\nTop 5 miast:\n{df['city'].value_counts().head()}")
print(f"\nRozkład seniority:\n{df['seniority'].value_counts()}")