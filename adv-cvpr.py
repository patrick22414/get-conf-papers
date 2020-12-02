import csv
import os
import dataclasses
from os import path
from typing import List

import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup


@dataclasses.dataclass
class CvprPaper:
    title: str = ""
    authors: List[str] = dataclasses.field(default_factory=list)
    pdf: str = "--"
    pdf_supp: str = "--"
    abs_url: str = ""
    abstract: str = "--"
    arxiv: str = "--"


REQUEST_ABS = True

iclr_files = [
    [
        #
        "html/cvpr2019-day1.html",
        "html/cvpr2019-day2.html",
        "html/cvpr2019-day3.html",
    ],
    [
        #
        "html/cvpr2020-day1.html",
        "html/cvpr2020-day2.html",
        "html/cvpr2020-day3.html",
    ],
]

for filename_list in iclr_files:
    all_papers = []

    for filename in filename_list:
        conference = path.splitext(path.split(filename)[-1])[0]
        conference, _ = conference.split("-")

        print()
        print(conference, _)

        with open(filename, "r") as html:
            soup = BeautifulSoup(html, "html.parser")

        for dt in soup.find_all("dt", "ptitle"):
            paper = CvprPaper()

            paper.title = dt.get_text()
            paper.abs_url = "https://openaccess.thecvf.com/" + dt.a["href"]

            authors_dd = dt.find_next("dd")
            paper.authors = [a.get_text().strip() for a in authors_dd.find_all("a")]

            for a in authors_dd.find_next("dd").find_all("a"):
                a_text = a.get_text()
                if "pdf" in a_text:
                    paper.pdf = "https://openaccess.thecvf.com/" + a["href"]
                elif "supp" in a_text:
                    paper.pdf_supp = "https://openaccess.thecvf.com/" + a["href"]
                elif "arXiv" in a_text:
                    paper.arxiv = a["href"]

            all_papers.append(paper)

    if REQUEST_ABS:

        async def _fetch(session, paper):
            async with session.get(paper.abs_url) as response:
                if response.status == 200:
                    print("OK", repr(paper.title))
                    content = await response.text()
                    abs_soup = BeautifulSoup(content, "html.parser")
                    abs_div = abs_soup.find("div", id="abstract")
                    paper.abstract = abs_div.get_text().strip()
                else:
                    print("Failed", response.reason)

        async def _fetch_all():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for paper in all_papers:
                    tasks.append(_fetch(session, paper))
                await asyncio.gather(*tasks, return_exceptions=True)

        asyncio.run(_fetch_all())

    print(len(all_papers))

    tsv_filename = f"tsv/adv-{conference}.tsv"
    with open(tsv_filename, "w") as fout:
        writer = csv.DictWriter(
            fout,
            fieldnames=[
                "PDF",
                "Supplementary PDF",
                "ArXiv",
                "Title",
                "Authors",
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
                writer.writerow(
                    {
                        "PDF": paper.pdf,
                        "Supplementary PDF": paper.pdf_supp,
                        "ArXiv": paper.arxiv,
                        "Title": paper.title,
                        "Authors": ", ".join(paper.authors),
                        "Abstract": paper.abstract,
                    }
                )
        print("filtered =", counter)
