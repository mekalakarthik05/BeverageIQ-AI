import re

# Simple keyword-based intent detection
INTENTS = {
    "sales": ["sales", "sold", "volume", "units"],
    "revenue": ["revenue", "turnover", "income", "money", "earned"],
    "inventory": ["inventory", "stock", "stockout", "received", "opening", "closing"],
    "promotion": ["promotion", "promo", "discount", "offer"],
    "top_products": ["top selling", "best selling", "top products", "most popular", "highest"],
    "bottom_products": ["worst selling", "bottom products", "lowest", "worst"],
    "trend": ["trend", "weekly", "monthly", "over time", "history"],
    "comparison": ["compare", "vs", "versus"]
}

def detect_intent(query: str) -> str:
    """
    Detects the main analytical intent from the user query.
    Defaults to 'sales' if no specific intent is found.
    """
    query = query.lower()
    
    # Check for specific intents
    for intent, keywords in INTENTS.items():
        if any(keyword in query for keyword in keywords):
            return intent
            
    return "sales" # Default intent

def extract_entities(query: str) -> dict:
    """
    Extracts potential entities (like regions or categories) from the query.
    This is a basic regex/keyword implementation suitable for the assessment.
    """
    query_lower = query.lower()
    entities = {
        "regions": [],
        "categories": [],
        "limit": None
    }
    
    # Regions
    for region in ["north", "south", "east", "west"]:
        if region in query_lower:
            entities["regions"].append(region.capitalize())
            
    # Categories
    for cat in ["carbonated", "juice", "water", "energy"]:
        if cat in query_lower:
            entities["categories"].append(cat.capitalize())
            
    # Limits (e.g., top 5)
    limit_match = re.search(r'top (\d+)|bottom (\d+)|limit (\d+)', query_lower)
    if limit_match:
        # Extract the first non-None group
        for group in limit_match.groups():
            if group:
                entities["limit"] = int(group)
                break
                
    return entities
