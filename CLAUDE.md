# 사내 AI Specialist 추천서 작성 절대 규칙

## 작업 정의
- **목적**: 사내 AI Specialist 추천 서류 (Word 변환 예정 .md)
- **출력**: `D:/project/fbm_paper/recommendation/01_career_profile.md` + `D:/project/fbm_paper/recommendation/02_ai_portfolio.md`
- **본질**: **사내 지원서 (논문 아님)** — 임원에게 직접 보고하는 형식

## 절대 규칙

### Rule 1 (최우선): 논문이 아닌 지원서다
- 학회 인용 (CVPR/ICCV/NeurIPS/arXiv/et al.) 본문에 금지
- "N1-N9 contributions" / "paper integrity" / "retract" / "84-iteration cycle" 같은 논문 운영 표현 금지
- "본 논문" / "투고" / "학술" 표현 금지. 최신 양식에서는 별도 요약 섹션을 만들지 않으므로 해당 framing 문장도 사용하지 않는다.
- 기법명 자체 (ConvNeXtV2, CutMix, HDBSCAN 등) 는 한글 + 영문 병기로 유지

### Rule 2: 톤 = 임원 보고 + 존댓말
- 종결구 `~합니다 / ~입니다 / ~했습니다 / ~드립니다 / ~됩니다`
- 본인 호칭: "본인"
- 표 / 코드 / ASCII 다이어그램 / 부제목은 평어 유지

### Rule 3: 합격 평가 기준 (사용자 명시)
> **"반도체 역량 → AI 적용 → 현업 문제 개선"**
> 
> AI 기술 역량은 필수 조건이지만 결정적 차별성은 위 3-step 인과 chain.

이 메시지는 허용된 양식 안에서만 반복 반영한다. 최신 사용자 정정에 따라 `01_career_profile.md`에는 `기술 분야` / `업무경력`, `02_ai_portfolio.md`에는 `AI 프로젝트 수행 전체이력` / `대표 과제 상세 기술서` 외 별도 요약, 표지, 결론을 추가하지 않는다.

### Rule 4: 3개 프로젝트 구조
1. **P1**: FBM(Fail-Bit Map) 이미지 데이터 생성 + Known-CNN 2-stage 분류 + Unknown-contrastive 검출
2. **P2**: Chip multi-label classification. **main 성과는 FCM-PM 본인 신규 적용**이며, 서술 순서는 `CutMix 선정 → CutMix + Pair Mask 로 background loss 제외 → Full-Cover Mixup + Pair Mask (FCM-PM) 구성` 으로 둔다. val_margin / best-margin / temperature / ensemble / KD 는 FCM-PM 이후의 모델 최적화 보조 성과로 배치한다.
3. **P3**: Anomaly-detection. **main 성과는 AI 모델 자체가 아니라 데이터 생성**이다. BBD/Overlay/CD 현업 경험으로 형성된 trend 도메인 지식을 episode 합성 generator 로 코드화하고, Region 5종 / Noise 3종 / 일반 trend 불량 4종 + context 1종 / Fleet enforcement floor 를 설계한 점을 우선 서술한다. trend 이상 감지 모델은 특별한 skill 로 과장하지 말고, 생성 데이터가 학습 가능한지 확인하는 검증용 baseline / PoC 로 낮춰 쓴다.

### Rule 5: 본인 기여도 (★ 사용자 정정, 최종 ★)
- **P1**: 본인 **60%** / 현업 엔지니어 (아이디어 발의 및 불량 분석 교육) **20%** / 관리자 매니징 **20%**
- **P2**: 본인 **80%** / 관리자 매니징 **20%**
- **P3**: 본인 **80%** / 관리자 매니징 **20%**

### Rule 6: 팀 에이전트 4개 구조
1. **Master Orchestrator**: 모든 것 관장 + 최종 승인 (본 대화의 메인 thread)
2. **지원서 작성 agent**: .md 파일 작성/수정
3. **냉정한 평가 심사위원 agent**: 부족한 점 지적 + 합격률 추적
4. **자료조사 agent**: 폴더별 독립 병렬 + 이미지 분석 (하위 에이전트 폴더별 분리)

### Rule 7: 참조 폴더 6개 (모두 활용)
- `D:/project/known-cnn`
- `D:/project/mapviewer`
- `D:/project/unknown-contrastive`
- `D:/project/anomaly-detection`
- `D:/project/fail-map`
- `D:/project/fbm_paper`

### Rule 7.5: ★ 추천서 2 파일 분리 (사용자 최신 양식 명시) ★

사용자 직접 명시:
- 1차: "추천서는 따로다. 경력 기술서 (보유 기술) + 대표 과제 상세 기술서. 이거 2개를 따로 만드는 거다"
- 2026-05-14 양식 정정 이력: **"양식이 바뀌었다 다시 만들자 새로운 파일명으로"**, **"기술 분야도 기술표준 용어"**
- 2026-05-14 파일 수 정정: **"파일 2개다"** — 최종 제출물은 새 양식 기준 경력기술서 1개 + 포트폴리오 1개
- 2026-05-15 Codex 작업 대상 정정: 현재 제출본 수정 대상은 `01_career_profile.md` + `02_ai_portfolio.md` 2개다. `portfolio.md` 는 이미지/기존 내용 참조용으로만 사용하고, 사용자가 명시하지 않으면 제출본으로 직접 수정하지 않는다.

**출력 파일 2개** (반드시 분리):

