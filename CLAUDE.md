
# 사내 AI Specialist 추천서 작성 절대 규칙

## Rule -1 (Rule 0 위 최상위 절대규칙, 2026-05-16): 창 / cmd / popup 절대 안 뜸
- 10분 주기 cycle 무한 루프 돌더라도 **cmd 창 / PowerShell 창 / OS notification / popup 절대 띄우지 않는다**.
- background agent 들에게 다음 금지 규칙을 매 dispatch 마다 prompt 안에 명시한다:
  - Bash tool 호출 금지
  - PowerShell tool 호출 금지
  - PushNotification 호출 금지
  - 외부 알림 / SendMessage / cmd 실행 금지
  - 작업은 Read / Grep / Glob / Edit / Write tool 만 사용
- cron prompt 도 동일 규칙 박은 채 등록한다.
- 사용자가 "창 뜬다" 보고 시 즉시 CronDelete 로 중단하고 원인 추적.

## Rule 0 (최상위 절대규칙): AI 문체 금지
- 결국 내가 사내 AI 전문가로 인정받기위해 반도체역량을 바탕으로 AI 모델을 어떻게 설계하고 개밣했고 추가로 성능을 올리기위해 어떤 방법들을 적용시켰냐 이런게 중요
- 심사위원이 어떤 기법들인지도 느끼고 전체 설계도 이해하게 그리고 역량이 뛰어나구나 느낄 수 있게해서 합격하도록 만들자
- 추천서 문장은 절대 AI가 자동 작성한 것처럼 보이면 안 된다.
- 사람이 직접 쓴 지원서처럼 자연스럽고 담백하게 쓴다.
- 수치나 로그를 억지로 끼워 넣지 않는다. 심사자가 읽었을 때 "왜 이 말이 여기 나오지?" 싶은 문장은 삭제한다.
- 같은 문장 구조, 과한 요약체, 홍보 문구, 근거 없는 성과 포장은 전부 금지한다.
- 사용자가 직접 거부한 표현이나 어색하다고 지적한 문장은 이후 루프에서 다시 살리지 않다.
- **★ 절대 금지 기호 (2026-05-20)**: `§` (절 기호) — 본문, 표, ASCII 박스, inline 참조 어디에도 사용 금지. inline 참조는 `**[참조]**` 굵은 대괄호 형식만.
- **★ 호칭 (2026-05-20)**: 추천서에서 "운영자" 표현 금지. 현업에서 도구를 다루는 사람은 모두 "담당자" 로 통일.


## 작업 정의
- **목적**: 사내 AI Specialist 추천 서류 (Word 변환 예정 .md)
- **출력**: `D:/project/fbm_paper/recommendation/01_career_profile.md` + `D:/project/fbm_paper/recommendation/02_ai_portfolio.md`
- **본질**: **사내 지원서 (논문 아님)** — 임원에게 직접 보고하는 형식

## 절대 규칙

### ★★★★★ Rule 0.5 (양식 구조 절대규칙 — 2026-05-18 → 2026-05-19 정정): 대표 과제 상세 기술서 양식

각 프로젝트 (P1 / P2 / P3) 의 §대표 과제 상세 기술서는 다음 구조를 **그대로** 따른다. 6 ㅁ section, 각 안에 bracket block + 대시 bullet 으로만 내용을 단다.

