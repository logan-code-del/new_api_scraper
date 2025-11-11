from fastapi import FastAPI
import feedparser, requests, re, time
from newspaper import Article
from bs4 import BeautifulSoup
import spacy
from sentence_transformers import SentenceTransformer, util
from dateutil import parser as dateparser

app = FastAPI()

# -------------------------------------------
# CONFIG
# -------------------------------------------
RSS_FEEDS = [
    "http://feeds.reuters.com/reuters/topNews",
    "https://www.bbc.co.uk/feeds/rss/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
]

MAX_ARTICLES = 5
MIN_SUPPORTING_SOURCES = 2
SIMILARITY_THRESHOLD = 0.68

nlp = spacy.load("en_core_web_sm")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------------------------
# UTILS
# -------------------------------------------
def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def fetch_rss(limit=30):
    articles = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)
        for e in parsed.entries:
            articles.append({
                "title": e.get("title"),
                "link": e.get("link"),
                "source": parsed.feed.get("title", feed),
                "published": e.get("published")
            })
    # Sort newest first
    def dt(e):
        try:
            return dateparser.parse(e["published"])
        except:
            return dateparser.parse("1970-01-01")
    articles = sorted(articles, key=dt, reverse=True)
    return articles[:limit]


def get_article_text(url):
    try:
        art = Article(url); art.download(); art.parse()
        return clean(art.text)
    except:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            return clean(" ".join(p.get_text() for p in soup.find_all("p")))
        except:
            return ""


def extract_statements(text):
    doc = nlp(text)
    out = []
    for s in doc.sents:
        st = s.text.strip()
        if len(st) < 35:
            continue
        if any(x in st.lower() for x in ["i think", "opinion", "we believe"]):
            continue
        out.append(clean(st))
    return out


def build_corpus(rss_articles, exclude):
    corpus = []
    for a in rss_articles:
        if a["link"] == exclude:
            continue
        t = get_article_text(a["link"])
        if t:
            corpus.append({"url": a["link"], "source": a["source"], "text": t})
    return corpus


def cross_reference(statement, corpus):
    out = []
    stmt_emb = embed_model.encode(statement, convert_to_tensor=True)
    for doc in corpus:
        sentences = [
            s for s in re.split(r"(?<=[.!?])\s+", doc["text"])
            if len(s) > 40
        ]
        if not sentences:
            continue
        emb = embed_model.encode(sentences, convert_to_tensor=True)
        sims = util.cos_sim(stmt_emb, emb)[0]
        top = int(sims.argmax())
        score = float(sims[top])
        if score >= SIMILARITY_THRESHOLD:
            out.append({
                "source": doc["source"],
                "url": doc["url"],
                "matched_sentence": sentences[top],
                "similarity": score
            })
    return out


# -------------------------------------------
# API ROUTES
# -------------------------------------------
@app.get("/")
def root():
    return {"status": "OK", "endpoints": ["/news"]}


@app.get("/news")
def get_news():
    rss = fetch_rss(MAX_ARTICLES * 3)
    selected = rss[:MAX_ARTICLES]

    output = []

    for a in selected:
        text = get_article_text(a["link"])
        if not text:
            continue

        statements = extract_statements(text)
        corpus = build_corpus(rss, exclude=a["link"])

        results = []
        corroborated = []
        uncorroborated = []

        for st in statements:
            support = cross_reference(st, corpus)
            entry = {
                "statement": st,
                "support_count": len(support),
                "supporting_sources": support
            }
            if len(support) >= MIN_SUPPORTING_SOURCES:
                corroborated.append(entry)
            else:
                uncorroborated.append(entry)

            results.append(entry)

        output.append({
            "title": a["title"],
            "url": a["link"],
            "published": a["published"],
            "corroborated_facts": corroborated,
            "uncorroborated_claims": uncorroborated
        })

        time.sleep(1)

    return output
