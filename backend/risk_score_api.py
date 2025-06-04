from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd

router = APIRouter()


@router.get("/top-risk-countries")
async def get_top_risk_countries():
    data = [
        {"partner": "CountryA", "trade_value": 100, "dependency_pct": 0.6},
        {"partner": "CountryB", "trade_value": 80, "dependency_pct": 0.5},
        {"partner": "CountryC", "trade_value": 60, "dependency_pct": 0.75},
        {"partner": "CountryD", "trade_value": 30, "dependency_pct": 0.2},
    ]
    df = pd.DataFrame(data)
    df["political_risk_index"] = [1.2, 1.5, 1.0, 2.0]
    df["risk_score"] = df["dependency_pct"] * df["political_risk_index"]
    top_3 = df.sort_values(by="risk_score", ascending=False).head(3)

    return JSONResponse(
        content=top_3[["partner", "dependency_pct", "risk_score"]].to_dict(
            orient="records"
        )
    )
