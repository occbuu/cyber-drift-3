import requests
import sys

sys.stdout.reconfigure(encoding="utf-8")

queries = [
    "open set network intrusion detection zero day",
    "network intrusion detection distribution shift temporal",
    "conformal prediction false discovery rate novelty detection",
    "conformal prediction online covariate shift time series",
    "network intrusion detection survey deep learning 2023",
    "intrusion detection CICIDS2017 CSE-CIC-IDS2018 ToN-IoT dataset",
]

for query in queries:
    url = "https://api.crossref.org/works"
    params = {"query": query, "filter": "from-pub-date:2018-01-01,type:journal-article", "rows": 20}
    data = requests.get(url, params=params, timeout=30).json()["message"]["items"]
    print("\n###", query)
    for item in data:
        title = (item.get("title") or [""])[0].replace("\n", " ")
        year = (item.get("published-print") or item.get("published-online") or item.get("issued") or {}).get("date-parts", [[None]])[0][0]
        doi = item.get("DOI", "")
        journal = (item.get("container-title") or [""])[0]
        print(f"{year}\t{doi}\t{journal}\t{title}")
