"""Estrae il country da una stringa (che sia affiliazione)."""

import pytest
import logging
import re
import json
from pathlib import Path
from typing import TypedDict, NewType
from pylatexenc.latex2text import LatexNodes2Text as PL
from pylatexenc.latexencode import (
    UnicodeToLatexEncoder,
    UnicodeToLatexConversionRule,
    RULE_REGEX,
)


# In questo modo possiamo insegnare allo script le sostituzioni UTF-8
# che non è in grado di fare.
UL = UnicodeToLatexEncoder(
    conversion_rules=[
        UnicodeToLatexConversionRule(
            rule_type=RULE_REGEX,
            rule=[
                (re.compile(r"ȧ"), r"\.{a}"),
            ],
        ),
        "defaults",
    ]
)


class dictCountry(TypedDict):
    """Dict per indirizzo: address, country, other."""

    address: str
    country: str
    other: str


nString = NewType("Normalized String", str)

logger = logging.getLogger(__name__)
myDict = Path(__file__).parent / "country.json"
with open(myDict, "r") as f:
    countries = json.load(f)


def splitCountry(string: str) -> dictCountry:
    """Trova la country nell'indirizzo."""
    if string is None or string.strip() == '':
        return {'country': '', 'address': '', 'other': ''}
    normStr = normalizeString(string, latex=False)
    affStr = correctString(normStr)
    splitted = affStr.split(",")
    if affStr == "":
        logger.critical("Passed empty (or equivalent) string. Please check...")
        return {"country": "", "address": "", "other": ""}
    guess = 0
    address = string
    country = ""
    other = ""
    if len(splitted) < 2:
        # Troppi pochi pezzi o troppo corto
        logger.warning(
            'Not enough pieces for country in "%s"',
            string,
        )
        return {"country": country, "address": normStr, "other": other}
    # Cerca all'interno del database degli stati
    while (
        country not in countries["names"]
        and country not in countries["aliases"]
    ):
        guess = guess - 1
        try:
            country = splitted[guess]
        except IndexError:  # as error:
            logger.error(
                'Cannot find a country in my internal dictionary for "%s"'
                " (could be in cluster). May need manual info...",
                string,
            )
            return dict(country="", address=address, other="")
            # raise error
            # return ask4suggestion(normStr)
    address = ", ".join(splitted[:guess])
    other = r", ".join(splitted[len(splitted) + guess + 1:])
    return {"country": country, "address": address, "other": other}


def normalizeString(string: str, latex: bool = True) -> nString:
    """Normalizza la stringa facendo pulizia."""
    norm = PL().latex_to_text(string)
    # Rimozione egli spazi non secabili
    norm = norm.replace("\xa0", " ")
    # Stripping e pulizie
    norm = re.sub(r"(\w\)*)[\s,;]+(\.*$)", r"\1\2", norm)
    norm = re.sub(r"\s+", " ", norm)
    norm = norm.strip()
    # Controlla che sia normalizzata
    assert isNormalized(norm)
    # Torna alla versione latex
    if latex:
        norm = UL.unicode_to_latex(norm)
    # Rimette gli a capo
    return norm


def isNormalized(string: str) -> bool:
    """Verify that the given string is normalized."""
    start = re.search(r"[\s,;]", string[0]) is None
    end = re.search(r"[\s,;]", string[-1]) is None
    return start and end


def correctString(string: str) -> str:
    """Corregge la stringa, e altre piccole cose."""
    string = string.replace(";", ",")
    string = re.sub(r"\s*,\s*", ",", string)
    string = re.sub(r"\^", "", string)
    return string


# def ask4suggestion(string: str) -> dictCountry:
#     """Chiede all'utente di spezzare a mano i nomi se non ce la fa"""
#     country = extendedInput(" -> Tell me the country: ", history=string)
#     if country != "":
#         # Deve imparare la nuova stringa?
#         if country in string:
#             if questionYesNo("Do you want me to remeber it [y/n]? "):
#                 countries["aliases"].append(country)
#                 with open(myDict, "w") as f:
#                     json.dump(countries, f, indent=4)
#     address = extendedInput(
#         " -> Tell me the address: ", default=string, history=string
#     )
#     note = extendedInput(" -> Tell me other data: ", history=string)
#     return {"country": country, "address": address, "other": note}


# region [ TEST ] ######################################################################

splitCountryData = [
    (
        r"Centro Brasileiro de Pesquisas F{\'\i}sicas (CBPF), Rio de Janeiro, Brazil",
        {
            "country": "Brazil",
            "address": "Centro Brasileiro de Pesquisas Físicas (CBPF), Rio de Janeiro",
            "other": "",
        },
    ),
    (
        r"NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv, Ukraine",
        {
            "country": "Ukraine",
            "address": "NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv",
            "other": "",
        },
    ),
    (
        r"School of Physics and Astronomy, Monash University, Melbourne, Australia, associated to $^{56}$",
        {
            "country": "Australia",
            "address": "School of Physics and Astronomy, Monash University, Melbourne",
            "other": "associated to 56",
        },
    ),
    (
        r"NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv, Ukrailla",
        {
            "country": "",
            "address": "NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv, Ukrailla",
            "other": "",
        },
    ),
    (
        r"Texas A\&M University, College Station, Texas, USA",
        {
            "country": "USA",
            "address": "Texas A&M University, College Station, Texas",
            "other": "",
        },
    ),
    (
        r"Texas A\&M University, College Station, Texas; U.S.A.",
        {
            "country": "U.S.A.",
            "address": "Texas A&M University, College Station, Texas",
            "other": "",
        },
    ),
    (
        r"Department of Physics, University of Alberta, Edmonton AB; Canada",
        {
            "country": "Canada",
            "address": "Department of Physics, University of Alberta, Edmonton AB",
            "other": "",
        },
    ),
    (
        "Nanyang Technological University, Singapore",
        {
            "country": "Singapore",
            "address": "Nanyang Technological University",
            "other": "",
        },
    ),
    (
        " ",
        {
            "country": "",
            "address": "",
            "other": "",
        },
    ),
]


@pytest.mark.parametrize("inStr,expected", splitCountryData)
def test_splitCountry(inStr: str, expected: dictCountry) -> None:
    """Test split."""
    outStr = splitCountry(inStr)
    assert outStr == expected


normalizeData = [
    (
        r"Ciao\,po\~nllo~cà\\no;\.a~~\"{u}o%p\;ppo~,~\ ~",
        'Ciao po\\~nllo c\\`a no;\\.{a} \\"uo',
    ),
    (
        r"`siao'\,po\~nllo~cà\\no;\.a~~\"{u}op\;ppo~,~\ ~",
        "`siao' po\\~nllo c\\`a no;\\.{a} \\\"uop ppo",
    ),
    (r" Cia#o ,", "Cia\\#o"),
    (
        r"`siao'\,po\~nllo~cà\\no;\.a~~\"{u}op\;ppo~,~\ ~U.S.A.",
        "`siao' po\\~nllo c\\`a no;\\.{a} \\\"uop ppo , U.S.A.",
    ),
]


@pytest.mark.parametrize("inStr,outStr", normalizeData)
def test_normaliseString(inStr: str, outStr: str) -> None:
    """Test string normalization."""
    x1 = normalizeString(inStr)
    x2 = normalizeString(normalizeString(inStr))
    # print(x1.encode('raw_unicode_escape'))
    assert x1 == x2
    assert x1 == outStr
    assert isNormalized(x1)


# endregion
