## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2024년 ~ 현재 | P1. Failbit Map Known & Unknown 불량 분석 아키텍처 | 3인 협업, 본인 60% 리딩<br>DRAM 전제품 라인 양산 운영<br>일 약 2만 장 wafer 처리 | S3 수집, Cython/Python 파싱, palette PNG / chip 좌표 JSON 생성, Web App 운영, Known / Unknown AI 모델 설계, 개발 및 검증 | 10% | 40% | 50% |
| 2025년 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC, 본인 80% 리딩<br>16+ class × 약 3,850 chip<br>controlled synthetic benchmark | FCM-PM 합성 및 손실 마스킹 구조 구성, 학습 및 평가 체계 구축, best-model 선택 기준과 KD 압축 가능성 검토 | 20% | 40% | 40% |
| 2025년 ~ 현재 | P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 검증 PoC | 2인 PoC, 본인 80% 리딩<br>1,500 sample 합성 trend chart 데이터 생성 | 합성 generator 설계, 도메인 자산 코드화, 생성 데이터의 정상/이상 구분 신호 확인 | 5% | 55% | 40% |

## 2. 대표 과제 상세 기술서

**ㅁ P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Failbit Map Known & Unknown 불량 분석 아키텍처 |
| 수행기간 | 2024년 ~ 현재 |
| 참여인원 | 본인 / 현업 엔지니어 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 구분 | 역할 | 기여도 |
|----|------|------|--------|
| 1 | 본인 | 데이터 변환/저장/조회 파이프라인, Web App, Known/Unknown 모델 기술 구현 | 60% |
| 2 | 현업 엔지니어 | 현업 문제정의 및 불량 분석 교육 | 20% |
| 3 | 관리자 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

본인은 Failbit Map 의 의미와 현업 사용자의 분석 방식을 먼저 익힌 뒤, 대량 변환, 저장 및 조회 파이프라인, Web App, Known 2-stage 분류, Unknown self-supervised 검출을 하나의 운영 흐름으로 연결했습니다. Unknown 쪽은 같은 모양의 패턴도 wafer 내 발생 영역에 따라 다른 불량으로 볼 수 있다는 현업 특성을 반영해, global embedding 과 local loss 를 함께 쓰는 구조로 설계했습니다. 모델만 따로 만든 것이 아니라, 현업 엔지니어가 대량 Failbit Map 을 빠르게 보고 비교할 수 있는 화면과 처리 흐름까지 같이 만든 점이 본인의 주요 기여입니다.

P1 기여도 60%는 본인이 데이터 변환 및 저장 파이프라인, Web App, Known 2-stage 모델, Unknown 후보 검출 구조를 직접 설계, 개발 및 검증한 기준입니다. 현업 엔지니어는 현업 문제정의와 불량 분석 교육을 맡았고, 관리자는 일정, 방향성 및 리뷰 매니징을 담당했습니다. Unknown 후보 13건 중 현업이 실제 불량으로 확인한 7건은 별도 검증 근거로 반영했습니다.

데이터 처리 단에서는 Cython 기반 hex-to-grade 변환으로 wafer 당 약 1,000만 cell 변환 병목을 약 100배 가속했고, 32-color palette-indexed PNG 저장으로 Failbit Map 저장 용량을 약 75% 절감해 양산 운영의 처리량과 저장 비용을 동시에 확보했습니다.

