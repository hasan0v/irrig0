import functools
from flask import session, redirect, url_for, flash, request

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            # Assuming 'login' is the endpoint name for the login view in app.py
            return redirect(url_for('login', next=request.url)) # Pass next URL for redirect after login
        return view(**kwargs)
    return wrapped_view
