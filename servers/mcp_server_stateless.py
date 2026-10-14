import json
import logging
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Configure logging
UTC = timezone.utc
logging.Formatter.formatTime = lambda self, record, datefmt=None: datetime.fromtimestamp(record.created, UTC).isoformat(timespec='milliseconds')
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configuration
SERVER_NAME = "Kyoto Travel Tools"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Create a MCP Server using the FastMCP
mcp = FastMCP(name=SERVER_NAME, host=SERVER_HOST, port=SERVER_PORT, stateless_http=True)


# Tools
@mcp.tool()
def search_kyoto_attractions(interests: list[str]) -> str:
    """
    Search for Kyoto attractions based on interests

    Args:
        interests: List of interests (such as temples, gardens, food, culture)

    Returns:
        Recommended Kyoto attractions
    """
    logger.info(f"Tool called: search_kyoto_attractions")

    attractions = {
        "temples": "Kinkaku-ji (Golden Pavilion), Fushimi Inari Taisha, Kiyomizu-dera",
        "gardens": "Ryoan-ji Zen Garden, Arashiyama Bamboo Grove, Philosopher's Path",
        "food": "Nishiki Market, Gion district restaurants, Traditional kaiseki",
        "culture": "Gion Geisha district, Tea ceremony experiences, Traditional crafts workshops"
    }

    results = []
    for interest in interests:
        if interest.lower() in attractions:
            results.append(f"{interest.title()}: {attractions[interest.lower()]}")

    return "\n".join(results) if results else "No attractions found for specified interests"


# Resources
@mcp.resource("file:///travel/kyoto_preferences.json")
def get_kyoto_travel_preferences() -> str:
    """User's Kyoto travel preferences"""
    return '''{
        "preferredAirline": "JAL",
        "interests": ["temples", "gardens", "food"],
        "accommodationType": "ryokan",
        "dietaryRestrictions": ["vegetarian"]
    }'''


# Prompts
@mcp.prompt()
def plan_kyoto_trip(duration: int, budget: float = None, focus: str = "temples") -> list[TextContent]:
    """
    Guide through Kyoto trip planning process
    """
    budget_text = f" with a budget of {budget:,.0f} JPY" if budget else ""
    return [
        TextContent(
            type="text",
            text=f"Help me plan a {duration}-day trip to Kyoto{budget_text}, focusing on {focus}."
        )
    ]

if __name__ == "__main__":
    logger.info(f"Starting MCP server on {SERVER_HOST}:{SERVER_PORT}")
    mcp.run(transport="streamable-http")
