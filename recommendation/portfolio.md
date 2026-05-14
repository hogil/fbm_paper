## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2022년 ~ 현재 | P1. Failbit Map AI 분류 시스템 | 3인 협업 / 본인 70% 리딩 / DRAM 전제품 라인 양산 운영 / 일 약 2만 장 wafer 처리 | S3 수집, Cython/Python 파싱, palette PNG / chip 좌표 JSON 생성, Web App 운영, Known / Unknown AI 모델 설계·개발·검증 | 10% | 40% | 50% |
| 2025년 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC / 본인 90% 리딩 / 16+ class × 약 3,850 chip controlled synthetic benchmark | FCM-PM 합성 및 손실 마스킹 구조 구성, 학습·평가 체계 구축, best-model 선택 기준 및 운영 후보 검증 | 20% | 40% | 40% |
| 2025년 ~ 현재 | P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC | 2인 PoC / 본인 90% 리딩 / 1,500 sample 합성 trend chart 데이터 생성 | 합성 generator 설계, 도메인 자산 코드화, 생성 데이터 학습 가능성 검증 | 5% | 55% | 40% |

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
| 1 | 본인 | 개인정보 입력란 | 개인정보 입력란 | Frontend, Backend, AI 모델 개발, 데이터 처리, 생성 파이프라인 전 영역 직접 수행 | 70% |
| 2 | 현업 엔지니어 | 개인정보 입력란 | 개인정보 입력란 | 아이디어 발의 및 불량 분석 교육, Unknown 후보 13개 중 실제 불량 7개 확인 | 20% |
| 3 | 관리자 | 개인정보 입력란 | 개인정보 입력란 | 방향성, 일정, 리뷰 매니징 | 10% |

**ㅁ 개인별 기여 서술**

본인은 Failbit Map 의 의미와 현업 사용자 분석 방식을 먼저 학습한 뒤, 대량 변환·저장·조회 파이프라인, Web App, Known 2-stage 분류, Unknown self-supervised 검출을 하나의 운영 흐름으로 연결했습니다. 반도체 분석 현장에서 쌓은 이해를 AI 모델 구조와 데이터 처리 설계에 직접 반영하고, 그 결과를 현업 분석 부담을 줄이는 운영 시스템으로 끌고 간 점이 본인의 핵심 기여입니다.

데이터 처리 단에서는 Cython 기반 hex-to-grade 변환으로 wafer 당 약 1,000만 cell 변환 병목을 약 100배 가속했고, 32-color palette-indexed PNG 저장으로 Failbit Map 저장 용량을 약 75% 절감해 양산 운영의 처리량과 저장 비용을 동시에 확보했습니다.

AI 모델 단에서는 ConvNeXtV2 + ROI YOLO 2-stage 로 16 class / 1,500 sample **[실전 현업 데이터]** 에서 weighted F1 0.95 를 달성했으며, Unknown 검출은 **[실전 현업 데이터]** 5일 운영 데이터 10,000장 학습 + 별도 1일 2,000장 적용 결과 13 후보 중 7개가 실제 불량으로 현업 확인되었습니다. ROI YOLO 의 한계를 보완하기 위해 chip-CNN 결과를 wafer 좌표계 object-id map 으로 재구성하는 2차 보정 구조를 **[추가 생성 chip 데이터, 개발 중]** 기반으로 개발 중에 있습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | Failbit Map 은 EDS Test 에서 wafer 당 약 1,000만 cell 의 Grade 로 표현되는 초고해상도 데이터이며, 분석 엔지니어 수작업 판독만으로는 전수 분석이 어렵습니다. |
| 기존 방식의 한계 | 기존 조회는 1회 48매 수준에 머물렀고, 제품 / 시간 / lot 단위 누적 대량 분석이 어려웠습니다. 등록 외 신규 결함 패턴은 known classifier 만으로 검출하기 어렵습니다. |
| 기술적 / 환경적 제약 | label 데이터 부족 (16 class / 1,500 sample), 일 약 2만 장 wafer 처리, 1시간 주기 적재, 대량 이미지 저장 용량, Web App 응답성, 신규 unknown pattern 검출이 동시에 요구되었습니다. |

