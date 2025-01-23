import os
import re


def read_certificates():
    certificates = []
    dirname = os.path.dirname(os.path.relpath(__file__))
    with open(os.path.join(dirname, "data", "certificates.dat")) as f:
        for line in f:
            name, initials = [x.strip() for x in line.split(";")]
            certificates.append((name, initials))

    return certificates


def read_it_skills():
    skills = []
    dirname = os.path.dirname(os.path.relpath(__file__))
    with open(os.path.join(dirname, "data", "it_skills.dat")) as f:
        for line in f:
            synonyms = [x.strip() for x in line.split(",")]
            skills.append(synonyms)

    return skills


class RegexExtractor:
    def __init__(self):
        self.certificates = read_certificates()
        self.it_skills = read_it_skills()

    def extract_certificates(self, text):
        found = []
        for certificate in self.certificates:
            name, initials = certificate
            if re.search(re.escape(name), text, re.IGNORECASE):
                found.append((name, initials))
            elif re.search(re.escape(initials), text):
                found.append((name, initials))

        return found

    def extract_it_skills(self, text):
        found = []
        for synonyms in self.it_skills:
            for term in synonyms:
                if re.search(re.scape(term), text, re.IGNORECASE):
                    found.append(synonyms[0])
                    break

        return found

    def extract_salary_range(self, text):
        match = re.search(
            r"[\$€]\s*\d+\,?\d*\s*(?:to|and|\-)\s*[\$€]\d*\d+\,?\d*", text
        )
        if match:
            salary = match.group()
            return re.sub("\s*(?:and|to)\s*", "-", salary)
        else:
            return None
