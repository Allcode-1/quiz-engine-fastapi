from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.quiz import Quiz, Question, Choice, Attempt, Category
from app.schemas.quiz import QuizCreate, QuizResponse, QuizSubmission, AttemptResponse, QuizUpdate
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    quiz_data: QuizCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new quiz with questions and choices.
    """
    if quiz_data.category_id:
        category = db.query(Category).get(quiz_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    # 1. Quiz creation
    new_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        creator_id=current_user.id,
        category_id=quiz_data.category_id,
        time_limit=quiz_data.time_limit
    )
    db.add(new_quiz)
    db.flush() 

    # 2. Process questions
    for q_data in quiz_data.questions:
        new_question = Question(text=q_data.text, quiz_id=new_quiz.id)
        db.add(new_question)
        db.flush()

        # 3. Process answer choices
        for c_data in q_data.choices:
            new_choice = Choice(
                text=c_data.text, 
                is_correct=c_data.is_correct, 
                question_id=new_question.id
            )
            db.add(new_choice)

    db.commit()
    db.refresh(new_quiz)
    return new_quiz


@router.get("/", response_model=List[QuizResponse])
def get_all_quizzes(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all quizzes with optional category filtering.
    """
    query = db.query(Quiz)
    if category_id:
        query = query.filter(Quiz.category_id == category_id)
    return query.all()


@router.get("/my", response_model=List[QuizResponse])
def get_my_quizzes(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Get all quizzes created by the current user.
    """
    return db.query(Quiz).filter(Quiz.creator_id == current_user.id).all()


@router.get("/my-attempts", response_model=List[AttemptResponse])
def get_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's quiz attempts ordered by date.
    """
    return db.query(Attempt).filter(
        Attempt.user_id == current_user.id
    ).order_by(Attempt.created_at.desc()).all()


@router.post("/{quiz_id}/start", response_model=AttemptResponse)
def start_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new quiz attempt and trigger the timer.
    """
    quiz = db.query(Quiz).get(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    new_attempt = Attempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=0.0
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)
    return new_attempt


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific quiz.
    """
    quiz = db.query(Quiz).get(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/submit/{attempt_id}", response_model=AttemptResponse)
def submit_quiz(
    quiz_id: int,
    attempt_id: int,
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit answers, check time limit, and calculate final score.
    """
    # 1. Validate attempt
    attempt = db.query(Attempt).filter(
        Attempt.id == attempt_id, 
        Attempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt.completed_at:
        raise HTTPException(status_code=400, detail="This attempt is already finished")

    quiz = db.query(Quiz).get(quiz_id)

    # 2. Timer check
    if quiz.time_limit:
        now = datetime.now(timezone.utc)
        start_time = attempt.started_at.replace(tzinfo=timezone.utc) if attempt.started_at.tzinfo is None else attempt.started_at
        
        elapsed_time = (now - start_time).total_seconds()
        
        if elapsed_time > (quiz.time_limit + 10):
            attempt.score = 0.0
            db.commit()
            raise HTTPException(status_code=400, detail="Time is up! Result is 0")

    # 3. Calculate score
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    user_answers = {ans.question_id: ans.choice_id for ans in submission.answers}
    correct_count = 0

    for question in questions:
        submitted_choice_id = user_answers.get(question.id)
        if submitted_choice_id:
            choice = db.query(Choice).filter(
                Choice.id == submitted_choice_id, 
                Choice.question_id == question.id
            ).first()
            if choice and choice.is_correct:
                correct_count += 1

    # 4. Update attempt
    attempt.score = (correct_count / len(questions)) * 100
    db.commit()
    db.refresh(attempt)
    return attempt


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a quiz. Only the creator can perform this action.
    """
    quiz = db.query(Quiz).get(quiz_id)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db.delete(quiz)
    db.commit()
    return None


@router.patch("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: int,
    quiz_in: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update quiz details partially.
    """
    quiz = db.query(Quiz).get(quiz_id)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Clean partial update
    update_data = quiz_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)

    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("/{quiz_id}/leaderboard")
def get_quiz_leaderboard(
    quiz_id: int, 
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get the top scores for a specific quiz.
    """
    leaderboard = db.query(Attempt, User).join(User, Attempt.user_id == User.id).filter(
        Attempt.quiz_id == quiz_id
    ).order_by(desc(Attempt.score)).limit(limit).all()
    
    return [
        {
            "username": user.username,
            "score": attempt.score,
            "date": attempt.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for attempt, user in leaderboard
    ]