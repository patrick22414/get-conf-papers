import csv
import os
import dataclasses
from os import path
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class IcmlPaper:
    title: str = ""
    authors: List[str] = dataclasses.field(default_factory=list)
    pdf: str = "--"
    supp_pdf: str = "--"
    code_url: str = "--"
    abstract: str = "--"


icml_files = ["html/icml2019-proceedings.html", "html/icml2020-proceedings.html"]

REQUEST_ABS = True

for filename in icml_files:
    conference = path.splitext(path.split(filename)[-1])[0]
    print()
    print(conference)

    with open(filename, "r") as fin:
        soup = BeautifulSoup(fin, "html.parser")

    all_papers = []
    for div in soup.find_all("div", "paper"):
        paper = IcmlPaper()

        paper.title = div.find("p", "title").get_text()
        paper.authors = div.find("span", "authors").get_text().split(",\xa0")

        links = div.find("p", "links")
        for a in links.find_all("a"):
            a_text = a.get_text()
            if "Download PDF" in a_text:
                paper.pdf = a["href"]
            elif "Supplementary PDF" in a_text:
                paper.supp_pdf = a["href"]
            elif "Code" in a_text or "Software" in a_text:
                paper.code_url = a["href"]
            elif "abs" in a_text:
                if REQUEST_ABS:
                    print("Getting", repr(paper.title), end=" ")
                    resp = requests.get(a["href"])
                    if not resp.ok:
                        print("Failed")
                        continue

                    print("OK")

                    abs_soup = BeautifulSoup(resp.content, "html.parser")
                    abs_div = abs_soup.find("div", "abstract")

                    if abs_div is None:
                        continue

                    paper.abstract = " ".join(abs_div.stripped_strings)

        all_papers.append(paper)

    with open(f"tsv/adv-{conference}.tsv", "w") as fout:
        writer = csv.DictWriter(
            fout,
            fieldnames=[
                "Title",
                "Authors",
                "PDF",
                "Supplementary PDF",
                "Code",
                "Abstract",
            ],
            delimiter="\t",
            dialect="unix",
        )

        writer.writeheader()

        include = [
            lambda s: "adversarial robust" in s.lower(),
            lambda s: "adversarial training" in s.lower(),
            lambda s: "adversarial examples" in s.lower(),
            lambda s: "adversarial attack" in s.lower(),
        ]

        exclude = [
            lambda s: "GAN" in s,
            lambda s: "generative adv" in s.lower(),
            lambda s: "adversarial network" in s.lower(),
        ]

        counter = 0
        for paper in all_papers:
            if any(
                any(cond(s) for cond in include)
                and not any(cond(s) for cond in exclude)
                for s in [paper.title, paper.abstract]
            ):
                counter += 1
                print(paper.title)
                writer.writerow(
                    {
                        "Title": paper.title,
                        "Authors": ", ".join(paper.authors),
                        "PDF": paper.pdf,
                        "Supplementary PDF": paper.supp_pdf,
                        "Code": paper.code_url,
                        "Abstract": paper.abstract,
                    }
                )
