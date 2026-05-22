# AI Interview Assistant MVP

CLI MVP for resume parsing, question generation, Q&A simulation, and answer quality evaluation.

## What it does
- Parse resume (PDF/DOCX/TXT)
- Parse JD (file or pasted text)
- Generate role-specific interview questions
- Run a Q&A session in the terminal
- Score answers and export a report JSON

## Setup
1) Create a virtual env (optional)
2) Install deps:

```
pip install -r requirements.txt
```

3) Create a .env file based on .env.example and set:
- ARK_API_KEY
- ARK_BASE_URL
- ARK_MODEL

## Run
```
python main.py --resume "path/to/resume.pdf" --jd "path/to/jd.txt"
```

You can also pass JD as a string:
```
python main.py --resume "path/to/resume.docx" --jd "Your JD text here"
```

## Output
A JSON report is saved under outputs/ with:
- Questions
- Answers
- Scores by dimension
- Summary feedback

## Notes
- This assumes Volcengine Ark provides an OpenAI-compatible endpoint.
- If you use a different provider, update .env and src/config.py.
