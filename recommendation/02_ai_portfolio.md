## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2022년 ~ 현재 | P1. Failbit Map AI 분류 시스템 | 3인 협업, 본인 70% 리딩<br>DRAM 전제품 라인 양산 운영<br>일 약 2만 장 wafer 처리 | S3 수집, Cython/Python 파싱, palette PNG / chip 좌표 JSON 생성, Web App 운영, Known 2-stage 분류 (0.78 → 0.87 → 0.92 → 0.95 ladder), Unknown self-supervised 검출은 현업 후보 13건 중 실제 불량 7건 확인, 정량 metric 은 추가 생성 데이터로 개발 중 | 10% | 40% | 50% |
| 2025년 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC, 본인 90% 리딩<br>16+ class × 약 3,850 chip<br>controlled synthetic benchmark | FCM-PM 합성 및 손실 마스킹 구조 구성, 학습·평가 체계 구축, best-model 선택 기준 및 운영 후보 검증 | 20% | 40% | 40% |
| 2025년 ~ 현재 | P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC | 2인 PoC, 본인 90% 리딩<br>1,500 sample 합성 trend chart 데이터 생성 | 합성 generator 설계, 도메인 자산 코드화, 생성 데이터 학습 가능성 검증 | 5% | 55% | 40% |

## 2. 대표 과제 상세 기술서

**ㅁ P1. Failbit Map AI 분류 시스템**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Failbit Map 대량 데이터 파이프라인 + single-label Known 2-stage 분류 + Unknown self-supervised 검출 |
| 수행기간 | 2022년 ~ 현재 |
| 참여인원 | 본인 / 현업 엔지니어 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 본인 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | Frontend, Backend, AI 모델 개발, 데이터 처리, 생성 파이프라인 전 영역 직접 수행 | 70% |
| 2 | 현업 엔지니어 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | 아이디어 발의 및 불량 분석 교육, Unknown 후보 13개 중 실제 불량 7개 확인 | 20% |
| 3 | 관리자 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | 방향성, 일정, 리뷰 매니징 | 10% |

**ㅁ 개인별 기여 서술**

본인은 Failbit Map 의 의미와 현업 사용자 분석 방식을 먼저 학습한 뒤, 대량 변환·저장·조회 파이프라인, Web App, Known 2-stage 분류, Unknown self-supervised 검출을 하나의 운영 흐름으로 연결했습니다. 반도체 분석 현장에서 쌓은 이해를 AI 모델 구조와 데이터 처리 설계에 직접 반영하여, 현업 분석 부담을 줄이는 운영 시스템으로 구현한 점이 본인의 핵심 기여입니다.

데이터 처리 단에서는 Cython 기반 hex-to-grade 변환으로 wafer 당 약 1,000만 cell 변환 병목을 약 100배 가속했고, 32-color palette-indexed PNG 저장으로 Failbit Map 저장 용량을 약 75% 절감해 양산 운영의 처리량과 저장 비용을 동시에 확보했습니다.

AI 모델 단에서는 ConvNeXtV2 + ROI YOLO 2-stage 로 16 class / 1,500 labeled samples / 4:1 stratified split **[실전 현업 데이터]** 에서 weighted F1 0.95 를 달성했으며, Unknown 검출은 **[실전 현업 데이터]** 5일 운영 데이터 10,000장 학습 + 별도 1일 2,000장 적용 결과 13 후보 중 7개가 실제 불량으로 현업 확인되었습니다. ROI YOLO 의 한계를 보완하기 위해 chip-CNN 결과를 wafer 좌표계 object-id map 으로 재구성하는 2차 보정 구조를 **[추가 생성 chip 데이터, 개발 중]** 기반으로 개발 중에 있습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | Failbit Map 은 EDS Test 에서 wafer 당 약 1,000만 cell 의 Grade 로 표현되는 초고해상도 데이터이며, 분석 엔지니어 수작업 판독만으로는 전수 분석이 어렵습니다. |
| 기존 방식의 한계 | 기존 조회는 1회 48매 수준에 머물렀고, 제품 / 시간 / lot 단위 누적 대량 분석이 어려웠습니다. 등록 외 신규 결함 패턴은 known classifier 만으로 검출하기 어렵습니다. |
| 기술적 / 환경적 제약 | label 데이터 부족 (16 class / 1,500 sample), 일 약 2만 장 wafer 처리, 1시간 주기 적재, 대량 이미지 저장 용량, Web App 응답성, 신규 unknown pattern 검출이 동시에 요구되었습니다. |

**ㅁ 기술적 해결 방안**

