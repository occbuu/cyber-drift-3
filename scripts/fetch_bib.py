import requests
import re
import html
import unicodedata
from pathlib import Path

items = {
    "almeida2025survey": "10.1007/s44163-025-00578-1",
    "cevallos2025hero": "10.1016/j.comnet.2025.111264",
    "comnet2024fedsurvey": "10.1016/j.comnet.2024.111023",
    "cose2024sequential": "10.1016/j.cose.2024.103928",
    "guerra2023shift": "10.3390/computers12100209",
    "mohammadi2020survey": "10.1016/j.jnca.2020.102767",
    "khraisat2019survey": "10.3390/app9204396",
    "iot2024feature": "10.1016/j.iot.2024.101367",
    "csa2024iot": "10.1016/j.csa.2024.100082",
    "mnet2024canopen": "10.1109/mnet.2024.3367303",
    "mnet2023federated": "10.1109/mnet.018.2200349",
    "comnet2025trafficllm": "10.1016/j.comnet.2025.111847",
    "aos2024adaptive": "10.1214/23-AOS2338",
    "test2024conformal": "10.1007/s11749-024-00934-w",
    "jrssb2025sets": "10.1093/jrsssb/qkae120",
    "jrssb2024covshift": "10.1093/jrsssb/qkad069",
    "jrssb2024doubly": "10.1093/jrsssb/qkae009",
    "biomet2023localized": "10.1093/biomet/asac040",
    "biomet2025null": "10.1093/biomet/asae051",
    "tii2025conformal": "10.1109/TII.2025.3529920",
    "applied2025timeseries": "10.1007/s10489-025-06708-7",
    "aos2018onlinefdr": "10.1214/17-AOS1559",
    "aos2024edge": "10.1214/24-AOS2359",
    "biomet2026weighted": "10.1093/biomet/asaf066",
    "neurips2025nonexchange": "10.52202/085713-5278",
    "neurips2025risk": "10.52202/085713-2355",
    "biomet2023evalues": "10.1093/biomet/asad057",
    "biomet2024evalues": "10.1093/biomet/asae050",
    "uq2024nids": "10.1007/s40860-024-00238-8",
    "comnet2025bayesian": "10.1016/j.comnet.2025.111436",
    "patcog2023bridge": "10.1016/j.patcog.2023.109385",
    "aaai2023contrastive": "10.1609/aaai.v37i9.26253",
    "patcog2024semantic": "10.1016/j.patcog.2024.110781",
    "ieee2024shift": "10.1109/access.2024.3350197",
    "ciciomt2024benchmark": "10.1016/j.iot.2024.101351",
    "cicids2021case": "10.1109/spw53761.2021.00009",
    "ton2021architecture": "10.1016/j.scs.2021.102994",
    "ton2020federated": "10.1109/trustcom50675.2020.00114",
    "network2025survey": "10.3390/network6020041",
}

def clean(s):
    value = html.unescape(str(s or ""))
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return value.replace("&", r"\&").replace("_", r"\_")

def author_text(authors):
    out=[]
    for a in authors or []:
        fam=clean(a.get("family")); giv=clean(a.get("given"))
        out.append(f"{fam}, {giv}" if giv else fam)
    return " and ".join(out)

def year(item):
    for key in ("published-print", "published-online", "issued", "created"):
        p=item.get(key, {}).get("date-parts", [])
        if p and p[0]: return p[0][0]
    return ""

def bib(key, item, doi):
    title=clean((item.get("title") or [""])[0]).replace("{", "").replace("}", "")
    journal=clean((item.get("container-title") or [""])[0])
    fields=[f"  author  = {{{author_text(item.get('author'))}}}",
            f"  title   = {{{title}}}",
            f"  journal = {{{journal}}}",
            f"  year    = {{{year(item)}}}",
            f"  doi     = {{{doi}}}"]
    if item.get("volume"): fields.insert(4, f"  volume  = {{{item['volume']}}}")
    if item.get("issue"): fields.insert(5, f"  number  = {{{item['issue']}}}")
    if item.get("page"): fields.insert(5, f"  pages   = {{{item['page']}}}")
    return "@article{"+key+",\n"+",\n".join(fields)+"\n}\n"

out=[]
for key, doi in items.items():
    try:
        item=requests.get("https://api.crossref.org/works/"+doi,timeout=30).json()["message"]
        out.append(bib(key,item,doi))
    except Exception as exc:
        print("FAILED", key, doi, exc)
Path("elsarticle_21/references_recent.bib").write_text("\n".join(out), encoding="utf-8")
print("wrote", len(out), "entries")
