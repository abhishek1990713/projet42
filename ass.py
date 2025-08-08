def is_continuation(current_text):
    """
    Returns True if the current text is the start or part of a broken URL,
    such as starting with http/https/www or being part of a domain (e.g., 'honeyw', 'ell.com').
    """
    current_text = current_text.strip()
    
    # If it starts with http or www
    if current_text.startswith("http") or current_text.startswith("www."):
        return True
    
    # If it's a partial domain (e.g., honeyw, ell.com, .com/us)
    if re.match(r'^[\w\.-]*\.(com|net|org|co|jp|in|gov|us|de|uk)(/.*)?$', current_text, re.IGNORECASE):
        return True
    
    # If it's a known broken URL fragment
    if re.match(r'^[\w-]+$', current_text) and len(current_text) > 3:
        return True
    
    return False