데이터 파이프라인은 설비 raw log 를 Failbit Map 이미지로 변환하고, AI 모델이 신규 불량 후보를 현업 검토 대상으로 올리며, 엔지니어가 대량 Failbit Map 을 빠르게 조회·비교·확인할 수 있도록 Web App 에 표시하는 end-to-end 운영 흐름으로 설계했습니다.

```
[EDS Test raw log]
        ↓
[S3 적재 / 압축 해제]
        ↓
[fail-map 변환: Cython hex-to-grade + palette PNG + chip 좌표 JSON]
        ↓
[mapviewer: FastAPI 제공 / 조회 / 비교 / WebGL2 렌더링]
        ↓
[Known 2-stage 분류]
        ├─ Stage 1: ConvNeXtV2 wafer-level classification
        └─ Stage 2: ROI YOLO refinement
        ↓
[Unknown self-supervised 후보 grouping]
        ↓
[Web App 결과 표시 및 현업 검증]
```

Backbone 선정은 Transformer 와 CNN 계열을 비교해 판단했습니다. Transformer 계열은 wafer 전체 구조를 보는 데 강점이 있으나, 본 과제의 결함은 특정 zone 또는 국소 영역에 나타나는 경우가 많아 CNN 계열 ConvNeXtV2 의 지역 특징 추출이 더 적합하다고 판단했습니다. 같은 판단은 연세대 인공지능 컴퓨팅 학부 전해곤 교수 (이미지 분류 전공) 교수 자문으로도 확인했으며, label 이 부족한 본 도메인에서는 전역 attention 기반 ViT 계열보다 국소 결함을 잘 잡는 ConvNeXtV2-Base 같은 CNN 계열이 baseline 으로 적합하다는 의견을 받았습니다. 실제 비교에서도 ConvNeXtV2 는 MaxViT 와 동일한 weighted F1 0.87 을 보이면서 파라미터 약 26% 감소, FLOPs 약 39% 감소로 효율이 높았습니다.

```
[Input wafer image]
        ↓
[ConvNeXtV2 wafer classifier]
        ↓ confidence < gate
[ROI YOLO refinement]
        ↓
[Known class prediction]
```

2차 개발은 ROI YOLO 의 class 확장성과 throughput 한계를 보완하기 위한 구조입니다.

```
[Wafer image]
        ↓
[chip crop / chip-CNN defect classification]
        ↓
[chip별 defect id]
        ↓
[wafer 좌표계 object-id map 재구성]
        ↓
[최종 보정 classifier 입력]
```

**ㅁ 구현 성과**

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[실전 현업 데이터]** | Known 2-stage | weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split) |
| **[실전 현업 데이터]** | Known 단계별 개선 | 0.78 (baseline) → 0.87 (ConvNeXtV2 backbone) → 0.92 (+Optuna) → **0.95** (+ROI YOLO 2-stage) |
| **[실전 현업 데이터]** | Unknown 실전 운영 확인 | 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 7개 실제 불량 확인 |
| **[양산 운영]** | 운영 파이프라인 | 일 약 2만 장 wafer / 1시간 주기 적재 |
| **[양산 운영]** | 데이터 처리 | Cython hex-to-grade 약 **100배** 가속, 32-color palette PNG 약 **75%** 저장 절감 |
| **[양산 운영]** | Web App | 12일 누적 **2,317 요청**, peak 1,801 요청 (2026-03-07) |
| **[추가 생성 데이터, 개발 중]** | 후속 고도화 | Unknown metric 고도화 (ARI / capture rate 기반 cluster quality 정량화) 와 chip-CNN object-id map 보정 구조를 실전 성과와 분리해 개발 중 |

Unknown 검출은 실전 운영에서 13 후보 중 7개 실제 불량을 확인한 뒤, 추가 개선 및 정량 metric 측정을 위해 생성 데이터 기반 benchmark 를 별도로 구축해 개발 중입니다. 아래 표는 **[추가 생성 데이터, 개발 중]** 기반 보조 개발 metric 이며, 실전 Unknown 운영 성과를 대체하는 지표가 아닙니다.

