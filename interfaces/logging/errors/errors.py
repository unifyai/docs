import unify
import datetime
from random import randint, choice

client = unify.Unify("gpt-4o@openai")


def simulate_usr_question():
    return f"{randint(0, 100)} {choice(['+', '-'])} {randint(0, 100)}"


def evaluate_response(question: str, response: str) -> float:
    correct_answer = eval(question)
    try:
        response_int = int(
            "".join([c for c in response.split(" ")[-1] if c.isdigit()]),
        )
        return correct_answer == response_int
    except ValueError:
        return False


def simulate_traffic(evaluator):
    for _ in range(50):
        question = simulate_usr_question()
        response = client.generate(question)
        correct = evaluator(question, response)
        # simulating the derived column
        ts = datetime.datetime.utcnow()
        ts_rounded = ts - datetime.timedelta(
            minutes=ts.minute,
            seconds=ts.second % 10,
            microseconds=ts.microsecond,
        )
        unify.log(
            timestamp=ts.isoformat(),
            timestamp_rounded=ts_rounded.timestamp(),
            # end simulation
            question=question,
            response=response,
            correct_answer=eval(question),
            correct=correct,
        )


unify.activate("Errors", overwrite=True)
simulate_traffic(evaluate_response)


def evaluate_response(question: str, response: str) -> float:
    correct_answer = eval(question)
    try:
        response_int = int(
            "".join([c for c in response.split(" ")[-1] if (c.isdigit() or c == "-")]),
        )
        return correct_answer == response_int
    except ValueError:
        return False


simulate_traffic(evaluate_response)


client.set_system_message(
    "You are a helpful maths assistant, adept at answering arithmetic questions. Please respond with the integer answer as the final part of your answer",
)


simulate_traffic(evaluate_response)