```
ㅁ 과제 기본정보 (과제명 / 수행기간 / 참여인원)
ㅁ 과제 참여 인력 및 역할 (NO, 성명, Knox Id, 소속, 역할, 기여도)

ㅁ 개인별 기여 서술
   [본인이 독자적으로 수행한 핵심 모듈]
   - 과제 안에서 타 구성원과 차별화되는 본인만의 구체적 담당 영역
   - 본인의 기술적 해결책이 과제 성패에 미친 영향

ㅁ 문제정의
   [현장 난제 및 해결 목표]
   - 기존 방식의 한계 및 AI 도입의 구체적 배경
   - 과제 수행 시 해결해야 했던 기술적 / 환경적 제약 조건

ㅁ 기술적 해결 방안
   [본인이 직접 수행한 핵심 로직]
   - 데이터: 데이터 수집 경로, 전처리 기법 및 피처 엔지니어링 근거
   - 알고리즘: 선정한 모델 아키텍쳐와 선택 사유 (Logic Flow 중심)
   - 최적화: 성능 향상을 위해 본인이 직접 시도한 기술적 해법

ㅁ 구현 성과
   [정량적/정성적 성과]
   - 기술 지표: (예: 모델 정확도 향상, 추론 속도 개선 등)
   - 현업 임팩트: (예: 수율 향상, 불량률 감소 등)
```

**★ 형식 절대 규칙**:
- 대괄호 `[...]` 와 대시 `-` 사이에는 어떤 텍스트도 쓰지 않는다. 대괄호 라인 바로 다음 줄에 대시 bullet 이 와야 한다.
- 양식 spec 의 항목 설명 ("데이터 수집 경로, 전처리 기법 및 피처 엔지니어링 근거" 등) 은 대시 bullet 옆에 그대로 적되, 본문 내용은 대시 bullet **아래**로 옮긴다.
- 대시 bullet 항목 (데이터 / 알고리즘 / 최적화 / 기술 지표 / 현업 임팩트 등) 을 `**[데이터]: ...**` 같은 sub-bracket header 로 변환하지 않는다. 항상 `- 데이터: ...` 대시 bullet 형식 유지.
- 이 양식 외 추가 ㅁ section (예: 표지 / Executive Summary / 핵심 요약 / 종합 평가 / 부록) 절대 신설 금지.
- 양식 내부에서 가독성용 sub-heading (bold label, 짧은 소제목, 표 안 제목) 은 허용. 단 `##` / `###` / `####` markdown heading 으로 새 section 신설은 금지.

### Rule 1 (최우선): 논문이 아닌 지원서다
- 그냥 회사에 AI 전문가 인증제에 지원하는거다
- "본 논문" / "투고" / "학술" 표현 금지. 최신 양식에서는 별도 요약 섹션을 만들지 않으므로 해당 framing 문장도 사용하지 않는다.

### Rule 2: 톤 = 임원 보고 + 존댓말
- 종결구 `~합니다 / ~입니다 / ~했습니다 / ~드립니다 / ~됩니다`
- 본인 호칭: "본인"
- 절대 전제조건: 문장은 AI가 자동 요약한 것처럼 보이면 안 된다. 사람이 직접 작성한 보고서처럼 자연스럽고 구체적으로 쓴다.
- 같은 문장 구조를 반복하지 않는다. 특히 `핵심은 ... 점입니다`, `...확인했습니다`, `...구성했습니다` 같은 표현이 연속으로 나오면 문장을 나누거나 바꾼다.
- 과장된 홍보 문장보다 실제로 한 일, 판단 이유, 확인한 수치를 담담하게 쓴다.
- mapviewer / 운영 뷰어 request count, 특정일 peak 같은 사용 로그 숫자는 사용자 승인 없이 추천서에 넣지 않는다.
- 근거 문서끼리 흔들리는 생성 데이터 세부 metric은 추천서 본문에 직접 넣지 않는다. 다만 P2처럼 현업 defect chip을 원천으로 삼고, 부족한 조합 defect를 반도체 도메인 분포에 맞춰 생성한 경우에는 단순 생성 실험처럼 낮춰 쓰지 않는다. "현업 defect 원천 + 도메인 확률분포 기반 생성/검증"으로 정확히 쓰고, 실제 현업 defect를 AI 학습 가능한 조합 문제로 바꾼 역량이 먼저 읽히게 한다.

### Rule 3: 합격 평가 기준 (사용자 명시)
> **"반도체 역량 → AI 적용 → 현업 문제 개선"**
> 
> AI 기술 역량은 필수 조건이지만 결정적 차별성은 위 3-step 인과 chain.

