import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


class BusinessAnalysis(BaseModel):
    currency: str = "EUR"
    executive_summary: str
    key_insights: list[str]
    risks: list[str]
    recommendations: list[str]


def analyze_with_ai(analysis_data):
    analysis_json = json.dumps(analysis_data, indent=4)

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You are a business intelligence analyst.

Analyse the provided sales KPIs and trend data.

Rules:
- All monetary amounts are in EUR (euros). Label every monetary amount with EUR; do not convert values. Percentages and counts are not currency.
- Only use the supplied data.
- Never invent numbers.
- Do not modify the supplied financial values.
- Use both percentage change and absolute change when relevant.
- Identify the main drivers of revenue growth and decline.
- Pay attention to unusually large percentage changes caused by a small previous-period baseline.
- Highlight meaningful business risks.
- Provide practical recommendations.
- Keep the analysis concise and business-focused.
- Do not calculate or introduce new numeric values that are not explicitly present in the supplied data.
- You may compare and interpret supplied values, but every number in your response must come directly from the provided input.
"""
            },
            {
                "role": "user",
                "content": analysis_json
            }
        ],
        text_format=BusinessAnalysis
    )

    return response.output_parsed

