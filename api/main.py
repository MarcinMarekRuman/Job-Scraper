from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(
    title="Python Jobs Market API",
    description="API z danymi o ofertach pracy dla Python developerów z NoFluffJobs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv("data/jobs.csv")
df["salary_avg"] = (df["salary_from"] + df["salary_to"]) / 2
df["city"] = df["city"].fillna("Remote")
df["seniority"] = df["seniority"].fillna("Nieznany")


@app.get("/")
def root():
    return {
        "message": "Python Jobs Market API",
        "endpoints": ["/jobs", "/stats", "/docs"]
    }


@app.get("/jobs")
def get_jobs(
    city: str = Query(None, description="Filtruj po mieście, np. Warszawa"),
    seniority: str = Query(None, description="Filtruj po seniority: Mid, Senior"),
    remote: bool = Query(None, description="Tylko oferty remote: true/false"),
    min_salary: float = Query(None, description="Minimalne wynagrodzenie od"),
    max_salary: float = Query(None, description="Maksymalne wynagrodzenie do"),
):
    result = df.copy()

    if city:
        result = result[result["city"].str.contains(city, case=False, na=False)]
    if seniority:
        result = result[result["seniority"].str.contains(seniority, case=False, na=False)]
    if remote is not None:
        result = result[result["remote"] == remote]
    if min_salary:
        result = result[result["salary_from"] >= min_salary]
    if max_salary:
        result = result[result["salary_to"] <= max_salary]

    return {
        "count": len(result),
        "jobs": result.to_dict(orient="records")
    }


@app.get("/stats")
def get_stats():
    return {
        "total_jobs":      len(df),
        "avg_salary_b2b":  round(df["salary_avg"].mean(), 0),
        "median_salary":   round(df["salary_avg"].median(), 0),
        "min_salary":      round(df["salary_from"].min(), 0),
        "max_salary":      round(df["salary_to"].max(), 0),
        "top_cities":      df["city"].value_counts().head(5).to_dict(),
        "seniority_split": df["seniority"].value_counts().to_dict(),
        "remote_count":    int(df["remote"].sum()),
    }


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = df[df["id"] == job_id]
    if job.empty:
        return {"error": "Nie znaleziono oferty"}
    return job.to_dict(orient="records")[0]