이 메시지는 허용된 양식 안에서만 반복 반영한다. 최신 사용자 정정에 따라 `01_career_profile.md`에는 `기술 분야` / `업무경력`, `02_ai_portfolio.md`에는 `AI 프로젝트 수행 전체이력` / `대표 과제 상세 기술서` 외 별도 요약, 표지, 결론을 추가하지 않는다.

#### ★ P1/P2 평가 framing 최신 정정 ★
- 추천서 본문에는 `논문`, `학술`, `투고` 표현을 쓰지 않는다. 다만 심사자가 읽는 인상은 아래처럼 가야 한다.
- **P1**은 단순 모델 실험이 아니라 **운영형 산업 AI 시스템**으로 쓴다. raw log를 Failbit Map 이미지와 chip position JSON으로 바꾸고, Known은 CNN -> ROI-YOLO로 재확인하며, Unknown은 contrastive embedding + HDBSCAN으로 현업 검토 후보 group을 줄인 구조다. 핵심은 raw data 변환, 모델 분기, 현업 검증 흐름을 하나로 연결했다는 점이다.
- **P2**는 단순 chip multi-label 분류가 아니라 **FCM-PM 방법론**으로 쓴다. 실제 현업 single defect chip patch를 원천으로 사용하고, 부족한 multi-defect 조합 label 문제를 해결하기 위해 Full-Cover Mixup과 Pair Mask loss를 결합한 구조다.
- P2에서 BCE 자체를 고급 기술처럼 쓰지 않는다. BCE는 multi-label 기본 loss이고, 높은 수준으로 평가받을 부분은 **BCE 위에 얹은 FCM-PM 데이터 구성, Pair Mask loss 제어, val-margin checkpoint selection, max-prob gate, bit_F1 + FAR 동시 평가**다.
- P2 전체 flow는 `현업 single defect 원천 -> FCM-PM으로 2-combo 학습 데이터 구성 -> Pair Mask로 background 오학습 억제 -> BCE 기반 multi-label 학습 -> val-margin으로 checkpoint 선택 -> max-prob gate로 Normal / Invalid / OOD FAR 억제 -> bit_F1 + FAR 동시 평가`로 보이게 한다.
- P2 핵심 주장은 다음 순서로 보이게 한다: `Grade 0-7 원값 보존 필요 -> 일반 Mixup 부적합 -> CutMix 계열 선택 -> random CutMix의 defect 잘림 문제 -> Full-Cover로 coverage 보장 -> background 오학습 문제 -> Pair Mask로 loss 분리 -> val-margin으로 FAR 기준 모델 선택`.
- P2 검증 신뢰도 방어 문장은 반드시 포함한다: **원천 chip 단위 split을 먼저 수행한 뒤, train 원천에서만 FCM-PM 조합을 생성하고, test 원천 chip은 조합 생성 과정에서 완전히 배제했다.**
- P2 ablation 흐름은 `Baseline BCE -> Focal -> ASL -> CutMix only -> CutMix + Pair -> FCM-PM best val_f1 -> FCM-PM best val_margin -> Ensemble -> KD` 순서로 관리한다. 메시지는 "loss만 바꿔도 안 되고, 단순 CutMix도 부족하며, 반도체 Grade image에서는 defect coverage와 background loss 분리가 필요하다"이다.
- P2에서 ensemble은 최종 운영 모델처럼 쓰지 말고, **성능 상한과 seed/checkpoint 안정성 확인용 teacher**로 쓴다. 4-bag ensemble은 추론 비용이 4배에 가까우므로 운영 생산성 관점에서는 무겁다는 점을 같이 둔다.
- P2에서 KD는 새 기술 발명처럼 쓰지 않는다. 강점은 **FCM-PM 기반 ensemble teacher의 판단을 single student로 압축해, multi-label defect 성능과 추론 생산성의 trade-off를 줄이는 운영 배포 설계**다. KD 성능값이 아직 없으면 `TBD`, `후보 검토`, `dispatch 예정`으로 둔다.
- KD까지 쓰는 표에는 성능 지표뿐 아니라 **Latency / Throughput / Params** 축을 같이 둔다. 메시지는 "ensemble으로 성능 상한을 확인했고, KD student로 single-model 운영성을 확보하는 구조까지 검토했다"이다.
- P1 Unknown은 계속 조심한다. 실전 운영 Unknown은 F1/ARI/AMI가 아니라 `13개 후보 group 중 7개 실제 불량`으로만 쓴다. 추가 생성 데이터 metric 표는 운영 성과가 아니라 후속 개발과 metric 관리를 위한 benchmark로만 둔다.


