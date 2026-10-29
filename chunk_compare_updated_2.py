#!/usr/bin/env python3
"""
DSDA 310 - chunk size comparison (In-class, Oct 29).
Taman & Jeremy - Project 2 (beloit-rag).

    python3 -m pip install --user scikit-learn
    python3 chunk_compare.py                 # uses SIZES below
    python3 chunk_compare.py 250 500 750     # or pass your own sizes

Run it from the repo root, so that corpus/ is beside it.

Retrieval here is TF-IDF keyword matching, the same method as the first half of
ICA 10. It is NOT what Project 2 will use. It is here because today's question
is what chunk SIZE does, and holding the search method fixed is how you see that
on its own.

WHAT CHANGED FROM THE HANDOUT VERSION
  1. chunk() is written: word windows, overlap, sentence-boundary snapping.
  2. CORPUS points at corpus/, not documents.tsv. documents.tsv is the INPUT
     manifest (id, kind, url, title, pages) - it never held document text, so
     pointing a chunker at it could not have worked. corpus/*.txt is the output
     of ingestion and is what gets chunked.
  3. The script grades itself. analysis/test_questions.md records the source
     document for every question, so GOLD below encodes those, and the report
     answers "did the right document come back first?" instead of leaving it to
     you to squint at previews.
  4. Q10 (the unanswerable one) is included on purpose. It has no gold
     document, so its top score shows what a confident-looking false positive
     is worth at each size - which is a threshold decision for Project 2.
"""
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CORPUS
# ---------------------------------------------------------------------------
CORPUS = Path("corpus")

# The sizes being compared today, in words.
SIZES = [250, 750]

# (short label, question text, gold document ids, answer probes)
#
# gold   - source documents from analysis/test_questions.md. Empty means the
#          corpus genuinely does not answer it.
# probes - literal strings from the expected answer. A chunk that is missing one
#          of these cannot support a complete answer even if it ranks first, so
#          this is how the script checks handout question 2 (does the top chunk
#          hold the WHOLE answer) instead of leaving it to eyeballing previews.
QUESTIONS = [
    ("Q1 full-time units",
     "What is the minimum number of units a student must be registered for to be considered full-time?",
     ["catalog-adding-dropping-withdrawing"],
     ["full-time", "3.0 units", "2.25", "1.50"]),
    ("Q2 housing exemption",
     "Which students are exempt from the requirement to live in College housing during their first six credit terms?",
     ["handbook-housing-living-on-campus"],
     ["six credit terms", "married", "veteran", "dependent", "30-minute"]),
    ("Q3 ESA approval",
     "Who must approve an emotional support animal before a student brings it to campus?",
     ["handbook-disability-and-support-animals"],
     ["Director of Learning Enrichment", "prior to bringing"]),
    ("Q10 parking cost",
     "How much does a student parking permit cost?",
     [],      # unanswerable - verified absent in handbook-motor-vehicles-parking
     []),
]

# ---------------------------------------------------------------------------
# THE CHUNKING DECISIONS - these are what goes in ingestion_plan.md
# ---------------------------------------------------------------------------
# 1. OVERLAP. A sentence that straddles a boundary leaves neither chunk holding
#    the whole answer. Repeating the tail of each chunk at the head of the next
#    fixes that, and costs storage. Set as a FRACTION of chunk size so the two
#    sizes are compared on equal terms: 250 -> 30 words, 750 -> 90. A flat word
#    count would give the small size more relative redundancy and you would be
#    moving two variables at once.
OVERLAP_FRACTION = 0.12

# 2. BOUNDARIES. Cutting at exactly `size` words cuts mid-sentence. Instead look
#    for the nearest sentence end or paragraph break within this fraction of the
#    target. Chunks then vary in length: cleaner text, less predictable size.
#    0.0 disables snapping.
SNAP_FRACTION = 0.20

# 3. THE HEADER. Keeping the title OUT of the chunk text means it travels as
#    metadata and does not affect the match. Flip to True and the ESA chunks
#    start matching on "Disability Policy" wording from the title even where the
#    body text of that chunk never says it. Worth running once both ways before
#    you defend either choice in the plan.
TITLE_IN_CHUNK = False

# 4. BOILERPLATE. Every page of the handbook PDF carries a running header that
#    says to click to return to the table of contents. Repeated across ~30
#    documents it adds nothing and eats chunk budget. The [page N] markers are
#    kept, because they are what makes a retrieved chunk citable back to a page.
STRIP_BOILERPLATE = True
BOILERPLATE = [
    re.compile(r"Click here to return to Table of Contents\s*", re.I),
]

# A tail shorter than this after snapping is folded into the previous chunk.
MIN_CHUNK_WORDS = 40

# How deep to look when reporting where the gold document actually landed.
SEARCH_DEPTH = 10


def need(mod, pipname=None):
    try:
        return __import__(mod)
    except ImportError:
        sys.exit(f"Missing package '{mod}'. Run:  python3 -m pip install --user {pipname or mod}")


