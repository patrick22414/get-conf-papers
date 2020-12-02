import csv
import os
import dataclasses
from os import path
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class IclrPaper:
    title: str = ""
    authors: List[str] = dataclasses.field(default_factory=list)
    accepted_as: str = ""
    pdf_url: str = "--"
    keywords: List[str] = dataclasses.field(default_factory=list)
    tldr: str = "--"
    abstract: str = "--"
    code_url: str = "--"


if __name__ == "__main__":
    iclr_files = [
        [
            #
            "html/iclr2019-oral.html",
            "html/iclr2019-poster.html",
        ],
        [
            #
            "html/iclr2020-oral.html",
            "html/iclr2020-spotlight.html",
            "html/iclr2020-poster.html",
        ],
    ]

    for filename_list in iclr_files:
        all_papers = []

        for filename in filename_list:
            conference = path.splitext(path.split(filename)[-1])[0]
            conference, accepted_as = conference.split("-")

            print()
            print(conference, accepted_as)

            with open(filename, "r") as html:
                soup = BeautifulSoup(html, "html.parser")

            for note in soup.ul.find_all("li", recursive=False):
                paper = IclrPaper(accepted_as=accepted_as)

                if note.h4 is None:
                    continue

                paper.title = " ".join(note.h4.a.stripped_strings)

                pdf_link = note.find("a", "pdf-link")
                if pdf_link:
                    paper.pdf_url = "https://openreview.net" + pdf_link["href"]

                for author in note.find("div", "note-authors").find_all("a"):
                    paper.authors.append(author.get_text())

                for child in note.find("ul", "note-content").find_all("li"):
                    field = child.strong.string.lower()
                    value = " ".join(child.span.stripped_strings)
                    if "tl;dr" in field:
                        paper.tldr = value
                    elif "keywords" in field:
                        paper.keywords = value.split(", ")
                    elif "abstract" in field:
                        paper.abstract = " ".join(s.strip() for s in value.split("\n"))
                    elif "code" in field:
                        paper.code_url = value

                all_papers.append(paper)

        print(len(all_papers))

        tsv_filename = f"tsv/adv-{conference}.tsv"
        with open(tsv_filename, "w") as fout:
            writer = csv.DictWriter(
                fout,
                fieldnames=[
                    "PDF",
                    "Accepted as",
                    "Title",
                    "Authors",
                    "Keywords",
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
                    for s in [paper.title, "".join(paper.keywords), paper.abstract]
                ):
                    counter += 1
                    writer.writerow(
                        {
                            "PDF": paper.pdf_url,
                            "Accepted as": paper.accepted_as,
                            "Title": paper.title,
                            "Authors": ", ".join(paper.authors),
                            "Keywords": "; ".join(paper.keywords) or "--",
                            "Abstract": paper.abstract,
                        }
                    )
            print("filtered =", counter)
