from abc import ABC, abstractmethod
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

from .prompts import *

from agents.core import *

class BaseNode(ABC):
    def __init__(self, **kwargs):
        self.name = "BaseNode"
        self.verbose = False
        if "verbose" in kwargs:
            self.verbose = kwargs["verbose"]

    @abstractmethod
    def execute(self, state: SecretFriendState) -> SecretFriendState:
        pass

    def logging(self, method_name, **kwargs):
        if self.verbose:
            print(f"[{self.name}] {method_name}")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

    def __call__(self, state: SecretFriendState):
        return self.execute(state)


class MusicRecommendationNode(BaseNode):
    """음악 추천을 담당하는 노드"""
    
    def __init__(self, music_agent_executor, **kwargs):
        super().__init__(**kwargs)
        self.name = "MusicRecommendationNode"
        self.music_agent_executor = music_agent_executor
        
        # Pydantic 파서 초기화
        self.music_parser = PydanticOutputParser(pydantic_object=MusicResponse)
        
        # 음악 추천 프롬프트 템플릿
        self.music_chat_prompt = get_music_prompt(
            format_instructions=self.music_parser.get_format_instructions()
        )

    def execute(self, state: SecretFriendState) -> SecretFriendState:
        """음악 추천 실행""" 
        # music_agent_executor를 사용하여 음악 추천 실행
        raw = self.music_agent_executor.invoke({"input": state['diary_body']})
        # 추천 결과 파싱
        music_resp = self.music_parser.parse(raw['output'])
        return SecretFriendState(
            music=music_resp,
        )

    def get_prompt(self):
        """프롬프트 반환 (외부에서 사용할 때)"""
        return self.music_chat_prompt
    
    def get_parser(self):
        """파서 반환 (외부에서 사용할 때)"""
        return self.music_parser


class QuoteRecommendationNode(BaseNode):
    """명언 추천을 담당하는 노드"""
    
    def __init__(self, quote_agent_executor, **kwargs):
        super().__init__(**kwargs)
        self.name = "QuoteRecommendationNode"
        self.quote_agent_executor = quote_agent_executor
        
        # Pydantic 파서 초기화
        self.quote_parser = PydanticOutputParser(pydantic_object=QuoteResponse)
        
        # 명언 추천 프롬프트 템플릿
        self.quote_chat_prompt = get_quote_prompt(
            format_instructions=self.quote_parser.get_format_instructions()
        )

    def execute(self, state: SecretFriendState) -> SecretFriendState:
        """명언 추천 실행"""
        # quote_agent_executor를 사용하여 명언 추천 실행
        raw = self.quote_agent_executor.invoke({"input": state['diary_body']})
        # 추천 결과 파싱
        quote_resp = self.quote_parser.parse(raw['output'])
        return SecretFriendState(
            quote=quote_resp,
        )

    def get_prompt(self):
        """프롬프트 반환 (외부에서 사용할 때)"""
        return self.quote_chat_prompt
    
    def get_parser(self):
        """파서 반환 (외부에서 사용할 때)"""
        return self.quote_parser


class PraiseNode(BaseNode):
    """칭찬 생성을 담당하는 노드"""
    
    def __init__(self, llm, **kwargs):
        super().__init__(**kwargs)
        self.name = "PraiseNode"
        self.llm = llm
        
        self.praise_prompt = get_praise_prompt()

    def execute(self, state: SecretFriendState) -> SecretFriendState:
        """칭찬 생성 실행"""
        diary = state['diary_body']
        
        # LLM invoke로 템플릿 실행
        response = self.llm.invoke([self.praise_prompt.format(diary_body=diary)])
        
        return SecretFriendState(
            praise=response.content.strip(),
        )

    def get_prompt(self):
        """프롬프트 반환 (외부에서 사용할 때)"""
        return self.praise_prompt


class MBTIFeedbackNode(BaseNode):
    """MBTI 성향별 피드백 생성을 담당하는 노드"""
    
    def __init__(self, llm, **kwargs):
        super().__init__(**kwargs)
        self.name = "MBTIFeedbackNode"
        self.llm = llm
        
        # MBTI 피드백 프롬프트 템플릿들
        self.f_feedback_prompt = get_f_feedback_prompt()
        self.t_feedback_prompt = get_t_feedback_prompt()

    def execute(self, state: SecretFriendState) -> SecretFriendState:
        """MBTI 피드백 생성 실행"""
        
        diary = state['diary_body']
        
        # F 유형 위로 메시지 생성
        f_resp = self.llm.invoke([self.f_feedback_prompt.format(diary_body=diary)])
        
        # T 유형 조언 메시지 생성
        t_resp = self.llm.invoke([self.t_feedback_prompt.format(diary_body=diary)])
        
        return SecretFriendState(
            F_feedback=f_resp.content.strip(),
            T_feedback=t_resp.content.strip(),
        )

    def get_f_prompt(self):
        """F 유형 피드백 프롬프트 반환"""
        return self.f_feedback_prompt
    
    def get_t_prompt(self):
        """T 유형 피드백 프롬프트 반환"""
        return self.t_feedback_prompt


class StartNodeCheck(BaseNode):
    """워크플로우 시작 시 상태 검증을 담당하는 노드"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "StartNodeCheck"

    def execute(self, state: SecretFriendState) -> SecretFriendState:
        """초기 상태 검증 및 준비"""        
        diary_body = state.get('diary_body', '').strip()
        
        if not diary_body:
            raise ValueError("일기 본문이 비어 있습니다. 일기를 작성해주세요.")
        
        # 상태가 유효하면 그대로 반환 (병렬 처리를 위해)
        return state


class LetterMarkdownNode(BaseNode):
    """비밀친구 편지를 마크다운 형식으로 생성하는 노드"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "LetterMarkdownNode"

    def execute(self, state: SecretFriendState) -> SecretFriendState:
        """마크다운 편지 생성"""
        
        # 구조 분해
        music = state['music']
        quote = state['quote']
        praise = state['praise']
        F_feedback = state['F_feedback']
        T_feedback = state['T_feedback']

        markdown_content = f"""# 💌 비밀친구의 편지

너를 위해 작지만 따뜻한 편지를 준비했어.

---

## 🌟 오늘의 칭찬

> {praise}

---

## 🎵 오늘의 음악 추천

**{music.title}** - *{music.artist}*  
🔗 [음악 들으러 가기]({music.url})  
_👉 {music.reason}_

---

## 📝 오늘의 명언

> “{quote.quote}”  
> — *{quote.author}*  
{quote.explanation}

---

## 🌷 F의 위로

{F_feedback}

---

## 🧭 T의 조언

{T_feedback}

---

비밀친구가 여기 있다는 걸 잊지 마.  
내일도 네 편이 되어줄게.

다 잘 될 거야! ☁️
잘 자.

— 너의 비밀친구가 -
"""

        return SecretFriendState(
            letter_markdown=markdown_content,
        )