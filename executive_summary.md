# Executive Summary

## Overview / Problem Statement
The goal was to create a system that Beloit College students can use to answer questions about various student affairs at Beloit. We do so by retrieving relevant documents, and giving those documents as context to an LLM to create a grounded response.

## How it does
It got 24 of 29 asked questions correct. The 5 that it got incorrect were only because it had refused to answer a question that it should have been able to with the information available. The 21 questions where it did respond, it responded correctly.

**Example:** "How many total units of earned credit are required to graduate, and how many of those must be completed at Beloit College?"\
**Answer:** All students must have at least 31 units of earned credit to graduate, and at least 16 of those units must be completed at Beloit College.
**Cited Quotes:** "At least 31 units of earned credit. All students must have at least 31 units of earned credit..."\
"At least 16 units must be completed at Beloit College."\
**Cited Sources:** catalog-domain-and-unit-requirements

## Would we let people use it?
Given that it does not directly give any misleading information and the only failures were refusals to answer, we would let people use it. There is no harm in refusing to answer a problem that it could have, but there is plenty of harm in answering a question incorrectly when it should not have tried to answer at all.

If the number of correct refusals was less than the number of unanswerable questions, then we would be weary about letting people use it.