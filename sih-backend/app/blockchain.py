# --- keep your imports and BlueCarbonClient definition above ---

# Lazy / optional initialization
import os

_bluecarbon_client = None  # private singleton

def get_blockchain_client():
    """
    Return a singleton BlueCarbonClient if ENABLE_BLOCKCHAIN=1,
    otherwise return None (so the app can run without chain).
    """
    global _bluecarbon_client
    if os.getenv("ENABLE_BLOCKCHAIN", "0") != "1":
        return None
    if _bluecarbon_client is None:
        _bluecarbon_client = BlueCarbonClient()
    return _bluecarbon_client

# Backwards compatible name (for older imports, won’t connect until asked)
bluecarbon_client = get_blockchain_client()