| # | Recipe | P1 capture | P2 noise | P3 Comp | P4 Hom | ARI | AMI | Sil |
|---|--------|-----------:|---------:|--------:|-------:|----:|----:|----:|
| 1 | Global InfoNCE only | 1.000 | 6.20% | 0.960 | 0.929 | 0.823 | 0.929 | 0.582 |
| 2 | + Local DenseCL (LW=0.5) | 1.000 | 3.93% | 0.967 | 0.935 | 0.851 | 0.939 | 0.514 |
| 3 | + MoCo Queue 4096 | 1.000 | 1.31% | 0.983 | 0.937 | 0.846 | 0.950 | 0.573 |
| 4 | + NV-Retriever NEG 0.72 | 1.000 | 0.52% | 0.985 | 0.944 | 0.861 | 0.956 | 0.611 |
| 5 | + NeCo 0.2 | 1.000 | 0.96% | 0.980 | 0.940 | 0.856 | 0.950 | 0.610 |
| 6 | NEW (Local 제거, 4-tool) | 1.000 | 1.48% | 0.994 | 0.942 | 0.859 ± 0.018 | 0.960 | 0.781 |
| 7 | NEW + τ=0.5 post-reassign | 1.000 | 0.00% | 0.994 | 0.942 | 0.868 ± 0.013 | 0.960 | 0.781 |
| 8 | NEW cross-anchor 확인 | 38/38 | 4.73% | 0.936 | 0.786 | 0.444 | 0.851 | 0.521 |

**ㅁ P2. Chip Multi-label Classification**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Chip multi-label classification - CutMix → CutMix + Pair Mask → FCM-PM |
| 수행기간 | 2025년 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 본인 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | FCM-PM 합성 및 손실 마스킹 구조 신규 적용, val_margin 기준 도입, KD 운영 후보 검증, 학습·평가 운영 | 90% |
| 2 | 관리자 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | 방향성, 일정, 리뷰 매니징 | 10% |

**ㅁ 개인별 기여 서술**

P2 의 핵심 성과는 FCM-PM 을 본 과제 데이터 특성에 맞게 신규 적용한 점입니다. 본인은 chip 내부 defect 위치를 사전에 알 수 없는 조건에서 일반 CutMix 가 defect signal 을 잘라낼 수 있다는 한계를 인지하고, `CutMix 선정 → CutMix + Pair Mask 로 background loss 제외 → Full-Cover Mixup + Pair Mask 구성` 순서로 방법을 확장했습니다.

먼저 CutMix 계열로 Grade 값을 보존하는 합성을 구성했고, Pair Mask 를 결합해 합성 background 영역을 loss 에서 제외함으로써 background 를 defect 로 오학습하는 문제를 차단했습니다. 이어 Full-Cover Mixup 으로 chip 전체 grid 를 cover 하여 defect 위치 사전 미지 조건을 합성 단계에 반영했습니다. 합성 기법 선택은 연세대 인공지능 컴퓨팅 학부 박은병 교수 (이미지 생성 전공) 교수 자문으로 한 번 더 확인했으며, Grade 0-7 양자화 이미지에서 픽셀값이 중간 색으로 섞이는 Mixup / Diffusion 계열보다 양자화 의미를 보존하는 CutMix 계열이 적합하다는 의견을 받았습니다.

학습·평가 운영 측면에서는 val_margin 기준을 도입해 작은 validation set 에서 val_f1 plateau 로 checkpoint 선택이 흔들리는 문제를 줄였으며, KD single student 로 1× inference cost 운영 후보를 함께 확인했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | chip 내부 defect 위치를 사전에 알 수 없고, single defect chip 을 조합해 multi-label 평가로 확장해야 합니다. |
| 기존 방식의 한계 | 일반 CutMix 는 일부 영역만 잘라 붙이므로 defect signal 이 잘릴 수 있습니다. background 영역까지 defect 로 학습하면 Normal / Invalid / OOD negative 에서 false-positive 가 증가합니다. |
| 기술적 / 환경적 제약 | multi-label 조합 label 부족, 작은 validation set, OOD / negative false-positive 억제, 운영 후보의 inference cost 제약이 동시에 존재했습니다. |

**ㅁ 기술적 해결 방안**

```
[single 4 class chip]
        ↓
[CutMix 계열 선정: Grade 값 보존]
        ↓
[CutMix + Pair Mask: 합성 background loss 제외]
        ↓
[Full-Cover Mixup: chip 전체 grid cover]
        ↓
[FCM-PM 학습]
        ↓
[val_margin best checkpoint selection]
        ↓
[대표 모델 / KD single 비교]
```

val_margin 은 `positive bits 평균 score - negative bits 최대 score` 로 정의했습니다. 작은 validation set 에서 val_f1 이 plateau 로 포화되는 문제를 줄이고, false-positive 위험까지 반영해 best-model 선택 신호로 사용했습니다.

