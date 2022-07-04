"""Utility functions.

Kept in a separate module, so that pytest does not need DB access when
importing from this module.
"""

import re


def normalizeString(string: str) -> str:
    """Normalizza la stringa facendo pulizia."""
    string = string.replace("–", "-")  # EN DASH
    # string = string.replace("-", "-")  # HYPHEN-MINUS
    string = re.sub("[\n();,-]", ", ", string)  # most delimiters to ", "
    string = string.replace("\xa0", " ")  # spazi non secabili
    string = string.replace("’", "'")  # RIGHT SINGLE QUOTATION MARK to APOSTROPHE
    string = re.sub(r"\s+,", ",", string)  # no space before ","
    string = re.sub(r"\s+", " ", string)  # no multiple spaces
    string = re.sub(r",,+", ",", string)  # no multiple commas
    string = re.sub(r"^[ ,.]+", "", string)  # no comma or period at the beginning
    string = re.sub(r"[ ,.]+$", "", string)  # no comma or period at the end
    string = string.strip()
    # # Capitalize Each Piece
    # # This is in the hope of normalizing all-upper/lowercase strings,
    # # but it breaks transliteration of oriental names and Irish names
    # # e.g.: HochiMinh City, McGill University
    # string = " ".join(map(str.capitalize, string.split()))
    # string = string.replace(" Of ", " of ")  # "of" is always lowercase
    return string
