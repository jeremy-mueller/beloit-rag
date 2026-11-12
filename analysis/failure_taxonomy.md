# Failure Taxonomy

## Categories
|Category|Count|Question #s
|-|-|-|
|Missing Context|3|5, 6, 20|
|Refusal with Context|2|7, 23|

## Missing Context
Question 20: A student has 24 earned units and wants to take a course at another college next term. What class year are they, and how much credit can they transfer?\
Answer: I am sorry, but the provided context does not contain information to determine the student's class year based on having 24 earned units.

Retrieved Documents: `catalog-student-records-and-honors`, `registrar-transfer-ap-gce-ib-credit`, `catalog-domain-and-unit-requirements`\
Required Documents: `catalog-adding-dropping-withdrawing`, `registrar-transfer-ap-gce-ib-credit`

Since retrieval did not get the proper document for class year, it refused to answer the entire question. The same is true for the other examples in this category, where it will get one of the documents correct, but not the other and then refuse to answer entirely instead of giving a partial answer.

## Refusal with Context
Question 23: A student fails a course in their first semester and ends with a 0.9 cumulative GPA. Can they repeat the course, and what is their academic standing?\
Answer: I am sorry, but the provided context does not contain information about whether a student can repeat a course after failing it in their first semester.

Retrieved Documents: `catalog-academic-standing`, `catalog-grading-and-incompletes`, `catalog-satisfactory-academic-progress`\
Required Documents: `catalog-grading-and-incompletes`, `catalog-academic-standing`

Snippets:
```
A student may be subject to academic dismissal if his or her cumulative grade point average
at the end of the semester is below 1.0 after the frst term; below 1.5 after the second term;
below 1.65 after the third term; below 1.8 after the fourth term; below 1.85 after the ffth term;
or below 1.9 after the sixth term. A student is subject to academic dismissal for a semester of all “F” grades.
Normally frst-term, frst-year students are not dismissed for academic defciency,
but are instead warned, put on academic probation, or suspended.
```
```
Repeated Courses: Students may repeat a course if they received a grade of “D+” or lower.
```

The necessary context for the question is provided for both parts of the question, but the model still refuses to answer.
