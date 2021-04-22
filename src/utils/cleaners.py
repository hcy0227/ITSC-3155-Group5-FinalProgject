import re


# clean stock symbols to only upper case letters
def clean_symbol(s: str):
    return re.sub(r"[^A-Z]", "", s.upper())


# clean stock name to remove extra words after company name
def clean_stock_name(name: str) -> str:
    endings = ["Inc", "Company", "Corp", "Limited"]
    for e in endings:
        i = name.find(e)
        if i != -1:
            name = name[:i + len(e)]
    return name.strip()