AI 모델 단에서는 fine-tuned ConvNeXtV2 checkpoint 를 Failbit Map task-specific fine-tuning 으로 보정하고 ROI YOLO 2-stage 를 결합해, 16 class / 1,500 labeled samples / 4:1 stratified split 의 평가용 hold-out set 기준 **[실전 현업 데이터]** weighted F1 0.95 를 확인했습니다. 이 수치는 운영 적용 결과와 분리한 분류 성능 지표입니다. Unknown 검출은 **[실전 현업 데이터]** 5일 운영 데이터 10,000장으로 SimCLR 계열 contrastive embedding 을 학습하고, 별도 1일 2,000장에 HDBSCAN grouping 을 적용했습니다. 이때 같은 외형이라도 center, edge, top, bottom 등 발생 영역이 다르면 다른 불량으로 볼 수 있어, 6×6 grid structured local sampling 과 Local InfoNCE loss 를 함께 넣었습니다. 적용 결과 13 후보 중 현업이 실제 불량으로 확인한 건은 7건입니다. ROI YOLO 의 한계를 보완하기 위한 2차 구조는 chip-CNN 결과를 object-id map(chip 위치별 불량 chip id로 제작한 map)으로 재구성하는 방식이며, 현재 **[추가 생성 chip 데이터, 개발 중]** 기준으로 검증하고 있습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | Failbit Map 은 EDS Test 에서 wafer 당 약 1,000만 cell 의 Grade 로 표현되는 초고해상도 데이터이며, 분석 엔지니어 수작업 판독만으로는 전수 분석이 어렵습니다. |
| 기존 방식의 한계 | 기존 조회는 1회 48매 수준에 머물렀고, 제품 / 시간 / lot 단위 누적 대량 분석이 어려웠습니다. 등록 외 신규 결함 패턴은 known classifier 만으로 검출하기 어렵습니다. |
| 기술적 / 환경적 제약 | label 데이터 부족 (16 class / 1,500 sample), 일 약 2만 장 wafer 처리, 1시간 주기 적재, 대량 이미지 저장 용량, Web App 응답성, 신규 unknown pattern 검출, 같은 모양이라도 발생 영역에 따라 다른 불량으로 구분해야 하는 제약이 동시에 요구되었습니다. |

**ㅁ 기술적 해결 방안**

데이터 파이프라인은 설비 raw log 를 Failbit Map 이미지로 바꾸고, AI 모델이 신규 불량 후보를 현업 검토 대상으로 올리는 흐름으로 설계했습니다. 엔지니어는 Web App 에서 대량 Failbit Map 을 조회, 비교 및 확인할 수 있도록 했습니다.

```
[EDS Test raw log]
        ↓
[S3 적재 / 압축 해제]
        ↓
[fail-map 변환: Cython hex-to-grade + palette PNG + chip 좌표 JSON]
        ↓
[Web App: FastAPI 제공 / 조회 / 비교 / WebGL2 렌더링]
        ↓
[Known 2-stage 분류]
        ├─ Stage 1: ConvNeXtV2 task-specific fine-tuned wafer classifier
        └─ Stage 2: ROI YOLO refinement
        ↓
[Unknown self-supervised embedding]
        ├─ Global InfoNCE
        └─ 6×6 grid local sampling + Local InfoNCE loss
        ↓
[HDBSCAN 후보 grouping]
        ↓
[Web App 결과 표시 및 현업 검증]
```

**알고리즘 / 모델 아키텍처 선택 흐름**

P1의 모델 선택 기준은 `wafer 전체 분포를 볼 것인가`, `chip 내부 defect evidence 를 볼 것인가`, `등록 class 밖의 신규 패턴을 찾을 것인가`로 나눴습니다. 처음부터 하나의 모델에 모든 역할을 넣기보다, 각 단계가 잘하는 일을 분리했습니다.

```
[문제 조건]
    - 16 class / 1,500 labeled sample
    - wafer 전체 위치 정보와 chip 내부 defect 모양이 모두 중요
    - center / edge / top / bottom 에 따라 같은 모양도 다른 불량이 될 수 있음
    - 일 약 2만 장 운영 처리량 필요
        ↓
[Stage 1: ConvNeXtV2 wafer classifier]
    - 전체 wafer map 을 빠르게 1차 분류
    - CNN 계열이라 국소 defect texture 와 zone pattern 을 안정적으로 반영
    - MaxViT 대비 동일 F1 구간에서 파라미터와 FLOPs 가 낮아 운영 부담이 작음
        ↓
if confidence 충분:
    [Known class 바로 출력]
else:
    [Stage 2: ROI YOLO]
    - center scratch / center scratch_rot 처럼 map-level 에서 헷갈리는 class 를 ROI chip evidence 로 재확인
    - chip마다 box 와 defect class 를 확인해 wafer-level 예측을 보정
        ↓
if 등록 class 로 설명되지 않음:
    [Unknown self-supervised embedding]
    - Global InfoNCE 로 전체 패턴을 보고,
    - 6×6 local sampling + Local InfoNCE 로 발생 위치 정보를 보존
    - HDBSCAN 으로 현업 확인 후보를 grouping
        ↓
if class 수 증가 / ROI YOLO 확장 한계:
    [chip-CNN → object-id map]
    - chip별 defect id 를 32×32 wafer 좌표계로 재구성
    - raw map 에서 비슷해 보이는 wafer 를 defect object 분포로 다시 구분
```

