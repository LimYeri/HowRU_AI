from typing import List
from langchain.tools import tool
from .models import CoreEmotionType, emotion_keyword_map, SpotifyToolInput

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Type
from pydantic import BaseModel
from langchain.tools import BaseTool
import random

from langchain_tavily import TavilySearch

# Diary
@tool
def suggest_keywords_tool(core_emotion: CoreEmotionType) -> List[str]:
    """
    Suggests related emotion keywords based on the user's selected core emotion.
    Args:
        core_emotion: The user's selected core emotion (e.g., "joy", "sadness").
    Returns:
        A list of emotion-related keywords for the LLM to present to the user.
    """
    return emotion_keyword_map.get(core_emotion, [])


# SecretFriend
# Spotify API 인증 설정
sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"), client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)


class SpotifyTool(BaseTool):
    """
    Spotify Music Recommender
    - Input: diary를 args_schema로 직접 받음
    - Output: 일기에서 추출한 키워드를 기반으로 Spotify 검색 API 사용해 단 하나의 곡 추천
    """
    name: str = "spotify_recommender_tool"
    description: str = (
        "일기 본문을 받아, 일기에서 주요 키워드를 추출한 뒤,"
        "Spotify 검색 API를 활용해 단 하나의 곡을 추천합니다."
    )
    args_schema: Type[BaseModel] = SpotifyToolInput
    
    def _run(self, diary: str, keyword: str) -> str:
        diary_body = diary.strip()
        if not diary_body:
            return "일기 본문을 입력해주세요."
        
        keyword = keyword.strip()
        if not keyword:
            return "keyword를 다시 생성해 입력해주세요."

        query = f"{keyword}"
        offset = random.randint(0, 50)  # 오프셋을 랜덤으로 설정하여 다양한 곡 추천
        results = sp.search(q=query, type="track", limit=1, offset=offset, market="KR")
        items = results.get("tracks", {}).get("items", [])
        if items:
            track = items[0]
            title = track.get("name")
            artist_name = track.get("artists", [{}])[0].get("name")
            url = track.get("external_urls", {}).get("spotify")
            return f"""제목은 [{title}], 가수는 [{artist_name}], url은 [{url}] 입니다."""

        return f"'{keyword}' 키워드에 맞는 추천 곡을 찾지 못했습니다."

    def _arun(self):
        raise NotImplementedError("Spotify Music Recommender does not support ")


def create_web_search_tool():
    # 웹 검색 도구 생성
    tavily_tool = TavilySearch(
                    max_results=3,             # 최대 답변 수
                    include_answer=True,       # 원본 쿼리에 대한 짧은 답변 포함
                    include_raw_content=True   # HTML 원본 내용 포함
                )
    
    tavily_tool.description = (
        "일기 내용을 기반으로 사용자를 위로하거나 격려할 수 있는 명언을 검색합니다. "
        "사용자가 제공한 일기 텍스트에 적합한 명언과 간단한 해설을 최대 3건 반환합니다."
    )
    return tavily_tool