import os
import re

HTML_TAG_PATTERN = "<[^<]+?>"
HTML_SPACE_PATTERN = "&nbsp"
HTML_PLUS_SIGN = r"&#43;?"


def remove_html(text):
    for pattern, replacement in [
        (HTML_TAG_PATTERN, " "),
        (HTML_SPACE_PATTERN, " "),
        (HTML_PLUS_SIGN, "+"),
    ]:
        text = re.sub(pattern, replacement, text)

    return text


def read_country_codes(path):
    country_codes = {}
    with open(path) as f:
        next(f)  # skip header
        for line in f:
            name, alpha2, alpha3, numeric = line.strip().split("\t")
            country_codes.setdefault(alpha2, name)

    return country_codes


class CountryCodeMatcher:
    def __init__(self):
        dirname = os.path.dirname(os.path.relpath(__file__))

        self.country_codes = read_country_codes(
            os.path.join(dirname, "data", "country_codes.tsv")
        )

    def complete_location(self, loc):
        name = loc.get("country")
        alpha2 = loc.get("alpha2")
        if name is not None:
            if "United States" in name:
                name = "United States of America"

        if alpha2 is not None:
            name = self.get_country_name(alpha2)
        elif name is not None:
            alpha2 = self.get_country_code(name)
        else:
            loc["name"] = name
            return loc

        loc["country"] = name
        loc["alpha2"] = alpha2

        return loc

    def get_country_name(self, alpha2):
        return self.country_codes.get(alpha2)

    def get_country_code(self, name):

        for alpha2, country in self.country_codes.items():
            if country == name:
                return alpha2
        return None
