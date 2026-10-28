# 📊 프로젝트 수행 결과 보고서

## 최신 진행 상황 — 2026년 10월 28일

### 반영한 기능과 화면

- **챗봇 구성 정보**: `data/sllm_info.json`에 엔진 방식, 지식 파일, 지원 언어, 번역 제공자, 유지 관리 방법을 기록했습니다. `/api/sllm-info` 및 챗봇 화면의 정보 보기에서 열람할 수 있습니다.
- **언어 지원**: 한국어와 베트남어(`vi`), 영어(`en`), 크메르어(`km`, 캄보디아), 네팔어(`ne`), 우즈베크어(`uz`)를 번역기와 챗봇 답변 번역 버튼에서 선택할 수 있습니다. 크메르어 질문 키워드도 추가했습니다.
- **번역 동작 보완**: 자동 감지를 한국어로 강제하지 않도록 수정하고, 짧은 정상 번역 결과를 허용했습니다. 긴 입력은 UTF-8 바이트 단위로 나누며 입력을 잘라 버리지 않습니다. API 입력 검증, 장애 시 HTTP 503, 실패 결과 캐시 방지를 적용했습니다.
- **디자인**: `static/campus.css`에 공통 스타일을 분리했습니다. 짙은 청록색과 민트색을 바탕으로 홈의 기능 바로가기, 챗봇, 번역기, 안내 상세 화면을 통일했습니다. 모바일 메뉴 접근, 가로 넘침, 다크 모드 및 키보드 초점 표시를 보완했습니다.

### 검증 결과

- `python -m unittest discover -s tests -v`: 12개 테스트 통과. 언어 조합, 자동 감지 전달, 긴 입력 보존, API 오류 및 재시도, 크메르어 챗봇 검색을 검증했습니다.
- 브라우저: 모바일 화면에서 ‘장학금’을 입력하고 크메르어 번역 결과가 표시되는 흐름을 확인했습니다. 이 검증은 내장 학사 용어 사전을 사용합니다.
- 홈, 모바일 번역기, 챗봇 다크 모드, 학사 안내 상세 화면을 확인했습니다. 검사한 모바일 화면의 페이지 가로 넘침은 없었습니다.
- `design-preview.png`: 수정한 홈 화면 캡처.

### 현재 구현 범위와 후속 작업

현재 엔진은 `data/procedures.json`과 `data/notices.json`을 검색해 템플릿 답변을 구성합니다. 신경망 sLLM 모델이나 추론 서버는 아직 연결되지 않았습니다. 외부 번역 서비스는 자동 테스트에서 모의 응답을 사용했으며 실환경 품질 검증은 별도입니다. 학사 규정·일정 JSON의 현행성도 운영 전 담당 부서 확인이 필요합니다.

아래는 기존 단계의 기록입니다.

---

