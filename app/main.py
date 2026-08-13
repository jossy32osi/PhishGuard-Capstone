import json

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="PhishGuard",
    description="Phishing Awareness & Education Platform",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


def load_scenarios():
    with open("app/data/scenarios.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_quiz():
    with open("app/data/quiz.json", "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "PhishGuard",
        },
    )


@app.get("/learn")
async def learn(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="learn.html",
        context={
            "title": "Learn",
        },
    )


@app.get("/spot")
async def spot(request: Request, scenario: int = 0):
    scenarios = load_scenarios()

    if scenario >= len(scenarios):
        scenario = 0

    current = scenarios[scenario]

    return templates.TemplateResponse(
        request=request,
        name="spot.html",
        context={
            "title": "Spot the Phish",
            "scenario": current,
            "scenario_number": scenario,
            "total": len(scenarios),
        },
    )


@app.post("/spot/check")
async def check_spot(
    request: Request,
    scenario_id: int = Form(...),
    answer: str = Form(...),
):
    scenarios = load_scenarios()

    scenario = next(
        item for item in scenarios
        if item["id"] == scenario_id
    )

    user_answer = answer.lower() == "phishing"
    correct = user_answer == scenario["is_phishing"]

    current_index = next(
        index
        for index, item in enumerate(scenarios)
        if item["id"] == scenario_id
    )

    next_index = current_index + 1

    if next_index >= len(scenarios):
        next_index = 0

    return templates.TemplateResponse(
        request=request,
        name="spot.html",
        context={
            "title": "Spot the Phish",
            "scenario": scenario,
            "scenario_number": current_index,
            "total": len(scenarios),
            "answered": True,
            "correct": correct,
            "next_index": next_index,
        },
    )

@app.get("/respond")
async def respond(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="respond.html",
        context={
            "title": "What To Do",
        },
    )


@app.get("/quiz")
async def quiz(request: Request, question: int = 0):
    questions = load_quiz()

    if question >= len(questions):
        question = 0

    current = questions[question]

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "title": "Phishing Awareness Quiz",
            "question": current,
            "question_number": question,
            "total": len(questions),
        },
    )


@app.post("/quiz/check")
async def check_quiz(
    request: Request,
    question_id: int = Form(...),
    answer: int = Form(...),
    score: int = Form(0),
):
    questions = load_quiz()

    current_index = next(
        index
        for index, item in enumerate(questions)
        if item["id"] == question_id
    )

    question = questions[current_index]

    is_correct = answer == question["answer"]

    if is_correct:
        score += 1

    next_index = current_index + 1

    if next_index >= len(questions):
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "title": "Quiz Result",
                "score": score,
                "total": len(questions),
            },
        )

    next_question = questions[next_index]

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "title": "Phishing Awareness Quiz",
            "question": next_question,
            "question_number": next_index,
            "total": len(questions),
            "score": score,
        },
    )