**ㅁ 구현 성과**

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[추가 생성 chip 데이터, PoC]** | 평가셋 | single 4 + 2-combo 6 + Normal + Invalid + OOD 4 = **16+ class × 약 3,850 chip** 추가 생성 chip 데이터 기반 controlled synthetic benchmark |
| **[추가 생성 chip 데이터, PoC]** | FCM-PM 대표 모델 | bit F1 **0.9943**, Normal / Invalid / OOD negative false-positive **0건** |
| **[추가 생성 chip 데이터, PoC]** | FCM-PM 내 Pair Mask 제거 비교 | FCM-PM 구조에서 Pair Mask 를 제거하면 FAR **100%** 로 전면 오판. 단순 CutMix + Pair Mask 가 아니라 Full-Cover Mixup 과 Pair Mask 를 함께 쓰는 조합이 핵심임을 확인 |
| **[추가 생성 chip 데이터, PoC]** | val_margin 기준 도입 | false-positive 위험까지 반영하는 best-model 선택 기준으로 적용 |
| **[추가 생성 chip 데이터, PoC]** | KD single student | bit F1 **0.9872** / FAR **0.5%** / 1× inference cost |

아래 표는 추가 생성 chip 데이터 기반 per-class 2,000 평가로 계속 갱신할 학습 metric 입니다. 학습이 계속 진행되면서 aggregate 가 완성되면 TBD 칸을 순차적으로 채워 넣습니다. row 1~5 의 bit_F1 / FAR / NI-FAR / OOD-FAR 는 FINAL bit/FAR matrix 기준이며, single / 2combo 는 기존 aggregate 값 또는 아직 집계 중인 TBD 입니다. 위 대표 성과의 bit F1 0.9943 은 기존 요약 평가 기준이며, 아래 0.9964 는 per-class 2,000 갱신 metric 으로 평가 단위가 다릅니다.

| # | Recipe | bit_F1 | single | 2combo | FAR | NI-FAR | OOD-FAR | Note |
|---|--------|-------:|-------:|-------:|----:|-------:|--------:|------|
| 1 | Baseline (BCE+LS=0.30, no CutMix) | 0.1093 | 0.1662 | 0.0652 | 99.47% | 99.65% | 98.91% | FINAL bit/FAR matrix 확인, baseline collapse |
| 2 | Focal Loss (sigmoid focal, no CutMix) | 0.7980 | 0.7981 | 0.3987 | 45.72% | 35.55% | 77.50% | FINAL bit/FAR matrix 확인 |
| 3 | ASL (Asymmetric Loss, no CutMix) | 0.6435 | 0.6000 | 0.4874 | 100.00% | 100.00% | 100.00% | FINAL bit/FAR matrix 확인, FAR collapse |
| 4 | CutMix only (random rect, no pair) | 0.9359 | 1.0000 | 0.4138 | 42.05% | 37.00% | 57.81% | FINAL bit/FAR matrix 확인, FAR high |
| 5 | CutMix + Pair (random rect + masked) | 0.9256 | TBD | TBD | 100.00% | 100.00% | 100.00% | FINAL bit/FAR matrix 확인, Pair Mask 단독이 아니라 FCM-PM 조합 필요성 확인 |
| 6 | FCM-PM best val_f1 | 0.9964 | 0.9961 | 0.9999 | 0.83% | 약 1.00% | 약 0.78% | val_f1 기준 선택 |
| 7 | FCM-PM best val_margin | 0.9964 | 0.9961 | 0.9999 | 0.83% | 약 1.00% | 약 0.78% | val_margin 최대도 동일 epoch 선택 |
| 8 | Ensemble 4-bag | 0.9909 | TBD | TBD | 0.00% | TBD | TBD | k=3 기준 Total FAR 0.00% |
| 9 | KD distill 4-bag → student | 0.9872 | TBD | TBD | 12.86% | 약 0.00% | TBD | OOD over-fire 확인, 운영 후보가 아닌 보조 검증 |

[추가 생성 chip 데이터, PoC] 2026-05-15 pair-sweep 보조 확인에서 추가 Pair Mask 변형 2종 (Complement + Pair Mask, grid 4x2, p=0.25 / Single Pair Mask, p=0.50) 은 stage1 report 기준 macro F1 0.8913 / micro F1 0.8840 / top1 11-class 0.7990 으로 확인됐고, 후속 자동 집계 기준 두 변형 모두 bit_F1 0.8743 / Total FAR 100.00% / NI-FAR 100.00% / OOD-FAR 100.00% 로 확인했습니다. 이는 Pair Mask 계열 단독 변형도 negative false-positive 를 억제하지 못한 보조 근거이며, single / 2combo breakdown 은 아직 산출되지 않아 위 표의 TBD 갱신 대상에서 제외합니다.

