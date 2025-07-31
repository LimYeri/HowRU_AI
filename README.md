# 🧠 HowRU AI – 감정 기록 AI 에이전트

> **“감정을 기록하고, 나를 탐색하고, AI 비밀친구와 하루를 마무리해요.”**

---

## 📌 프로젝트 개요

> 우리는 하루에도 수십 번 ‘How are you?’라는 말을 주고받습니다.
> 
> 
> 하지만, 정작 **내 자신에게** 그 질문을 해본 적은 언제였을까요?
>

**HowRU AI**는 사용자의 하루 감정을 기반으로  
- 일기를 쉽게 기록하고  
- 감정을 시각화하고  
- AI 비밀친구에게 위로받을 수 있는  
**LangGraph 기반 멀티에이전트 일기 작성 시스템**입니다.

### 🙋‍♀️ 왜 이 프로젝트를 시작했나요?
**감정을 돌아보고 나를 이해할 수 있는 공간**을 만들고 싶었습니다.  
또한 최근 LangChain, LangGraph 등 **AI Agent Framework**를 깊이 있게 학습하며 실제 사용자 시나리오에 녹여낼 수 있는 프로젝트가 필요했습니다.

---

### 🗓️ 개발 기간
2025년 7월 27일 - (ing)

---

## 🛠️ 기술 스택

| 범주 | 기술 |
|------|------|
| Language | Python 3.11 |
| Framework | LangChain, LangGraph |
| LLM | OpenAI GPT-4o |
| Tool Integration | Tavily Search, Spotify API (Spotipy) |
| Data Modeling | Pydantic |
| Package & Env | Poetry |
| Version Control | Git, GitHub |

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| ✅ 일기 수집 대화 에이전트 | 자연스러운 대화를 통해 하루의 이벤트와 감정을 수집 |
| ✅ 감정 키워드 추천 및 색상 시각화 | 선택된 감정에 따라 감정 세부 키워드 자동 추천 |
| ✅ 비밀친구 편지 생성 | 명언, 음악 추천, 오늘의 칭찬 등을 포함한 편지 작성 |
| ✅ 멀티 에이전트 구조 | 각 기능을 병렬 처리하여 응답 속도 개선 및 확장성 확보 |
| ⏳ 향후: Web UI 및 API 배포 예정 | 현재는 로컬 환경에서 동작하며, UI 인터페이스도 구축 예정 |

---

## 🏗️ 아키텍처
`main_workflow`
<br>
<img width="773" height="531" alt="Image" src="https://github.com/user-attachments/assets/20d57991-ef82-476b-8a58-88c93cc7f1b1" />
<br>
`secretfriend_workflow`
<br>
<img width="515" height="432" alt="Image" src="https://github.com/user-attachments/assets/ee3bc990-e078-42ed-be0b-be0c78e4402b" />
<br>

> `main_workflow`에서 일기 내용을 수집하고 정제한 후,  
> `secretfriend_workflow`에서 다양한 피드백 요소(명언, 음악, 칭찬 등)를 생성하여  
> 사용자의 하루를 감정적으로 마무리합니다.

---

## 👥 기여도 및 역할

| 이름 | 역할 |
|------|------|
| 임예리 | 전체 설계 및 구현<br>main_workflow / secretfriend_workflow 설계<br>Tool 연동 (Spotify, Tavily)<br>LangGraph 기반 상태 흐름 설계 및 디버깅 |

---

## 🏁 결과

| 항목 | 내용 |
|------|------|
| 🎯 정량적 구성 | 일기 이벤트 단위 수집 구조 및 에이전트 분기 설계 완료 |
| 💡 기술적 성과 | LangGraph를 활용한 Node 기반 구조 완성 및 도구 연동 |
| 🤝 사용자 중심 설계 | '비밀친구'라는 콘셉트를 통해 일기 작성을 감정적으로 유도 |
| 🎯 확장 가능성 | 추가 피드백 요소(사주, 점성술, 명상 등) 연결 가능 구조로 설계 |

---

## 🔮 그 외 (향후 계획 및 회고)

- [ ] Web 인터페이스 (Streamlit or Django & react) 구축 예정
- [ ] 감정 차트 분석 기반 일/주/월간 통계 기능 추가 (감정 분석 보고서 작성)
- [ ] LLM Context를 활용한 일기 회고 RAG 기능 고도화
- [ ] 데이터 베이스 연동

### 💬 프로젝트를 통해 배운 점
- LangGraph의 강력한 흐름 제어 능력과 상태 공유 방식의 이해
- Tool 기반 에이전트 설계의 중요성 및 병렬 처리 구조의 이점
- 사용자의 감정 데이터를 다룰 때의 섬세한 설계 필요성

---

## 📎 기타

- 이 프로젝트는 개인의 감정 회고 및 정서적 성장을 위한 비영리 목적의 토이 프로젝트입니다.
- 모든 명언 검색은 Tavily Search 기반이며, 음악 추천은 Spotify API를 사용합니다.

---

> 🤗 당신의 하루는 어땠나요?  
> HowRU AI와 함께 하루를 돌아보고, 따뜻한 위로를 받아보세요.

> “AI가 당신의 감정을 기록해주고, 감정이 당신을 기억해주는 공간.”
> 그것이 **HowRU AI**입니다.
