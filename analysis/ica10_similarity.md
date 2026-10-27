# In-Class Activity 10
Jeremy Mueller\
Taman Azad

## Passages
All passages come from [Agreement between Beloit College and Beloit Student Workers United, 2025-2027](https://www.beloit.edu/live/blurbs/agreement-beloit-college-and-beloit-student-workers-united). Each passage corresponds with an article of the same name.
* just-cause (Article 6)
* pay-cycle (Article 7)
* health-safety-breaks-leave (Article 10)
* job-postings (Article 11)
* wages-and-compensation (Article 13)
* holiday-pay (Article 14)
* hours-worked (Article 15)
* scheduling (Article 16)
* healthcare (Article 17)

## Questions
1. What's the current base wage for beloit college student workers as of October 22nd, 2026
2. If I hold a student worker role/job on campus that falls on Tier 3, what is my expected hourly compensation?
3. Will there be a pay increase soon?
4. Will I have to find coverage if I fall ill?

## D1
Q: What's the current base wage for beloit college student workers as of October 22nd, 2026?\
    0.254  wages-and-compensation

Q: If I hold a student worker role/job on campus that falls on Tier 3, what is my expected hourly compensation?\
    0.145  wages-and-compensation

Q: Will there be a pay increase soon?\
    0.157  wages-and-compensation

## D2
Question: Will I have to find coverage if I fall ill?

Passage: If a Student Worker reports to their supervisor that they are sick, the Student Worker will not have the responsibility to find a substitute for their shift, and they will not be required to work while sick. (health-safety-breaks-leave)

## D3
Q: Will I have to find coverage if I fall ill?\
    0.090  wages-and-compensation\
    0.000  just-cause\
    0.000  pay-cycle

wages-and-compensation won, but the actual passage that covered sick days was health-safety-breaks-leave. This is likely because wages-and-compensation has a subarticle titled “Coverage”, although it is used in a different context. This shows that the keyword method needs exact wording.

## D4
We predict that the embedding half will accurately select health-safety-breaks-leave as the passage that will answer question 4. We believe this because embeddings will be able to understand the nuances between different words that the plain keyword method could not.

## D5
0.650  healthcare\
0.640  health-safety-breaks-leave

While it did not get health-safety-breaks-leave as the primary passage, the gap between it and the first place is very small (0.01).

## Reflection
1. The keyword method only looked for the exact words from our question in the passage. When the question does not share any exact words with the passage, the keyword method is unable to match any. This tells us that it cannot measure anything with the same meaning as long as words are different.
2. The gap between the top two passages in the embedding run is very small. This tells us that it can be confident about multiple passages and that the top passage on its own may not be the answer. You would likely want to consider any passages above a certain score.
3. If the retrieval picks the wrong passage, then the system would be forced to answer the question using a passage that can’t actually answer what is being asked. You would find out that this happened by manually investigating the question, selected passage, and answer it gives to see if everything makes sense.