**ㅁ P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Trend episode 데이터 생성 기반 Anomaly-detection 검증 PoC |
| 수행기간 | 2025년 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 본인 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | trend episode 합성 generator 설계, Region / Noise / trend 불량 type 코드화, 생성 데이터 학습 가능성 검증 | 90% |
| 2 | 관리자 | 사내 양식 기입 대상 | 사내 양식 기입 대상 | 방향성, 일정, 리뷰 매니징 | 10% |

**ㅁ 개인별 기여 서술**

P3 의 핵심 성과는 **데이터 생성**입니다. 본인은 BBD/Overlay/CD 현업 경험에서 형성된 trend 도메인 지식을 synthetic trend episode generator 의 parameter 로 코드화했습니다. Binary gate + Type classifier 는 생성 데이터가 정상 / 이상 패턴을 학습 가능하게 담고 있는지 확인하기 위한 검증용 baseline 입니다.

먼저 Region 5종으로 계측 밀도 차이를 코드화하고, Noise 3종으로 설비 산포·hunting·drift 를 통계 분포로 매핑한 뒤, trend 불량 5종으로 mean shift / standard deviation change / spike / drift / context pattern 을 구성했습니다.

생성 데이터의 신뢰도 확보를 위해 fleet_std 기반 enforcement floor 로 이상 강도가 정상 산포에 묻히지 않도록 하한을 보장했고, target_std 를 fleet_within_std × 1.2 이내로 정렬해 합성 normal chart 의 통계 특성이 실전 정상 chart 와 가까워지도록 보정했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 함께 봐야 합니다. |
| 기존 방식의 한계 | 실전 trend abnormal data 는 충분한 양과 균형 label 을 확보하기 어렵고, 수작업 chart 판독은 초보자 누락과 시간 소모가 큽니다. |
| 기술적 / 환경적 제약 | 실전 label 부족을 전제로, 먼저 현업 trend domain knowledge 를 학습 가능한 synthetic data 로 만드는 것이 핵심 과제입니다. |

**ㅁ 기술적 해결 방안**

P3는 현업 trend 통계와 불량 발생 양상을 synthetic generator 로 코드화한 과제입니다.

```
[BBD / Overlay / CD 현업 trend 경험]
        ↓
[Region 5종: dense / sparse / very_sparse / thin / missing]
        ↓
[Noise 3종: Gaussian / Laplacian / correlated drift]
        ↓
[trend 불량 5종: mean_shift / std / spike / drift / context]
        ↓
[fleet_std 기반 enforcement floor]
        ↓
[224×224 trend chart PNG rendering]
        ↓
[검증용 baseline 학습: Binary gate + Type classifier]
        ↓
[생성 데이터 학습 가능성 확인]
```

생성 데이터 검증용 baseline 의 수렴 안정화를 위해, 일시적 spike 에 checkpoint 선택이 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 적용했습니다.

**ㅁ 구현 성과**

_데이터 생성 그룹 (주 성과)_

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[합성 trend chart, PoC]** | 생성 평가셋 | normal 750 + abnormal 5종 각 150 = 총 **1,500 sample** |
| **[합성 trend chart, PoC]** | Region 코드화 | `dense` 70-100%, `sparse` 40-70%, `very_sparse` 20-35%, `thin` 10-20%, `missing` 0% |
| **[합성 trend chart, PoC]** | Noise 코드화 | Gaussian 0.80, Laplacian 0.15, correlated drift 0.05 |
| **[합성 trend chart, PoC]** | trend 불량 코드화 | mean_shift / std / spike / drift / context |
| **[합성 trend chart, PoC]** | chart rendering | 224×224 chart PNG, 12-25 episode mix |

_검증용 baseline 학습 그룹 (생성 데이터 학습 가능성 확인)_

아래 baseline 수치는 위 데이터 생성 그룹이 학습 가능한 자산인지 확인한 부속 검증입니다.

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[합성 trend chart, PoC]** | 1차 Binary gate | Binary F1 **0.9967**, Abnormal Recall **0.9987**. 생성 데이터 학습 가능성 확인용 참고 수치입니다. |
| **[합성 trend chart, PoC, 개발 중]** | 2차 Type classifier | mean_shift ↔ drift 혼동 등으로 type-level accuracy 는 추가 개발 중 (1차 binary 안정성과 분리하여 보고합니다) |

BBD/Overlay/CD trend 판단 기준을 synthetic data generator 로 코드화해, 실전 label 부족 상황에서도 AI 검증을 시작할 수 있는 데이터 기반을 마련했습니다.
