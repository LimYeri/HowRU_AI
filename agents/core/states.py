from langgraph.graph.message import add_messages
from typing import Annotated, List
from typing_extensions import TypedDict
from datetime import date, time
from .models import DiaryEntry, MusicResponse, QuoteResponse

# State 정의 (Diary)
class State(TypedDict):
    messages: Annotated[list, add_messages]
    entries: List[DiaryEntry]  # 여러 개의 이벤트 수집용 리스트
    user_name: str
    today_date: date
    written_at: time  # or datetime
    one_liner: str
    diary_body: str
    final_markdown: str  # optional

    emotion_pie_chart_url: str
    emotion_timeline_chart_url: str
    emotion_score_chart_url: str


# State 정의 (SecretFriend)
class SecretFriendState(TypedDict):
    diary_body: str
    praise: str
    music: MusicResponse
    quote: QuoteResponse
    F_feedback: str
    T_feedback: str
    letter_markdown: str