Backbone 은 Transformer 계열과 CNN 계열을 함께 비교했습니다. Transformer 계열은 wafer 전체 구조를 보는 데 강점이 있지만, 본 과제의 결함은 특정 zone 또는 국소 영역에 나타나는 경우가 많았습니다. 그래서 지역 특징 추출에 강한 ConvNeXtV2 를 우선 후보로 잡았습니다. 선정한 fine-tuned ConvNeXtV2 checkpoint 는 Failbit Map task-specific fine-tuning 과 HPO 로 보정했습니다. 이미지 분류 전문가 검토 의견도 참고했으며, label 이 부족하고 국소 결함이 중요한 도메인에서는 ConvNeXtV2-Base 같은 CNN 계열을 baseline 으로 두는 판단이 무리가 없다고 봤습니다. 실제 비교에서도 ConvNeXtV2 는 MaxViT 와 동일한 weighted F1 0.87 을 보이면서 파라미터 약 26% 감소, FLOPs 약 39% 감소로 운영 부담이 낮았습니다.

```
[Input wafer image]
        ↓
[ConvNeXtV2 task-specific fine-tuned wafer classifier]
        ↓ confidence < gate
[ROI YOLO refinement]
        ↓
[Known class prediction]
```

Unknown 검출은 정답 class 를 미리 정의하기 어려운 운영 이미지를 후보 grouping 문제로 봤습니다. 단순히 wafer 전체 모양만 임베딩하면 center, edge, top, bottom 처럼 위치가 다른 불량을 같은 그룹으로 묶을 수 있습니다. 그래서 6×6 grid structured local sampling 으로 위치별 feature 를 뽑고, Local InfoNCE loss 를 함께 적용해 발생 영역 정보가 embedding 에 남도록 했습니다. 이후 HDBSCAN 으로 유사 패턴을 묶어 현업 검토 대상을 줄였습니다.

2차 개발은 ROI YOLO 의 class 확장성과 throughput 한계를 보완하기 위한 구조입니다. 아래 예시는 실제 wafer map 에서 1차 CNN 이 낮은 확신도를 보이는 경우, ROI 영역을 다시 확인해 chip 단위 defect evidence 로 보정하는 흐름입니다.

_Known 2-stage ROI YOLO 보정 흐름_

<img src="./figures/p1_known_roi_yolo_real.png" width="620" alt="Known 2-stage ROI YOLO 보정 흐름">

_wafer map + object-id map 결합 예시_

<img src="./figures/p1_object_id_map_real_pair.png" width="620" alt="실제 wafer map과 object-id map 결합 예시">

```
[Wafer image]
        ↓
[chip crop / chip-CNN defect classification]
        ↓
[chip별 defect id]
        ↓
[object-id map 재구성]
        ↓
[최종 보정 classifier 입력]
```

**ㅁ 구현 성과**

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[실전 현업 데이터]** | Known 2-stage | weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split 의 평가용 hold-out set 기준, 운영 적용 결과와 별도) |
| **[실전 현업 데이터]** | Known 단계별 개선 | 0.78 (baseline) → 0.87 (ConvNeXtV2 task-specific fine-tuning) → 0.92 (+Optuna HPO) → **0.95** (+ROI YOLO 2-stage) |
| **[실전 현업 데이터]** | Unknown 실전 운영 확인 | SimCLR 계열 contrastive embedding + 6×6 grid local sampling + Local InfoNCE loss + HDBSCAN. 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 현업 확인 실제 불량 7건 |
| **[양산 운영]** | 운영 파이프라인 | 일 약 2만 장 wafer / 1시간 주기 적재 |
| **[양산 운영]** | 데이터 처리 | Cython hex-to-grade 약 **100배** 가속, 32-color palette PNG 약 **75%** 저장 절감 |
| **[양산 운영]** | Web App | 12일 누적 **2,317 요청**, peak 1,801 요청 (2026-03-07) |
| **[추가 생성 데이터, 개발 중]** | Unknown 부록성 개발 지표 | 실전 운영 성과와 분리한 후속 benchmark 입니다. same-anchor defect-class capture 43/43 (capture ratio 1.000), ARI **0.859 ± 0.018**, Completeness **0.994**, Homogeneity **0.942**. 후처리 기준 ARI **0.868 ± 0.013** |
| **[추가 생성 chip 데이터, 개발 중]** | Stage 2 보정 구조 | chip-CNN 기반 object-id map 구조를 실전 성과와 분리해 개발 중 |

