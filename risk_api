from fastapi import FastAPI
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

app = FastAPI(title="Supply Chain Risk API")

# --- Load Data ---
imports_df = pd.read_csv(r"C:\Users\aishw\Downloads\Cleaned_U_S_Imports_from_2012.csv")
lpi_df = pd.read_csv(r"C:\Users\aishw\Downloads\Interpolated_LPI_2015-2024.csv")
wgi_df = pd.read_excel(r"C:\Users\aishw\Downloads\widget1.xlsx")
consumption_df = pd.read_excel(r"C:\Users\aishw\Downloads\demo_data_2015_2025.xlsx")

# --- Clean and Prepare WGI ---
wgi_df_cleaned = wgi_df[wgi_df["estimate"] != ".."].copy()
wgi_df_cleaned["estimate"] = pd.to_numeric(wgi_df_cleaned["estimate"], errors="coerce")
wgi_pivot = wgi_df_cleaned.pivot_table(
    index=["countryname", "year"],
    columns="indicator",
    values="estimate"
).reset_index()
wgi_pivot.columns.name = None
wgi_pivot = wgi_pivot.rename(columns={
    "countryname": "Country", "year": "Year",
    "cc": "WGI_ControlOfCorruption", "ge": "WGI_GovtEffectiveness",
    "rl": "WGI_RuleOfLaw", "rq": "WGI_RegulatoryQuality",
    "va": "WGI_VoiceAccountability", "pv": "WGI_PoliticalStability"
})

# --- Clean Other Data Sources ---
lpi_clean = lpi_df[["Country", "Year", "LPI_Score_Interpolated"]].rename(columns={"LPI_Score_Interpolated": "LPI_Score"})
imports_clean = imports_df[imports_df["Country"] != "World Total"].copy()
consumption_clean = consumption_df.rename(columns={
    "Year": "ConsumptionYear", "Commodity Type": "Commodity",
    "Overall Consumption Percentage": "ConsumptionPercentage"
})

# --- Merge All ---
merged = imports_clean.merge(lpi_clean, on=["Country", "Year"], how="left")
merged = merged.merge(wgi_pivot, on=["Country", "Year"], how="left")
merged = merged.merge(consumption_clean[["ConsumptionYear", "Commodity", "ConsumptionPercentage"]],
                      left_on=["Year", "Commodity"],
                      right_on=["ConsumptionYear", "Commodity"],
                      how="left")

# --- Filter Valid Rows ---
required_cols = [
    "ImportValueUSD", "LPI_Score",
    "WGI_ControlOfCorruption", "WGI_GovtEffectiveness", "WGI_PoliticalStability",
    "WGI_RuleOfLaw", "WGI_RegulatoryQuality", "WGI_VoiceAccountability"
]
filtered_df = merged.dropna(subset=required_cols).copy()

# --- Normalize Inputs ---
scaler = MinMaxScaler()
filtered_df["Norm_Imports"] = scaler.fit_transform(filtered_df[["ImportValueUSD"]])
filtered_df["Norm_LPI"] = 1 - scaler.fit_transform(filtered_df[["LPI_Score"]])
filtered_df["Norm_Consumption"] = scaler.fit_transform(filtered_df[["ConsumptionPercentage"]].fillna(0))

wgi_cols = [
    "WGI_ControlOfCorruption", "WGI_GovtEffectiveness", "WGI_PoliticalStability",
    "WGI_RuleOfLaw", "WGI_RegulatoryQuality", "WGI_VoiceAccountability"
]
for col in wgi_cols:
    filtered_df[f"Norm_{col}"] = 1 - scaler.fit_transform(filtered_df[[col]])

# --- Base Risk Score ---
filtered_df["BaseRiskScore"] = (
    filtered_df["Norm_Imports"] * 0.3 +
    filtered_df["Norm_Consumption"] * 0.2 +
    filtered_df["Norm_LPI"] * 0.1 +
    filtered_df[[f"Norm_{col}" for col in wgi_cols]].mean(axis=1) * 0.4
)

# --- Adjust by Market Share ---
filtered_df["CountryCommodityShare"] = (
    filtered_df.groupby(["Commodity", "Year"])["ImportValueUSD"]
    .transform(lambda x: x / x.sum())
)
filtered_df["AdjustedRiskScore"] = filtered_df["BaseRiskScore"] * filtered_df["CountryCommodityShare"]
filtered_df["RiskPercentage"] = (
    filtered_df.groupby(["Commodity", "Year"])["AdjustedRiskScore"]
    .transform(lambda x: x / x.sum()) * 100
).round(2)

# --- Final Output ---
final_df = filtered_df[["Country", "Year", "Commodity", "RiskPercentage"]]

# --- API Endpoints ---
@app.get("/top-risk-countries/")
def get_top_risks(commodity: str, year: int, top_n: int = 3):
    subset = final_df[(final_df["Commodity"] == commodity) & (final_df["Year"] == year)]
    if subset.empty:
        return {"error": "No data found for selected parameters."}
    top_risks = subset.sort_values(by="RiskPercentage", ascending=False).head(top_n)
    return {
        "commodity": commodity,
        "year": year,
        "top_risks": top_risks[["Country", "RiskPercentage"]].to_dict(orient="records")
    }

@app.get("/risk-score/")
def get_risk_for_all(commodity: str, year: int):
    subset = final_df[(final_df["Commodity"] == commodity) & (final_df["Year"] == year)]
    if subset.empty:
        return {"error": "No data found for selected parameters."}
    return {
        "commodity": commodity,
        "year": year,
        "all_countries": subset.sort_values(by="RiskPercentage", ascending=False)[["Country", "RiskPercentage"]].to_dict(orient="records")
    }
