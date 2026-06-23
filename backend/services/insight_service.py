import os
from dotenv import load_dotenv
from google import genai

from backend.database.mongodb import db


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


async def get_segment_stats():

    pipeline = [
        {
            "$group": {
                "_id": "$segment",
                "count": {"$sum": 1}
            }
        }
    ]

    results = {}

    async for doc in db.user_segments.aggregate(pipeline):
        results[doc["_id"]] = doc["count"]

    return results



async def generate_insights():

    try:

        stats = await get_segment_stats()

        prompt = f"""
        Analyze this customer segmentation data.

        Customer segments:
        {stats}

        Provide:
        1. Important business insights
        2. Customer behavior patterns
        3. Marketing recommendations

        Keep it concise.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        return {
            "source": "gemini",
            "insights": response.text
        }


    except Exception as e:

        return {
            "source": "fallback",
            "insights": [
                "VIP customers contribute the highest revenue.",
                "Frequent buyers show strong purchase activity.",
                "Window shoppers require targeted marketing campaigns.",
                "Gaming category has high recent engagement."
            ],
            "error": str(e)
        }