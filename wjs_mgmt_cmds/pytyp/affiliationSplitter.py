"""Estrae il country da una stringa (che sia affiliazione)."""

import logging
import re
from collections import namedtuple
from argparse import Namespace
from core.models import Country
from .utils import normalizeString

Address = namedtuple("Address", ["country", "organization"])
logger = logging.getLogger(__name__)

# hmmm... sorting by length to avoid homonyms-like misses
# (e.g. "India" vs. "British Indian Ocean Territory")
# makes sense only if I search country_name in input_string,
# not viceversa.
#
# If I sort "by most frequently used country" do I get a performance
# increase?

country_names = sorted(
    Country.objects.values_list("name", flat=True), key=len, reverse=True
)
country_keys = {x.lower(): x for x in country_names}

# core.models.Country have a limited set of names.
# I must alias some.
# NB: delicate! We expect that the values of this dict are existing `Country.name`s!
aliases = {
    "aquila": "Italy",
    "brasil": "Brazil",
    "cern": "Switzerland",
    "desy": "Germany",
    "durham university": "United Kingdom",
    "fermilab": "United States",
    "kek": "Japan",
    "korea": "Korea, Republic of",
    "harvard university": "United States",
    "indiana": "United States",
    "iran": "Iran, Islamic Republic of",
    "italia": "Italy",
    "london": "United Kingdom",
    "méxico": "Mexico",
    "maroc": "Morocco",
    "moscow": "Russian Federation",
    "pr china": "China",
    "p.r. china": "China",
    "people's republic of china": "China",
    "perú": "Peru",
    "republic of korea": "Korea, Republic of",
    "roma": "Italy",
    "paris": "France",
    "sissa": "Italy",
    "sissa medialab": "Italy",
    "slovenija": "Slovenia",
    "stanford university": "United States",
    "the netherlands": "Netherlands",
    "tokyo": "Japan",
    "torino": "Italy",
    "toronto": "Canada",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "university of amsterdam": "Netherlands",
    "university of cambridge": "United Kingdom",
    "university of oxford": "United Kingdom",
    "usa": "United States",
    "u.s.a.": "United States",
    "vietnam": "Viet Nam",
    "zaragoza": "Spain",
}
alias_keys = sorted(aliases, key=len, reverse=True)


def find_country(normStr: str):
    """Find the Country in a string.

    Expects a "normalized" string (see function `normalizeString()`).
    Return a tuple of (Country, source_string).
    """
    # Trying different approach in order of perceived[*] computational
    # complexity.
    #
    # [*] "perceived" because I didn't do any test (yet) ;)

    # do all comparison case-insensitive
    normStr = normStr.lower()

    # step 1:
    # if last piece after split-at-comma is a known country or alias,
    # then use it
    candidate = normStr.split(",")[-1].strip().lower()
    if candidate in country_keys:
        return (Country.objects.get(name=country_keys[candidate]), candidate)
    if candidate in alias_keys:
        return (Country.objects.get(name=aliases.get(candidate)), candidate)

    # step 2:
    # if last piece after split-at-space is a known country or alias,
    # then use it
    candidate = normStr.split(" ")[-1].strip().lower()
    if candidate in country_keys:
        return (Country.objects.get(name=country_keys[candidate]), candidate)
    if candidate in alias_keys:
        return (Country.objects.get(name=aliases.get(candidate)), candidate)

    # step 3
    # step 3a:
    # sort known countries by length,
    # grep country in string
    for country_key in country_keys:
        # if country_key in normStr:  # NO! Indiana University -> India
        if re.search(rf"\b{country_key}\b", normStr):
            return (
                Country.objects.get(name=country_keys[country_key]),
                country_key,
            )

    # step 3b
    # sort known aliases by length,
    # grep alias in string
    for country_key in alias_keys:
        if country_key in normStr:
            return (
                Country.objects.get(name=aliases.get(country_key)),
                country_key,
            )

    # logger.warning('Cannot identify country in "%s".', normStr)
    return (None, None)


def splitCountry(string: str, options: Namespace = None) -> Address:
    """Trova la country nell'indirizzo."""
    if string is None or string.strip() == "":
        return Address(None, None)
    normStr = normalizeString(string)

    (country, source_string) = find_country(normStr)
    if country is None:
        return Address(None, None)
    assert source_string in normStr.lower()
    organization = normStr
    return Address(country, organization)
