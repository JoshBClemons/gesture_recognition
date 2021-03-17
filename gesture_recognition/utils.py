import time
from flask import url_for as _url_for, current_app, _request_ctx_stack

def timestamp():
    """Return the current timestamp as an integer."""
    
    return int(time.time())