### Rule 5: 본인 기여도 (★ 사용자 정정, 최종 ★)
- **P1**: 본인 **60%** (fail-map 데이터 파이프라인, mapviewer 운영 뷰어 연동/기여, Known CNN -> ROI-YOLO 2-stage, Unknown contrastive learning, 후속 chip-CNN obj-id map 개발 구조 설계/구현) / 현업 엔지니어 **20%** (아이디어 발의, Failbit Map 의미 및 불량 분석 교육, Unknown 후보 현업 검증 협업) / 관리자 **20%** (방향성, 일정, 리뷰 매니징)
- **P2**: 본인 **80%** (현업 single defect chip 원천 정의, 반도체 결함 위치/강도/Grade 0-7 확률분포 설계, 2-combo 조합 생성, CutMix 계열 선정, Pair Mask, FCM-PM, val-margin best-model selection, temperature scaling, ensemble/KD 후보 검토) / 관리자 **20%** (방향성, 일정, 리뷰 매니징)
- **P3**: 본인 **70%** (trend episode generator, Region 5종, Noise 3종, anomaly 5종, 정상 산포 기준 최소 이상 강도 보정, 1차 binary gate 검증 PoC 설계/구현) / 관리자 **20%** (방향성, 일정, 리뷰 매니징) / 동료 엔지니어 (공동 연구자) **10%** (AI 모델 실행, 데이터 정리, 실험 결과 취합)

### Rule 5.5: 프로젝트 수행기간 (★ 사용자 정정, 최종 ★)
- **P1**: **2024년 10월 ~ 현재**
- **P2**: **2025년 3월 ~ 현재**
- **P3**: **2026년 1월 ~ 현재**
- `01_career_profile.md` 와 `02_ai_portfolio.md` 의 과제명, 수행기간, 본인 역할, 기여도는 항상 동일하게 유지한다.

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



#### ★ 허용 — 양식 내 가독성용 내부 라벨 / 소제목 ★
사용자 직접 정정: **"원래 양식내에 소제목으로 가독성 키우는 건 괜찮다"**

- 허용된 2개 항목 / 대표 과제 상세 기술서 내부 6개 block 안에서 가독성을 높이기 위한 **굵은 라벨**, 짧은 내부 소제목, 표 내부 제목, 텍스트 박스 제목은 허용한다.
- 예: `핵심 이미지`, `KD 원리 요약`, `현업 임팩트`, `Multi-modal 개발`, `데이터 생성 차별성 요약` 등은 해당 sub-section 본문 안에 들어가면 허용한다.
- 단, `##` / `###` / `####` markdown heading 으로 새 section 을 만들거나, 표지 / Executive Summary / 종합 평가 / 부록 같은 양식 외 독립 항목을 신설하는 것은 계속 금지한다.
- 심사위원이 "소제목처럼 보인다"는 이유만으로 삭제 권고하더라도, 양식 안의 가독성용 라벨이면 유지한다.


