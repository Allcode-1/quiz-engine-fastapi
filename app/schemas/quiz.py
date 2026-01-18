from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

# answer variant
class ChoiceCreate(BaseModel):
    text: str
    is_correct: bool

class ChoiceResponse(ChoiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

# question
class QuestionCreate(BaseModel):
    text: str
    choices: List[ChoiceCreate] 

class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    choices: List[ChoiceResponse]

# Quiz
class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    time_limit: Optional[int] = None  # in seconds
    questions: List[QuestionCreate]

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    creator_id: int
    category_id: Optional[int]
    time_limit: Optional[int]
    questions: List[QuestionResponse]

# answer item
class AnswerItem(BaseModel):
    question_id: int
    choice_id: int

# submission for quizzes
class QuizSubmission(BaseModel):
    answers: List[AnswerItem]

# attempt response
class AttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quiz_id: int
    user_id: int
    score: float
    created_at: datetime 
    started_at: datetime
    completed_at: Optional[datetime] = None

# category schemas
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int