Unknown 검출의 실전 운영값은 13 후보 중 7개 실제 불량을 현업 확인한 후보 발굴 결과입니다. 실전 운영 모델의 핵심은 Global InfoNCE 만이 아니라, wafer 영역별 불량 의미를 반영하기 위한 Local InfoNCE loss 와 6×6 grid structured local sampling 을 함께 둔 점입니다. 아래 수치는 **[추가 생성 데이터, 개발 중]** 기반 부록성 개발 metric 이며, 실전 Unknown 운영 성과를 대체하는 지표가 아닙니다.

아래는 후속 benchmark 에서 비교한 contrastive recipe 입니다. 실전 운영 성과와 별도로, 어떤 구성에서 embedding 품질이 안정되는지 보기 위한 보조 실험입니다.

| # | Recipe | P1 capture rate | P2 noise | P3 Comp | P4 Hom | ARI | AMI | Sil |
|---|--------|-----------:|---------:|--------:|-------:|----:|----:|----:|
| 1 | Global InfoNCE only | 1.000 | 6.20% | 0.960 | 0.929 | 0.823 | 0.929 | 0.582 |
| 2 | + Local DenseCL (LW=0.5) | 1.000 | 3.93% | 0.967 | 0.935 | 0.851 | 0.939 | 0.514 |
| 3 | + MoCo Queue 4096 | 1.000 | 1.31% | 0.983 | 0.937 | 0.846 | 0.950 | 0.573 |
| 4 | + NV-Retriever NEG 0.72 | 1.000 | 0.52% | 0.985 | 0.944 | 0.861 | 0.956 | 0.611 |
| 5 | + NeCo 0.2 | 1.000 | 0.96% | 0.980 | 0.940 | 0.856 | 0.950 | 0.610 |
| 6 | 최종 선택 recipe | 1.000 | 1.48% | 0.994 | 0.942 | 0.859 ± 0.018 | 0.960 | 0.781 |
| 7 | 최종 선택 recipe + τ=0.5 reassignment | 1.000 | 0.00% | 0.994 | 0.942 | 0.868 ± 0.013 | 0.960 | 0.781 |

**ㅁ P2. Chip Multi-label Classification**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Chip multi-label classification - CutMix → CutMix + Pair Mask → FCM-PM |
| 수행기간 | 2025년 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 구분 | 역할 | 기여도 |
|----|------|------|--------|
| 1 | 본인 | FCM-PM 합성 및 손실 마스킹 구조 신규 적용, val_margin 기준 도입, KD 압축 가능성 검토, 학습 및 평가 운영 | 80% |
| 2 | 관리자 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

P2 에서는 multi-label 불량 조합 label 을 실제 환경에서 충분히 확보하기 어렵고, 대부분 single-label defect chip 만 먼저 확보된다는 점이 가장 큰 제약이었습니다. 본인은 single-label defect chip 을 조합해 multi-label 학습 데이터를 만들고, 조합 안에 들어간 각 single class 를 빠짐없이 맞히는지 평가하는 구조를 설계했습니다. 일반 CutMix 는 defect signal 을 일부 잘라낼 수 있었고, CutMix + Pair Mask 만으로도 negative false-positive 가 충분히 줄지 않았습니다. 그래서 chip 전체 grid 를 cover 하는 Full-Cover Mixup 과 Pair Mask 를 함께 쓰는 FCM-PM 구조로 정리했습니다.

먼저 CutMix 계열로 Grade 값을 보존하는 합성을 만들었습니다. 이후 Pair Mask 로 합성 background 영역을 loss 에서 제외했고, Full-Cover Mixup 으로 chip 전체 grid 를 cover 하도록 바꿨습니다. defect 위치를 미리 알 수 없는 실제 조건을 합성 단계에 넣기 위한 조치였습니다. 이미지 생성 전문가 검토 의견도 참고했으며, Grade 0-7 양자화 이미지에서는 픽셀값이 중간 색으로 섞이는 Mixup / Diffusion 계열보다 양자화 의미를 보존하는 CutMix 계열이 더 맞다고 봤습니다.