#### ★ 자문 교수 실명 표기 규칙 ★
사용자 직접 정정: **"교수실명은 그냥 적는거다"**
- 단, 교수는 과제 참여 인력이 아니므로 `과제 참여 인력 및 역할` 표에 넣지 않는다. Knox Id / 소속 / 역할 / 기여도 컬럼에도 넣지 않는다.
- P1 백본 선정 문장 안에서만 자문을 반영한다. 예: transformer 계열은 wafer 전체 context 파악에 강하고, ConvNeXtV2 는 CNN 계열의 sliding-window 성격으로 특정 영역 국소 불량에 민감하며 실제 성능도 좋아 최종 backbone 으로 선정했습니다 (연세대 인공지능학과 전해곤 교수 자문).
- P2 CutMix 계열 선정 문장 안에서만 자문을 반영한다. 예: Grade 0-7 범주형 이미지에서는 픽셀값이 중간값으로 섞이는 Mixup / Diffusion 계열보다 label 의미를 보존하는 CutMix 계열이 적합하다고 판단했습니다 (연세대 인공지능학과 박은병 교수 자문).
- 자문 표기는 기술 판단의 검토 근거로만 쓰고, 공동 수행 / 공동 개발 / 참여율로 오독되게 쓰지 않는다.


### Rule 9.5: ★ 데이터 출처 구분 — 실전 현업 데이터 vs 도메인 생성 데이터 ★
사용자 최신 정정 (2026-05-16): **P2는 단순 생성 데이터 PoC가 아니다. 실제 현업 chip defect 데이터를 원천 single defect로 사용했고, 현업에서 2-combo defect를 충분히 평가하기 어려워 반도체 도메인 확률분포에 맞춰 현업 이미지와 비슷한 조합 chip을 생성해 학습/평가한 것이다.**

- P2를 `추가 생성 chip 데이터 기반 PoC`처럼 낮춰 쓰면 안 됩니다.
- P2 평가의 핵심은 "없는 데이터를 가짜로 만든 것"이 아닙니다. 실제 현업 single defect chip의 결함 형태를 보존한 채, 현업에서 희소한 2-combo 결함을 반도체 도메인 확률분포로 재현해 multi-label 학습 문제로 바꾼 점입니다.
- P2의 본질은 **현업 single defect chip 원천 → 반도체 결함 분포/Grade 의미 보존 → FCM-PM으로 부족한 2-combo 결함 생성 → multi-label 학습과 false alarm 평가 가능화**입니다.
- 추천서에서는 P2를 **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]** 또는 **[현업 chip defect 원천 기반 결함 조합 학습]**으로 표기합니다.
- 표현 기준은 "현업 평가 데이터 부족을 보완하기 위해 현업 defect 원천과 도메인 분포를 반영해 생성/검증한 방법론"입니다. 추천서 본문에서는 한계 문장을 길게 붙여 낮춰 쓰지 말고, 현업 데이터 희소성을 AI 학습 문제로 바꾼 설계 역량을 앞세웁니다.
- 이 능력 자체가 평가 포인트입니다. 현업 이미지를 단순 복제한 것이 아니라, 반도체 Grade 0-7 의미, defect 위치/강도/조합 분포, Normal/Invalid/OOD false alarm 조건을 설계해 현업 이미지와 유사한 확률분포의 평가 데이터를 만든 것은 반도체 역량과 AI 설계 역량이 결합된 강점으로 써야 합니다.