**ㅁ 기술적 해결 방안**

데이터 파이프라인은 설비 raw log 를 Failbit Map 이미지로 변환하고, 이미지 분석 AI 결과를 Web App 에 표시하는 end-to-end 구조로 설계했습니다.

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

Backbone 선정은 Transformer 와 CNN 계열을 비교해 판단했습니다. Transformer 계열은 wafer 전체 구조를 보는 데 강점이 있으나, 본 과제의 결함은 특정 zone 또는 국소 영역에 나타나는 경우가 많아 CNN 계열 ConvNeXtV2 의 지역 특징 추출이 더 적합하다고 판단했습니다. 실제 비교에서도 ConvNeXtV2 는 MaxViT 와 동일한 weighted F1 0.87 을 보이면서 파라미터 약 26% 감소, FLOPs 약 39% 감소로 효율이 높았습니다.

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

| 구분 | 성과 |
|------|------|
| Known 2-stage **[실전 현업 데이터]** | weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split) |
| Known 단계별 개선 **[실전 현업 데이터]** | 0.78 → 0.87 → 0.92 → **0.95** |
| Unknown 실전 운영 확인 **[실전 현업 데이터]** | 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 7개 실제 불량 확인 |
| Unknown 보조 개발 지표 **[추가 생성 데이터, 개발 중]** | same-anchor ARI **0.8588±0.018** / class capture **1.000 (43/43)**, cross-anchor ARI **0.4437**. 실전 운영 성과가 아니라 합성 wafer 데이터 기반 표현학습 품질 점검 지표입니다. |
| 운영 파이프라인 **[양산 운영]** | 일 약 2만 장 wafer / 1시간 주기 적재 |
| 데이터 처리 **[양산 운영]** | Cython hex-to-grade 약 **100배** 가속, 32-color palette PNG 약 **75%** 저장 절감 |
| Web App **[양산 운영]** | 12일 누적 **2,317 요청**, peak 1,801 요청 (2026-03-07) |
| chip-CNN 보조 개발 **[추가 생성 데이터, 개발 중]** | 생성 chip 데이터 **1.16M** 기준 val_f1 **0.9946** / test_f1 **0.9872** / 5-seed **0.9838±0.0092**. 2-stage 통합 성과가 아니라 chip 분류기 단독 지표입니다. |

**Unknown contrastive 구성요소 성능표 [추가 생성 데이터, 개발 중 - 학습 후 정량 채움]**

| # | Recipe | P1 | P2 | P3 | P4 | ARI | AMI | Sil |
|---|--------|----|----|----|----|-----|-----|-----|
| 1 | B0 Global InfoNCE only | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 | 학습 후 채워짐 |
| 2 | + Local DenseCL (LW=0.5) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 3 | + MoCo Queue 4096 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 4 | + NV-Retriever NEG 0.72 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 5 | + NeCo 0.2 (B5 5-tool full) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 6 | NEW (B5 - Local, 4-tool) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 7 | NEW + tau=0.5 post-reassign | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

위 표는 실전 운영 성과가 아니라, Unknown contrastive 추가 생성 데이터에서 baseline B0 부터 NEW recipe 까지 구성요소 단위 성능을 단계적으로 채우는 관리 표입니다. P1-P4 / ARI / AMI / Sil 은 학습 후 정량 측정으로 갱신합니다. Known / Unknown 실전 현업 데이터 성능은 현재 프로젝트 폴더의 실전 데이터 근거를 기준으로 관리합니다.

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
| 1 | 본인 | 개인정보 입력란 | 개인정보 입력란 | FCM-PM 합성 및 손실 마스킹 구조 신규 적용, val_margin 기준 도입, ensemble / KD 검증, 학습·평가 운영 | 90% |
| 2 | 관리자 | 개인정보 입력란 | 개인정보 입력란 | 방향성, 일정, 리뷰 매니징 | 10% |

**ㅁ 개인별 기여 서술**