학습 및 평가 운영 측면에서는 val_margin 기준을 도입해 작은 validation set 에서 val_f1 plateau 로 checkpoint 선택이 흔들리는 문제를 줄였습니다. KD single student 는 1× inference cost 로 줄일 수 있는지 확인한 압축 실험이며, stress 평가에서 FAR 이 높게 나와 바로 운영 대상으로 보지는 않았습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | multi-label 불량 조합 label 을 충분히 확보하기 어렵고, 실제로는 single-label defect chip 중심으로 데이터가 쌓입니다. |
| 기존 방식의 한계 | single-label defect 를 단순 조합하면 multi-label chip 안의 각 single class 를 안정적으로 맞춰야 하는데, 일반 CutMix 는 일부 영역만 잘라 붙이므로 defect signal 이 잘릴 수 있습니다. background 영역까지 defect 로 학습하면 Normal / Invalid / OOD negative 에서 false-positive 가 증가합니다. |
| 기술적 / 환경적 제약 | single-label 기반 multi-label 조합 생성, chip 내부 defect 위치 사전 미지, 작은 validation set, OOD / negative false-positive 억제, inference cost 제약이 동시에 존재했습니다. |

**ㅁ 기술적 해결 방안**

```
[single 4 class chip]
        ↓
[CutMix 계열 선정: Grade 값 보존]
        ↓
[CutMix + Pair Mask 중간 검증: background loss 제외만으로는 부족]
        ↓
[FCM-PM: Full-Cover Mixup + Pair Mask]
        ↓
[FCM-PM 학습]
        ↓
[val_margin best checkpoint selection]
        ↓
[대표 모델 / KD single 비교]
```

P2의 아키텍처 선택은 “없는 multi-label label 을 어떻게 만들고, 그 조합을 어떻게 오학습 없이 학습시킬 것인가”에서 출발했습니다.

```
[실제 조건]
    - 확보 가능한 데이터는 대부분 single-label defect chip
    - multi-label defect 조합은 충분한 label 확보가 어려움
    - Grade 0~7 양자화 이미지라 픽셀값의 의미를 보존해야 함
        ↓
[CutMix 계열 선택]
    - Mixup / Diffusion 보다 Grade 값을 직접 보존하기 쉬움
        ↓
[일반 CutMix 한계]
    - random crop 이 defect signal 을 잘라낼 수 있음
    - background 까지 defect 로 학습하면 Normal / Invalid / OOD 오탐 증가
        ↓
[FCM-PM 선택]
    - Full-Cover Mixup: chip 전체 grid 를 cover 해 defect 위치 사전 미지 조건 반영
    - Pair Mask: 합성 background 영역은 loss 에서 제외
    - Pair Mask 단독 변형은 FAR 100% 로 실패했고, Full-Cover Mixup 과 함께 쓸 때 효과 확인
        ↓
[checkpoint 선택]
    - val_f1 이 작은 validation set 에서 plateau 로 흔들림
    - val_margin 으로 정답 score 와 오답 최고 score 간 여유폭을 확인
        ↓
[후속 검토]
    - 4-bag ensemble: negative 안정성 확인
    - KD single student: 1× inference cost 압축 가능성 확인, FAR 추가 개선 필요
```

_single-label chip 기반 multi-label 조합 예시_

<img src="./figures/p2_raw_a_raw_b_2combo.png" width="520" alt="raw A, raw B, 2-combo chip 예시">

val_margin 은 `정답 class score 평균 - 오답 class score 최대값` 으로 정의했습니다. 쉽게 말해 모델이 맞춰야 하는 class 를 얼마나 높게 보고, 동시에 틀리면 안 되는 class 를 얼마나 낮게 누르고 있는지 보는 여유폭입니다. 작은 validation set 에서 val_f1 이 plateau 로 포화되는 문제를 줄이고, false-positive 위험까지 반영해 best-model 선택 신호로 사용했습니다.

```
정답 bits score: [0.92, 0.88]        → 평균 0.90
오답 bits score: [0.12, 0.31, 0.08]  → 최대 0.31

val_margin = 0.90 - 0.31 = 0.59

0.0 ───── 0.31(오답 최대) ───────────── 0.90(정답 평균) ── 1.0
        false-positive 위험선              맞춰야 하는 class 신호
```

