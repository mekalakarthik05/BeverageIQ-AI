def is_valid_query(query: str) -> bool:
    """
    Validates if the user query is reasonably formed.
    """
    if not query or not isinstance(query, str):
        return False
    
    if len(query.strip()) < 3:
        return False
        
    return True
