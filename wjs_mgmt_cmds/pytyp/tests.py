"""Tests for affiliationSplitter functions."""

import pytest
from .utils import normalizeString
# from .affiliationSplitter import splitCountry
# from .affiliationSplitter import Address

# splitCountryData = [
#     (
#         r"Centro Brasileiro de Pesquisas Físicas (CBPF), Rio de Janeiro, Brazil",
#         {
#             "country": "Brazil",
#             "address": "Centro Brasileiro de Pesquisas Físicas (CBPF), Rio de Janeiro",
#             "other": "",
#         },
#     ),
#     (
#         r"NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv, Ukraine",
#         {
#             "country": "Ukraine",
#             "address": "NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv",
#             "other": "",
#         },
#     ),
#     (
#         r"School of Physics and Astronomy, Monash University, Melbourne, Australia, associated to $^{56}$",
#         {
#             "country": "Australia",
#             "address": "School of Physics and Astronomy, Monash University, Melbourne",
#             "other": "associated to 56",
#         },
#     ),
#     (
#         r"NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv, Ukrailla",
#         {
#             "country": "",
#             "address": "NSC Kharkiv Institute of Physics and Technology (NSC KIPT), Kharkiv, Ukrailla",
#             "other": "",
#         },
#     ),
#     (
#         r"Texas A\&M University, College Station, Texas, USA",
#         {
#             "country": "USA",
#             "address": "Texas A&M University, College Station, Texas",
#             "other": "",
#         },
#     ),
#     (
#         r"Texas A\&M University, College Station, Texas; U.S.A.",
#         {
#             "country": "U.S.A.",
#             "address": "Texas A&M University, College Station, Texas",
#             "other": "",
#         },
#     ),
#     (
#         r"Department of Physics, University of Alberta, Edmonton AB; Canada",
#         {
#             "country": "Canada",
#             "address": "Department of Physics, University of Alberta, Edmonton AB",
#             "other": "",
#         },
#     ),
#     (
#         "Nanyang Technological University, Singapore",
#         {
#             "country": "Singapore",
#             "address": "Nanyang Technological University",
#             "other": "",
#         },
#     ),
#     (
#         " ",
#         {
#             "country": "",
#             "address": "",
#             "other": "",
#         },
#     ),
#     # "Department of Physics, Nanchang University, Nanchang 330031,People’s Republic of China"
#     # "shiraz university, department of physics, shiraz,iran "
#     # "Dept. of Physics, Institute of Technology of HochiMinh City-Vietnam"
#     # "Brown University, Providence USA"
#     # "Institute of Physics, P.O.Box 769, Neishabour, Iran."
#     # "Institut de Physique Théorique, Université Paris Saclay, CEA, CNRSFrance"
#     # "CFTP - IST (Lisbon, Portugal)"
#     # "Dipartimento di Fisica Galileo Galilei, via Marzolo 8, I-35131, Italia"
#     # "Dip.  di Fisica, Universita' di Trento (Italia)"
#     # "Department of Mathematics, North Eastern Hill University, Shillong-793022 (INDIA)"
#     # "Universidad de Guanajuato, Campus Leon, Mexico."
#     # "Instituto Nacional de Comunicação Pública da Ciência e Tecnologia e Fundação Oswaldo Cruz, Brasil"
#     # "Universidad Nacional Autónoma de México, Campus Morelia (Mexico)"
#     # "Pará Federal Institute of Education,Science and Technology - IFPA (Belém, Brazil)"
#     # "Geological Museum, The National Institute of Advanced Industrial Science and Technology, JAPAN."
#     # "Department of Philosophy, Sociology, Education and Applied Psychology (FISPPA) - University of Padua (Italy)"
#     # "UNIVERSITY OF HYDERABAD, INDIA"
#     # "Science Time, Kampala Uganda"
#     # "National Museum of Natural Sciences (Madrid, Spain)"
#     # "Laboratory of Immunology, Faculty of Medicine, University of Kasdi Merbah, Ouargla 30000, Algeria"
#     # "Ebonyi State University, Abakaliki Nigeria"
#     # "Universidade Estadual de Londrina, Paraná, Brazil."
#     # "UNIVERSIDAD CIENTÍFICA DEL SUR, LIMA, PERÚ"
#     # "Seth G.S.Medical College and KEM Hospital, Parel Mumbai India"
#     # "Adama Science and Technology University, Ethiopia"
#     # "Dipartimento di Fisica, Universita' di Milano-Bicocca, Piazza della Scienza 3, Milano, ITALY"
#     # "Centre for High Energy Physics, Indian Institute of Science, Bangalore 560012, India. "
#     # "Faculty of Physics, Amirkabir University of Technology (Tehran Polytechnic) P.O.Box: 15875-4413, Tehran, IRAN"
#     # "Jagiellonian University, Krakow, Poland."
#     # "CQUeST, Sogang Univ. Republic of Korea"
#     # "LUMS School of Science & Engineering, Lahore, Pakistan."
#     # "Institute of Theoretical Physics, Lanzhou University, Lanzhou 730000, P. R. China"
#     # "Cankaya University, Ankara, Turkey."
#     # "Dipartimento di Fisica ``Galileo Galilei'', Padova (Italy)"
#     # "Institute of Theoretical Physics University of Tokushima Tokushima 770-8502, JAPAN  "
#     # "school of studies of physics,ujain,india"
#     # "Ministry of Education, Culture, Sports, Science and Technology –Japan"
#     # "federal university of technology akure, nigeria"
#     # "Facultad de Ciencias, Universidad de la Republica, Uruguay"
#     # "Jozef Stefan Institute, Ljubljana, Slovenija"
#     # "Department of Physics - INFN, University of Milan-Bicocca - Italy "
#     # "Modern University, Cairo, Egypt."
#     # "Sana'a University, Sana'a. Yemen"
#     # "j.stefan institute, ljubljana, slovenia"
#     # "University of New Brunswick, Fredericton, NB, Canada."
#     # "Institute of Physics, Ha Noi, Viet Nam"
#     # "Payame Noor U. , Tabriz- Iran"
# ]