# ---------------------------------------------------------------------------
# LOADING
# ---------------------------------------------------------------------------
def load_documents():
    """Read corpus/*.txt, split the ingest header off, return (id, title, body)."""
    if not CORPUS.exists():
        sys.exit(f"Cannot find {CORPUS}/. Run this from the repo root.")
    docs = []
    for path in sorted(CORPUS.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        head, _, body = text.partition("-" * 60 + "\n")
        if not body:
            head, body = "", text
        title = ""
        for line in head.splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
        if STRIP_BOILERPLATE:
            for pat in BOILERPLATE:
                body = pat.sub("", body)
        docs.append((path.stem, title or path.stem, body.strip()))
    if not docs:
        sys.exit(f"{CORPUS}/ has no .txt files. Run the ingest script first.")

    lengths = sorted(len(b.split()) for _, _, b in docs)
    print(f"{len(docs)} documents, {sum(lengths):,} words "
          f"(shortest {lengths[0]:,}, median {lengths[len(lengths) // 2]:,}, "
          f"longest {lengths[-1]:,})")

    known = {d for _, _, g, _ in QUESTIONS for d in g}
    missing = known - {d for d, _, _ in docs}
    if missing:
        print(f"  WARNING: gold documents not in corpus/: {', '.join(sorted(missing))}")
    return docs


# ---------------------------------------------------------------------------
# CHUNKING
# ---------------------------------------------------------------------------
_SENTENCE_END = re.compile(r"[.!?][\"')\]]*$")
_ABBREV = {"mr.", "mrs.", "ms.", "dr.", "prof.", "st.", "no.", "vs.", "etc.",
           "e.g.", "i.e.", "approx.", "dept.", "u.s.", "p.m.", "a.m."}


def _tokenize(body):
    """Words plus a flag per word marking where a chunk may legally end."""
    words, breaks = [], []
    for para in re.split(r"\n\s*\n", body):
        ws = para.split()
        if not ws:
            continue
        for w in ws:
            words.append(w)
            breaks.append(bool(_SENTENCE_END.search(w)) and w.lower() not in _ABBREV)
        breaks[-1] = True  # a paragraph break is always a legal stop
    return words, breaks


def _snap(breaks, target, window, low, high):
    """Nearest legal break to `target` within +/- window, else `target`."""
    for d in range(window + 1):
        for cand in ((target - d), (target + d)):
            if low < cand <= high and breaks[cand - 1]:
                return cand
    return min(max(target, low + 1), high)


def chunk(body, size, title=None):
    """
    Split one document into overlapping chunks of roughly `size` words.

    Take words `size` at a time, nudge each cut to the nearest sentence or
    paragraph end within SNAP_FRACTION of the target, then start the next chunk
    OVERLAP_FRACTION * size words back from that cut. Every word of body appears
    in at least one chunk.
    """
    words, breaks = _tokenize(body)
    n = len(words)
    if n == 0:
        return []

    overlap = max(0, round(size * OVERLAP_FRACTION))
    window = max(0, round(size * SNAP_FRACTION))

    pieces, start = [], 0
    while start < n:
        target = start + size
        if target >= n:
            end = n
        else:
            end = _snap(breaks, target, window, start, n)
            if n - end < MIN_CHUNK_WORDS:   # ragged tail, absorb it
                end = n
        piece = " ".join(words[start:end])
        if TITLE_IN_CHUNK and title:
            piece = f"{title}. {piece}"
        pieces.append(piece)
        if end >= n:
            break
        start = max(end - overlap, start + 1)   # max() guarantees progress
    return pieces


def build(docs, size):
    """Chunk every document; return parallel lists of text, doc id, chunk id."""
    texts, doc_ids, chunk_ids = [], [], []
    for doc_id, title, body in docs:
        for i, piece in enumerate(chunk(body, size, title)):
            piece = piece.strip()
            if piece:
                texts.append(piece)
                doc_ids.append(doc_id)
                chunk_ids.append(f"{doc_id}#{i}")
    return texts, doc_ids, chunk_ids


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------
def search(texts, questions, top=SEARCH_DEPTH):
    """TF-IDF cosine. Returns, per question, a list of (index, score)."""
    need("sklearn", "scikit-learn")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform(texts)
    out = []
    for q in questions:
        scores = cosine_similarity(vec.transform([q]), matrix)[0]
        out.append(sorted(enumerate(scores), key=lambda p: -p[1])[:top])
    return out


def probes_in(text, probes):
    """Which answer probes the given chunk actually contains."""
    low = text.lower()
    return [p for p in probes if p.lower() in low]


def first_complete(ranked, texts, probes):
    """1-based rank of the first chunk holding EVERY probe, or None."""
    for rank, (idx, _) in enumerate(ranked, start=1):
        if len(probes_in(texts[idx], probes)) == len(probes):
            return rank
    return None


def gold_rank(ranked, doc_ids, gold):
    """1-based rank of the first chunk from a gold document, or None."""
    for rank, (idx, _) in enumerate(ranked, start=1):
        if doc_ids[idx] in gold:
            return rank
    return None


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------
def main():
    sizes = [int(a) for a in sys.argv[1:]] or SIZES

    docs = load_documents()
    raw_words = sum(len(b.split()) for _, _, b in docs)
    print(f"\nsettings: overlap {OVERLAP_FRACTION:.0%}, snap {SNAP_FRACTION:.0%}, "
          f"title in chunk: {TITLE_IN_CHUNK}, strip boilerplate: {STRIP_BOILERPLATE}\n")

    texts_only = [q for _, q, _, _ in QUESTIONS]
    results = {}
    for size in sizes:
        texts, doc_ids, chunk_ids = build(docs, size)
        lens = [len(t.split()) for t in texts]
        stored = sum(lens)
        print(f"size {size:>4}:  {len(texts):>4} chunks | "
              f"min {min(lens)}, mean {stored // len(texts)}, max {max(lens)} words | "
              f"{stored:,} stored vs {raw_words:,} original "
              f"(+{(stored / raw_words - 1):.0%} overlap cost)")
        results[size] = (texts, doc_ids, chunk_ids, search(texts, texts_only))

    print()
    grid = {}
    for qi, (label, question, gold, probes) in enumerate(QUESTIONS):
        print("=" * 76)
        print(f"{label}:  {question}")
        print(f"  gold document: {gold[0] if gold else '(none - unanswerable)'}")
        for size in sizes:
            texts, doc_ids, chunk_ids, ranked = results[size]
            hits = ranked[qi]
            print(f"\n  --- chunks of {size} words ---")
            for rank, (idx, score) in enumerate(hits[:3], start=1):
                mark = " <-- GOLD" if doc_ids[idx] in gold else ""
                preview = " ".join(texts[idx].split())[:150]
                print(f"  {rank}. {score:.4f}  {chunk_ids[idx]}{mark}")
                print(f"     ({len(texts[idx].split())} words) {preview}...")
            gap = hits[0][1] - hits[1][1] if len(hits) > 1 else 0.0
            gr = gold_rank(hits, doc_ids, gold)
            if gold:
                verdict = "HIT at #1" if gr == 1 else (
                    f"MISS - gold at #{gr}" if gr else f"MISS - gold not in top {SEARCH_DEPTH}")
            else:
                verdict = f"top score {hits[0][1]:.4f} on a question with no answer"
            print(f"     gap 1st-2nd: {gap:.4f}"
                  f"{'  <- near coin flip' if gap < 0.02 else ''}   {verdict}")

            complete = None
            if probes:
                have = probes_in(texts[hits[0][0]], probes)
                complete = len(have) == len(probes)
                missing = [p for p in probes if p not in have]
                fc = first_complete(hits, texts, probes)
                print(f"     answer probes in the #1 chunk: {len(have)}/{len(probes)}"
                      + ("  COMPLETE" if complete
                         else f"  INCOMPLETE - missing {missing}"))
                if not complete:
                    print(f"     first chunk holding the whole answer is at rank "
                          f"{fc if fc else '>' + str(SEARCH_DEPTH)}")
            grid[(label, size)] = (gr if gold else None, gap, hits[0][1],
                                   bool(gold), complete)
        print()

    # ---- summary -----------------------------------------------------------
    print("=" * 76)
    print("SUMMARY\n")
    head = f"{'question':<24}" + "".join(f"{'size ' + str(s):<34}" for s in sizes)
    print(head)
    print("-" * len(head))
    for label, _, gold, _ in QUESTIONS:
        row = f"{label:<24}"
        for size in sizes:
            gr, gap, top, has_gold, complete = grid[(label, size)]
            if has_gold:
                tag = "HIT" if gr == 1 else f"MISS@{gr or '>' + str(SEARCH_DEPTH)}"
                cell = f"{tag}  {'whole answer' if complete else 'PARTIAL'}  gap {gap:.3f}"
            else:
                cell = f"top {top:.3f}  gap {gap:.3f}"
            row += f"{cell:<34}"
        print(row)

    answerable = [q for q in QUESTIONS if q[2]]
    print()
    for size in sizes:
        hits = sum(1 for label, *_ in answerable if grid[(label, size)][0] == 1)
        whole = sum(1 for label, *_ in answerable if grid[(label, size)][4])
        print(f"  size {size}: gold document ranked #1 on {hits}/{len(answerable)}; "
              f"#1 chunk held the complete answer on {whole}/{len(answerable)}")

    print("""
Write down, per question per size:
  1. Right document first?  The HIT/MISS column answers this.
  2. Does the top chunk contain the WHOLE answer or part of it?  The probe
     line answers this. PARTIAL means the retriever found the right document
     but handed the generator a chunk that cannot support the full answer.
  3. How close was second place?  Under ~0.02 and the ranking was a coin flip
     that a reworded question would likely tip, exactly like the Coverage
     collision in ICA 10 D3.

Then one sentence for ingestion_plan.md: which size, and what it costs - the
overlap cost line gives you storage, the mean chunk length gives you how much
irrelevant text rides along with every hit, and Q10 gives you the score a
confident wrong answer earns when the corpus has nothing.
""")


if __name__ == "__main__":
    main()
