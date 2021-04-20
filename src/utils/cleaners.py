import re


# clean stock symbols to only upper case letters
def clean_symbol(s: str):
    return re.sub(r"[^A-Z]", "", s.upper())
