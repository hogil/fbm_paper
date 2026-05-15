## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2024년 ~ 현재 | P1. Failbit Map Known & Unknown 불량 분석 아키텍처 | 3인 협업, 본인 60% 담당<br>DRAM 전제품 라인<br>일 약 2만 장 wafer 운영 데이터 | S3 수집, Cython/Python 파싱, palette PNG / chip 좌표 JSON 생성, Web App 운영, Known / Unknown AI 모델 설계, 개발 및 검증 | 10% | 40% | 50% |
| 2025년 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC, 본인 80% 담당<br>16+ class<br>약 3,850 chip 통제 합성 평가셋 | FCM-PM 합성 및 손실 마스킹 구조 구성, 학습 및 평가 체계 구축, 최종 모델 선택 기준과 KD 압축 가능성 검토 | 20% | 40% | 40% |
| 2025년 ~ 현재 | P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 불량 검증 | 2인 PoC, 본인 80% 담당<br>총 7,000 sample<br>normal 3,500 + 불량 5종×700 | Domain Knowledge 기반 데이터 합성 generator 설계, trend 불량 rule 코드화, AI 기준 모델 fine-tuning 및 성능 검증 | 5% | 55% | 40% |

## 2. 대표 과제 상세 기술서

**ㅁ P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

핵심은 양산 Failbit Map 처리 흐름과 AI 불량 후보 검출을 하나의 운영 구조로 묶은 점입니다.