#### 파일 1: `D:/project/fbm_paper/recommendation/01_career_profile.md` (경력기술서)
- 기술 분야
  - 기술 분야명은 반드시 기술표준 용어로 작성한다.
  - 예: Computer Vision / Image Classification, Self-Supervised Representation Learning, Synthetic Data Engineering, Machine Learning Optimization, MLOps / Data Pipeline Engineering, AI Systems Engineering.
  - 과제명, 사내 시스템명, 세부 수치는 `대표 적용 기법 / 방식` 칸에 배치한다.
- 업무경력
  - ㅁ 과제명
  - (1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과
  - (2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론

#### 파일 2: `D:/project/fbm_paper/recommendation/02_ai_portfolio.md` (포트폴리오)
- AI 프로젝트 수행 전체이력
  - 기간, 내용(과제명, 리딩 규모, 담당업무, 과제관리, 설계, 개발비중)
- 대표 과제 상세 기술서
  - P1 / P2 / P3 를 하나의 포트폴리오 파일 안에서 프로젝트별로 분리
  - 각 프로젝트는 `과제 기본정보` → `과제 참여 인력 및 역할` → `개인별 기여 서술` → `문제정의` → `기술적 해결 방안` → `구현 성과` 흐름 유지
  - `과제 참여 인력 및 역할` 표는 `NO / 성명 / Knox Id / 소속 / 역할 / 기여도` 컬럼을 사용한다.
  - `개인별 기여 서술`은 `[본인이 독자적으로 수행한 핵심 모듈]` 아래에 본인 핵심 모듈, 타 구성원과 차별화되는 담당영역, 기술적 해결책이 성패에 미친 영향을 쓴다.
  - `기술적 해결 방안`은 `[본인이 직접 수행한 핵심 로직]` 아래에 `데이터 / 알고리즘 / 최적화`를 쓰고, 실제 코드는 제외한 아키텍쳐 설계도 / 플로우차트를 둔다.
  - `구현 성과`는 `[정량적/정성적 성과]` 아래에 `기술 지표 / 현업 임팩트`를 구분해 쓴다.

#### 절대 규칙
- 2 파일 모두 `./figures/` 상대경로 유지 (같은 폴더)
- **통합 `ai_specialist.md` 삭제됨** (사용자 명시 "파일 따로 제출이라 지우자" — 2026-05-14)
- 최신 동기화 대상은 `01_career_profile.md` / `02_ai_portfolio.md` 2 파일이다.
- `recommendation/portfolio.md` 는 이미지와 기존 figure 참조용으로만 사용한다.

### Rule 7.6: ★ 에이전트 실시간 소통 ★

사용자 직접 명시: **"심사위원이랑 실시간 소통하고 자료조사랑도 실시간 소통해라"**

- **단발 호출 금지**: 심사위원 / 자료조사 에이전트는 한 번 호출 후 종료하지 말고 작업 사이클 동안 **SendMessage 로 재소통** (양방향 대화)
- **심사위원 에이전트 사전 확인 필수**: 심사위원 에이전트는 평가 시작 전 반드시 repo root 의 `CLAUDE.md` 최신 규칙을 먼저 확인하고, 사용자 최신 정정 / 금지 표현 / 데이터 출처 구분 / 양식 외 항목 금지 규칙을 평가 기준으로 삼는다.
- **심사위원 에이전트**: 평가 → 추천서 수정 → 같은 심사위원에게 재평가 요청 (sendMessage with `to: <agent-name>`)
- **자료조사 에이전트**: 자료 받음 → 추가 정보 필요 시 같은 에이전트에게 재질문
- **agent name 명시**: Agent 호출 시 `name` 파라미터로 식별자 부여 → SendMessage 로 재호출
- 단 사용자 추가 정정으로 작업 context 가 크게 바뀐 경우에는 새 에이전트 시작

### Rule 8: ★★★ 추천서 구조 — 사용자 양식 외 항목 추가 절대 금지 (영구 절대 규칙) ★★★

사용자 직접 명시 (영구 박힘):
> **"2개 파일을 만들어야 한다 하기 양식말고 다른 양식 추가는 절대금지"**

#### `01_career_profile.md` (경력기술서) — 다음 2 항목만, 그 외 절대 추가 금지
1. 기술 분야
2. 업무경력

#### `02_ai_portfolio.md` (포트폴리오) — 다음 2 항목만, 그 외 절대 추가 금지
1. AI 프로젝트 수행 전체이력
2. 대표 과제 상세 기술서

#### 대표 과제 상세 기술서 내부 양식 — P1 / P2 / P3 각각 다음 6 block 유지
1. 과제 기본정보 (과제명 / 수행기간 / 참여인원)
2. 과제 참여 인력 및 역할 (NO / 성명 / Knox Id / 소속 / 역할 / 기여도)
3. 개인별 기여 서술
4. 문제정의
5. 기술적 해결 방안 (★ 데이터 / 알고리즘 / 최적화 + 실제 코드 제외 아키텍처 설계도 / 플로우 차트 ★)
6. 구현 성과

#### 대표 과제 상세 기술서 내부 block별 최신 작성 형식
- `개인별 기여 서술`
  - `[본인이 독자적으로 수행한 핵심 모듈]`
  - 본인이 직접 맡은 핵심 모듈
  - 과제 안에서 타 구성원과 차별화되는 본인만의 구체적 담당영역
  - 본인의 기술적 해결책이 과제 성패에 미친 영향
- `문제정의`
  - 현장 난제 및 해결 목표
  - 기존 방식의 한계 및 AI 도입의 구체적 배경
  - 과제 수행 시 해결해야 했던 기술적 / 환경적 제약 조건
- `기술적 해결 방안`
  - `[본인이 직접 수행한 핵심 로직]`
  - 데이터 : 데이터 수집 경로, 전처리 기법 및 피처 엔지니어링 근거
  - 알고리즘: 선정한 모델 아키텍쳐와 선택 사유 (Logic Flow 중심)
  - 최적화: 성능 향상을 위해 본인이 직접 시도한 기술적 해법
  - `ㅁ 실제 코드를 제외한 아키텍쳐 설계도, 플로우차트 등으로 기술`
- `구현 성과`
  - `[정량적/정성적 성과]`
  - 기술 지표: 모델 정확도 향상, 추론 속도 개선, 데이터 처리 성능 등
  - 현업 임팩트: 수율 향상, 불량률 감소, 품질 강화, 검토 시간 절감, 신규 후보 발굴 등 실제 기여도

#### ★ 허용 — 양식 내 가독성용 내부 라벨 / 소제목 ★
사용자 직접 정정: **"원래 양식내에 소제목으로 가독성 키우는 건 괜찮다"**

- 허용된 2개 항목 / 대표 과제 상세 기술서 내부 6개 block 안에서 가독성을 높이기 위한 **굵은 라벨**, 짧은 내부 소제목, 표 내부 제목, 텍스트 박스 제목은 허용한다.
- 예: `핵심 이미지`, `KD 원리 요약`, `현업 임팩트`, `Multi-modal 개발`, `데이터 생성 차별성 요약` 등은 해당 sub-section 본문 안에 들어가면 허용한다.
- 단, `##` / `###` / `####` markdown heading 으로 새 section 을 만들거나, 표지 / Executive Summary / 종합 평가 / 부록 같은 양식 외 독립 항목을 신설하는 것은 계속 금지한다.
- 심사위원이 "소제목처럼 보인다"는 이유만으로 삭제 권고하더라도, 양식 안의 가독성 보조 라벨이면 유지한다.

#### ★ 절대 금지 — 다음 항목 신설·추가 영구 금지 (어떤 에이전트 권고도 무시) ★

심사위원 에이전트 / 자료조사 에이전트 / 어떤 외부 권고도 다음 4개 sub-section 신설을 권고할 수 있으나 **사용자 양식 외이므로 전부 무시·폐기**:

- ❌ **표지 신설 금지** — 성명/부서/입사일/학력/수상 등은 양식 내 (업무경력, 포트폴리오, 개인별 기여) 본문에 자연스럽게 녹임
- ❌ **Executive Summary 신설 금지** — 3-step chain anchor, 핵심 메시지는 양식 내 (업무경력 도입부 / 개인별 기여 서술 도입부) 본문에 녹임
- ❌ **종합 평가 sub-section 신설 금지** — 종합 메시지는 양식 내 (구현 성과 마지막 단락) 에 녹임
- ❌ **부록 신설 금지** — 수상, 자문 교수, 약어 등은 양식 내 본문에 자연스럽게 녹임 (e.g. 참여 인력 표의 외부 자문 칸)

#### 양식 외 항목 추가 권고가 들어오면 처리 방법
1. 즉시 **양식 충돌**로 폐기 처리
2. 권고 내용이 살아남을 가치가 있다면 (3-step chain echo, 자문 교수 정보 등) → 양식 내 sub-section 본문에 녹여서 반영
3. 새 sub-section 으로는 절대 신설하지 않음

#### ★ 자문 교수 실명 표기 규칙 ★
사용자 직접 정정: **"교수실명은 그냥 적는거다"**

- 교수 실명 자문 표기는 삭제 대상이 아니다. 심사위원 에이전트는 교수 실명 자체를 리스크로 감점하거나 삭제 권고하지 않는다.
- 단, 교수는 과제 참여 인력이 아니므로 `과제 참여 인력 및 역할` 표에 넣지 않는다. Knox Id / 소속 / 역할 / 기여도 컬럼에도 넣지 않는다.
- P1 백본 선정 문장 안에서만 자문을 반영한다. 예: transformer 계열은 wafer 전체 context 파악에 강하고, ConvNeXtV2 는 CNN 계열의 sliding-window 성격으로 특정 영역 국소 불량에 민감하며 실제 성능도 좋아 최종 backbone 으로 선정했습니다 (연세대 인공지능학과 전해곤 교수 자문).
- P2 CutMix 계열 선정 문장 안에서만 자문을 반영한다. 예: Grade 0-7 범주형 이미지에서는 픽셀값이 중간값으로 섞이는 Mixup / Diffusion 계열보다 label 의미를 보존하는 CutMix 계열이 적합하다고 판단했습니다 (연세대 인공지능학과 박은병 교수 자문).
- 자문 표기는 기술 판단의 검토 근거로만 쓰고, 공동 수행 / 공동 개발 / 참여율로 오독되게 쓰지 않는다.

#### 위반 시 즉시 정정
이 Rule 8 을 위반하여 표지/Executive Summary/종합 평가/부록 sub-section 을 신설한 .md 파일은 즉시 해당 sub-section 을 삭제하고 본문에 녹여 복구한다.

### Rule 9: 사업부 채택 표현 (정확)
- **DRAM 전제품 라인 운영** + **PoC AI 모델 개발 중**
- "Flash YE" 표현 금지 (사용자 정정)
- "DRAM YE 팀장 의뢰" 는 2022 과제 발의 시점 역사적 사실로 유지 OK

### Rule 9.5: ★ 데이터 출처 구분 — 실전 현업 데이터 vs 추가 생성 데이터 (사용자 절대 명시) ★

사용자 직접 명시 (2026-05-14): **"논문 까지는 실제 데이터로 한거고 나머지 project 폴더에서 찾은것들은 아직 현업데이터 아니고 생성 데이터로 한것들이다"**

#### 실전 현업 데이터 (사내 실제 불량 이미지 데이터, 사내 실전 검증값)
- **출처**: `D:/project/fbm_paper/` 현재 프로젝트 폴더의 본문/추천서 근거
- **해당 항목**:
  - **P1 본인 1차 개발 ROI YOLO 2-stage weighted F1 0.95** (16-class · 1,500 labeled samples · 4:1 stratified split)
  - **P1 backbone 5종 비교 표** (ViT 0.81 / Swin 0.84 / EffNetV2 0.85 / MaxViT 0.87 / ConvNeXtV2 0.87 / +Optuna 0.92 / +ROI 0.95)
  - **P1 Unknown 5일 운영 데이터 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 → 7 실제 불량 현업 확인 (정량 metric 없음)**
  - **Cython 100배 / palette PNG 75% / 1시간 주기 적재 / 일 약 2만 장** 운영 수치
  - **mapviewer 12일 누적 2,317 요청** 운영 수치
- **추천서 라벨**: `[실전 현업 데이터]` 또는 `[양산 운영 / 사내 실전 검증]`

#### 추가 생성 데이터 개발 (baseline → 성능 향상 개발 중)
- **출처**: 다음 폴더의 추가 개발/PoC 정량 수치
  - `D:/project/known-cnn/` — chip 단위 결함 분류 결과를 wafer 좌표계에 재구성하는 보정 구조, chip multi-label (P1 본인 2차 개발 + P2 전체)
  - `D:/project/unknown-contrastive/` — Unknown self-supervised 추가 생성 데이터 개발 (WM-811K 분포 생성 9,250 PNG)
  - `D:/project/anomaly-detection/` — trend chart episode 합성 (P3 전체)
- **해당 항목**:
  - **P1 본인 2차 개발 chip 단위 결함 분류기 val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838±0.0092** (추가 생성 chip 데이터셋, Stage 2 개발 중)
  - **P1 Unknown same-anchor ARI 0.8588 ± 0.018 / same-anchor capture 43/43 / cross-anchor ARI 0.4437 / cross-anchor capture 38/38** (WM-811K 분포 생성 9,250 PNG self-supervised, baseline → 성능 향상 개발 중)
  - **P2 bit F1 0.9943 / Total FAR 0.00% / val_f1 → val_margin +5.2%p / Spearman ρ +0.56** (추가 생성 chip 평가셋 16+ class × ~3,850)
  - **P3 Binary F1 0.9967 / Abnormal Recall 0.9987 / 5-seed sweep 0.9944~0.9988** (합성 trend chart 6 class × 125 sample, 모델 차별성 주장이 아니라 생성 데이터 학습 가능성 확인용 참고 수치)
- **추천서 라벨**: `[추가 생성 데이터, 개발 중]` 또는 `[PoC / 생성 평가셋]`

#### 추천서 작성 절대 원칙
- 모든 정량 수치 옆에 **데이터 출처 라벨** 명시 (실전 현업 / 추가 생성 데이터)
- "실전 현업 데이터" 와 "추가 생성 데이터 개발" 을 혼동 표기 금지 — 임원 신뢰 손상 위험
- 추가 생성 데이터 수치는 PoC/개발 중 명시 + "baseline부터 성능 향상 개발 중" 일관 표현
- 실전 현업 데이터 기반 시각화와 추가 생성 데이터 기반 시각화를 캡션에서 구분

#### ★ P1 Unknown 서술 순서 절대 규칙 — 실전 운영 확인 후 생성 데이터 metric 개발 ★
사용자 직접 정정: **"실전 운영은 지표가 없다. 13후보 7실제 불량밖에 없고, 데이터 생성해서 metric 보면서 개발중이다"**

- P1 Unknown 의 실전 운영에는 **F1 / ARI / capture 같은 정량 metric 이 없습니다.**
- 실전 현업 근거는 오직 **[실전 현업 데이터] 5일 운영 데이터 10,000장 학습 + 별도 1일 운영 데이터 2,000장 적용 → 13 후보 → 7 실제 불량 현업 확인** 입니다.
- `unknown-contrastive` 폴더의 ARI / capture / cross-anchor 등은 **실전 운영 확인 이후**, 추가 개선 및 정량 metric 측정을 위해 생성 데이터를 만들어 개발 중인 보조 지표입니다.
- 추천서 본문에서는 P1 Unknown 을 `실전 운영 적용 및 현업 확인 (13 후보 / 7 실제 불량, 정량 metric 없음) → 추가 개선/metric 측정을 위한 생성 데이터 PoC` 순서로 씁니다.
- `실전 운영 검증 완료` 라는 표현이 정량 metric 검증 완료로 오독될 수 있으면 쓰지 말고, **실전 운영 적용 및 현업 확인** 으로 표현합니다.
- ARI / capture / cross-anchor 를 실전 현업 성과처럼 앞세우거나, 실전 운영 확인보다 먼저 배치하면 안 됩니다.
- 생성 데이터 지표 라벨은 반드시 `[추가 생성 데이터, 개발 중]` 또는 `[PoC / 생성 평가셋]` 로 둡니다.
- Unknown recipe 비교표를 넣을 경우 전체 실험 로그를 복붙하지 말고, 대표 recipe 만 압축 표로 넣습니다. 표에는 `Global InfoNCE baseline`, `Local DenseCL`, `MoCo Queue`, `NV-Retriever NEG`, `NeCo`, `NEW recipe 3-seed avg`, `KNN-softmax 후처리`, `cross-anchor stress test` 정도만 남기고, **paper / SOTA / iter / iteration** 같은 논문 운영 표현은 추천서 제출본에서 삭제합니다.
- 제출본에서 Unknown contrastive 추가 생성 데이터 성능표를 넣을 때는 아래 skeleton 을 사용합니다. 이는 실전 현업 성과가 아니라 **추가 개선 및 metric 측정을 위한 생성 데이터 개발 관리표**입니다. 빈 칸은 `TBD` 또는 `학습 후 채워짐` 으로 둡니다.

| # | Recipe | P1 | P2 | P3 | P4 | ARI | AMI | Sil |
|---|--------|----|----|----|----|-----|-----|-----|
| 1 | B0 Global InfoNCE only | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 |
| 2 | + Local DenseCL (LW=0.5) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 3 | + MoCo Queue 4096 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 4 | + NV-Retriever NEG 0.72 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 5 | + NeCo 0.2 (B5 5-tool full) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 6 | NEW (B5 - Local, 4-tool) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 7 | NEW + tau=0.5 post-reassign | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

#### ★ P1 Known 2-stage 서술 절대 규칙 — 실전 검증 구조와 생성 데이터 추가 개발 구조 분리 ★
사용자 직접 정정: **"P1 known 은 2 stage 실전데이터로 검증 한거고 cnn -> roi-yolo 에서 현재 다양한 평가를 위해 생성한 데이터셋으로 cnn->chip-cnn obj id map 으로 분류하려한다"**

- P1 Known 의 **실전 검증 완료 성과**는 반드시 **CNN → ROI-YOLO 2-stage** 로 씁니다.
- 해당 실전 검증 성과는 추천서 제출본에서 **[실전 현업 데이터] 사내 실제 불량 이미지 데이터, 16-class · 1,500 labeled samples · 4:1 stratified split, weighted F1 0.95** 로 중립 표기합니다. BBD/Overlay/CD 경험 근거처럼 오독되지 않도록 P1 Known 데이터 출처 설명에서 BBD 표현을 반복하지 않습니다.
- 현재 추가 개발 중인 구조는 기존 **CNN → ROI-YOLO** 구조를 대체/확장하기 위한 **CNN → chip-CNN obj-id map** 구조입니다.
- `known-cnn` 폴더의 chip-CNN / obj-id map / chip 단위 결함 분류 수치는 **다양한 평가를 위해 생성한 데이터셋 기반의 추가 개발값**입니다.
- 추천서 본문에서는 P1 Known 을 `실전 데이터로 검증된 CNN → ROI-YOLO 2-stage 성과 → 생성 데이터셋 기반 CNN → chip-CNN obj-id map 추가 개발` 순서로 씁니다.
- chip-CNN obj-id map 수치를 ROI-YOLO 0.95 와 동일한 실전 현업 성과처럼 쓰거나, 실전 검증 완료 수치로 표현하면 안 됩니다.
- chip-CNN obj-id map 라벨은 반드시 `[추가 생성 chip 데이터, 개발 중]` 또는 `[PoC / 생성 평가셋]` 로 둡니다.

#### ★ P2 Multi-label 생성 성능표 placeholder 규칙 ★
- P2 생성 성능표는 `Baseline → Focal loss → ASL → CutMix only → CutMix + Pair → FCM-PM best val_f1 → FCM-PM best val_margin → Ensemble → KD` 순서로 둡니다.
- 빈 칸은 조작하거나 임의 하향하지 말고 `TBD` 로 둡니다. 사용자가 제공한 수치가 있는 row 만 입력합니다.
- 제출본에서는 `SOTA` 라는 표현을 쓰지 않습니다. 사용자 초안에 `SOTA single` 이 있으면 **`best single 후보`** 로 바꿉니다.
- 제출본에서는 논문 운영처럼 보이는 `iter` 표현을 쓰지 않습니다. run 식별자가 필요하면 `run112`, `run116J` 처럼 중립 표기하거나 생략합니다.
- 현재 placeholder 표는 아래 값으로 관리합니다.

| # | Recipe | bit_F1 | single | 2combo | FAR | NI-FAR | OOD-FAR | Note |
|---|--------|--------|--------|--------|-----|--------|---------|------|
| 1 | Baseline (BCE+LS=0.30, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 2 | Focal loss (T9 sigmoid_focal, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 3 | ASL (T4 asymmetric, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 4 | CutMix only (random rect, no pair) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 5 | CutMix + Pair (random rect + masked) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 6 | FCM-PM best val_f1 (run112 ep=20) | 0.9652 | 1.0000 | 0.9517 | 0.15 | 0.00 | 0.62 | val_f1 best |
| 7 | FCM-PM best val_margin (run116J) | 0.9918 | 0.9996 | 0.9892 | 0.00 | 0.00 | 0.00 | best single 후보 |
| 8 | Ensemble 4-bag g=2/2/3/4 (A+C+J+F) thr=0.3 | 0.9615 | 1.0000 | 0.9475 | 0.00 | 0.00 | 0.00 | g-diverse FCM-PM |
| 9 | KD distill 4-bag → student | TBD | TBD | TBD | TBD | TBD | TBD | 4-bag 후 dispatch |

### Rule 10: 다이어그램은 텍스트 (이미지 새로 생성 X)
- workflow / architecture flow 는 ASCII 또는 텍스트 박스
- 새 이미지 생성 시도 금지 ("이미지는 잘 못 만드네" — 사용자 평가)

### Rule 11: 잘못 박은 표현 (영구 금지)
- "overlay bit data 분석" / BBD 앞에 photo 를 붙이는 표현 — 부정확한 표현. **"BBD 등 불량 / Overlay 측정·분석"** 으로 통일
- **BBD / Overlay / CD 불량 분석 경험 적용 범위 절대 규칙**: BBD 담당, Overlay, CD 불량 분석은 본인 현업 시절의 경험 자산이며, 이 경험은 **P3 anomaly-detection 의 trend episode 생성 / noise 매핑 / 불량 trend 형상 코드화에 활용한 것**입니다. **P1/P2의 직접 근거로 쓰면 안 됩니다.** P1/P2는 Failbit Map 의미 인지, 현업 사용자 학습, 이미지 처리/모델 설계 경험을 근거로 서술합니다.
- "wafer bit map (grade 0-7 + BIN) 의미 사전 인지" — 본인 photo 경력에 없는 표현. **"Failbit Map 의미 인지 (인접 부서 협업으로 자연 인지)"** 또는 **"본 과제 시작 시점에 현업 사용자로부터 수개월간 학습"**
- "도메인 × AI 융합" — 기술 분류표에 들어갈 항목 아님. 강점 narrative 에서만 사용
- "향후 계획 LLM / 강화학습 ▲" — 보유 기술표에 들어갈 항목 아님
- "Top 1 강점" / "★ 핵심 표 N ★" 같은 자기홍보 / 강조 인플레이션 — 학술 톤으로 정제

### Rule 12: 작업 진행 패턴
- 사용자 추가 정보 / 정정 → 즉시 반영 + push (commit 1회 / 사이클)
- 각 사이클: 자료조사 → draft/revise → 심사위원 검토 → 합격률 추적
- 자료조사 에이전트는 폴더별 독립 병렬 (서로 보지 말 것)
- 학술 인용 다수 금지 — 핵심 기법만 (사용자 평가: "추천서는 논문이 아니다 핵심 기법만")

### Rule 13: 이미지 활용 규칙 (★★ 사용자 절대 명시 — 최종 정책 ★★)

**Absolute Rule (위반 시 즉시 정정)**:
> "chip map이나 wafer map은 절대로 생성하지마라"
> "E:/data/images 여기서 복사해와서 ./figures/ 유지"

#### 13.1 ★ 최종 정책: E:/data/images 원본 → ./figures/ 복사 → 추천서 상대경로 사용 ★

**원본 출처** (E:/data/images):
- **합성 wafer 이미지**: `E:/data/images/unknown/<class>/*.png`
  - `Center_fork`, `Edge-Ring_bank_boundary`, `Donut_scratch`, `Edge-Top_scratch`, `Edge-Ring_scratch_rot`, `RingDots` 등 wafer-class 폴더
- **chip 단일 이미지**: `E:/data/images/classification_chips/<obj>/*.png`
  - `bank_boundary`, `fork`, `scratch`, `scratch_rot`, `invalid_main`
- **chip multi-label 평가**: `E:/data/images/chip_multilabel_v15direct/<class>/*.png`
  - single + 2-combo (`bank_boundary+fork`, `fork+scratch` 등) + Normal + Invalid + OOD (`Starburst`, `CenterDonut`, `CrossScratch`, `DiagonalSmear`)
- **chip multi-label mega eval**: `E:/data/images/chip_multilabel_mega_eval_n200/<class>/*.png`
  - 3-combo 까지 포함

**복사 destination**: `D:/project/fbm_paper/recommendation/figures/`

**추천서 사용 경로**: `./figures/<filename>.png` (모든 .md 파일이 상대경로 사용)

**작업 flow**:
1. 이미지 분석 에이전트가 E:/data/images 탐색 → 적절한 wafer/chip 식별
2. `cp` 로 D:/project/fbm_paper/recommendation/figures/ 에 복사 (파일명 단순화)
3. 추천서 markdown 에서 `./figures/<filename>.png` 상대경로 참조

#### 13.2 절대 금지
- **chip map / wafer map 새로 생성 절대 금지** (Python plot / matplotlib / PIL 등 어떤 방법으로도 X)
- **추천서 본문에 `E:/data/images/...` 절대경로 직접 삽입 금지**
- **E:/data/images 에서 선별한 파일은 반드시 `D:/project/fbm_paper/recommendation/figures/` 로 복사 후 `./figures/<filename>.png` 로 참조**
- **manager_report 의 figs / heatmap / preview 등 보조 이미지를 wafer/chip 대체로 사용 금지**
- **이미지 파일 절대 삭제 금지** (★ 사용자 직접 명시: "이미지는 절대로 지우지마라")
  - 예외: 사용자가 특정 이미지를 직접 지시하여 삭제 요청한 경우만

#### 13.6 ★ hybrid_fig 6장 사용 절대 금지 ★
사용자 직접 명시 (이미지 6장 보여주며): **"이것들은 지우고 다시는 쓰지 마"**
- 금지: `hybrid_fig1_overview.png` / `hybrid_fig2_distribution.png` / `hybrid_fig3_matching.png` / `hybrid_fig4_flowchart.png` / `hybrid_fig5_zoomed_example.png` / `hybrid_fig6_confusion_pairs.png`
- 추천서 어떤 형식으로도 참조 X
- 이미 figures/ 에서 삭제됨
- 도식 대용 = ASCII 다이어그램 + 실제 wafer 이미지 (E:/data/images/unknown/)

#### 13.3 추천서에 삽입 방식
- **`./figures/<filename>.png` 상대경로** 사용 (모든 .md 파일 통일)
- 마크다운: `![캡션](./figures/wafer_center_fork.png)`
- 또는 `<img src="./figures/<filename>.png" width="200" />` HTML
- Word 변환 시 같은 폴더 내 figures/ 자동 인식

#### 13.4 다이어그램 / Workflow / Architecture Flow
- **텍스트(ASCII) 시각화** (이미지로 만들지 X)
- 사용자 평가: "이미지는 잘 못 만드네" — 새 이미지 생성 시도 절대 금지

#### 13.5 이미지 분석 에이전트 역할
- `E:/data/images/` 폴더 탐색해서 적절한 wafer / chip 이미지 식별
- `cp` 로 `D:/project/fbm_paper/recommendation/figures/` 에 복사 (파일명 단순화)
- 추천서 markdown 에서 `./figures/` 상대경로 참조
- 캡션 작성 및 삽입 위치 결정

### Rule 14: 기술적 해결 방안 표현 규칙 (사용자 첫 메시지 명시)
사용자 첫 메시지 원문:
> "실제 코드를 제외한 **아키텍쳐 설계도, 플로우 차트 등으로 기술**"

- §6.X.4 (기술적 해결 방안) 에서 **실제 코드 인용 금지**
- `기술적 해결 방안`은 반드시 `[본인이 직접 수행한 핵심 로직]`으로 시작한다.
- 내부 구성은 `데이터 / 알고리즘 / 최적화` 3개 축으로 쓴다.
  - 데이터 : 데이터 수집 경로, 전처리 기법 및 피처 엔지니어링 근거
  - 알고리즘: 선정한 모델 아키텍쳐와 선택 사유 (Logic Flow 중심)
  - 최적화: 성능 향상을 위해 본인이 직접 시도한 기술적 해법
- 아키텍처 설계도 / 플로우 차트 / 의사결정 트리 = **텍스트 박스 / ASCII 다이어그램 / 표** 로 시각화
- Logic flow 중심 (코드 라인 X)
- `구현 성과`는 반드시 `[정량적/정성적 성과]`으로 시작하고, `기술 지표`와 `현업 임팩트`를 분리한다.
- 예시:
  ```
  [Input wafer] → [Stage 1: wafer-level CNN]
                    ↓ confidence < τ_gate
                  [Stage 2: chip-level CNN]
                    ↓
                  [chip별 결함 종류 지도 → G channel]
                    ↓
                  [Compound CNN → 33-class]
  ```

### Rule 15: 팀 에이전트 4 분리 (사용자 첫 메시지 명시)
1. **Master Orchestrator**: 모든 것 관장 + 최종 승인 (메인 thread)
2. **지원서 작성 agent**: .md 작성/수정
3. **냉정한 평가 심사위원 agent**: 부족 점 지적 + 합격률 추적
4. **자료조사 agent**: 폴더별 독립 병렬 + **이미지 분석 에이전트** 포함

이미지 분석 에이전트 (자료조사 하위):
- 실제 이미지 찾고 복사
- 추천서 삽입 위치 결정
- 캡션 작성

## 사용자 핵심 평가 메시지 (영구 박을 anchor)
> "회사에서는 반도체 역량을 AI 에 어떻게 적용해서 현업 문제 개선을 해내나 그걸 합격으로 볼 것이다. AI 기술 역량 뛰어난 것도 물론이고."

이게 본 추천서 평가의 메인 기준. 모든 결정은 이 메시지로 정렬.

---

## 사용자 첫 메시지 원문 (영구 보존, 빠짐없이)

> 자 사내 ai specialist 추천 서류를 작성할거다
>
> 총 3개 프로젝트 할거고
> 1. 현재 논문에도 나와있는 이미지 데이터 생성 및 known-cnn 2stage 그리고 unkown-contrastive
> 2. multi label classification- 이미지 cut mix부터 fcmpm    bestmodel margin 확정방식     temp 등 특히 새로운 방식들 만들어서 진행해나가는
> 3. anomaly-detection 이거는 데이터 생성에 주를 이루자 뒤에는 너무 식상하니까 domain kowlegde로 trend를 episode 방식으로 만들고 anomaly 값도 실제 불량 발생방식들 넣고
> noise 3종류 각각 설비 상태변동 산포 spike 에 매칭되는 것들 등 설명
>
> 팀 에이전트로 할거고
>
> 1. maser orchestrator
> 모든 것을 관장하고 이상 없는 지 확인하며 최종 승인한다
>
> 2. 지원서작성 agent
> .md 파일로 만들면 내가 word로 옮길게
> -------------------------------------------------------------------------------------
>
>
> 2개 파일을 만들어야 한다  하기 양식말고 다른 양식 추가는 절대금지
> 1. 경력 기술서  2. 포트폴리오
> 1. 경력 기술서  
> - 기술 분야 (기술표준 용어로 해야하고  예시들알려줄게 이런 형식으로한다  comuter vision llmnlp  강화학습 머신러닝 ai시스템 인지니어링 파이프라인구축 모델 최적화 등 똑같이 하지 않아도된다)
> - 업무경력
>      ㅁ 과제명
>         (1) 과제 개요 및 규모 담당 역할 수행 업무 성과(정량지표 권장)
>         (2) 과제 관련 도메인 ai 기술 모델 방법론 등
>
> 2. 포트폴리오
> - ai 프로젝트 수행 전체이력
>       기간, 내용(과제명, 리딩 규모, 담당업무, 과제관리, 설계, 개발비중:)
>
> - 대표 과제 상세 기술서
>    3개 프로젝트니까 다 적으면 된다
>    ㅁ 과제 기본정보(과제명:   수행기간:    참여인원:)
>    ㅁ 과제 참여 인력 미 역할(NO, 성명, Knox Id, 소속, 역할, 기여도)
>    ㅁ 개인별 기여 서술(본인이 독자적으로 수행한 핵심 모듈 -> 과제 내에서 타 구성원과 차별화되는 본인만의 구체적 담당영역, 본인의 기술적 해결책이 과제 성패에 미친 영향)
>    ㅁ 문제정의(현장 난제 및 해결 목표 -> 기존 방식의 한계 및 AI 도입의 구체적 배경, 과제 수행 시 해결해야 했던 기술적/환경적 제약 조건)
>    ㅁ 기술적 해결 방안(본인이 직접 수행한핵심 로직 -> 데이터 : 데이터 수집 경로, 전처리 기법 및 피처 엔지니어링 근거, 알고리즘 : 선정한 모델 아키텍쳐와 선택 사유 logic flow 중심, 
>                      최적화: 성능 향상을 위해 본인이 직접 시도한 기술적 해법) ㅣ 실제코드를 제외한 아키텍쳐 설계도, 플로우 차트 등으로 기술 
>    ㅁ 구현 성과(정량적/정성적 성과 -> 기술지표: ex 모델 정확도 향상, 추론속도 개선 등, 현업 임팩트: ex 수율향상, 불량률 감소 품질강화 등)
>
>    여기서부터는 양식은 아니고 주요사항
>    ㅁ 기술내용의 구체성(단순 툴 활용 능력이 아닌 현장 난제 해결을 위해 적용한 본인만의기술적 해법 troubleshooting 이 드러나도록 서술)
>    ㅁ 용어 표준화(사내 약어 사용은 가급적 지양하고, 전문가 심사위원이 이해할 수 있는 기술표준 용어 및 공식 평가지표 사용)
>    ㅁ 서류간 정합성 확보(데이터 일관성 -> 2개 문서가 일치해야한다  프로젝트명 수행기간 보니역할 )
>    
>
> -------------------------------------------------------------------------------------
>
> 심사위원 에이전트에게 전달하고 피드백 받고
> 자료조사 에이전트를활용해서 계속 자료들을 조사받아라
>
> 3. 냉정한 평가 심사위원 에이전트
> 너는 지원자들을 평가하는 에이전트로 부족한 점을 계속 지적해서 지원서 작성 agent에게 피드백해줘
>
> 4. 자료조사 에이전트
> 너는 아래의 파일과 폴더들읠 계속해서 조사해서 지원서 작성 agent에게 전달해줘
>
> 현재 프로젝트 폴더의 내용과
>
>   [OUT] D:/project/unknown-contrastive/docs/paper/manager_report/SUMMARY.md
>   [OUT] D:/project/unknown-contrastive/docs/paper/manager_report/cross_anchor_eval_260514.md
>   [OUT] D:/project/unknown-contrastive/outputs_contrastive_260514_001210/eval_E/eval_summary.json
>   [OUT] https://github.com/hogil/unknown-contrastive (commits 9c1873e, 0be76bf)
>
>  [OUT] D:/project/known-cnn/docs/chip-multilabel/manager_report/REPORT_beginner.md
>   [OUT] https://github.com/hogil/known-cnn/commit/3f3490e
>
>   [OUT] D:/project/known-cnn/docs/paper/figures/hybrid_fig1_overview.png
>   [OUT] D:/project/known-cnn/docs/paper/figures/hybrid_fig2_distribution.png
>   [OUT] D:/project/known-cnn/docs/paper/figures/hybrid_fig3_matching.png
>   [OUT] D:/project/known-cnn/docs/paper/figures/hybrid_fig4_flowchart.png
>   [OUT] D:/project/known-cnn/docs/paper/figures/hybrid_fig5_zoomed_example.png
>   [OUT] D:/project/known-cnn/docs/paper/figures/hybrid_fig6_confusion_pairs.png
>   [OUT] D:/project/known-cnn/docs/paper/02_method.md
>   [OUT] D:/project/known-cnn/docs/paper/00_abstract.md
>   [OUT] D:/project/known-cnn/docs/paper/CHANGELOG.md
>   [OUT] D:/project/known-cnn/hybrid_match/_paper_fig_hybrid.py
>
> D:\project\known-cnn D:\project\mapviewer D:\project\unknown-contrastive D:\project\anomaly-detection D:\project\fail-map D:\project\fbm_paper
> 이폴더들 참조

위 첫 메시지는 본 작업의 절대 사양이다. 어떤 항목도 빠뜨리지 말 것.
