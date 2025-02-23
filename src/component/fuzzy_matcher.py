from fuzzywuzzy import process

def fuzzy_match(value, choices, threshold=80):
    match, score = process.extractOne(value, choices)
    return match if score >= threshold else None
