import json
import os
import requests
import re

from dotenv import load_dotenv

from process_learning_objectives import extract_qs, extract_cs_questions

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)
url = "https://api.unify.ai/v0/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ.get('UNIFY_API_KEY')}",
}


def generate(prompt, sys_prompt=None):
    messages = [{"role": "user", "content": prompt}]

    if sys_prompt:
        messages = [{"role": "system", "content": sys_prompt}] + (messages)

    payload = {
        "model": "claude-3.5-sonnet@aws-bedrock",
        # "model": "gpt-4o@openai",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 4096,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(response.status_code)
        print(response.text)
        raise Exception


def extract(s):
    pattern = r"<question>([\s\S]*?)<\/question>"
    matches = re.findall(pattern, s)
    return [m.strip() for m in matches]


def find_tags(s):
    pattern = r"<([^/]*?)>"
    return re.findall(pattern, s)


def extract_tags(tag, s):
    pattern = f"<{tag}>(.*?)</{tag}>"
    try:
        return re.findall(pattern, s, re.DOTALL)[0]
    except:
        print(f"failed to extract {tag} from \n {s}")
        return []


## ONE MARKERS
def short_q_template(specification_point):
    example_specification_point = "P1.1b describe the atom as a positively charged nucleus surrounded by negatively charged electrons, with the nuclear radius much smaller than that of the atom and with almost all of the mass in the nucleus"

    example_q1 = (
        "How does the size of the nucleus compare to the size of the entire atom?"
    )
    example_q2 = "Where is most of the mass of an atom located?"
    example_q3 = "Which subatomic particles are found orbiting the nucleus?"

    prompt = f"""You are helping a high-school teacher create questions, based on points in the course syllabus. 
    Respond with questions, insde the <question> tag as in the example.
    It should be a one-mark question, i.e. only testing a single piece of knowledge.
    It doesn't have to test the whole point from the specification.

    <example>
    <specification>
    {example_specification_point}
    </specification>

    <question>
    {example_q1}
    </question>

    <question>
    {example_q2}
    </question>

    <question>
    {example_q3}
    </question>
    </example>

    <specification>
    {specification_point}
    </specification>
    """
    return prompt


def short_q_answer(specification_point, question):

    example_question = "What type of field does all matter possess?"
    example_specification_point = "P2.3g describe that all matter has a gravitational field that causes attraction, and the field strength is much greater for massive objects"
    example_mark_scheme = """1 mark: Gravitational field

Additional guidance for markers:
- The answer must specifically state "gravitational field" to receive the mark.
- Do not accept "gravity" alone, as the question asks for the type of field."""

    prompt = f"""
You are a high-school teacher, helping to write a mark scheme for a question.
Give your answer inside <mark_scheme> </mark_scheme> tags. Also return the number of marks at the end, inside <number_of_marks> tags, as in the example.


<example>
    <question>
    {example_question}
    </question>

    <syllabus>
    {example_specification_point}
    </syllabus>

    <mark_scheme>
    {example_mark_scheme}
    </mark_scheme>

    <number_of_marks>
    1
    </number_of_marks>
</example>


<question>
{question}
</question>

<syllabus>
{specification_point}
</syllabus>
    """
    return prompt


def gen_short_question(specification_point):
    prompt = short_q_template(specification_point)
    llm_qs = generate(prompt)
    qs = extract(llm_qs)

    # qs = ['What type of field does all matter possess?', 'What effect does a gravitational field have on objects?', 'How does the mass of an object affect its gravitational field strength?', 'Which has a stronger gravitational field: a planet or a pebble?', 'True or false: Only very large objects have gravitational fields.']
    q = qs[0]
    ans_prompt = short_q_answer(specification_point, q)
    llm_markscheme = generate(ans_prompt)

    mark_scheme = extract_tags("mark_scheme", llm_markscheme)
    number_of_marks = extract_tags("number_of_marks", llm_markscheme)

    mark_scheme = f"This question is worth {number_of_marks} \n\n" + mark_scheme

    return q, mark_scheme


def gen_cs_question(specification_point):
    prompt = short_q_template(specification_point)
    llm_qs = generate(prompt)
    qs = extract(llm_qs)

    # qs = ['What type of field does all matter possess?', 'What effect does a gravitational field have on objects?', 'How does the mass of an object affect its gravitational field strength?', 'Which has a stronger gravitational field: a planet or a pebble?', 'True or false: Only very large objects have gravitational fields.']
    ret = []
    for q in qs[:5]:
        ans_prompt = short_q_answer(specification_point, q)
        llm_markscheme = generate(ans_prompt)

        mark_scheme = extract_tags("mark_scheme", llm_markscheme)
        number_of_marks = extract_tags("number_of_marks", llm_markscheme)

        mark_scheme = f"This question is worth {number_of_marks} \n\n" + mark_scheme
        ret.append([q, mark_scheme])
    return ret


# subject = "chemistry"
# spec_points = extract_qs(f"syllabus/{subject}.txt")
# for sp in spec_points[100:130]:
#     try:
#         q, markscheme = gen_short_question(sp)
#         d = {"prompt": q, "ref_answer": markscheme}
#         with open(f"dataset/{subject}.jsonl", "a+") as f:
#             f.write(json.dumps(d)+"\n")
#     except Exception as e:
#         print(e)


subject = "cs"
spec_points = extract_cs_questions()
for sp in spec_points[:100]:
    rets = gen_cs_question(sp)
    for q, markscheme in rets:
        d = {"prompt": q, "ref_answer": markscheme}
        with open(f"dataset/{subject}.jsonl", "a+") as f:
            f.write(json.dumps(d) + "\n")
