import asyncio
import json
from fastmcp import FastMCP, Context
from enum import Enum

mcp = FastMCP("Travel-Booking-Agent")

class TripType(str, Enum):
    BUSINESS = "business"
    LEISURE = "leisure"
    FAMILY = "family"

DESTINATIONS = {
    "paris": {"name": "Paris, France", "flight": 450, "hotel": 180,
              "highlights": ["Eiffel Tower", "Louvre", "Notre-Dame"],
              "phrases": ["Bonjour", "Merci", "S'il vous plait"]},
    "tokyo": {"name": "Tokyo, Japan", "flight": 900, "hotel": 150,
              "highlights": ["Shibuya", "Senso-ji Temple", "Mt. Fuji day trip"],
              "phrases": ["Konnichiwa", "Arigato", "Sumimasen"]},
}

@mcp.resource("travel://destinations")
def list_destinations() -> str:
    """All available destinations with pricing."""
    return json.dumps({k: {"name": v["name"], "flight": v["flight"], "hotel": v["hotel"]}
                       for k, v in DESTINATIONS.items()}, indent=2)

@mcp.prompt()
def packing_list(destination: str, days: int, trip_type: str) -> str:
    """Generate packing list prompt."""
    return f"Create a {days}-day packing list for a {trip_type} trip to {destination}."

@mcp.tool()
async def plan_trip(ctx: Context) -> str:
    """Plan a complete trip using all MCP features."""
    dest_result = await ctx.elicit(message="Where would you like to go?\nOptions: Paris, Tokyo", response_type=str)
    if dest_result.action != "accept":
        return "Trip planning cancelled."
    dest_key = dest_result.data.lower().strip()
    dest = DESTINATIONS.get(dest_key, DESTINATIONS["paris"])
    days_result = await ctx.elicit(message="How many days? (3-14)", response_type=int)
    if days_result.action != "accept":
        return "Trip planning cancelled."
    days = max(3, min(14, days_result.data))
    total_steps = 5
    for step in range(1, total_steps + 1):
        await ctx.report_progress(progress=step, total=total_steps)
        await asyncio.sleep(0.4)
    flight_cost = dest["flight"]; hotel_cost = dest["hotel"] * days; total_cost = flight_cost + hotel_cost
    ai_tips = f"Enjoy {dest['name']}!"
    try:
        response = await ctx.sample(messages=f"Give 3 brief tips for a trip to {dest['name']}, {days} days. Max 60 words.", max_tokens=150)
        if hasattr(response, 'text') and response.text:
            ai_tips = response.text
    except Exception:
        ai_tips = f"Visit {dest['highlights'][0]}, try local food, learn basic phrases!"
    return f"BOOKING CONFIRMED! {dest['name']} {days} days TOTAL ${total_cost} TIPS {ai_tips}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, stateless_http=False)
