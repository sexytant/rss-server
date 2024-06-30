from hashlib import md5
from fastapi import APIRouter, Response
from feedgen.feed import FeedGenerator
from unstructured.partition.html import partition_html

router = APIRouter()

URL = "https://www.sekai-cheese.co.jp/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"


def parse():
    """
    Parse the Sekai Cheese website and extract the event dates
    :return: list of event dates
    """
    header = {"User-Agent": USER_AGENT}
    elements = partition_html(url=URL, headers=header)

    parsed_data = []

    parsed_contents_area = False
    for elem in elements:
        meta = elem.metadata.to_dict()
        if "emphasized_text_contents" in meta and "#チーズを捨てない" in " ".join(meta["emphasized_text_contents"]):
            parsed_contents_area = True
            continue
        if parsed_contents_area:
            if "b" not in meta["emphasized_text_tags"]:
                parsed_contents_area = False
                break
            parsed_data.append(meta["emphasized_text_contents"])

    flattened_data = sum(parsed_data, [])
    all_list = [d.replace("、", "").replace("～", "-") for d in flattened_data]
    all_set = list(dict.fromkeys(all_list))
    return all_set


@router.get("/sekai-cheese")
def generate_rss():
    all_event_date=parse()

    fg = FeedGenerator()
    fg.title("世界チーズ商会 ガレージセールRSS")
    fg.link(href="https://www.sekai-cheese.co.jp/", rel="alternate")
    fg.description("世界チーズ協会の毎月のガレージセールをRSS配信します")

    fe = fg.add_entry()
    content = ",".join(all_event_date)
    fe.title(content)
    fe.guid(md5(content.encode()).hexdigest(), permalink=False)
    fe.link(href="https://www.sekai-cheese.co.jp/")

    # XML文字列を生成し、レスポンスとして返す
    rss_str = fg.rss_str(pretty=True)
    return Response(content=rss_str, media_type="application/xml")