**ㅁ 구현 성과**

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[추가 생성 chip 데이터, PoC]** | 평가셋 | single 4 + 2-combo 6 + Normal + Invalid + OOD 4 = **16+ class × 약 3,850 chip** 추가 생성 chip 데이터 기반 controlled synthetic benchmark |
| **[추가 생성 chip 데이터, PoC]** | FCM-PM 대표 모델 | 기존 요약 평가: bit F1 **0.9943**, Normal / Invalid / OOD negative false-positive **0건**. per-class 2,000 갱신 평가: bit F1 **0.9964**, Total FAR **0.83%** |
| **[추가 생성 chip 데이터, PoC]** | FCM-PM 내 Pair Mask 제거 비교 | FCM-PM 구조에서 Pair Mask 를 제거하면 FAR **100%** 로 negative 전체 오탐이 발생했습니다. 단순 CutMix + Pair Mask 만으로는 부족했고, Full-Cover Mixup 과 Pair Mask 를 함께 써야 했습니다. |
| **[추가 생성 chip 데이터, PoC]** | val_margin 기준 도입 | false-positive 위험까지 반영하는 best-model 선택 기준으로 적용 |
| **[추가 생성 chip 데이터, PoC]** | KD single student | 기존 요약 평가에서는 bit F1 **0.9872** / FAR **0.5%** 였지만, per-class 2,000 stress 평가에서는 FAR **12.86%** 로 확인했습니다. 압축 가능성은 있으나 추가 보정이 필요합니다. |

아래 표는 본문 판단에 필요한 대표 비교만 남긴 것입니다. 전체 sweep 결과는 별도 실험 로그로 분리하고, 추천서에는 구조 선택과 운영 검토에 직접 필요한 수치만 표기했습니다.

| 구분 | 확인한 내용 | 결과 |
|------|-------------|------|
| FCM-PM best | 대표 구조 성능 | per-class 2,000 갱신 평가 bit F1 **0.9964**, Total FAR **0.83%** |
| Pair Mask 단독 변형 | Full-Cover Mixup 없이 background masking 만으로 충분한지 확인 | Total FAR **100.00%** 로 실패 |
| 4-bag ensemble | negative false-positive 억제 안정성 확인 | bit F1 **0.9909**, Total FAR **0.00%** |
| KD distill student | 1× inference cost 압축 가능성 확인 | bit F1 **0.9872**, stress 평가 FAR **12.86%** 로 추가 보정 필요 |

[추가 생성 chip 데이터, PoC] 추가 Pair Mask 변형 2종도 negative false-positive 를 억제하지 못했습니다. 본문에서는 Pair Mask 단독 변형의 한계와 FCM-PM 조합 필요성을 보여주는 보조 근거로만 정리하고, 세부 sweep 수치는 실험 로그로 분리했습니다.

**ㅁ P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 검증 PoC**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 검증 PoC |
| 수행기간 | 2025년 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 구분 | 역할 | 기여도 |
|----|------|------|--------|
| 1 | 본인 | trend episode 합성 generator 설계, Region / Noise / trend 불량 type 코드화, 생성 데이터의 정상/이상 구분 신호 확인 | 80% |
| 2 | 관리자 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

P3 는 실제 운영 trend chart 가 항상 깨끗한 full-sampling 형태로 나오지 않는다는 점에서 출발했습니다. BBD, Overlay, CD 업무를 하며 자주 보던 계측 결핍 영역, 희소 영역, 공핍 영역과 설비성 noise 를 synthetic trend episode generator 에 넣었습니다. Binary gate + Type classifier 는 이 데이터가 실제 운영 성능을 보장한다는 의미가 아니라, 생성 rule 이 정상 / 이상 구분 신호를 담고 있는지 확인하기 위한 기준 모델입니다.

구체적으로는 full-sampling 정상 chart 만 만들지 않았습니다. 계측 밀도, 설비성 noise, trend type, 정상 산포 기준 anomaly strength 를 따로 조절할 수 있게 두고, 조건 조합을 바꿔가며 episode 를 만들었습니다. 모델을 먼저 키우기보다 데이터 생성 rule 이 현장 chart 를 어느 정도 닮았는지부터 보려는 목적이었습니다.

생성 데이터가 너무 쉬운 문제로 흐르지 않도록 정상 산포를 기준으로 anomaly 강도의 하한을 보정했습니다. 반대로 normal chart 가 과도하게 흔들리지 않도록 target_std 를 정상 wafer 내부 산포의 1.2배 이내로 맞췄습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 함께 봐야 합니다. |
| 기존 방식의 한계 | 실전 trend abnormal data 는 충분한 양과 균형 label 을 확보하기 어렵고, 수작업 chart 판독은 초보자 누락과 시간 소모가 큽니다. |
| 기술적 / 환경적 제약 | 실전 label 이 부족하므로, 먼저 현업 trend 판단 기준을 AI 검증용 synthetic data 로 옮기는 것이 핵심입니다. |

