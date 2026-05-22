from __future__ import annotations

import argparse
import json
import os
import re
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.parsers import parse_jd, parse_resume


def _normalize_text(text: str, max_chars: int = 4000) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.strip()
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def _extract_json(text: str) -> Any:
    text = text.strip()
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")

    payload = text[start : end + 1]
    return json.loads(payload)


def _invoke_json(messages: list[SystemMessage | HumanMessage]) -> Any:
    llm = get_llm()
    response = llm.invoke(messages)
    return _extract_json(response.content)


def generate_questions(resume_text: str, jd_text: str, count: int) -> list[dict[str, Any]]:
    system = SystemMessage(
        content=(
            "You are an interview coach. Respond in Chinese. "
            "Return JSON with keys: questions (list). "
            "Each question: id, type, question, focus. "
            "Use types like: general, role, project, followup."
        )
    )

    human = HumanMessage(
        content=(
            f"Resume:\n{resume_text}\n\n"
            f"JD:\n{jd_text}\n\n"
            f"Generate {count} interview questions tailored to the JD and resume."
        )
    )

    data = _invoke_json([system, human])
    questions = data.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError("Invalid questions payload.")
    return questions


def evaluate_answer(resume_text: str, jd_text: str, question: str, answer: str) -> dict[str, Any]:
    system = SystemMessage(
        content=(
            "You are an interviewer. Respond in Chinese. "
            "Return JSON with keys: scores, feedback, improvement. "
            "scores is an object with: structure, relevance, clarity, evidence, overall (1-5)."
        )
    )

    human = HumanMessage(
        content=(
            f"Resume:\n{resume_text}\n\n"
            f"JD:\n{jd_text}\n\n"
            f"Question:\n{question}\n\n"
            f"Answer:\n{answer}\n"
        )
    )

    return _invoke_json([system, human])


def run_cli(resume_path: str, jd_input: str, count: int) -> None:
    resume_text = _normalize_text(parse_resume(resume_path))
    jd_text = _normalize_text(parse_jd(jd_input))

    questions = generate_questions(resume_text, jd_text, count)

    print("\nGenerated Questions:")
    for q in questions:
        q_id = q.get("id", "")
        q_type = q.get("type", "")
        q_text = q.get("question", "")
        print(f"- [{q_id}] ({q_type}) {q_text}")

    print("\nStart the interview. Press Enter to begin.")
    input()

    results = []
    for idx, q in enumerate(questions, start=1):
        question_text = q.get("question", "")
        print(f"\nQ{idx}: {question_text}")
        answer = input("Your answer: ").strip()
        if not answer:
            answer = "(no answer)"

        evaluation = evaluate_answer(resume_text, jd_text, question_text, answer)
        results.append(
            {
                "question": q,
                "answer": answer,
                "evaluation": evaluation,
            }
        )

        scores = evaluation.get("scores", {})
        overall = scores.get("overall", "-")
        print(f"Score (overall): {overall}")

    report = {
        "resume_path": resume_path,
        "jd_input": jd_input,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "questions": questions,
        "results": results,
    }

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", f"interview_{time.strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nReport saved: {out_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Interview Assistant MVP")
    parser.add_argument("--resume", help="Path to resume file (pdf/docx/txt)")
    parser.add_argument("--jd", help="JD text or path to JD file")
    parser.add_argument("--questions", type=int, default=6, help="Number of questions")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    resume = args.resume or input("Resume path (pdf/docx/txt, you can drag-drop): ").strip()
    jd = args.jd or input("JD text or path (pdf/docx/txt): ").strip()
    if not resume or not jd:
        raise SystemExit("Missing resume or JD input.")
    run_cli(resume, jd, args.questions)


if __name__ == "__main__":
    main()
