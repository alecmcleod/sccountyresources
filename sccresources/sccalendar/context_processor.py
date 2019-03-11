import os

def get_google_captcha_public_credentials():
    """Return path to credentials or raise ValueError"""
    try:
        return os.environ['GOOGLE_CAPTCHA_PUBLIC_KEY']
    except KeyError:
        raise ValueError('Set GOOGLE_CAPTCHA_PUBLIC_KEY to allow Google captcha to function')

def add_variables_to_context(request):
    return {
        'CAPTCHA_PUBLIC_KEY': get_google_captcha_public_credentials()
    }