**(1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Failbit Map Known & Unknown 불량 분석 아키텍처 |
| 수행기간 | 2024년 ~ 현재 |
| 참여인원 | 본인 / 현업 엔지니어 / 관리자 |
| 과제 개요 및 규모 | Failbit Map raw log 를 이미지와 chip 좌표 데이터로 변환해 Web App 에서 조회하고, Known 분류와 Unknown 후보 검출까지 연결한 양산 운영 과제입니다. DRAM 전제품 라인에서 일 약 2만 장 wafer 를 1시간 주기로 적재합니다. |

**ㅁ 과제 참여 인력 및 역할**

| NO | 구분 | 역할 | 기여도 |
|----|------|------|--------|
| 1 | 본인 | 데이터 변환/저장/조회 파이프라인, Web App, Known/Unknown 모델 기술 구현 | 60% |
| 2 | 현업 엔지니어 | 현업 문제정의 및 불량 분석 교육 | 20% |
| 3 | 관리자 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

[본인이 독자적으로 수행한 핵심 모듈]

- Failbit Map raw log 변환, palette PNG 저장, chip 좌표 JSON 생성, Web App 조회 흐름, Known 2-stage 분류, Unknown 자기지도 후보 검출 구조를 직접 설계 및 구현했습니다.
- 과제 안에서 타 구성원과 차별화되는 본인만의 구체적 담당영역은 반도체 Failbit Map 을 AI 입력 데이터와 운영 서비스 구조로 바꾸는 기술 구현 전반입니다. 현업 엔지니어는 문제정의와 불량 분석 교육을 맡았고, 관리자는 방향성, 일정 및 리뷰를 맡았습니다.
- 본인의 기술적 해결책이 과제 성패에 미친 영향은 대량 map 을 실제로 적재, 조회, 분류할 수 있는 운영 기반을 만든 점입니다. Known 은 ROI YOLO 2-stage 로 weighted F1 0.95 까지 올렸고, Unknown 은 6×6 grid structured local sampling 과 Local InfoNCE 를 적용해 13개 후보 중 7개 실제 불량 확인으로 이어졌습니다.

데이터 처리 단에서는 기존 Python 처리 대비 Cython 기반 hex-to-grade 변환으로 wafer 단위 변환 시간을 크게 줄였고, 32-color palette-indexed PNG 저장으로 저장 용량도 줄였습니다. 내부 측정 기준으로 약 100배 가속, 약 75% 절감 수준입니다.

Known 분류는 **[실전 현업 라벨 데이터]** 평가용 hold-out set 에서 weighted F1 0.95 를 확인했습니다. 이 수치는 운영 적용 결과가 아니라 평가 split 에서 본 분류 성능 지표입니다.

Unknown 검출은 **[실전 현업 데이터]** 5일 운영 데이터 10,000장으로 SimCLR 계열 대조학습 임베딩을 학습하고, 별도 1일 2,000장에 HDBSCAN grouping 을 적용했습니다. 적용 결과 13 후보 중 현업이 실제 불량으로 확인한 건은 7건입니다. 이 값은 정량 성능지표가 아니라 후보 발굴 및 현업 확인 결과이며, 나머지 후보의 판정 상태는 별도 검토 대상으로 분리했습니다.

같은 외형이라도 center, edge, top, bottom 등 발생 영역이 다르면 다른 불량으로 볼 수 있어, 6×6 grid structured local sampling 과 Local InfoNCE loss 를 함께 넣었습니다. ROI YOLO 의 한계를 보완하기 위한 object-id map 구조는 별도 생성 chip 데이터 기준의 추가 개발 항목입니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | Failbit Map 은 EDS Test 결과를 wafer 당 약 1,000만 개 block 의 Grade 0~7로 표현한 초고해상도 데이터입니다. 수율, BIN, FTN/QTN 같은 Measure 요약값만으로는 불량의 위치, 형상, 밀집도, 방향성을 확인하기 어렵기 때문에 map 기반 전수 분석이 필요했습니다. |
| 기존 방식의 한계 | 기존 환경은 설비 raw log 를 요청 시점에 받아 변환하는 온디맨드 방식에 가까웠고, wafer 당 10~50MB 수준의 log 를 대량 변환, 저장 및 조회하기 어려웠습니다. 전 제품 기준 일 약 2만 장 wafer 가 발생하지만 엔지니어가 한 번에 확인할 수 있는 map 은 약 48매 수준이었고, 불량 유형 판정도 수작업에 의존했습니다. |
| 기술적 / 환경적 제약 | 1시간 주기 자동 적재, wafer 당 약 1,000만 grade 변환, 대량 이미지 저장 용량, Web App 응답성, 16 class / 1,500 labeled sample 의 label 부족, low-confidence Known class 보정, 사전 class 가 없는 Unknown 후보 검출을 동시에 해결해야 했습니다. 특히 wafer map 은 같은 모양이라도 center / edge / top / bottom 등 발생 위치에 따라 다른 불량으로 해석될 수 있어, 위치 정보를 모델 구조에 반영해야 했습니다. |

**ㅁ 기술적 해결 방안**

[본인이 직접 수행한 핵심 로직]

- 데이터 : EDS Test raw log 를 S3 적재 경로에서 수집하고, 압축 해제 후 Cython 기반 hex-to-grade 변환으로 Grade 0~7 Failbit Map 을 만들었습니다. Failbit Map 이 제한된 색상 체계라는 점을 근거로 32-color palette PNG 를 사용했고, chip 좌표 JSON 을 함께 생성해 Web App 조회, AI 입력, 후속 object-id map 구성에서 같은 좌표계를 쓰도록 했습니다.
- 알고리즘: 전체 wafer 분포를 먼저 보는 ConvNeXtV2 wafer classifier 를 1차 모델로 두고, center scratch / center scratch_rot 처럼 map-level 에서 헷갈리는 class 는 ROI YOLO 로 chip 단위 증거를 다시 확인하는 2-stage 구조를 선택했습니다. 등록 class 밖 패턴은 SimCLR 계열 자기지도 임베딩, 6×6 grid structured local sampling, Local InfoNCE, HDBSCAN 순서로 후보화했습니다. Logic Flow 는 `wafer 전체 판단 → 저신뢰 샘플 ROI 재확인 → unknown 후보 grouping → chip-CNN object-id map 확장`입니다.
- 최적화: 변환 병목은 Cython 으로 줄이고, 저장 병목은 palette PNG 로 줄였습니다. 모델 쪽은 ConvNeXtV2 / MaxViT 비교 후 운영 부담이 낮은 ConvNeXtV2 를 선택했고, Optuna 기반 HPO, focal loss / class weight 조정, confidence gate, ROI YOLO 보정, 6×6 local sampling 을 직접 적용해 Known F1 과 Unknown 후보 품질을 같이 개선했습니다.

**ㅁ 실제 코드를 제외한 아키텍쳐 설계도 / 플로우차트**

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
[Unknown 자기지도 임베딩]
        ├─ Global InfoNCE
        └─ 6×6 grid local sampling + Local InfoNCE loss
        ↓
[HDBSCAN 후보 grouping]
        ↓
[Web App 결과 표시 및 현업 검증]
```

**Logic Flow 중심 모델 선택**

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
    - center scratch / center scratch_rot 처럼 map-level 에서 헷갈리는 class 를 ROI chip 단위 판단 근거로 재확인
    - chip마다 box 와 defect class 를 확인해 wafer-level 예측을 보정
        ↓
if 등록 class 로 설명되지 않음:
    [Unknown 자기지도 임베딩]
    - Global InfoNCE 로 전체 패턴을 보고,
    - 6×6 local sampling + Local InfoNCE 로 발생 위치 정보를 보존
    - HDBSCAN 으로 현업 확인 후보를 grouping
        ↓
if class 수 증가 / ROI YOLO 확장 한계:
    [chip-CNN → object-id map]
    - chip별 defect id 를 32×32 wafer 좌표계로 재구성
    - raw map 에서 비슷해 보이는 wafer 를 defect object 분포로 다시 구분
```

Backbone 은 Transformer 계열과 CNN 계열을 함께 비교했습니다. Transformer 계열은 wafer 전체 구조를 보는 데 강점이 있지만, 본 과제의 결함은 특정 zone 또는 국소 영역에 나타나는 경우가 많았습니다. 그래서 지역 특징 추출에 강한 ConvNeXtV2 를 우선 후보로 잡았습니다. backbone 단독 비교에서는 ConvNeXtV2 와 MaxViT 가 weighted F1 0.87 수준이었고, ConvNeXtV2 가 파라미터와 FLOPs 부담이 낮아 운영형 모델로 더 적합했습니다. 이후 모델 설정값 튜닝과 ROI YOLO 2-stage 보정을 더해 최종 평가 F1 0.95까지 확인했습니다.

```
[Input wafer image]
        ↓
[ConvNeXtV2 task-specific fine-tuned wafer classifier]
        ↓ confidence < gate
[ROI YOLO refinement]
        ↓
[Known class prediction]
```

Unknown 검출은 정답 class 를 미리 정의하기 어려운 운영 이미지를 후보 grouping 문제로 봤습니다. 단순히 wafer 전체 모양만 임베딩하면 center, edge, top, bottom 처럼 위치가 다른 불량을 같은 그룹으로 묶을 수 있습니다. 그래서 6×6 grid structured local sampling 으로 위치별 특징을 뽑고, Local InfoNCE loss 를 함께 적용해 발생 영역 정보가 임베딩에 남도록 했습니다. 이후 HDBSCAN 으로 유사 패턴을 묶어 현업 검토 후보로 올렸습니다.

학습/평가에 사용된 실제 wafer 이미지 예시입니다.

| Edge-Top Scratch | Edge-Ring Scratch_rot | Center Bank-Boundary |
|:----------------:|:---------------------:|:--------------------:|
| <img src="./figures/wafer_edge_top_scratch.png" width="180" /> | <img src="./figures/wafer_edge_ring_scratch_rot.png" width="180" /> | <img src="./figures/wafer_center_bank_boundary.png" width="180" /> |
| **BrokenRing** | **RingDots** | **CrescentArc** |
| <img src="./figures/wafer_brokenring.png" width="180" /> | <img src="./figures/wafer_ringdots.png" width="180" /> | <img src="./figures/wafer_crescentarc.png" width="180" /> |

ROI YOLO 2-stage 보정 흐름은 아래 예시처럼 잡았습니다. GT 가 center scratch 인 wafer 가 Stage 1 wafer-level CNN 만으로는 center scratch_rot 으로 오인 분류될 수 있고, Stage 2 ROI YOLO 가 chip 단위 bounding box 와 class 라벨을 다시 확인해 최종 class 를 보정합니다.

| Stage 1 raw wafer | Stage 2 ROI 영역 | Stage 2 chip box + class |
|:-----------------:|:----------------:|:------------------------:|
| <img src="./figures/wafer_center_scratch.png" height="280" /> | <img src="./figures/p1_roi_crop_real.png" height="280" /> | <img src="./figures/p1_chip_yolo_box_real.png" height="280" /> |

2차 개발은 ROI YOLO 의 class 확장성과 throughput 한계를 보완하기 위한 구조입니다.

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

아래 예시는 raw map 에서는 center 계열 불량이 비슷하게 보이지만, chip 단위 object-id map 에서는 defect object 분포가 달라지는 경우를 보여줍니다. 좌측 두 칸이 raw wafer map, 우측 두 칸이 동일 wafer 의 chip-CNN object-id map 입니다.

<table>
  <thead>
    <tr>
      <th colspan="2" align="center" style="text-align:center">raw wafer map</th>
      <th colspan="2" align="center" style="text-align:center">chip-CNN object-id map</th>
    </tr>
    <tr>
      <th align="center" style="text-align:center">center bank-boundary</th>
      <th align="center" style="text-align:center">center scratch_rot</th>
      <th align="center" style="text-align:center">center bank-boundary</th>
      <th align="center" style="text-align:center">center scratch_rot</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="25%" align="center"><img src="./figures/AAN585_00P_18_20260501_010000_97.6_2_EE_NORMAL_raw.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
      <td width="25%" align="center"><img src="./figures/ACZ452_00P_14_20260501_010000_97.6_2_PT_NORMAL_raw.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
      <td width="25%" align="center"><img src="./figures/AAN585_00P_18_20260501_010000_97.6_2_EE_NORMAL_objid.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
      <td width="25%" align="center"><img src="./figures/ACZ452_00P_14_20260501_010000_97.6_2_PT_NORMAL_objid.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
    </tr>
  </tbody>
</table>

**ㅁ 구현 성과**

[정량적/정성적 성과]

- 기술 지표: [실전 현업 라벨 데이터] Known 2-stage 는 16 class / 1,500 labeled samples / 평가용 hold-out set 기준 weighted F1 **0.95** 를 확인했습니다. 단계별로는 baseline 0.78 → ConvNeXtV2 task-specific fine-tuning 0.87 → Optuna 기반 모델 설정값 튜닝 0.92 → ROI YOLO 2-stage 0.95 로 개선했습니다. [양산 운영] 데이터 처리에서는 Cython hex-to-grade 약 **100배** 가속, 32-color palette PNG 약 **75%** 저장 절감을 확인했습니다. [추가 생성 데이터, 개발 중] Unknown 후속 benchmark 는 same-anchor defect-class capture 43/43, ARI **0.859±0.018**, Completeness **0.994**, Homogeneity **0.942** 입니다.
- 현업 임팩트: DRAM 전제품 라인에서 일 약 **2만 장 wafer** 를 1시간 주기로 적재하고, Web App 은 12일 누적 **2,317 요청**까지 운영되었습니다. Unknown 은 [실전 현업 데이터] 5일 10,000장 학습 + 별도 1일 2,000장 적용 결과 13개 후보 중 **7개 실제 불량**을 현업이 확인했습니다. 이 값은 F1 같은 정량 metric 이 아니라, 신규 후보를 압축해 현업 검토 대상으로 올린 운영 확인 결과입니다.

**ㅁ P2. Chip Multi-label Classification**

핵심은 부족한 multi-label label 문제를 single-label 불량 chip 조합과 배경 영역 loss 처리로 풀어낸 점입니다.

**(1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Chip multi-label classification - CutMix → CutMix + Pair Mask → FCM-PM |
| 수행기간 | 2025년 ~ 현재 |
| 참여인원 | 본인 / 관리자 |
| 과제 개요 및 규모 | 실제 환경에서 multi-label 불량 조합 label 을 충분히 모으기 어렵다는 조건을 두고, single-label 불량 chip 을 조합해 multi-label 불량을 예측하도록 만든 PoC 입니다. single 4 class 기반으로 2-combo, Normal, Invalid, OOD 를 포함한 16+ class × 약 3,850 chip 통제 합성 평가셋을 구성했습니다. |

**ㅁ 과제 참여 인력 및 역할**

| NO | 구분 | 역할 | 기여도 |
|----|------|------|--------|
| 1 | 본인 | FCM-PM 합성 및 손실 마스킹 구조 적용, val_margin 기준 도입, KD 압축 모델 가능성 검토, 학습 및 평가 운영 | 80% |
| 2 | 관리자 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

[본인이 독자적으로 수행한 핵심 모듈]

- single-label defect chip 을 조합해 multi-label 학습 데이터를 만드는 FCM-PM(Full-Cover Mixup + Pair Mask) 합성 구조, loss 마스킹, val_margin 기준, KD student 압축 실험을 직접 설계 및 검증했습니다.
- 과제 안에서 타 구성원과 차별화되는 본인만의 구체적 담당영역은 실제로 확보 가능한 single-label chip 만으로 multi-label 조합 문제를 만들고, 각 single class 를 빠짐없이 맞히는 학습 및 평가 구조를 만든 부분입니다. 관리자는 방향성, 일정 및 리뷰를 담당했습니다.
- 본인의 기술적 해결책이 과제 성패에 미친 영향은 label 부족 문제를 데이터 합성 문제로 바꿔 학습 가능하게 만든 점입니다. 일반 CutMix 에서 불량 신호가 잘리는 문제는 Full-Cover Mixup 으로 줄였고, 합성 background 를 defect 로 학습하는 문제는 Pair Mask 로 막았습니다. 그 결과 FCM-PM 대표 모델에서 per-class 2,000 갱신 평가 bit F1 0.9964, Total FAR 0.83% 를 확인했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | multi-label 불량 조합 label 을 충분히 확보하기 어렵고, 실제로는 single-label 불량 chip 중심으로 데이터가 쌓입니다. |
| 기존 방식의 한계 | single-label 불량을 단순 조합하면 multi-label chip 안의 각 single class 를 안정적으로 맞춰야 하는데, 일반 CutMix 는 일부 영역만 잘라 붙이므로 불량 신호가 잘릴 수 있습니다. 배경 영역까지 defect 로 학습하면 Normal / Invalid / OOD 평가에서 오탐이 증가합니다. |
| 기술적 / 환경적 제약 | single-label 기반 multi-label 조합 생성, chip 내부 defect 위치 사전 미지, 작은 검증셋, OOD 및 Normal/Invalid 오탐 억제, 추론 비용 제약이 동시에 존재했습니다. |

**ㅁ 기술적 해결 방안**

[본인이 직접 수행한 핵심 로직]

- 데이터 : 실제 환경에서 충분히 확보하기 어려운 multi-label chip label 대신, 확보 가능한 single-label defect chip 을 원천 데이터로 사용했습니다. Grade 0~7 양자화 값이 불량 의미를 가지므로 픽셀값을 섞는 Mixup / Diffusion 계열보다, 원래 Grade 값을 보존하는 CutMix 계열을 기본 합성 방식으로 선택했습니다. 합성 후에는 Normal / Invalid / OOD 평가셋을 따로 두어 multi-label 조합 학습이 오탐으로 흐르지 않는지 확인했습니다.
- 알고리즘: 핵심 Logic Flow 는 `single-label chip 확보 → multi-label 조합 생성 → 조합 안의 각 single class 예측 → Normal/Invalid/OOD 오탐 확인`입니다. 일반 CutMix 는 일부 defect 영역을 잘라낼 수 있어 chip 전체 grid 를 덮는 Full-Cover Mixup 을 적용했고, 합성 background 영역이 defect loss 로 들어가는 문제는 Pair Mask 로 제외했습니다. 최종 구조는 FCM-PM(Full-Cover Mixup + Pair Mask)입니다.
- 최적화: 작은 검증셋에서는 val_f1 만으로 모델 저장 시점을 고르기 어려워, 정답 score 와 오답 최고 score 사이의 여유를 보는 val_margin 을 추가했습니다. FCM-PM 구성요소 제거 비교로 Full-Cover Mixup 과 Pair Mask 의 필요성을 확인했고, 4-bag ensemble 과 KD student 모델을 비교해 오탐 안정성과 추론 비용 절감 가능성을 함께 검토했습니다.

**ㅁ 실제 코드를 제외한 아키텍쳐 설계도 / 플로우차트**

```
[single 4 class chip]
        ↓
[CutMix 계열 선정: Grade 값 보존]
        ↓
[CutMix + Pair Mask 중간 검증: 배경 영역 loss 제외만으로는 부족]
        ↓
[FCM-PM: Full-Cover Mixup + Pair Mask]
        ↓
[FCM-PM 학습]
        ↓
[val_margin 기준 모델 선택]
        ↓
[대표 모델 / KD 단일 모델 비교]
```

**Logic Flow 중심 모델 선택**

```
[실제 조건]
    - 확보 가능한 데이터는 대부분 single-label 불량 chip
    - multi-label defect 조합은 충분한 label 확보가 어려움
    - Grade 0~7 양자화 이미지라 픽셀값의 의미를 보존해야 함
        ↓
[CutMix 계열 선택]
    - Mixup / Diffusion 보다 Grade 값을 직접 보존하기 쉬움
        ↓
[일반 CutMix 한계]
    - random crop 이 불량 신호를 잘라낼 수 있음
    - 배경 영역까지 defect 로 학습하면 Normal / Invalid / OOD 오탐 증가
        ↓
[FCM-PM 선택]
    - Full-Cover Mixup: chip 전체 grid 를 cover 해 defect 위치 사전 미지 조건 반영
    - Pair Mask: 합성 background 영역은 loss 에서 제외
    - 구성요소 제거 비교 실험에서 오탐 억제 실패를 확인해 FCM-PM 조합 유지
        ↓
[모델 선택]
    - 작은 검증셋에서는 val_f1 만으로 최종 모델을 고르기 어려움
    - val_margin 으로 정답 score 와 오답 최고 score 간 여유폭을 확인
        ↓
[후속 검토]
    - 4-bag ensemble: 오탐 안정성 확인
    - KD 단일 student 모델: 추론 비용 압축 가능성 확인, FAR 추가 개선 필요
```

학습 single 4 class 예시 chip 입니다.

<p align="left">
  <img src="./figures/chip_eval_bank_boundary_selected.png" width="160" />
  <img src="./figures/chip_eval_fork_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_rot_selected.png" width="160" />
</p>

2-combo 합성 예시 chip 6종입니다.

<p align="left">
  <img src="./figures/chip_combo_bb_fork_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_scratch_scratch_rot_selected.png" width="130" />
</p>

Normal / Invalid / OOD 평가셋 예시입니다.

<p align="left">
  <img src="./figures/chip_eval_normal_selected.png" width="130" />
  <img src="./figures/chip_eval_invalid_selected.png" width="130" />
  <img src="./figures/chip_ood_starburst_selected.png" width="130" />
  <img src="./figures/chip_ood_centerdonut_selected.png" width="130" />
  <img src="./figures/chip_ood_crossscratch_selected.png" width="130" />
  <img src="./figures/chip_ood_diagonalsmear_selected.png" width="130" />
</p>

val_margin 은 `정답 class score 평균 - 오답 class score 최대값` 으로 정의했습니다. 작은 검증셋에서 val_f1 만으로 최종 모델을 고르기 어려워, 오탐 위험을 함께 보기 위한 모델 선택 신호로 사용했습니다.

```
정답 bits score: [0.92, 0.88]        → 평균 0.90
오답 bits score: [0.12, 0.31, 0.08]  → 최대 0.31

val_margin = 0.90 - 0.31 = 0.59

0.0 ───── 0.31(오답 최대) ───────────── 0.90(정답 평균) ── 1.0
        오탐 위험선                         맞춰야 하는 class 신호
```

**ㅁ 구현 성과**

[정량적/정성적 성과]

- 기술 지표: [추가 생성 chip 데이터, PoC] single 4 + 2-combo 6 + Normal + Invalid + OOD 4 로 **16+ class × 약 3,850 chip** 통제 합성 평가셋을 만들었습니다. FCM-PM 대표 모델은 기존 요약 평가셋 기준 bit F1 **0.9943**, Normal / Invalid / OOD 오탐 **0건**을 확인했고, per-class 2,000 갱신 평가에서는 bit F1 **0.9964**, Total FAR **0.83%** 였습니다. 4-bag ensemble 은 bit F1 **0.9909**, Total FAR **0.00%** 로 오탐 안정성을 확인했습니다.
- 현업 임팩트: 실제 현업에서는 multi-label 불량 조합 label 을 충분히 모으기 어렵기 때문에, single-label defect chip 만으로 multi-label 조합 학습과 검증을 시작할 수 있는 방법을 만들었습니다. Full-Cover Mixup 과 Pair Mask 구성요소 제거 비교에서 일부 변형은 Total FAR **100.00%** 로 실패해, FCM-PM 조합이 Normal / Invalid / OOD 오탐 억제에 필요한 구조임을 확인했습니다. KD student 는 bit F1 **0.9872** 였지만 가혹 조건 FAR **12.86%** 로 확인되어, 운영 적용 전 추가 보정 대상으로 분리했습니다.

**ㅁ P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 불량 검증**

핵심은 BBD / Overlay / CD 현업 trend 판단 기준을 모델보다 먼저 생성 데이터 구조로 옮긴 점입니다.

**(1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 불량 검증 |
| 수행기간 | 2025년 ~ 현재 |
| 참여인원 | 본인 / 관리자 |
| 과제 개요 및 규모 | 실전 abnormal label 이 부족한 상태에서 detector 를 먼저 고도화하기보다, 학습 가능한 trend abnormal 데이터를 만드는 데이터 생성 PoC 입니다. normal 3,500 + 불량 5종 각 700 = 불량 3,500, 총 7,000 sample 합성 trend chart 평가셋을 만들었습니다. |

**ㅁ 과제 참여 인력 및 역할**

| NO | 구분 | 역할 | 기여도 |
|----|------|------|--------|
| 1 | 본인 | Domain Knowledge 기반 trend episode 합성 generator 설계, Region / Noise / trend 불량 type 코드화, AI 기준 모델 fine-tuning 및 성능 검증 | 80% |
| 2 | 관리자 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

[본인이 독자적으로 수행한 핵심 모듈]

- BBD / Overlay / CD 현업 trend 경험을 바탕으로 Region 5종, Noise 3종, trend 불량 5종을 조합하는 Domain Knowledge 기반 trend episode 합성 generator 를 직접 설계했습니다.
- 과제 안에서 타 구성원과 차별화되는 본인만의 구체적 담당영역은 현업 chart 에서 보던 결핍 영역, 희소 영역, 공핍 영역, 얇은 계측 영역과 Gaussian noise(설비 산포), Laplacian noise(hunting), correlation noise(drift)를 생성 rule 로 옮긴 부분입니다. 관리자는 방향성, 일정 및 리뷰를 담당했습니다.
- 본인의 기술적 해결책이 과제 성패에 미친 영향은 실전 abnormal label 이 부족한 상황에서 먼저 학습 가능한 데이터셋을 만든 점입니다. normal 3,500건과 불량 5종 각 700건으로 총 7,000 sample 을 구성했고, 1단계 정상/이상 분류와 2단계 불량 type 분류로 생성 rule 이 실제 학습 신호를 담고 있는지 검증했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 함께 봐야 합니다. |
| 기존 방식의 한계 | 실전 trend abnormal data 는 충분한 양과 균형 label 을 확보하기 어렵고, 수작업 chart 판독은 누락 가능성과 시간 소모가 큽니다. |
| 기술적 / 환경적 제약 | 실전 label 이 부족하므로, 먼저 현업 trend 판단 기준을 AI 검증용 synthetic data 로 옮기는 것이 핵심입니다. |

**ㅁ 기술적 해결 방안**

[본인이 직접 수행한 핵심 로직]

- 데이터 : BBD / Overlay / CD 현업 trend 경험에서 봤던 정상 chart, 희소 영역, 공핍 영역, 얇은 계측 영역, 결핍 영역을 Region 5종으로 코드화했습니다. 설비 산포는 Gaussian noise, hunting 유사 흔들림은 Laplacian noise, drift 유사 흐름은 correlation noise 로 분리해 synthetic trend episode 의 입력 조건으로 만들었습니다.
- 알고리즘: 모델을 먼저 고도화하기보다 `domain knowledge → synthetic generator → 기준 모델 검증` 흐름을 선택했습니다. 실전 abnormal label 이 부족한 상태에서 복잡한 detector 를 바로 학습하면 모델 성능보다 데이터 편향을 먼저 학습할 수 있기 때문입니다. 생성된 chart 는 1단계 정상/이상 binary classification 과 2단계 5개 불량 type classification 으로 나눠 검증했습니다.
- 최적화: 생성 데이터가 너무 쉬운 문제가 되지 않도록 정상 산포 기준 최소 이상 강도를 보정했고, normal chart 가 과도하게 흔들리지 않도록 target_std 를 정상 wafer 내부 산포 범위 안에서 제한했습니다. mean_shift / std / spike / drift / context type 혼동이 보이면 모델보다 generator rule 과 label definition 을 먼저 보정하는 기준을 두었습니다.

**ㅁ 실제 코드를 제외한 아키텍쳐 설계도 / 플로우차트**

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
[기준 모델 학습: 1단계 정상/이상 분류 + 2단계 5개 불량 type 분류]
        ↓
[정상/이상 구분 신호 확인]
```

**Logic Flow 중심 모델 선택**

```
[실전 제약]
    - abnormal trend label 부족
    - chart 마다 계측 결핍 / 희소 / 공핍 영역이 다르게 나타남
    - 단순 threshold 로는 설비 산포 / hunting / drift / baseline 변화 구분이 어려움
    - 수작업 chart 판독에서는 spike, drift, context pattern 누락 가능
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
    - 1단계 정상/이상 binary classification
    - 2단계 5개 불량 type classification
        ↓
[판단]
    - 기준 모델 수렴 결과는 생성 데이터에 분류 가능한 신호가 있는지 보는 참고 근거로만 사용
    - type 혼동이 크면 모델보다 generator rule / label definition 을 먼저 수정
```

합성 trend chart 예시입니다.

| Normal | Mean Shift | Standard Deviation Change |
|:------:|:----------:|:-------------------------:|
| <img src="./figures/trend_normal.png" width="200" /> | <img src="./figures/trend_mean_shift.png" width="200" /> | <img src="./figures/trend_standard_deviation.png" width="200" /> |
| **Spike** | **Drift** | **Context** |
| <img src="./figures/trend_spike.png" width="200" /> | <img src="./figures/trend_drift.png" width="200" /> | <img src="./figures/trend_context.png" width="200" /> |

생성 데이터 점검 과정에서는 일시적인 검증 지표 변동에 흔들리지 않도록 평가 로그를 별도로 확인했습니다.

**ㅁ 구현 성과**

[정량적/정성적 성과]

- 기술 지표: [합성 trend chart, PoC] normal **3,500건**과 불량 5종 각 **700건**으로 불량 **3,500건**, 총 **7,000 sample** 의 합성 trend chart 평가셋을 만들고 224×224 chart PNG 로 rendering 했습니다. 1단계 정상/이상 분류에서는 Binary F1 **0.9967**, Abnormal Recall **0.9987** 을 확인했습니다. 2단계 5개 불량 type 분류는 mean_shift 와 drift 혼동이 남아 있어 generator rule 과 label definition 을 같이 보정하는 단계입니다.
- 현업 임팩트: BBD / Overlay / CD 현업 trend 판단 기준을 synthetic data generator 로 옮겨, 실전 abnormal label 이 부족한 상태에서도 anomaly detector 검증을 시작할 수 있는 데이터 기반을 만들었습니다. 이 수치는 실전 운영 성능이 아니라 생성 rule 이 정상/이상 구분 신호를 담고 있는지 확인한 PoC 결과이며, 실제 chart 적용 전 단계로 구분했습니다.
