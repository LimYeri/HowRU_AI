from abc import ABC, abstractmethod
from collections import Counter
from datetime import time
from typing import List
from pathlib import Path
import os
import platform
import uuid

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from langchain_core.messages import SystemMessage, BaseMessage, ToolMessage, HumanMessage, AIMessage
from langgraph.graph import END

from agents.core import *
from .prompts import *


class BaseNode(ABC):
    def __init__(self, **kwargs):
        self.name = "BaseNode"
        self.verbose = False
        if "verbose" in kwargs:
            self.verbose = kwargs["verbose"]

    @abstractmethod
    def execute(self, state: State) -> State:
        pass

    def logging(self, method_name, **kwargs):
        if self.verbose:
            print(f"[{self.name}] {method_name}")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

    def __call__(self, state: State):
        return self.execute(state)


class InfoNode(BaseNode):
    def __init__(self, llm_with_tool, **kwargs):
        super().__init__(**kwargs)
        self.name = "InfoNode"
        self.llm = llm_with_tool

    def _build_prompt(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        return [SystemMessage(content=get_diary_system_prompt())] + messages

    def execute(self, state: State) -> State:
        final_messages = self._build_prompt(state["messages"])
        response = self.llm.invoke(final_messages)

        return {"messages": [response]}


class SuggestKeywordsNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "SuggestKeywordsNode"
        self.tool = suggest_keywords_tool

    def execute(self, state: State) -> State:
        tool_call = state["messages"][-1].tool_calls[0]
        result = self.tool.invoke(tool_call["args"])
        
        # ToolMessage 생성
        tool_msg = ToolMessage(
            content=f"<RAW>추천된 감정 키워드는 다음과 같아: \n[{', '.join(result)}] \n이 중에서 1~3개를 골라줘.</RAW>",
            tool_call_id=tool_call["id"],
        )

        return State(messages=[tool_msg])


class CreateEntryNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "CreateEntryNode"

    def execute(self, state: State) -> State:
        tool_call = state["messages"][-1].tool_calls[0] # 필요 시 안전성 체크 추가 가능
        entry = DiaryEntry.model_validate(tool_call["args"])

        # 기존 entries가 없으면 빈 리스트로 시작
        existing_entries = state.get("entries", [])

        tool_msg = ToolMessage(
            content="혹시 오늘 다른 기억에 남는 일도 있었어?",
            tool_call_id=tool_call["id"],
        )

        return State(
            messages=[tool_msg],
            entries=existing_entries + [entry], # 누적 저장
        )


class GenerateDiaryBodyNode(BaseNode):
    """
    - state['entries']를 시간순으로 정렬해 요약(one_liner)과 줄글 본문(diary_body)을 생성
    - entries가 없으면 안내 메시지를 채우고 그대로 반환
    """
    def __init__(self, llm, **kwargs):
        super().__init__(**kwargs)
        self.name = "GenerateDiaryBodyNode"
        self.llm = llm

        # 프롬프트 템플릿 준비
        self.summary_prompt = get_summary_prompt()
        self.body_prompt = get_body_prompt()

    def execute(self, state: State) -> State:
        entries: list[DiaryEntry] = state.get("entries", [])

        if not entries:
            return State(
                one_liner="기록된 사건이 없습니다.",
                diary_body="오늘의 일기를 작성할 수 없습니다.",
            )

        # 시간순 정렬 (원본 로직 유지)
        sorted_entries = sorted(entries, key=lambda e: e.time_period)

        # 한줄 요약 생성 (원본 로직 유지)
        summary_chain = self.summary_prompt | self.llm
        one_liner_msg = summary_chain.invoke({"entries": sorted_entries})

        # 줄글 본문 생성 (원본 로직 유지)
        body_chain = self.body_prompt | self.llm
        diary_body_msg = body_chain.invoke({"entries": sorted_entries})

        return State(
            one_liner=one_liner_msg.content,
            diary_body=diary_body_msg.content,
        )
        

# 그래프 이미지 저장 폴더 (Django 연동 시 MEDIA_ROOT 등으로 대체 가능)
# CHART_OUTPUT_DIR = "./emotion_charts"
# 현재 파일 기준 project_root 절대경로
BASE_DIR = Path(__file__).resolve().parents[2]   # diary_nodes → diary → agents → project_root

CHART_OUTPUT_DIR = BASE_DIR / "emotion_charts"
CHART_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

emotion_to_index = {
    "분노": 0,
    "슬픔": 1,
    "두려움": 2,
    "불쾌함": 3,
    "평범함": 4,
    "놀라움": 5,
    "설렘": 6,
    "기쁨": 7,
}

emotion_colors = {
    "기쁨": "#FFD700",
    "설렘": "#FFB6C1",
    "평범함": "#C0C0C0",
    "놀라움": "#87CEFA",
    "불쾌함": "#8B0000",
    "두려움": "#292B2E",
    "슬픔": "#4682B4",
    "분노": "#FF4500",
}

class GenerateEmotionChartsNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "GenerateEmotionChartsNode"

    def execute(self, state: State) -> State:
        entries = state["entries"]

        # 데이터 준비
        emotion_counts = Counter(e.core_emotion for e in entries)
        sorted_entries = sorted(entries, key=lambda e: e.time_period)
        time_labels = [e.time_period.strftime("%H:%M") for e in sorted_entries]
        emotion_names = [e.core_emotion for e in sorted_entries]
        emotion_indices = [emotion_to_index[e] for e in emotion_names]
        emotion_scores = [e.emotion_score for e in sorted_entries]

        # 파일명 (UUID로 충돌 방지)
        today_str = state["today_date"].strftime("%Y%m%d")
        pie_filename = f"pie_{today_str}_{uuid.uuid4().hex}.png"
        flow_filename = f"flow_{today_str}_{uuid.uuid4().hex}.png"
        score_filename = f"score_{today_str}_{uuid.uuid4().hex}.png"

        pie_path = os.path.join(CHART_OUTPUT_DIR, pie_filename)
        flow_path = os.path.join(CHART_OUTPUT_DIR, flow_filename)
        score_path = os.path.join(CHART_OUTPUT_DIR, score_filename)

        # 한글 폰트 설정 (OS별)
        current_os = platform.system()
        if current_os == "Windows":
            font_path = "C:/Windows/Fonts/malgun.ttf"
            fontprop = fm.FontProperties(fname=font_path, size=12)
            plt.rc("font", family=fontprop.get_name())
        elif current_os == "Darwin":
            plt.rcParams["font.family"] = "AppleGothic"
        else:
            try:
                plt.rcParams["font.family"] = "NanumGothic"
            except:
                print("한글 폰트를 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")

        # 마이너스 폰트 깨짐 방지
        plt.rcParams["axes.unicode_minus"] = False

        # 감정 비율 원형 차트
        plt.figure(figsize=(6, 6))
        colors = [emotion_colors[e] for e in emotion_counts.keys()]
        plt.pie(
            emotion_counts.values(),
            labels=emotion_counts.keys(),
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontsize": 12},
        )
        plt.title("감정 비율", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(pie_path)
        plt.close()

        # 감정 흐름 선형 그래프
        plt.figure(figsize=(8, 4))
        _line_colors = [emotion_colors[e] for e in emotion_names]  # (원본 변수 유지용, 실제 사용 X)
        plt.plot(time_labels, emotion_indices, marker="o", color="#4169E1", linewidth=2)
        plt.fill_between(time_labels, emotion_indices, color="#ADD8E6", alpha=0.3)
        plt.yticks(list(emotion_to_index.values()), list(emotion_to_index.keys()))
        plt.xlabel("시간", fontsize=11)
        plt.ylabel("감정", fontsize=11)
        plt.title("시간 흐름에 따른 감정 변화", fontsize=14, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(flow_path)
        plt.close()

        # 감정 점수 꺾은선 그래프
        plt.figure(figsize=(8, 4))
        plt.plot(time_labels, emotion_scores, marker="o", color="#32CD32", linewidth=2)
        plt.fill_between(time_labels, emotion_scores, color="#98FB98", alpha=0.3)
        plt.ylim(0, 100)
        plt.xlabel("시간", fontsize=11)
        plt.ylabel("감정 점수 (0~100)", fontsize=11)
        plt.title("시간 흐름에 따른 감정 점수", fontsize=14, fontweight="bold")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(score_path)
        plt.close()

        return State(
            emotion_pie_chart_url=pie_path,
            emotion_timeline_chart_url=flow_path,
            emotion_score_chart_url=score_path,
        )


class GenerateDiaryNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "GenerateDiaryNode"

    def _format_time_kr(self, t: time) -> str:
        """시간을 한국어 표기로 변환 (오전/오후 HH시 mm분)"""
        hour = t.hour
        minute = t.minute
        period = "오전" if hour < 12 else "오후"
        display_hour = hour if 1 <= hour <= 12 else hour - 12 if hour > 12 else 12
        return f"{period} {display_hour}시 {f'{minute}분' if minute else ''}".strip()

    def execute(self, state: State) -> State:
        entries: list[DiaryEntry] = state["entries"]

        # 시간 순 정렬
        sorted_entries = sorted(entries, key=lambda e: e.time_period)

        # 오늘 날짜 및 시각
        today = state["today_date"].strftime("%Y년 %m월 %d일")
        written_at = state["written_at"].strftime("%H:%M")

        # 1) 사건 요약 테이블
        table_lines = [
            "| 시간대 | 사건명 | 감정 | 감정 키워드 | 함께한 사람 |",
            "|--------|--------|------|--------------|---------------|",
        ]
        for entry in sorted_entries:
            time_str = self._format_time_kr(entry.time_period)
            title = entry.event_title
            emotion = entry.core_emotion
            keywords = ", ".join(entry.emotion_keywords)
            companions = (
                ", ".join(
                    f"{c.name}({c.relationship})" if c.relationship else c.name
                    for c in entry.companions
                )
                or "혼자"
            )
            table_lines.append(
                f"| {time_str} | {title} | {emotion} | {keywords} | {companions} |"
            )

        table_md = "\n".join(table_lines)

        # 2) 전체 Markdown 조립
        md = f"""# 📘 {today} 일기
> ⏰ 작성 시각: {written_at}

## ☀️ 오늘의 한 줄
> {state['one_liner']}

---

## 📋 오늘의 사건 요약

{table_md}

---

## 📖 오늘의 일기

{state['diary_body']}

---

## 📊 감정 요약 그래프

### 🥧 감정 비율
![감정 비율]({state['emotion_pie_chart_url']})

### 📈 시간 흐름에 따른 감정 변화
![감정 흐름]({state['emotion_timeline_chart_url']})

### 🎯 감정 점수 추이
![감정 점수]({state['emotion_score_chart_url']})
"""

        # 상태에 Markdown 저장
        return State(final_markdown=md)



class RouterNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "RouterNode"

    def execute(self, state):
        messages = state["messages"]
        if not messages:
            return "info"

        last = messages[-1]

        # 1) AI tool call 처리
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            tool_call = last.tool_calls[0]
            name = tool_call.get("name")
            if name == "suggest_keywords_tool":
                return "suggest_keywords_message"
            elif name == "DiaryEntry":  # 실제 도구명과 정확히 일치하는지 확인 필요
                return "create_entry"

        # 2) Human "q" 분기 (길이 체크)
        if len(messages) >= 2:
            prev = messages[-2]
            if isinstance(prev, HumanMessage) and str(prev.content).strip().lower() == "q":
                return "generate_diary_body"

        # 3) 마지막이 HumanMessage가 아니면 종료
        if not isinstance(last, HumanMessage):
            return END

        return "info"
    
        # messages = state["messages"]

        # # 마지막 메시지가 AIMessage이고 도구 호출이 있는 경우
        # if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        #     tool_call = messages[-1].tool_calls[0]
        #     tool_name = tool_call["name"]

        #     # 핵심 감정 키워드 추천 도구 호출 시 → 키워드 메시지 노드로
        #     if tool_name == "suggest_keywords_tool":
        #         return "suggest_keywords_message"

        #     # 일기 작성 도구 호출 시 → create_entry 노드로
        #     elif tool_name == "DiaryEntry":
        #         return "create_entry"

        # # 마지막 메시지 HumanMessage → 'q' 입력 여부 판단
        # elif (
        #     isinstance(messages[-2], HumanMessage)
        #     and messages[-2].content.strip().lower() == "q"
        # ):
        #     return "generate_diary_body"

        # # 마지막 메시지가 HumanMessage가 아닌 경우 → 종료
        # elif not isinstance(messages[-1], HumanMessage):
        #     return END

        # # 기본적으로 정보 수집 상태 반환
        # return "info"
