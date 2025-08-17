from datetime import time
from pydantic import BaseModel, Field
from typing import Annotated, List, Literal

# Diary
class Companion(BaseModel):
    """
    Information about a person involved in the user's daily event.
    """
    
    name: Annotated[str, Field(..., description="이름 (예: '지연')")]
    relationship: Annotated[str, Field(..., description="관계 (예: '친구', '동료')")]
    note: Annotated[str, Field(default="", description="추가 메모 또는 별명 (예: '고등학교 친구')")]


CoreEmotionType = Literal["기쁨", "설렘", "평범함", "놀라움", "불쾌함", "두려움", "슬픔", "분노"]

emotion_keyword_map = {
    "기쁨": ["기분좋은", "즐거운", "고마운", "홀가분한", "사랑스러운", "재밌는", "기쁜", "뿌듯한", "속시원한", "만족스러운", "신나는", "행복한", "감동받은", "날아갈 것 같은"],
    "설렘": ["몽글몽글한", "두근거리는", "간질간질한", "설레는", "흥미로운", "신나는", "기대되는", "궁금한", "긴장되는", "안달나는", "텐션 높은", "간절한 마음의"],
    "평범함": ["잔잔한", "별 일 없는", "나쁘지 않은", "그저 그런", "만족스러운", "무난한", "피곤한", "괜찮은", "싱숭생숭한", "소소한", "평범한", "안정감이 드는", "편안한"],
    "놀라움": ["당황스러운", "어이 없는", "부끄러운", "심쿵한", "깜짝 놀란", "어안이 벙벙한", "멘탈 무너지는", "만감이 교차하는", "기가 막히는", "소름끼치는", "상상을 초월하는", "골때리는", "폭풍같은"],
    "불쾌함": ["피곤한", "지치는", "귀찮은", "재미없는", "지루한", "불편한", "불쾌한", "찝찝한", "소외감 느끼는", "우울한", "지긋지긋한", "토나오는", "기분 더러운"],
    "두려움": ["망설여지는", "걱정되는", "불안한", "심란한", "긴장되는", "막막한", "두려운", "큰일 난 것 같은", "겁나는", "무서운", "초조한", "쫄리는", "숨막히는", "도망치고 싶은", "끝이 보이지 않는"],
    "슬픔": ["무기력한", "실망스러운", "속상한", "외로운", "마음아픈", "후회되는", "힘든", "서러운", "슬픈", "허탈한", "막막한", "우울한", "혼자인 것 같은", "울고싶은",  "절망적인", "그리운", "공허한", "세상이 무너진 것 같은"],
    "분노": ["답답한", "짜증나는", "신경질나는", "어이없는", "이해할 수 없는", "화나는", "한심한", "킹받는", "억울한", "기분 더러운", "질투나는", "분한", "빡치는", "소리지르고 싶은"]
}

class DiaryEntry(BaseModel):
    """
    A structured representation of a diary entry containing event details and emotional context.
    """
    
    event_title: Annotated[str, Field(..., min_length=1, max_length=50, description="사건 제목 (예: '친구와 저녁 식사')")]
    time_period: Annotated[time, Field(..., description="사건이 발생한 시각 (예: 19:30:00 또는 07:30:00)")]
    core_emotion: Annotated[CoreEmotionType, Field(..., description="핵심 감정 1가지")]
    emotion_keywords: Annotated[List[str], Field(..., min_items=1, max_items=3, description="선택한 핵심 감정과 관련된 구체적인 감정 키워드 목록")]
    emotion_score: Annotated[int, Field(..., ge=0, le=100, description="감정 점수 (0은 매우 부정적, 100은 매우 긍정적)")]
    companions: Annotated[List[Companion], Field(..., description="함께한 사람들의 리스트 (이름, 관계, 메모 정보)")]
    thoughts: Annotated[str, Field(..., max_length=300, description="사건 당시 느낀 감정, 생각, 배운 점 등")]
    reflection: Annotated[str, Field(..., max_length=300, description="잘한 점이나 아쉬웠던 점에 대한 회고")]
    summary: Annotated[str, Field(..., max_length=150, description="전체 사건을 요약한 한 문장 (예: '친구와의 저녁 식사로 하루를 따뜻하게 마무리했다.')")]


# SecretFriend
class MusicResponse(BaseModel):
    """
    에이전트가 반환할 음악 추천 데이터를 구조화하기 위한 모델입니다.

    Attributes:
        title (str): 추천된 곡 제목.
        artist (str): 곡 아티스트 이름.
        url (str): Spotify 트랙 URL.
        reason (str): 추천 이유.
    """
    title: str = Field(..., description="추천된 곡 제목")
    artist: str = Field(..., description="곡 아티스트 이름")
    url: str = Field(..., description="Spotify 트랙 URL")
    reason: str = Field(..., description="추천 이유")


class QuoteResponse(BaseModel):
    """
    에이전트가 반환할 명언 데이터를 구조화하기 위한 모델입니다.

    Attributes:
        quote (str): 추천된 명언 텍스트.
        author (str): 명언을 남긴 사람의 이름 (출처).
        explanation (str): 왜 이 명언이 해당 일기 상황에 적절한지 설명하는 따뜻한 메시지.
    """
    quote: str = Field(..., description="추천 명언")
    author: str = Field(..., description="명언 출처(말한 사람)")
    explanation: str = Field(..., description="왜 이 명언이 적절한지에 대한 설명")


class SpotifyToolInput(BaseModel):
    diary: str = Field(
        ..., description="일기 본문 텍스트를 입력합니다."
    )
    keyword: str = Field(
        ..., description="일기에서 추출한 핵심 키워드"
    )
