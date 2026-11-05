# Ingestion Plan

## Documents
We currently have **37** documents, of which:\
16 are from the Student Handbook\
11 are from the Course Catalog\
6 are from the Registrar\
3 are from Financial Aid\
1 is the Agreement between Beloit College and BSWU

All of these documents are important for a student to understand general life and schooling at Beloit.

## Chunks
Currently, chunking with a size of 250 is giving us 271 chunks. Chunk size of 750 gives only 97 chunks.

## --check Output
The student handbook and course catalog do not start new pages for new sections. This meant that our pdf splitting by page would include bits from previous sections.

Additionally, every page had a header with a link to return to the table of contents for the student handbook. I dealt with it by manually trimming the documents in the corpus to remove unnecessary information.