**프로젝트명**: 중원대학교 AI 학생 어시스턴트 — Step 8 통합 프로토타입 구현 및 배포  
**작성일자**: 2026년 9월 30일  
**작업환경**: Windows / Python 3.12 / Flask 3.1.3 / Git  
**원격저장소**: [https://github.com/valuelux02/jungwon-ai-assistant](https://github.com/valuelux02/jungwon-ai-assistant)

---

## 1. 개요 및 목표

본 프로젝트는 분절되어 있던 이전 단계(Step 1~7)의 모듈들을 단일 웹 애플리케이션으로 결합하는 **Step 8 통합 프로토타입(Integrated Prototype)**을 완성하고, 사전 데이터베이스 오류 검토부터 로컬 서비스 안정화 및 **GitHub 원격 저장소 배포**까지 일괄 완료하는 것을 목표로 수행되었습니다.

---

## 2. 주요 작업 내용 및 결과

### ① 데이터베이스 DDL 스크립트 오류 분석 및 보정
* **문제점 진단**:
  * 테이블 정의 구문 끝 불필요한 콤마(Trailing Comma)로 인한 문법 오류(Syntax Error)
  * `students` 테이블의 기본키(PK) 누락으로 인한 `exam` 테이블의 외래키(FK) 참조 무결성 실패
  * `courses`와 `exam` 간의 외래키 제약조건명(`FksID`) 중복 충돌
* **조치 내용**: 
  * `students.studentID`에 `PRIMARY KEY` 설정 및 오타(`gendar` → `gender`) 정정
  * 외래키 제약조건명 분리(`FK_course_teacher`, `FK_exam_student`, `FK_exam_course`) 및 DDL 완전 정상화 코드 제공

---

### ② Step 8 통합 웹 애플리케이션 구현
이전 단계의 학생 행정 가이드에 더해 신규 기능들을 유기적으로 결합하여 통합 Flask 시스템을 구축했습니다.

* **AI 챗봇 인터페이스 (`/api/chat`)**:
  * 질문 키워드를 분석하여 행정 가이드 및 공지사항을 참조해 답변을 생성하는 RAG(검색 증강) 기반 챗봇 로직 구현
  * 휴학, 장학금, 기숙사, 증명서 등 자주 묻는 질문(FAQ) 원클릭 칩 버튼 지원
* **대학 공지사항 데이터 연동 (`data/notices.json`)**:
  * 학사, 장학, 기숙사, 외국인 유학생 등 주요 공지 데이터베이스 신규 생성 및 검색/상세보기 기능 연동
* **3개 국어(KO / EN / KM) UI 지원**:
  * 한국어, 영어, 크메르어(캄보디아어) 다국어 딕셔너리(i18n) 구축
  * 상단 언어 선택기를 통해 화면 텍스트 및 챗봇 환영 메시지가 실시간으로 전환되도록 처리
* **통합 검색 시스템**:
  * 한 번의 검색으로 행정 가이드와 대학 공지사항을 동시에 교차 검색(Cross-Search)
* **모니터링 및 엔드포인트 개선**:
  * 서버 상태, 등록 데이터 수, 포트 등을 반환하는 `/health` API 라우트 구현
  * 기본 서비스 포트를 5007번에서 **5008번**으로 마이그레이션

---

### ③ 프론트엔드 UI/UX 고도화
* `templates/index.html`: 탭 네비게이션(통합 홈, AI 챗봇, 행정 가이드, 공지사항)과 반응형 카드 뷰 적용
* `templates/procedure.html`: 행정 절차 상세 안내 화면 (목적, 대상, 필요 서류, 진행 단계, 담당 부서)
* `templates/notice.html`: 공지 상세 및 첨부파일/원문 링크 안내 화면

---

### ④ 가상환경 구축, 통합 검증 및 실행 오류 해결
* **가상환경 세팅**: `venv` 환경 생성 및 `Flask 3.1.3`을 포함한 의존성 패키지 설치 완료
* **자동화 검증 테스트**:
  * `/health`, 언어별 메인 페이지, `/procedure/<id>`, `/notice/<id>`, `/api/search`, `/api/chat` 전 항목 테스트 통과
* **연결 오류(`ERR_CONNECTION_REFUSED`) 해결**:
  * Flask 서버 백그라운드 구동 활성화 (`http://127.0.0.1:5008`)
  * 재부팅 후에도 원클릭으로 구동 가능한 `run_windows.bat` 및 `run_mac_linux.sh` 스크립트 최적화

---

### ⑤ Git 버전 관리 및 GitHub 배포 완료
* **보안 및 환경 설정**: 가상환경(`venv/`) 및 컴파일 캐시 파일 제외용 `.gitignore` 구성
* **네트워크/인증 이슈 해결**:
  * 학내/기관망 SSL 인증서 체인 오류(`CERT_TRUST_IS_PARTIAL_CHAIN`) 우회 설정 (`sslVerify false`)
  * 계정 권한 불일치(valuelux00 vs valuelux02) 진단 및 올바른 PAT 토큰을 통한 정상 인증 완료
* **배포 결과**:
  * **저장소**: `https://github.com/valuelux02/jungwon-ai-assistant`
  * **커밋**: `feat: Jungwon University AI Student Assistant - Step 8 Integrated Prototype`
  * **보안 조치**: 푸시 직후 로컬 Git 설정에 잔존하던 토큰 정보를 즉시 제거하여 보안성 확보

---

## 3. 최종 산출물 현황

```text
jungwon_step7/ (Step 8 Integrated Prototype)
├── app.py                  # Step 8 메인 Flask 애플리케이션 (Port 5008)
├── requirements.txt        # 의존성 라이브러리 목록
├── README.md               # Step 8 프로젝트 설명서
├── REPORT.md               # 금일 업무 수행 결과 보고서
├── .gitignore              # Git 형상관리 제외 설정
├── run_windows.bat         # Windows 원클릭 실행 스크립트
├── run_mac_linux.sh        # macOS / Linux 실행 스크립트
├── data/
│   ├── procedures.json     # 학생 행정 가이드 6종 데이터
│   └── notices.json        # 대학 공지사항 데이터
└── templates/
    ├── index.html          # 메인 탭 UI 및 챗봇 인터페이스
    ├── procedure.html      # 행정 절차 상세 뷰
    └── notice.html         # 공지사항 상세 뷰
```

---

## 4. 향후 권장 사항 (Next Steps)

1. **데이터 실체화**: 현재 포함된 행정 절차 및 마감일은 프로토타입용 예시 데이터이므로, 중원대학교 공식 학칙 및 최신 공지 PDF로 교체
2. **AI 엔진 확장**: 현재의 규칙/검색 기반 응답 로직을 실제 LLM(OpenAI/Gemini 등) 및 벡터 DB 기반의 RAG 파이프라인으로 연동
3. **다국어 실시간 번역**: 현재 UI 정적 번역 단계에서 나아가 챗봇 질의응답 내용 전체를 번역 API와 연계
