

def header(header: str):
    return header if str(header).startswith("<") and str(header).endswith(">") else f'"{header}"'