**ㅁ 기술적 해결 방안**

P3는 현업 trend 통계, 계측 영역 결핍, 설비성 noise, 불량 발생 양상을 synthetic generator 로 옮기는 작업입니다.

**알고리즘 / 모델 아키텍처 선택 흐름**

P3의 선택 기준은 모델 복잡도가 아니라 운영 환경 재현성이었습니다. 실제 chart 에서는 결핍 / 희소 / 공핍 영역, 설비 산포, hunting 유사 흔들림, drift 유사 흐름이 함께 나타납니다. 이 조건을 generator 에 먼저 넣어야 이후 anomaly detector 를 검증할 때도 결과를 해석할 수 있다고 봤습니다.

```
[BBD / Overlay / CD 현업 trend 경험]
        ↓
[Region 5종: 정상 / 희소 / 공핍 / 얇은 계측 / 결핍 영역]
        ↓
[Noise 3종: Gaussian noise(설비 산포) / Laplacian noise(hunting) / correlation noise(drift)]
        ↓
[trend 불량 5종: mean_shift / std / spike / drift / context]
        ↓
[정상 산포 기준 최소 이상 강도 보정]
        ↓
[224×224 trend chart PNG rendering]
        ↓
[기준 모델 학습: Binary gate + Type classifier]
        ↓
[정상/이상 구분 신호 확인]
```

선택 흐름은 `domain knowledge → synthetic generator → 기준 모델 검증` 순서입니다.

```
[실전 제약]
    - abnormal trend label 부족
    - chart 마다 계측 결핍 / 희소 / 공핍 영역이 다르게 나타남
    - 단순 threshold 로는 설비 산포 / hunting / drift / baseline 변화 구분이 어려움
    - 초보자가 chart 를 보면 spike, drift, context pattern 누락 가능
        ↓
[Generator first]
    - Region 5종으로 결핍 / 희소 / 공핍 영역을 운영 환경처럼 생성
    - Noise 3종으로 Gaussian noise(설비 산포), Laplacian noise(hunting), correlation noise(drift) 를 분리
    - 불량 5종으로 현업에서 보는 trend 형상을 명시적으로 생성
        ↓
[Anomaly strength 보정]
    - 정상 산포에 묻히는 약한 이상은 학습 신호로 쓰기 어려움
    - 정상 wafer 내부 산포를 기준으로 최소 이상 강도와 target_std 를 보정
        ↓
[기준 모델]
    - Binary gate: 정상 / 이상 분리 가능성 확인
    - Type classifier: 이상 type 구분 가능성 확인
        ↓
[판단]
    - 기준 모델이 안정적으로 수렴하면 생성 데이터에 정상/이상 분리 신호가 있다고 판단
    - type 혼동이 크면 모델보다 generator rule / label definition 을 먼저 수정
```

_Domain Knowledge 기반 trend episode 생성 예시_

<p>
  <img src="./figures/p3_trend_rule_annotation.png" alt="Domain knowledge 기반 trend episode 생성 rule 주석 예시" width="760" />
</p>

생성 데이터 평가가 일시적 spike 에 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 적용했습니다.

**ㅁ 구현 성과**

주요 성과는 모델 수치보다 **현업 trend 조건을 데이터로 옮긴 것**입니다. 정상 750건과 abnormal 5종 각 150건, 총 **1,500 sample** 의 합성 trend chart 평가셋을 만들고 224×224 chart PNG 로 rendering 했습니다.

검증 수치는 실전 성능이 아니라 생성 데이터 점검용입니다. 1차 Binary gate 에서는 Binary F1 **0.9967**, Abnormal Recall **0.9987** 을 확인했습니다. 2차 Type classifier 는 mean_shift 와 drift 혼동이 남아 있어, 현재 generator rule 과 label definition 을 같이 보정하는 단계입니다.

BBD/Overlay/CD trend 판단 기준을 synthetic data generator 로 옮기면서, 실전 label 이 부족한 상황에서도 AI 검증을 시작할 수 있는 데이터 기반을 마련했습니다. 아직 실전 운영 검증 전 단계이므로, 다음 단계는 실제 chart 로 generator rule 과 type label 을 다시 맞추는 것입니다.
