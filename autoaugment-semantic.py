import requests
import json
from os import path
import csv

url_format = "https://api.semanticscholar.org/v1/paper/CorpusID:{}".format

corpus_ids = {
    "autoaugment-arxiv": "43928340",
    "autoaugment-cvpr": "196208260",
    "randaugment-arxiv": "203593374",
    "randaugment-cvpr": "208006202",
}

use_cache = True

all_papers = {}

for k in corpus_ids:
    filename = f"json/{k}.json"
    if use_cache and path.exists(filename):
        with open(filename, "r") as fi:
            content = json.load(fi)
    else:
        url = url_format(corpus_ids[k])
        resp = requests.get(url)
        if resp.ok:
            content = json.loads(resp.content)
            with open(filename, "w") as fo:
                json.dump(content, fo, indent=4)
        else:
            print(resp)
            exit(1)

    citations = content["citations"]
    for cit in citations:
        if "augment" in cit["title"].lower() and cit["venue"]:
            _id = cit["paperId"]

            title = cit["title"]
            venue = cit["venue"]
            semsch_url = cit["url"]
            authors = "\n".join(author["name"] for author in cit["authors"])

            all_papers[_id] = {
                "Venue": venue,
                "Title": title,
                "Authors": authors,
                "Semantic Scholar URL": semsch_url,
            }

with open("csv/autoaug.csv", "w") as fo:
    csv_writer = csv.DictWriter(fo, fieldnames=all_papers[_id].keys())

    csv_writer.writeheader()
    for k in sorted(all_papers, key=lambda k: all_papers[k]["Venue"]):
        csv_writer.writerow(all_papers[k])
