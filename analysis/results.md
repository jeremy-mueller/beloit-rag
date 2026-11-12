# Results

## Baseline System
Our baseline system used a chunk size of 250, retrieved 3 documents, and used the following prompt:

```
You are an assistant answering questions for a Beloit College community member.
Use ONLY the provided context below. 
If the context does not contain the answer, set answerable to False and refuse to answer.

Context:
{context_str}

Question: {query}
```

## "Improved" System
Our attempt at an improved system used the same settings as above, except increasing the number of retrieved documents in an attempt to improve the hit rate.

## Metrics
|Metric|Baseline|Improved|Difference|
|-|-|-|-|
|Hit Rate|18 of 26|21 of 26|+3|
|Quote Fidelity|21 of 21|20 of 21|-1|
|Correctness|24 of 29|24 of 29|0|
|Correct Refusals|3 of 3|3 of 3|0|
|Wrong Refusals|5 of 26|5 of 26|0|

## Conclusion
The improvement did increase our hit rate, but it also decreased our quote fidelity (likely because there was more to work with and it got tripped up) and kept everything else the same.
