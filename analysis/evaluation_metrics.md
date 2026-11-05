

## Why we use the five numbers

Our system can fail in two places. The retriever can hand the generator the wrong text, or the generator can get the right text and still write a wrong answer. A single accuracy number mixes the two together, so a bad score would tell us the system is broken without telling us which half to fix.

These five numbers keep them apart. The first measures retrieval on its own. The next two measure what the generator did with the text it was given. The last two measure whether the system says "I don't know" at the right times. We score refusal in both directions, because refusing too little and refusing too much are opposite problems and need opposite fixes.

---

## The five numbers

### 1. Hit rate

Of the 26 answerable gold questions, how many had the expected document in the three chunks we retrieved.

We score this on the document, not the chunk. If the right document comes back but from the wrong section of it, we still count it as a hit. `retrieve()` ranks chunks, and what we want to know here is whether it pointed at the right source at all. Chunk precision is a separate question, and our chunk size comparison already covers it.

Hit rate sets the ceiling for everything after it. If the right document never arrives, the generator cannot answer from it however good our prompt is. A low hit rate means we fix retrieval before we touch anything else.

**Denominator:** 26 answerable questions. We leave the 3 unanswerable ones out, since they have no expected document to find.

### 2. Quote fidelity

Of the answers that came back with a supporting quote, how many of those quotes appear in the chunk the system said they came from.

Our schema makes the model return a `supporting_quote` with every answer. That quote is a claim about the source text, and we check the claim with a string search. A quote that is not in the chunk means the model wrote something that reads like evidence but is not. We care about this failure more than the others, because it produces confident text with a citation attached that nobody can trace back.

We check the quote against the chunk belonging to whichever document the model named in `source_document`. We want to know whether the quote came from the source the model cited. Whether it picked the right source to begin with is a different question, and hit rate answers that one.

**Denominator:** the answers that returned a quote. A correct refusal returns no quote, so we do not count it as a fidelity failure.

### 3. Correctness

Of all 29 gold questions, how many answers state the same fact we wrote down in advance.

We score this one by hand. The system answers in its own words, and string matching would mark a correct answer wrong for using different ones.

Correctness is also the only one of the five that catches a bad multi-document answer. Nine of our questions need two documents combined, and a response that handles one half and ignores the other can still earn a retrieval hit and a clean quote. Correctness is what marks it wrong.

**Denominator:** all 29 questions. We score an unanswerable question as correct when the system refuses.

**Rubric.** An answer is correct when it states the same fact as our gold answer, in whatever words. An answer is incorrect when it:

- states a different fact,
- leaves out a condition that changes what the person should do, or
- hedges so much that it commits to nothing.

The second case is the one that matters most for a policy corpus. "Yes, you can keep an emotional support animal" is incorrect even though the sentence in it is true. Dropping the prior approval requirement turns the answer into advice that gets a student's animal removed from campus.

**Process.** We each score all 29 on our own, then compare. We settle every disagreement before we report a number. We also record how many we disagreed on at the start, which tells us whether the rubric is doing any work.

### 4. Correct refusals

Of the 3 questions our corpus cannot answer, how many the system declined.

A refusal means `answer_found_in_context` came back `false`. Hedged prose with the flag set to `true` is a claimed answer, and we score it as one.

**Denominator:** 3. We report this as a fraction because three questions is thin evidence. A result of 2 of 3 sits one coin flip away from 3 of 3, so we should not read much into either.

### 5. Wrong refusals

Of the 26 answerable questions, how many the system refused anyway.

This number stops us gaming the last one. Any system scores 3 of 3 on correct refusals by refusing everything, so measuring refusal in one direction rewards a system that never answers. Taken together, the two tell us whether our refusal threshold is calibrated.

A wrong refusal usually means retrieval missed and the generator behaved well on bad input. When we see one, we check its hit rate row first. If the expected document never arrived, the generator did its job and the problem sits in retrieval.

---

## Decisions we hold fixed