# @pytest.mark.parametrize("inStr,expected", splitCountryData)
# def test_splitCountry(inStr: str, expected: Address) -> None:
#     """Test split."""
#     outStr = splitCountry(inStr, latex_input=True, latex_output=False)
#     assert outStr == expected


normalizeData = [
    # Found in field `organization` of jhep user 4921:
    # note the "," at the end of the string.
    ("Reametrix India Pvt. Ltd.,", "Reametrix India Pvt. Ltd"),
    ("Department of Physics, Nanchang University, Nanchang 330031,People’s Republic of China",
     "Department of Physics, Nanchang University, Nanchang 330031, People's Republic of China"),
    ("shiraz university, department of physics, shiraz,iran ",
     "Shiraz University, Department of Physics, Shiraz, Iran"),
    # Problematic: HochiMinh
    ("Dept. of Physics, Institute of Technology of HochiMinh City-Vietnam",
     "Dept. of Physics, Institute of Technology of Hochiminh City, Vietnam"),
    # Problematic: USA
    ("Brown University, Providence USA",
     "Brown University, Providence Usa"),
    # Problematic: P.O.Box
    ("Institute of Physics, P.O.Box 769, Neishabour, Iran.",
     "Institute of Physics, P.o.box 769, Neishabour, Iran"),
    # Problematic: Institut de Physique, CNRSFrance, CEA
    ("Institut de Physique Théorique, Université Paris Saclay, CEA, CNRSFrance",
     "Institut De Physique Théorique, Université Paris Saclay, Cea, Cnrsfrance"),
    ("CFTP - IST (Lisbon, Portugal)",
     "Cftp, Ist, Lisbon, Portugal"),
    ("Dipartimento di Fisica Galileo Galilei, via Marzolo 8, I-35131, Italia",
     "Dipartimento Di Fisica Galileo Galilei, Via Marzolo 8, I, 35131, Italia"),
    ("Dip.  di Fisica, Universita' di Trento (Italia)",
     "Dip. Di Fisica, Universita' Di Trento, Italia"),
    ("Department of Mathematics, North Eastern Hill University, Shillong-793022 (INDIA)",
     "Department of Mathematics, North Eastern Hill University, Shillong, 793022, India"),
    # Problematic: Universidad de Guanajuato
    ("Universidad de Guanajuato, Campus Leon, Mexico.",
     "Universidad De Guanajuato, Campus Leon, Mexico"),
    # Problematic: de, da, e
    ("Instituto Nacional de Comunicação Pública da Ciência e Tecnologia e Fundação Oswaldo Cruz, Brasil",
     "Instituto Nacional De Comunicação Pública Da Ciência E Tecnologia E Fundação Oswaldo Cruz, Brasil"),
    ("Universidad Nacional Autónoma de México, Campus Morelia (Mexico)",
     "Universidad Nacional Autónoma De México, Campus Morelia, Mexico"),
    ("Pará Federal Institute of Education,Science and Technology - IFPA (Belém, Brazil)",
     "Pará Federal Institute of Education, Science And Technology, Ifpa, Belém, Brazil"),
    ("Geological Museum, The National Institute of Advanced Industrial Science and Technology, JAPAN.",
     "Geological Museum, The National Institute of Advanced Industrial Science And Technology, Japan"),
    ("Department of Philosophy, Sociology, Education and Applied Psychology (FISPPA) - University of Padua (Italy)",
     "Department of Philosophy, Sociology, Education And Applied Psychology, Fisppa, University of Padua, Italy"),
    ("UNIVERSITY OF HYDERABAD, INDIA",
     "University of Hyderabad, India"),
    ("Science Time, Kampala Uganda",
     "Science Time, Kampala Uganda"),
    ("National Museum of Natural Sciences (Madrid, Spain)",
     "National Museum of Natural Sciences (Madrid, Spain)"),
    ("Laboratory of Immunology, Faculty of Medicine, University of Kasdi Merbah, Ouargla 30000, Algeria",
     "Laboratory of Immunology, Faculty of Medicine, University of Kasdi Merbah, Ouargla 30000, Algeria"),
    ("Ebonyi State University, Abakaliki Nigeria",
     "Ebonyi State University, Abakaliki Nigeria"),
    ("Universidade Estadual de Londrina, Paraná, Brazil.",
     "Universidade Estadual de Londrina, Paraná, Brazil."),
    ("UNIVERSIDAD CIENTÍFICA DEL SUR, LIMA, PERÚ",
     "UNIVERSIDAD CIENTÍFICA DEL SUR, LIMA, PERÚ"),
    ("Seth G.S.Medical College and KEM Hospital, Parel Mumbai India",
     "Seth G.S.Medical College and KEM Hospital, Parel Mumbai India"),
    ("Adama Science and Technology University, Ethiopia",
     "Adama Science and Technology University, Ethiopia"),
    ("Dipartimento di Fisica, Universita' di Milano-Bicocca, Piazza della Scienza 3, Milano, ITALY",
     "Dipartimento di Fisica, Universita' di Milano-Bicocca, Piazza della Scienza 3, Milano, ITALY"),
    ("Centre for High Energy Physics, Indian Institute of Science, Bangalore 560012, India. ",
     "Centre for High Energy Physics, Indian Institute of Science, Bangalore 560012, India. "),
    ("Faculty of Physics, Amirkabir University of Technology (Tehran Polytechnic) P.O.Box: 15875-4413, Tehran, IRAN",
     "Faculty of Physics, Amirkabir University of Technology (Tehran Polytechnic) P.O.Box: 15875-4413, Tehran, IRAN"),
    ("Jagiellonian University, Krakow, Poland.",
     "Jagiellonian University, Krakow, Poland."),
    ("CQUeST, Sogang Univ. Republic of Korea",
     "CQUeST, Sogang Univ. Republic of Korea"),
    ("LUMS School of Science & Engineering, Lahore, Pakistan.",
     "LUMS School of Science & Engineering, Lahore, Pakistan."),
    ("Institute of Theoretical Physics, Lanzhou University, Lanzhou 730000, P. R. China",
     "Institute of Theoretical Physics, Lanzhou University, Lanzhou 730000, P. R. China"),
    ("Cankaya University, Ankara, Turkey.",
     "Cankaya University, Ankara, Turkey."),
    ("Dipartimento di Fisica ``Galileo Galilei'', Padova (Italy)",
     "Dipartimento di Fisica ``Galileo Galilei'', Padova (Italy)"),
    ("Institute of Theoretical Physics University of Tokushima Tokushima 770-8502, JAPAN  ",
     "Institute of Theoretical Physics University of Tokushima Tokushima 770-8502, JAPAN  "),
    ("school of studies of physics,ujain,india",
     "school of studies of physics,ujain,india"),
    ("Ministry of Education, Culture, Sports, Science and Technology –Japan",
     "Ministry of Education, Culture, Sports, Science and Technology –Japan"),
    ("federal university of technology akure, nigeria",
     "federal university of technology akure, nigeria"),
    ("Facultad de Ciencias, Universidad de la Republica, Uruguay",
     "Facultad de Ciencias, Universidad de la Republica, Uruguay"),
    ("Jozef Stefan Institute, Ljubljana, Slovenija",
     "Jozef Stefan Institute, Ljubljana, Slovenija"),
    ("Department of Physics - INFN, University of Milan-Bicocca - Italy ",
     "Department of Physics - INFN, University of Milan-Bicocca - Italy "),
    ("Modern University, Cairo, Egypt.",
     "Modern University, Cairo, Egypt."),
    ("Sana'a University, Sana'a. Yemen",
     "Sana'a University, Sana'a. Yemen"),
    ("j.stefan institute, ljubljana, slovenia",
     "j.stefan institute, ljubljana, slovenia"),
    ("University of New Brunswick, Fredericton, NB, Canada.",
     "University of New Brunswick, Fredericton, NB, Canada."),
    ("Institute of Physics, Ha Noi, Viet Nam",
     "Institute of Physics, Ha Noi, Viet Nam"),
    ("Payame Noor U. , Tabriz- Iran",
     "Payame Noor U. , Tabriz- Iran"),
]


# # Needed because the list of known `Country`s is taken from the DB
# @pytest.mark.django_db


@pytest.mark.parametrize("inStr,outStr", normalizeData)
def test_normaliseString(inStr: str, outStr: str) -> None:
    """Test string normalization."""
    # Should be idempotent
    x1 = normalizeString(inStr)
    x2 = normalizeString(x1)
    assert x1 == x2
    assert x1 == outStr