P2의 main 성과는 FCM-PM 을 본 과제 데이터 특성에 맞게 신규 적용한 점입니다. 본인은 chip 내부 defect 위치를 사전에 알 수 없는 조건에서 일반 CutMix 가 defect signal 을 잘라낼 수 있다는 한계를 인지하고, `CutMix 선정 → CutMix + Pair Mask 로 background loss 제외 → Full-Cover Mixup + Pair Mask 구성` 순서로 방법을 확장했습니다.

먼저 CutMix 계열로 Grade 값을 보존하는 합성을 구성했고, Pair Mask 를 결합해 합성 background 영역을 loss 에서 제외함으로써 background 를 defect 로 오학습하는 문제를 차단했습니다. 이어 Full-Cover Mixup 으로 chip 전체 grid 를 cover 하여 defect 위치 사전 미지 조건을 합성 단계에 반영했습니다.

학습·평가 운영 측면에서는 val_margin 기준을 도입해 작은 validation set 에서 val_f1 plateau 로 checkpoint 선택이 흔들리는 문제를 줄였으며, 4-bag ensemble 과 KD single student 를 함께 돌려 성능 상한과 1× inference cost 운영 후보를 동시에 확인했습니다.

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
[대표 모델 / 4-bag ensemble / KD single 비교]
```

val_margin 은 `positive bits 평균 score - negative bits 최대 score` 로 정의했습니다. 작은 validation set 에서 val_f1 이 plateau 로 포화되는 문제를 줄이고, false-positive 위험까지 반영해 best-model 선택 신호로 사용했습니다.

**ㅁ 구현 성과**

| 구분 | 성과 |
|------|------|
| 평가셋 **[추가 생성 chip 데이터, PoC]** | single 4 + 2-combo 6 + Normal + Invalid + OOD 4 = **16+ class × 약 3,850 chip**. 실전 양산 데이터 검증이 아니라 controlled synthetic benchmark 입니다. |
| FCM-PM 대표 모델 **[추가 생성 chip 데이터, PoC]** | bit F1 **0.9943**, Normal / Invalid / OOD negative false-positive **0건** |
| Pair Mask 제거 비교 **[추가 생성 chip 데이터, PoC]** | FAR **100%** 로 전면 오판. Pair Mask background loss masking 의 결정성 확인 |
| val_margin 효과 **[추가 생성 chip 데이터, PoC]** | Spearman ρ **+0.56**, val_f1 ρ **-0.10** 대비 best-model 선택 신호 개선 |
| 4-bag ensemble **[추가 생성 chip 데이터, PoC]** | bit F1 **0.9953** / FAR **0.00%** / 약 4× inference cost |
| KD single student **[추가 생성 chip 데이터, PoC]** | bit F1 **0.9872** / FAR **0.5%** / 1× inference cost |

**Multi-label 합성 학습 recipe 성능표 [추가 생성 chip 데이터, PoC - per class 2000 학습 / 16+ class 평가셋]**

| # | Recipe | bit_F1 | single | 2combo | FAR | NI-FAR | OOD-FAR | Note |
|---|--------|--------|--------|--------|------|--------|---------|------|
| 1 | Baseline (BCE+LS=0.30, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 2 | Focal loss (T9 sigmoid_focal, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 3 | ASL (T4 asymmetric, no cutmix) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 4 | CutMix only (random rect, no pair) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 5 | CutMix + Pair (random rect + masked) | TBD | TBD | TBD | TBD | TBD | TBD | ladder BG |
| 6 | FCM-PM best val_f1 (run112 ep=20) | 0.9652 | 1.0000 | 0.9517 | 0.15 | 0.00 | 0.62 | val_f1 best |
| 7 | **FCM-PM best val_margin (run116J)** | **0.9918** | 0.9996 | 0.9892 | 0.00 | 0.00 | 0.00 | best single 후보 |
| 8 | Ensemble 4-bag g=2/2/3/4 (A+C+J+F) thr=0.3 | 0.9615 | 1.0000 | 0.9475 | 0.00 | 0.00 | 0.00 | g-diverse FCM-PM |
| 9 | KD distill 4-bag → student | TBD | TBD | TBD | TBD | TBD | TBD | 4-bag 후 dispatch |

위 표는 Baseline / Focal / ASL / CutMix / CutMix+Pair / FCM-PM (val_f1) / **FCM-PM (val_margin, best single 후보)** / 4-bag Ensemble / KD distill 9 단계의 recipe 성능 관리 표입니다. 빈 셀은 추가 학습 후 정량 채움 예정입니다.

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
| 1 | 본인 | 개인정보 입력란 | 개인정보 입력란 | trend episode 합성 generator 설계, Region / Noise / trend 불량 type 코드화, 생성 데이터 학습 가능성 검증 | 90% |
| 2 | 관리자 | 개인정보 입력란 | 개인정보 입력란 | 방향성, 일정, 리뷰 매니징 | 10% |

**ㅁ 개인별 기여 서술**

P3의 main 성과는 anomaly detection model 이 아니라 **데이터 생성**입니다. 본인은 BBD/Overlay/CD 현업 경험에서 형성된 trend 도메인 지식을 synthetic trend episode generator 의 parameter 로 코드화했습니다. Binary gate + Type classifier 는 생성 데이터가 정상 / 이상 패턴을 학습 가능하게 담고 있는지 확인하기 위한 검증용 baseline 입니다.

먼저 Region 5종으로 계측 밀도 차이를 코드화하고, Noise 3종으로 설비 산포·hunting·drift 를 통계 분포로 매핑한 뒤, trend 불량 5종으로 mean shift / standard deviation change / spike / drift / context pattern 을 구성했습니다.

생성 데이터의 신뢰도 확보를 위해 fleet_std 기반 enforcement floor 로 이상 강도가 정상 산포에 묻히지 않도록 하한을 보장했고, target_std 를 fleet_within_std × 1.2 이내로 정렬해 합성 normal chart 의 통계 특성이 실전 정상 chart 와 가까워지도록 보정했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 함께 봐야 합니다. |
| 기존 방식의 한계 | 실전 trend abnormal data 는 충분한 양과 균형 label 을 확보하기 어렵고, 수작업 chart 판독은 초보자 누락과 시간 소모가 큽니다. |
| 기술적 / 환경적 제약 | 실전 양산 데이터 검증은 아직 미실시이며, 먼저 현업 trend domain knowledge 를 학습 가능한 synthetic data 로 만드는 것이 핵심 과제입니다. |

**ㅁ 기술적 해결 방안**

P3는 실전 trend data 를 그대로 수집해 학습한 과제가 아니라, 현업 trend 통계와 불량 발생 양상을 synthetic generator 로 코드화한 과제입니다.

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

학습 안정화는 model 차별성 주장이 아니라 생성 데이터 검증용 baseline 의 수렴 안정화입니다. 일시적 spike 에 checkpoint 선택이 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 적용했습니다.

**ㅁ 구현 성과**

| 구분 | 성과 |
|------|------|
| 생성 평가셋 **[합성 trend chart, PoC]** | normal 750 + abnormal 5종 각 150 = 총 **1,500 sample** |
| Region 코드화 | `dense` 70-100%, `sparse` 40-70%, `very_sparse` 20-35%, `thin` 10-20%, `missing` 0% |
| Noise 코드화 | Gaussian 0.80, Laplacian 0.15, correlated drift 0.05 |
| trend 불량 코드화 | mean_shift / std / spike / drift / context |
| chart rendering | 224×224 chart PNG, 12-25 episode mix |
| 1차 Binary gate 검증 참고 수치 **[합성 trend chart, PoC]** | Binary F1 **0.9967**, Abnormal Recall **0.9987**, 5-seed sweep **0.9944~0.9988** (TN 746 / FN 1 / FP 4 / TP 749) |
| 2차 Type classifier 검증 단계 **[합성 trend chart, PoC, 개발 중]** | mean_shift ↔ drift 혼동 등으로 type-level accuracy 는 추가 개발 중 (1차 binary 안정성과 분리하여 보고합니다) |

위 성능 수치는 모델 차별성 주장이 아니라, 생성 데이터가 정상 / 이상 pattern 을 학습 가능하게 담고 있는지 확인한 참고 수치입니다. P3는 특별한 anomaly detection model 과제가 아니라, 현업 trend 이상 양상을 AI 학습 데이터로 만들 수 있게 한 domain-knowledge-driven synthetic data generation 과제입니다.
