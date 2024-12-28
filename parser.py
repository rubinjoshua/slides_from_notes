import re
import marko
import os
from bs4 import BeautifulSoup


def get_caption_from_question(question_soup):
    next_sibling = question_soup.nextSibling
    if next_sibling.name == "h4":
        return text_of(next_sibling)
    return None


def get_everything_until_next_tag(soup, name):
    name2tag = {"seif": "h1", "question": "h2", "rabbi": "h3"}
    next_tags = {"h1": "h2", "h2": "h3", "h3": None}
    data = BeautifulSoup()
    for s in soup.find_next_siblings():
        if s.name == name2tag[name]:
            break
        data.append(s)
    return data.find_all(next_tags[name2tag[name]])


def text_of(e):
    return e.get_text(strip=True)


def parse_rabbi_name_with_ref(rabbi_text):
    def split(rs):
        return [re.sub("[״׳]", "", r.strip()) for r in rs.split(",") if r.strip()]
    regex = re.compile("([^(]+)(?:\(בשם ([^)]+)\))?")
    rabbis_refs = []
    for rabbis, refs in regex.findall(rabbi_text):
        for rabbi in split(rabbis):
            rabbis_refs.append({"rabbi": rabbi, "refs": []})
        if refs:
            rabbis_refs[-1] = {"rabbi": rabbis_refs[-1]["rabbi"], "refs": split(refs)}
    return rabbis_refs


def parse_file(file_name):
    text = open(file_name).read()
    soup = BeautifulSoup(marko.convert(text), 'html5lib')
    d = {text_of(seif):
             {text_of(question):
                  {"caption": get_caption_from_question(question)} |
                  {i:
                       {"rabbis": parse_rabbi_name_with_ref(text_of(rabbi)),
                        "text": "\n".join(text_of(p)
                                          for p in get_everything_until_next_tag(rabbi, "rabbi"))}
                   for i, rabbi in enumerate(get_everything_until_next_tag(question, "question"))}
              for question in get_everything_until_next_tag(seif, "seif")}
         for seif in soup.find_all("h1")}
    return {"siman": re.sub("[^א-ת״]*([א-ת״]+)[^א-ת״]*", "\\1", os.path.basename(file_name))} | d


if __name__ == "__main__":
    data = parse_file("/Users/joshuarubin/Library/Mobile Documents/com~apple~CloudDocs/לימוד הלכה/שבת/ש״ח.md")
    print(data)