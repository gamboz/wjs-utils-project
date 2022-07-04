"""Tests for affiliationSplitter functions."""

import pytest
from .utils import normalizeString
# from .affiliationSplitter import Address


data = [
    # Found in field `organization` of jhep user 4921:
    # note the "," at the end of the string.
    ("Reametrix India Pvt. Ltd.,", "Reametrix India Pvt. Ltd", "India"),
    ("Department of Physics, Nanchang University, Nanchang 330031,People’s Republic of China",
     "Department of Physics, Nanchang University, Nanchang 330031, People's Republic of China",
     "China"),
    ("shiraz university, department of physics, shiraz,iran ",
     "shiraz university, department of physics, shiraz, iran",
     "Iran, Islamic Republic of"),
    # Problematic: HochiMinh
    ("Dept. of Physics, Institute of Technology of HochiMinh City-Vietnam",
     "Dept. of Physics, Institute of Technology of HochiMinh City, Vietnam",
     "Viet Nam"),
    # Problematic: USA
    ("Brown University, Providence USA",
     "Brown University, Providence USA",
     "United States"),
    # Problematic: P.O.Box
    ("Institute of Physics, P.O.Box 769, Neishabour, Iran.",
     "Institute of Physics, P.O.Box 769, Neishabour, Iran",
     "Iran, Islamic Republic of"),
    # Problematic: Institut de Physique, CNRSFrance, CEA
    ("Institut de Physique Théorique, Université Paris Saclay, CEA, CNRSFrance",
     "Institut de Physique Théorique, Université Paris Saclay, CEA, CNRSFrance",
     "France"),
    ("CFTP - IST (Lisbon, Portugal)",
     "CFTP, IST, Lisbon, Portugal",
     "Portugal"),
    ("Dipartimento di Fisica Galileo Galilei, via Marzolo 8, I-35131, Italia",
     "Dipartimento di Fisica Galileo Galilei, via Marzolo 8, I, 35131, Italia",
     "Italy"),
    ("Dip.  di Fisica, Universita' di Trento (Italia)",
     "Dip. di Fisica, Universita' di Trento, Italia",
     "Italy"),
    ("Department of Mathematics, North Eastern Hill University, Shillong-793022 (INDIA)",
     "Department of Mathematics, North Eastern Hill University, Shillong, 793022, INDIA",
     "India"),
    # Problematic: Universidad de Guanajuato
    ("Universidad de Guanajuato, Campus Leon, Mexico.",
     "Universidad de Guanajuato, Campus Leon, Mexico",
     "Mexico"),
    # Problematic: de, da, e
    ("Instituto Nacional de Comunicação Pública da Ciência e Tecnologia e Fundação Oswaldo Cruz, Brasil",
     "Instituto Nacional de Comunicação Pública da Ciência e Tecnologia e Fundação Oswaldo Cruz, Brasil",
     "Brazil"),
    ("Universidad Nacional Autónoma de México, Campus Morelia (Mexico)",
     "Universidad Nacional Autónoma de México, Campus Morelia, Mexico",
     "Mexico"),
    ("Pará Federal Institute of Education,Science and Technology - IFPA (Belém, Brazil)",
     "Pará Federal Institute of Education, Science and Technology, IFPA, Belém, Brazil",
     "Brazil"),
    ("Geological Museum, The National Institute of Advanced Industrial Science and Technology, JAPAN.",
     "Geological Museum, The National Institute of Advanced Industrial Science and Technology, JAPAN",
     "Japan"),
    ("Department of Philosophy, Sociology, Education and Applied Psychology (FISPPA) - University of Padua (Italy)",
     "Department of Philosophy, Sociology, Education and Applied Psychology, FISPPA, University of Padua, Italy",
     "Italy"),
    ("UNIVERSITY OF HYDERABAD, INDIA",
     "UNIVERSITY OF HYDERABAD, INDIA",
     "India"),
    ("Science Time, Kampala Uganda",
     "Science Time, Kampala Uganda",
     "Uganda"),
    ("National Museum of Natural Sciences (Madrid, Spain)",
     "National Museum of Natural Sciences, Madrid, Spain",
     "Spain"),
    ("Laboratory of Immunology, Faculty of Medicine, University of Kasdi Merbah, Ouargla 30000, Algeria",
     "Laboratory of Immunology, Faculty of Medicine, University of Kasdi Merbah, Ouargla 30000, Algeria",
     "Algeria"),
    ("Ebonyi State University, Abakaliki Nigeria",
     "Ebonyi State University, Abakaliki Nigeria",
     "Nigeria"),
    ("Universidade Estadual de Londrina, Paraná, Brazil.",
     "Universidade Estadual de Londrina, Paraná, Brazil",
     "Brazil"),
    ("UNIVERSIDAD CIENTÍFICA DEL SUR, LIMA, PERÚ",
     "UNIVERSIDAD CIENTÍFICA DEL SUR, LIMA, PERÚ",
     "Peru"),
    ("Seth G.S.Medical College and KEM Hospital, Parel Mumbai India",
     "Seth G.S.Medical College and KEM Hospital, Parel Mumbai India",
     "India"),
    ("Adama Science and Technology University, Ethiopia",
     "Adama Science and Technology University, Ethiopia",
     "Ethiopia"),
    ("Dipartimento di Fisica, Universita' di Milano-Bicocca, Piazza della Scienza 3, Milano, ITALY",
     "Dipartimento di Fisica, Universita' di Milano, Bicocca, Piazza della Scienza 3, Milano, ITALY",
     "Italy"),
    ("Centre for High Energy Physics, Indian Institute of Science, Bangalore 560012, India. ",
     "Centre for High Energy Physics, Indian Institute of Science, Bangalore 560012, India",
     "India"),
    ("Faculty of Physics, Amirkabir University of Technology (Tehran Polytechnic) P.O.Box: 15875-4413, Tehran, IRAN",
     "Faculty of Physics, Amirkabir University of Technology, Tehran Polytechnic, P.O.Box: 15875, 4413, Tehran, IRAN",
     "Iran, Islamic Republic of"),
    ("Jagiellonian University, Krakow, Poland.",
     "Jagiellonian University, Krakow, Poland",
     "Poland"),
    ("CQUeST, Sogang Univ. Republic of Korea",
     "CQUeST, Sogang Univ. Republic of Korea",
     "Korea, Republic of"),
    ("LUMS School of Science & Engineering, Lahore, Pakistan.",
     "LUMS School of Science & Engineering, Lahore, Pakistan",
     "Pakistan"),
    ("Institute of Theoretical Physics, Lanzhou University, Lanzhou 730000, P. R. China",
     "Institute of Theoretical Physics, Lanzhou University, Lanzhou 730000, P. R. China",
     "China"),
    ("Cankaya University, Ankara, Turkey.",
     "Cankaya University, Ankara, Turkey",
     "Turkey"),
    ("Dipartimento di Fisica ``Galileo Galilei'', Padova (Italy)",
     "Dipartimento di Fisica ``Galileo Galilei'', Padova, Italy",
     "Italy"),
    ("Institute of Theoretical Physics University of Tokushima Tokushima 770-8502, JAPAN  ",
     "Institute of Theoretical Physics University of Tokushima Tokushima 770, 8502, JAPAN",
     "Japan"),
    ("school of studies of physics,ujain,india",
     "school of studies of physics, ujain, india",
     "India"),
    ("Ministry of Education, Culture, Sports, Science and Technology –Japan",
     "Ministry of Education, Culture, Sports, Science and Technology, Japan",
     "Japan"),
    ("federal university of technology akure, nigeria",
     "federal university of technology akure, nigeria",
     "Nigeria"),
    ("Facultad de Ciencias, Universidad de la Republica, Uruguay",
     "Facultad de Ciencias, Universidad de la Republica, Uruguay",
     "Uruguay"),
    ("Jozef Stefan Institute, Ljubljana, Slovenija",
     "Jozef Stefan Institute, Ljubljana, Slovenija",
     "Slovenia"),
    ("Department of Physics - INFN, University of Milan-Bicocca - Italy ",
     "Department of Physics, INFN, University of Milan, Bicocca, Italy",
     "Italy"),
    ("Modern University, Cairo, Egypt.",
     "Modern University, Cairo, Egypt",
     "Egypt"),
    ("Sana'a University, Sana'a. Yemen",
     "Sana'a University, Sana'a. Yemen",
     "Yemen"),
    ("j.stefan institute, ljubljana, slovenia",
     "j.stefan institute, ljubljana, slovenia",
     "Slovenia"),
    ("University of New Brunswick, Fredericton, NB, Canada.",
     "University of New Brunswick, Fredericton, NB, Canada",
     "Canada"),
    ("Institute of Physics, Ha Noi, Viet Nam",
     "Institute of Physics, Ha Noi, Viet Nam",
     "Viet Nam",),
    ("Payame Noor U. , Tabriz- Iran",
     "Payame Noor U., Tabriz, Iran",
     "Iran, Islamic Republic of"),
]


# # Needed because the list of known `Country`s is taken from the DB
# @pytest.mark.django_db


@pytest.mark.parametrize("inStr,outStr,country", data)
def test_normaliseString(inStr: str, outStr: str, country: str) -> None:
    """Test string normalization."""
    # Just ignore `country` here.
    # Should be idempotent
    x1 = normalizeString(inStr)
    x2 = normalizeString(x1)
    assert x1 == x2
    assert x1 == outStr


# Needed because the list of known `Country`s is taken from the DB
@pytest.mark.django_db
@pytest.mark.parametrize("inStr,outStr,country", data)
def test_findCountry(inStr: str, outStr: str, country: str) -> None:
    """Test find country."""
    # Just ignore `inStr` here.
    # NB: import here, i.e. in django_db-marked function,
    # otherwise pytest will complain
    from .affiliationSplitter import find_country
    (country_obj, found_string) = find_country(inStr)
    assert country_obj.name == country


@pytest.mark.django_db
@pytest.mark.parametrize("inStr,outStr,country", data)
def test_splitCountry(inStr: str, outStr: str, country: str) -> None:
    """Test split."""
    # Just ignore `outStr` here.
    from .affiliationSplitter import splitCountry
    address = splitCountry(inStr)
    assert address.country.name == country