#### ★ P1 Unknown 서술 순서 절대 규칙 — 실전 운영 확인 후 생성 데이터 metric 개발 ★
사용자 직접 정정: **"실전 운영은 지표가 없다. 13후보 7실제 불량밖에 없고, 데이터 생성해서 metric 보면서 개발중이다"**
- 제출본에서 Unknown contrastive 추가 생성 데이터 성능표를 넣을 때는 아래 skeleton 을 사용합니다. 이는 실전 현업 성과가 아니라 **추가 개선 및 metric 측정을 위한 생성 데이터 개발 관리표**입니다. 빈 칸은 `TBD` 또는 `학습 후 채워짐` 으로 둡니다.
- **★★★ 표 캡션 필수 1줄 (사용자 직접 명시 2026-05-16)**: 7-recipe 표 직전 또는 직후 캡션에 "이 표는 P1 Unknown 실전 운영 성과 (13 후보 중 7 실제 불량 현업 확인) 와는 분리된 후속 개발 / metric 관리용 synthetic benchmark 결과다. 실전 운영 Unknown 에는 정답 label 이 없어 F1 / ARI / recall 같은 정량 metric 이 성립하지 않고, 13/7 운영 검증은 후보 압축 결과이지 분류 metric 이 아니다" 식 한 줄을 박는다. 이 구분 없이 표만 두면 심사자가 "실전 Unknown 에도 ARI 가 있었던 것처럼 쓴 것 아니냐" 라고 의심한다.

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
- 현재 추가 개발 중인 구조는 기존 **CNN → ROI-YOLO** 구조를 대체/확장하기 위한 **CNN → chip-CNN obj-id map** 구조입니다.(**CNN → chip-CNN obj-id map** 확장하는이유도 설명)
- `known-cnn` 폴더의 chip-CNN / obj-id map / chip 단위 결함 분류 수치는 **다양한 평가를 위해 생성한 데이터셋 기반의 추가 개발값**입니다.
- 추천서 본문에서는 P1 Known 을 `실전 데이터로 검증된 CNN → ROI-YOLO 2-stage 성과 → 생성 데이터셋 기반 CNN → chip-CNN obj-id map 추가 개발` 순서로 씁니다.
- chip-CNN obj-id map 수치를 ROI-YOLO 0.95 와 동일한 실전 현업 성과처럼 쓰거나, 실전 검증 완료 수치로 표현하면 안 됩니다.
- chip-CNN obj-id map 라벨은 반드시 `[추가 생성 chip 데이터, 개발 중]` 로 둡니다.

#### ★ P2 Multi-label — 현업 defect 원천 + 도메인 생성/검증 표기 규칙 ★
- P2 성능표는 단순 생성 PoC 표가 아니라, **현업 defect chip 원천을 기반으로 2-combo 부족 문제를 보완한 도메인 생성/검증 관리표**로 둡니다.
- P2 표는 `Baseline → Focal loss → ASL → CutMix only → CutMix + Pair → FCM-PM best val_f1 → FCM-PM best val_margin → Ensemble → KD` 순서로 둡니다.
- P2 표에는 `Latency / Throughput / Params` 운영성 열을 추가합니다. Ensemble은 `4x / 1/4x / 4x`, KD student는 성능 미확정이면 `1x / 1x / 1x`와 `TBD`를 함께 둡니다.
- 표 제목이나 본문에 `추가 생성 chip 데이터 기반 PoC`만 단독으로 쓰지 않습니다. 필요하면 **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]**으로 씁니다.
- `bit_F1 0.9943 / Total FAR 0.00%`는 현업 defect 원천과 도메인 생성 평가셋 위에서 FCM-PM 구조가 2-combo 학습 신호와 false alarm 억제를 만든 검증 지표로 씁니다. 추천서 본문에서는 방어적 한계 설명을 반복하지 말고, 단순 생성 PoC보다 높은 수준의 방법론 검증으로 다룹니다.
- **★★★★ data leakage 방지 chip 단위 split 문장 필수 (사용자 직접 명시 2026-05-16)**: P2 §데이터 또는 §수행 업무 본문에 "single defect chip 원천을 chip 단위로 먼저 train / test 로 split 한 뒤, 2-combo 와 Pair Mask 합성은 train 원천 chip 만 사용했고, test 원천 chip 은 합성 과정에서 완전히 배제했다" 식 한 줄을 반드시 박는다. 이 문장이 없으면 면접 / 사후 검증에서 train ↔ test 누수 의심에 약해진다.
- **★★★★ ablation 핵심 메시지**: 표 직후 narrative 에 "Focal / ASL 처럼 loss 만 바꾸는 접근도, 단순 CutMix 도 본 과제 Grade 0-7 양자화 chip 이미지에서는 부족했고, 결정적 두 축은 defect coverage 보장 (Full-Cover Mixup) 과 합성 background 의 loss 분리 (Pair Mask) 다. 이 두 축을 한 학습 구조에 결합한 것이 FCM-PM" 톤을 한 단락 박는다.
- **외부 학회 / 박사논문 비교 / 학술 venue 톤 본문 금지 (Rule 1 보강)**: "KDD ADS", "AAAI IAAI", "WACV", "IEEE TSM", "ASMC", "박사논문급" 같은 외부 학술 venue / 비교 표현은 본문에 쓰지 않는다. 사내 지원서 톤 유지. 외부 논문화는 별도 트랙.
- **누수 의심 6 항목 점검표** (편집 시 매번): (1) chip 단위 split 무결성, (2) 2-combo 생성 방식 train / test 차이, (3) Normal / Invalid / OOD 가 너무 쉬운 negative 인지, (4) FAR 0 이 threshold 과도 인지, (5) class 별 n=2000 이 독립 sample 인지 augmentation copy 인지, (6) run116J val_margin 이 test 에 맞춘 것 아닌지. 본문에서 직접 또는 간접 반증되어야 함.

