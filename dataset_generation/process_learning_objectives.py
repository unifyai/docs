import re


def extract_science_learning_objectives(text, subject):
    # source: claude

    # Split the text into lines
    lines = text.split("\n")

    objectives = []
    current_objective = ""

    for line in lines:
        # Check if the line starts with a learning objective code (e.g., P1.2f)
        if re.match(f"^{subject}\d+\.\d+[a-z]", line):
            # If we have a previous objective, add it to the list
            if current_objective:
                objectives.append(current_objective.strip())

            # Start a new objective
            current_objective = line
        elif current_objective and not line.strip().startswith(("M", "W")):
            # Continue adding to the current objective if it's not a new one and doesn't start with M or W
            current_objective += " " + line.strip()
        elif current_objective and (
            line.strip().startswith("M") or line.strip().startswith("W")
        ):
            # If we encounter M or W, add the current objective to the list and reset
            objectives.append(current_objective.strip())
            current_objective = ""

    # Add the last objective if there is one
    if current_objective:
        objectives.append(current_objective.strip())

    return objectives


def extract_cs_questions():
    path = "syllabus/cs.txt"
    with open(path) as f:
        text = f.read()

    lines = text.split("\n")

    sections = {}
    current_section = None
    current_content = []

    # Regular expression to match section headers (e.g., 2.3.1, 2.4.1)
    section_pattern = re.compile(r"^\d+\.\d+\.\d+")

    for line in lines:
        if section_pattern.match(line):
            # If we find a new section, save the previous one (if any)
            if current_section:
                sections[current_section] = "\n".join(current_content)

            # Start a new section
            current_section = line.strip()
            current_content = []
        else:
            # Add the line to the current section's content
            current_content.append(line)

    # Add the last section
    if current_section:
        sections[current_section] = "\n".join(current_content)

    ret = []
    for s_title, s_info in sections.items():
        ret.append(f"{s_title} \n {s_info}")
    return ret


def extract_qs(path):
    if path.startswith("physics"):
        subject = "P"
    elif path.startswith("chemistry"):
        subject = "C"
    elif path.startswith("biology"):
        subject = "B"

    with open(path) as f:
        text = f.read()
        objectives = extract_science_learning_objectives(text, subject=subject)
    return objectives


if __name__ == "__main__":
    # objectives = extract_qs(path="physics.txt")
    # objectives = extract_qs(path="chemistry.txt")
    # objectives = extract_qs(path="biology.txt")
    objectives = extract_cs_questions()
    for r in objectives:
        print(r)
        break
