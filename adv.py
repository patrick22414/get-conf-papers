import csv
import os
import dataclasses
from os import path
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class NipsPaper:
    title: str = ""
    authors: List[str] = dataclasses.field(default_factory=list)
    pdf_url: str = "--"
    abstract_url: str = "--"


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


def _split_and_rejoin(s: str, at="\n"):
    return " ".join(ss.strip() for ss in s.strip().split(at))


def get_iclr_papers():
    iclr_files = [
        "html/iclr2019-oral.html",
        "html/iclr2019-poster.html",
        "html/iclr2020-oral.html",
        "html/iclr2020-spotlight.html",
        "html/iclr2020-poster.html",
    ]

    for filename in iclr_files:
        conference = path.splitext(path.split(filename)[-1])[0]
        conference, accepted_as = conference.split("-")

        print()
        print(conference, accepted_as)

        with open(filename, "r") as html:
            soup = BeautifulSoup(html, "html.parser")

        all_papers = []
        for item in soup.ul.find_all("li", recursive=False):
            paper = IclrPaper()

            if item.h4 is None:
                continue

            title = _split_and_rejoin(item.h4.get_text())
            if "adversarial" in title.lower() and "generative" not in title.lower():
                paper = IclrPaper(title, accepted_as=accepted_as)

                pdf_link = item.find("a", "pdf-link")
                if pdf_link:
                    paper.pdf_url = "https://openreview.net" + pdf_link["href"]

                for author in item.find("div", "note-authors").find_all("a"):
                    # authors = [x.string or x.get_text() for x in result.children]
                    paper.authors.append(
                        _split_and_rejoin(next(author.stripped_strings))
                    )

                for child in item.find_all("li"):
                    field = child.strong.string.lower()
                    value = child.span.string or ""
                    if "tl;dr" in field:
                        paper.tldr = _split_and_rejoin(value)
                    elif "keywords" in field:
                        paper.keywords = [
                            _split_and_rejoin(s) for s in value.split(",")
                        ]
                        # paper.keywords = [
                        #     _split_and_rejoin(kw) for kw in paper.keywords
                        # ]
                    elif "abstract" in field:
                        paper.abstract = _split_and_rejoin(value)
                    elif "code" in field:
                        paper.code_url = value

                all_papers.append(paper)

        csv_filename = f"csv/adv-{conference}.csv"
        has_file = path.exists(csv_filename)
        with open(csv_filename, "a" if has_file else "w") as fout:
            writer = csv.DictWriter(
                fout,
                fieldnames=[
                    "PDF URL",
                    "Accepted as",
                    "Title",
                    "Authors",
                    "Keywords",
                    "Abstract",
                    "TL;DR",
                    "Code URL",
                ],
            )

            if not has_file:
                writer.writeheader()

            for paper in all_papers:
                print(paper.title)
                writer.writerow(
                    {
                        "PDF URL": paper.pdf_url,
                        "Accepted as": paper.accepted_as,
                        "Title": paper.title,
                        "Authors": "\n".join(paper.authors),
                        "Keywords": "; ".join(paper.keywords),
                        "Abstract": paper.abstract,
                        "TL;DR": paper.tldr,
                        "Code URL": paper.code_url,
                    }
                )


def get_nips_papers(request_pdf=True):
    nips_files = [
        "html/nips2019-proceedings.html",
        "html/nips2020-pre-proceedings.html",
    ]

    for filename in nips_files:
        conference = path.splitext(path.split(filename)[-1])[0]

        with open(filename, "r") as fin:
            soup = BeautifulSoup(fin, "html.parser")

        all_papers = []
        for li in soup.ul.find_all("li", recursive=False):
            a = li.a
            check_title = a.get_text().lower()
            if "adversarial" in check_title and "generative" not in check_title:
                title = _split_and_rejoin(a.get_text())
                authors = li.i.get_text().split(", ")
                abstract_url = "https://proceedings.neurips.cc" + a["href"]

                paper = NipsPaper(title, authors, abstract_url=abstract_url)

                if request_pdf:
                    resp = requests.get(abstract_url)
                    if resp.ok:
                        detail_soup = BeautifulSoup(resp.content, "html.parser")
                        btn = detail_soup.find("a", text="Paper »")
                        if btn:
                            paper.pdf_url = (
                                "https://proceedings.neurips.cc" + btn["href"]
                            )

                all_papers.append(paper)

        with open(f"csv/adv-{conference}.csv", "w") as fout:
            writer = csv.DictWriter(
                fout, fieldnames=["Title", "Authors", "PDF URL", "Abstract URL"]
            )

            writer.writeheader()
            for paper in all_papers:
                writer.writerow(
                    {
                        "Title": paper.title,
                        "Authors": "\n".join(paper.authors),
                        "PDF URL": paper.pdf_url,
                        "Abstract URL": paper.abstract_url,
                    }
                )


if __name__ == "__main__":
    get_iclr_papers()