| # | Recipe | bit_F1 | single | 2combo | FAR | NI-FAR | OOD-FAR | Latency | Throughput | Params | Note |
|---|--------|--------|--------|--------|-----|--------|---------|---------|------------|--------|------|
| 1 | Baseline (BCE+LS=0.30, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 2 | Focal loss (T9 sigmoid_focal, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 3 | ASL (T4 asymmetric, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 4 | CutMix only (random rect, no pair) | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 5 | CutMix + Pair (random rect + masked) | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 6 | FCM-PM best val_f1 | 0.9652 | 1.0000 | 0.9517 | 0.15 | 0.00 | 0.62 | 1x | 1x | 1x | val_f1 best |
| 7 | FCM-PM best val_margin  | 0.9943 | - | - | 0.00 | 0.00 | 0.00 | 1x | 1x | 1x | REPORT 기준 bit_F1/FAR만 제출 |
| 8 | Ensemble | 0.9615 | 1.0000 | 0.9475 | 0.00 | 0.00 | 0.00 | 4x | 1/4x | 4x | teacher / 상한 확인 |
| 9 | KD distill  | TBD | TBD | TBD | TBD | TBD | TBD | 1x | 1x | 1x | deployable student 후보 |

### Rule 10: 다이어그램은 텍스트 (이미지 새로 생성 X)
- workflow / architecture flow 는 ASCII 또는 텍스트 박스
- 너무 단순하게하지마라 자세하게 만들고 어떻게 성능올렸는지와 성능올린 방식 초보자도 이해할 수 있게 작성
- 새 이미지 생성 시도 금지 ("이미지는 잘 못 만드네" — 사용자 평가)


### Rule 16: fail-map vs mapviewer 역할 분리 + 사내 인프라 노출 금지
- **fail-map** = FBM 이미지 데이터 **생성** 파이프라인 (Cython 100x, palette PNG, positions JSON, 이중 원천 병렬 처리).
 (`positions_module.py` / `cython_functions.pyx` / palette 생성).
- **web app** = FBM 이미지 **뷰어/검색** 시스템 (Vanilla JS + FastAPI + pyvips). commits 수가 많아도 본인 ownership 으로 과장하지 말고 "운영 뷰어 기여" 톤으로 조절. 면접에서 commit 비중 검증 시 위험.

### Rule 17: BBD / Overlay / CD 도메인 경험 표기 — 본인 담당 경험 기반 톤 (★ 사용자 직접 명시 2026-05-16)
- 사용자 직접 명시: **"BBD담당 / Overlay담당 등의 업무 경험을 바탕으로 뭔가해냈다고 그렇게 적어야지"**
- ❌ 금지 (추상 약어 나열): "BBD / Overlay / CD trend 판단 기준" / "BBD/Overlay/CD trend 해석 경험" / "BBD/Overlay/CD 현업에서 형성된 trend 도메인 지식"
- ✅ 권장 (본인 담당 경험 → 무엇을 해냈는지): "본인이 BBD담당 / Overlay담당 / CD담당 으로 쌓은 trend 분석 경험을 바탕으로 ~ 을 코드화했습니다 / ~ 을 generator parameter 로 옮겼습니다 / ~ 의 통계 분포를 직접 설계했습니다"
- P3 뿐 아니라 BBD / Overlay / CD 가 언급되는 모든 위치에 일관 적용.
- 본인의 BBD/Overlay/CD 담당 경력 → trend 도메인 지식 → 합성 generator 코드화 의 인과 chain 이 임원에게 명확히 읽혀야 한다.

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
  Claude 작업 대상:
  - D:/project/fbm_paper/recommendation/portfolio.md
  - D:/project/fbm_paper/recommendation/career_resume.md

  Codex 작업 대상 :
  - D:/project/fbm_paper/recommendation/01_career_profile.md
  - D:/project/fbm_paper/recommendation/02_ai_portfolio.md
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
>    ㅁ 개인별 기여 서술
>      [본인이 독자적으로 수행한 핵심 모듈]
>      - 과제 안에서 타 구성원과 차별화되는 본인만의 구체적 담당영역
>      - 본인의 기술적 해결책이 과제 성패에 미친 영향
>    ㅁ 문제정의(현장 난제 및 해결 목표 -> 기존 방식의 한계 및 AI 도입의 구체적 배경, 과제 수행 시 해결해야 했던 기술적/환경적 제약 조건)
>    ㅁ 기술적 해결 방안
>      [본인이 직접 수행한 핵심 로직]
>      - 데이터 : 데이터 수집 경로, 전처리 기법 및 피처 엔지니어링 근거
>      - 알고리즘: 선정한 모델 아키텍쳐와 선택 사유 (Logic Flow 중심)
>      - 최적화: 성능 향상을 위해 본인이 직접 시도한 기술적 해법
>      ㅁ 실제 코드를 제외한 아키텍쳐 설계도, 플로우차트 등으로 기술
>    ㅁ 구현 성과
>      [정량적/정성적 성과]
>      - 기술 지표: (예: 모델 정확도 향상, 추론 속도 개선 등)
>      - 현업 임팩트: (예: 수율 향상, 불량률 감소 등 실제 기여도)
>
> ----------------------------------------------------------------------------------
>
>여기서부터는 양식은 아니고 주요사항
>    1. 기여도 및 역할 기술의 객관성
>      ㅁ 실질 기여도 명시
>        ㅇ 팀단위 과제의 경우, 본인이 직접 설계하고 구현한 범위를 타 참여자의 역할과 엄격히 구분하여 기술해야함
>        ㅇ 전체 과제의 성과를 본인만의성과로 오인하도록 서술할 경우, 면접 심사 및 사후검증 시 불이익을 받을 수 있음
>      ㅁ 참여자 정보 일치
>        ㅇ 포트폴리오에 기재하는 참여 인력 및 기여도 정보는 해당 과제의 공식 기록(과제관리 시스템 등)과 부합해야 함
>    2. 기술 내용의 구체성
>      ㅁ 정량적 지표 중심 서술
>        ㅇ '성능향상', '수율개선' 등 추상적 표현을지양하고. as-is 대비 to-be의 개선 효과(%)를 명확히 기재
>        ㅇ 단순 툴 활용 능력이 아닌, 현장 난제 해결을 위해 적용한 본인만의 기술적 해법(Troubleshooting)이 드러나도록 서술
>      ㅁ 용어 표준화
>        ㅇ 사내 약어 사용은 가급적 지양하고, 전문가 심사위원이 이해할 수 있는 기술 표준 용어 및 공식 평가지표를 사용 할 것
>    3. 서류간 정합성확보
>      ㅁ 데이터 일관성
>        ㅇ '개발 경력서', '포트폴리오', 간의 프로젝트명 수행기간, 본인 역할 정보가 모두 일치해야함
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
