from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from query_functions import query_handling_using_LLM_updated  

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Request body
class QueryRequest(BaseModel):
    query: str

# Response model
class Assessment(BaseModel):
    assessment_name: str
    url: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]
    skills: List[str]  

class RecommendationResponse(BaseModel):
    recommended_assessments: List[Assessment]

@app.post("/recommend", response_model=RecommendationResponse)
def recommend_assessments(request: QueryRequest):
    try:
        df: pd.DataFrame = query_handling_using_LLM_updated(request.query)

        if df.empty:
            raise HTTPException(status_code=404, detail="No assessments found.")

        results = []

        for _, row in df.iterrows():
            results.append({
                "assessment_name": row["Assessment Name"],
                "url": row["URL"],
                "adaptive_support": row["Adaptive/IRT"],
                "description": row["Description"],
                "duration": int(row["Duration"]),
                "remote_support": row["Remote Testing Support"],
                "test_type": row["Test Type"] if isinstance(row["Test Type"], list) else [row["Test Type"]],
                "skills": row["Skills"] if isinstance(row["Skills"], list) else [skill.strip() for skill in str(row["Skills"]).split(",")]
            })

        return {"recommended_assessments": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
