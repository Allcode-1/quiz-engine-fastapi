import pytest

def test_create_quiz_full_cycle(client, db):
    # 1. imitate user registration and login to get auth token
    client.post("/users/", json={"email": "q@test.com", "username": "quizmaster", "password": "password"})
    login_res = client.post("/auth/login", data={"username": "q@test.com", "password": "password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. create category
    cat_res = client.post("/categories/", json={"name": "Programming"}, headers=headers)
    cat_id = cat_res.json()["id"]

    # 3. create quiz with questions and choices
    quiz_data = {
        "title": "Python Test",
        "description": "Basic questions",
        "category_id": cat_id,
        "time_limit": 60,
        "questions": [
            {
                "text": "2 + 2?",
                "choices": [
                    {"text": "4", "is_correct": True},
                    {"text": "5", "is_correct": False}
                ]
            }
        ]
    }
    quiz_res = client.post("/quizzes/", json=quiz_data, headers=headers)
    assert quiz_res.status_code == 201
    quiz_id = quiz_res.json()["id"]

    # 4. start quiz attempt
    start_res = client.post(f"/quizzes/{quiz_id}/start", headers=headers)
    attempt_id = start_res.json()["id"]

    # 5. submit answers
    # need to get question and choice IDs from created quiz
    q_id = quiz_res.json()["questions"][0]["id"]
    c_id = [c["id"] for c in quiz_res.json()["questions"][0]["choices"] if c["is_correct"]][0]

    submit_data = {
        "answers": [{"question_id": q_id, "choice_id": c_id}]
    }
    submit_res = client.post(f"/quizzes/{quiz_id}/submit/{attempt_id}", json=submit_data, headers=headers)
    
    assert submit_res.status_code == 200
    assert submit_res.json()["score"] == 100.0