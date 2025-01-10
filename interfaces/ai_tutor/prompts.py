QUESTION_DETECTION = """
Your task is to detect the numeric question numbers [1, 2, 3 etc.] and letter questions [a, b, c etc.] that are present in the following text.

Please **do not** include sub-questions such as (i), (ii), (iii) etc.

When deciding whether the number refers to a question, look at the *subsequent text*.

Does it look like a question or a description of a problem for subsequent 
questioning? If so, then it's likely a question.

The first question on the page can either be a number (new question) or a letter (continuation of question on the previous page).

Please respond in the exact order presented on the current page, starting either with a number or a letter, whichever appears on the page first.

If there are any numbered questions on the page, then the first of these numbers will be `{n0}`. 
The presence of this specific number {n0} before any explanatory text or question means that this represents the question number, and should be included in your answer. 
If there are any letters on the page, the *first* letter will be `{c0}`.

Think through your reasoning in detail, step by step.

As the final part of your response, please respond with "answer: " followed by a 
single comma separated list of numbers and letters on a new line, like either of the two examples below:
answer: {n0}, a, b, {n1}, a, {n2}, a, b, c
answer: {c0}, {c1}, {c2}, {n0}, a, b

If you do not see any clear questions on the page, then just explain why, with no comma-seperated list at the end.
"""

QUESTION_ANSWER_DETECTION = """
Your task is to detect the numeric question numbers [1, 2, 3 etc.] and letter 
questions [a, b, c etc.] that are present in the following markscheme text, 
which contains questions and answers.

Please **do not** include sub-questions such as (i), (ii), (iii) etc.

When deciding whether the number refers to a question, look at *all of* the text within 
the corresponding row in the table.

Please ignore general guidelines to the marker, which may also come ordered with 
numbers. If this is what you see, then please give an empty response as explained 
below. Similarly, if the table of questions is part of an Assessment Objectives (AO) 
Grid, then please give an empty response (this is not the mark scheme).

Sometimes the table will not include any headings such as Question, Answer etc. The 
question numbers are always on the left hand side, and M1, M2 indicate the marks for 
each point. If you see this, it means this is part of the mark scheme, and there is 
likely a number and/or letter to be extracted. 

The first question on the page can either be a number (new question) or a letter (continuation of question on the previous page).

Please respond in the exact order presented on the current page, starting either with a number or a letter, whichever appears on the page first.

If there are any numbered questions on the page, then the first of these numbers will be `{n0}`. 
The presence of this specific number {n0} highly suggests that this corresponds to 
the question number, and should be included in your answer. 
Similarly, if there are any letters on the page, the *first* letter will be `{c0}`.

Think through your reasoning in detail, step by step.

As the final part of your response, please respond with "answer: " followed by a 
single comma separated list of numbers and letters on a new line, like either of the two examples below:
answer: {n0}, a, b, {n1}, a, {n2}, a, b, c
answer: {c0}, {c1}, {c2}, {n0}, a, b

If you do not believe any of the text on the screen corresponds to questions in the 
mark scheme table,then just explain why, with no comma-seperated list at the end.
"""

QUESTION_PARSER = """
Your task is to extract the full contents of question {question_number} from the 
following text, and *nothing else*. You should *not* extract any parts of the 
preceding question {preceding} or subsequent question {subsequent}. The question was
parsed from a PDF, and the formatting might be strange or wrong as a result of this
conversion to pure text. If the formatting could be improved to make the question more
readable, please make any formatting improvements as you see fit.
"""

DIAGRAM_DETECTION_ON_PAGE = """
Your task is to determine whether there is a diagram included as part of the pdf page
presented. Given the full text on the page and the screenshot of the page. 
Of course, the PDF screenshot is itself an image, but the question is whether there 
is a *diagram* within the questions presented anywhere on the PDF page, as part of 
one of the questions. 
Simply respond either yes or no as the last part of your response, on a new line.
"""

DIAGRAM_DETECTION_IN_QUESTION = """
Your task is to determine whether the diagrams in the attached screenshot(s) are part of
 question {question_number}, or another question. 
You should *not* consider the preceding question {preceding} or subsequent question
{subsequent}. Looking only at whether the diagram is part of question {question_number}.
simply respond either yes or no as the last part of your response, on a new line.
"""

TEXT_ONLY_DETECTION = """
Your task is to determine whether the following question can be answered in a 
text-only manner, or if it requires drawing on the page in a non-textual manner.
The answer can still be text-only even if there is a diagram as part of the question
(not included in the text you're provided with).
Presuming that the recipient *does* have access to any necessary diagrams, 
we want to determine if the question can be trivially answered via alphanumeric text 
with a keyboard.
Please simply respond on a new line with yes if the question can be answered using 
only a keyboard, and no if it requires drawing on the page in some way,
like one of the following examples:
yes
no
"""

GENERATE_PROMPT = """
Given the following question:
{question}

With the following mark scheme:
{mark_scheme}

Provide an answer to the question which will achieve a score of {achieved_mark} out 
of {available_marks}
"""

STUDENT_PROMPT = """
Answer the following question to the best of your ability:
{question}
"""

JUDGE_PROMPT = """
Given the following question:
{question}

The following mark scheme guidelines for the question:
{guidelines}

And the following response from a student:
{response}

Please inform the student whether their answer was correct, partially correct, 
or incorrect, with a clear justification. Provide this assessment as a string on a new 
line as the final part of your response, like so:
correct|partially correct|incorrect
"""