| Decision | Setting |
|---|---|
| Retrieval depth | k = 3. A hit means the expected document is in those three. |
| Hit granularity | Document level, not chunk level. |
| Quote matching | Lowercase, collapse runs of whitespace, then substring search. No stemming and no fuzzy matching. We check it in code and never by eye. |
| Quote comparison target | The chunk from the document named in `source_document`. |
| Refusal | `answer_found_in_context == false`. Hedged prose with the flag `true` does not count. |
| Unanswerable marker | `expected_source` is `None`. |
| Correctness | Hand scored, both of us on our own, disagreements settled before we report. |
| Temperature | 0.0, so a second run gives the same numbers. |

---

## How we compute them

Field names below match `pipeline.ipynb`. `retrieve()` returns dicts with `source` and `text`, and our response schema returns `answer_found_in_context`, `answer`, `supporting_quote` and `source_document`. Note that `expected_source` holds the `.txt` filename, since that is what `retrieve()` puts in `source`. The document ids in `evaluation_set.md` are bare.

```python
import json, time
import pandas as pd

def norm(s):
    return " ".join((s or "").lower().split())

rows = []
for item in eval_set:                       # all 29 gold questions
    retrieved = retrieve(item["question"], k=3)
    retrieved_sources = [d["source"] for d in retrieved]

    result = json.loads(ask_system(item["question"]))

    quote = result.get("supporting_quote", "")
    cited = result.get("source_document", "")
    # the chunk the model says it quoted from
    cited_chunk = next((d["text"] for d in retrieved if d["source"] == cited), "")

    rows.append({
        "qid":            item["qid"],
        "answerable":     item["expected_source"] is not None,
        "hit":            int(item["expected_source"] in retrieved_sources)
                          if item["expected_source"] else None,
        "returned_quote": int(bool(quote)),
        "quote_found":    int(norm(quote) in norm(cited_chunk)) if quote else 0,
        "correct":        None,             # we fill this in by hand
        "refused":        int(result.get("answer_found_in_context") is False),
    })
    time.sleep(4)                           # the API rate limits us without this

pd.DataFrame(rows).to_csv("analysis/eval_rows.csv", index=False)
```

Once we have both filled in the `correct` column and settled our disagreements:

```python
df     = pd.read_csv("analysis/eval_rows.csv")
ans    = df[df.answerable]                  # 26 answerable
unans  = df[~df.answerable]                 # 3 unanswerable
quoted = df[df.returned_quote == 1]

print("hit rate:        ", int(ans.hit.sum()),            "of", len(ans))
print("quote fidelity:  ", int(quoted.quote_found.sum()), "of", len(quoted))
print("correctness:     ", int(df.correct.sum()),         "of", len(df))
print("correct refusals:", int(unans.refused.sum()),      "of", len(unans))
print("wrong refusals:  ", int(ans.refused.sum()),        "of", len(ans))
```

Writing the rows out to `eval_rows.csv` between the two steps matters. Hand scoring takes a while, and without the file every disagreement we want to recheck costs us another full run against the API.

---

## What these five do not capture

We should say this plainly so we do not over read our own numbers.

**Hit rate only half measures our multi-document questions.** Nine of the 29 need two documents combined. Hit rate as we have defined it checks one expected document, so a question that retrieved one of its two sources counts as a full hit. We list the document the answer leans on most as `expected_source` and keep the second one in an `also_requires` field that the five metrics ignore. If our hand scoring shows multi-document questions failing correctness while passing hit rate, that field is what we use to diagnose it, and the count of questions where both documents came back is worth a sentence in `results.md` even though it is not one of the five.

**Three unanswerable questions is a small denominator.** Both refusal numbers rest on very little. We report them as fractions and we hold off on concluding much from either.

**Quote fidelity does not check relevance.** A quote can sit in the cited chunk and still not support the answer built on top of it. Correctness is what catches that, which is part of why we score correctness by hand.

---

## Reporting

Every number goes into `results.md` as a fraction with its denominator, so "22 of 26" and not "85%". With denominators of 26, 29 and 3, a percentage claims a precision our sample size does not support. The 3 question denominator is the worst case, since it would read as "67%" and hide how thin the evidence is.

Alongside the five, we report how many correctness disagreements we had before settling them. A high count means our rubric was too loose, and the correctness number deserves less weight than the other four.
