## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2022년 ~ 현재 | P1. Failbit Map AI 분류 시스템 | 3인 협업, 본인 60% 리딩<br>DRAM 전제품 라인 양산 운영<br>일 약 2만 장 wafer 처리 | S3 수집, Cython/Python 파싱, palette PNG / chip 좌표 JSON 생성, Web App 운영, Known / Unknown AI 모델 설계·개발·검증 | 20% | 35% | 45% |
| 2025년 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC, 본인 80% 리딩<br>16+ class × 약 3,850 chip<br>controlled synthetic benchmark | FCM-PM 합성 및 손실 마스킹 구조 구성, 학습·평가 체계 구축, best-model 선택 기준 및 대표 모델 검증 | 20% | 40% | 40% |
| 2025년 ~ 현재 | P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC | 2인 PoC, 본인 80% 리딩<br>10,000 scenarios 구성<br>test 1,500 sample 평가 | 합성 generator 설계, 도메인 자산 코드화, 생성 데이터 학습 가능성 검증 | 20% | 45% | 35% |

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
| 1 | 본인 | 개인정보 입력란 | 개인정보 입력란 | Frontend, Backend, AI 모델, 데이터 처리, 생성 파이프라인 주요 설계와 구현 주도 | 60% |
| 2 | 현업 엔지니어 | 개인정보 입력란 | 개인정보 입력란 | 아이디어 발의 및 불량 분석 교육, Unknown 후보 13개 중 실제 불량 7개 확인 | 20% |
| 3 | 관리자 | 개인정보 입력란 | 개인정보 입력란 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

본인은 Failbit Map 의 의미와 현업 사용자 분석 방식을 먼저 학습한 뒤, 대량 변환·저장·조회 파이프라인, Web App, Known 2-stage 분류, Unknown self-supervised 검출을 하나의 운영 흐름으로 연결했습니다. 반도체 분석 현장에서 쌓은 이해를 AI 모델 구조와 데이터 처리 설계에 직접 반영하여, 현업 분석 부담을 줄이는 운영 시스템으로 구현한 점이 본인의 핵심 기여입니다.

데이터 처리 단에서는 Cython 기반 hex-to-grade 변환으로 wafer 당 약 1,000만 cell 변환 병목을 약 100배 가속했고, 32-color palette-indexed PNG 저장으로 Failbit Map 저장 용량을 약 75% 절감해 양산 운영의 처리량과 저장 비용을 동시에 확보했습니다.

AI 모델 단에서는 ConvNeXtV2 + ROI YOLO 2-stage 로 16 class / 1,500 labeled samples / 4:1 stratified split **[실전 현업 데이터]** 에서 weighted F1 0.95 를 달성했으며, Unknown 검출은 **[실전 현업 데이터]** 5일 운영 데이터 10,000장 학습 + 별도 1일 2,000장 적용 결과 13 후보 중 7개가 실제 불량으로 현업 확인되었습니다. 후속 개선 및 지표 측정용으로 **[추가 생성 데이터, 개발 중]** WM-811K 분포 기반 추가 생성 anchor 셋 (9,250 wafer / 43 defect class + Normal) 에서 보조 metric 을 확인하고 있고, 최종 recipe 에서 capture 43/43, ARI 0.859 ± 0.018 까지 도달한 수준입니다. ROI YOLO 의 한계를 보완하기 위한 chip-CNN 결과를 wafer 좌표 보정 지도 (object-id map) 로 재구성하는 2차 보정 구조 역시 **[추가 생성 chip 데이터, 개발 중]** 기준 V3 obj-only chipgrid val_f1 0.9946 / test_f1 0.9872, 5-seed 평균 val_f1 0.9838 ± 0.0092 로 추가 개발하고 있습니다.

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

알고리즘은 다음 3단계 logic flow 로 구성했고, 각 단계마다 도메인 특성에 맞춰 모델 아키텍처를 선정했습니다.

**(1) Stage 1 Backbone 선정 — ConvNeXtV2**

Transformer 와 CNN 계열을 비교 평가했습니다. ViT, Swin 같은 Transformer 계열은 wafer 전체 구조를 보는 전역 attention 에 강점이 있으나, 본 과제의 결함은 특정 zone 이나 국소 영역에 나타나는 경우가 많아 CNN 계열의 sliding-window 기반 지역 특징 추출이 더 적합하다고 판단했습니다. 동일한 weighted F1 0.87 을 보이는 MaxViT 와 비교하더라도 ConvNeXtV2 가 파라미터 26% 감소 (119.5M → 88.6M), FLOPs 39% 감소 (74.2G → 45.1G) 로 양산 운영 inference 비용 측면에서 효율적이어서 최종 backbone 으로 채택했습니다. 백본 선택 비교표 (ViT 0.81 / Swin 0.84 / EffNetV2 0.85 / MaxViT 0.87 / ConvNeXtV2 0.87) 도 동일 결론으로 수렴했습니다.

**(2) Stage 2 ROI 보정 — YOLO**

Stage 1 만으로는 center 영역 chip 분포가 유사한 class (center scratch ↔ center scratch_rot 등) 가 혼동되는 한계가 있었습니다. 이를 보완하기 위해 wafer 안의 ROI 영역에서 chip 단위 bounding box 와 class 라벨을 다수 출력해 종합 판단하는 ROI YOLO 보정 stage 를 결합했습니다. 단일 wafer-level prediction 의 confidence 가 gate 보다 낮을 때만 ROI 단계로 넘어가는 cascade 구조로, throughput 손실은 최소화하면서 헷갈리는 class 의 분리력만 선택적으로 보강했습니다. 이 2-stage 조합으로 weighted F1 0.92 → 0.95 로 향상했습니다.

**(3) 후속 보정 — chip-CNN object-id map 재구성 (개발 중)**

ROI YOLO 는 box prediction throughput 과 class 확장성에 한계가 있어, 후속으로 chip-CNN 결과를 wafer 좌표계로 재구성하는 object-id map 보정 구조를 개발하고 있습니다. chip 단위 defect class 를 grid 32×32 의 one-hot 채널에 매핑하면, raw map 에서는 비슷해 보이는 wafer 도 object-id map 으로는 center 영역 결함이 즉시 식별됩니다.

```
[Input wafer image]
        ↓
[ConvNeXtV2 wafer classifier]
        ↓ confidence < gate
[ROI YOLO refinement]
        ↓
[Known class prediction]
```

학습/평가에 사용된 실제 wafer 이미지 예시 (2행 3열, 좌측부터):

| Edge-Top Scratch | Edge-Ring Scratch_rot | Center Bank-Boundary (신규) |
|:----------------:|:---------------------:|:---------------------------:|
| <img src="./figures/wafer_edge_top_scratch.png" width="180" /> | <img src="./figures/wafer_edge_ring_scratch_rot.png" width="180" /> | <img src="./figures/wafer_center_bank_boundary.png" width="180" /> |
| **BrokenRing** | **RingDots** | **CrescentArc (신규)** |
| <img src="./figures/wafer_brokenring.png" width="180" /> | <img src="./figures/wafer_ringdots.png" width="180" /> | <img src="./figures/wafer_crescentarc.png" width="180" /> |

ROI YOLO 2-stage 보정 흐름은 다음 도식과 같습니다. GT 가 center scratch 인 wafer 가 Stage 1 wafer-level CNN 만으로는 center scratch_rot 으로 오인 분류되지만, Stage 2 ROI YOLO 가 chip 단위 bounding box 와 class 라벨을 다수 출력해 최종 정확한 class 로 보정합니다.

| Stage 1 (raw wafer) | Stage 2 ROI 영역 | Stage 2 chip 단위 box + class |
|:-------------------:|:----------------:|:-----------------------------:|
| <img src="./figures/wafer_center_scratch.png" height="280" /> | <img src="./figures/p1_roi_crop_real.png" height="280" /> | <img src="./figures/p1_chip_yolo_box_real.png" height="280" /> |

표 좌측은 GT = center scratch 인 raw wafer 입력으로, Stage 1 wafer-level CNN 만 보면 center scratch_rot 으로 오인 분류됩니다. 표 우측은 Stage 2 ROI YOLO 의 chip 단위 bounding box + class 라벨 출력으로, 다수 chip 의 예측을 종합해 최종 center scratch 로 정확히 보정합니다.

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

chip-CNN object-id map 재구성 결과는 raw wafer map 으로는 center 영역 분포가 비슷해 즉시 구분하기 어려운 두 class 가, object-id map 에서는 chip 단위 defect 분포 패턴이 즉시 식별되는 효과를 보여줍니다. 좌측 두 칸이 raw wafer map (center bank-boundary / center scratch_rot), 우측 두 칸이 **동일 wafer** 의 chip-CNN object-id map 입니다.

<table>
  <thead>
    <tr>
      <th colspan="2" align="center" style="text-align:center">raw wafer map</th>
      <th colspan="2" align="center" style="text-align:center">chip-CNN obj-id map</th>
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

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[실전 현업 데이터]** | Known 2-stage | weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split) |
| **[실전 현업 데이터]** | Known 단계별 개선 | 0.78 (baseline) → 0.87 (ConvNeXtV2 backbone) → 0.92 (+Optuna) → **0.95** (+ROI YOLO 2-stage) |
| **[실전 현업 데이터]** | Unknown 실전 운영 확인 | 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 7개 실제 불량 확인 |
| **[양산 운영]** | 운영 파이프라인 | 일 약 2만 장 wafer / 1시간 주기 적재 |
| **[양산 운영]** | 데이터 처리 | Cython hex-to-grade 약 **100배** 가속, 32-color palette PNG 약 **75%** 저장 절감 |
| **[양산 운영]** | Web App | 12일 누적 **2,317 요청**, peak 1,801 요청 (2026-03-07) |
| **[추가 생성 데이터, 개발 중]** | Unknown 후속 개선 및 지표 측정용 보조 metric | baseline 대비 최종 recipe 에서 ARI 0.859 ± 0.018, Completeness 0.9938, Homogeneity 0.9424, defect class capture 43/43, noise 1.48%. 후처리 (noise 임계 τ=0.5) 로 noise 0.00%, ARI 0.868 ± 0.013. cross-anchor 평가에서는 capture 38/38, ARI 0.4437 로 도메인 shift 영향 확인. |
| **[추가 생성 chip 데이터, 개발 중]** | chip-CNN object-id map 보정 구조 | V3 obj-only chipgrid 32×32×5 one-hot 기준 val_f1 **0.9946**, test_f1 **0.9872**, 5-seed 평균 val_f1 **0.9838 ± 0.0092**. ROI YOLO 의 한계를 보완하기 위한 wafer 좌표 보정 지도 (object-id map) 재구성 구조로 개발 중. |

**Unknown contrastive 구성요소 성능표 [추가 생성 데이터, 개발 중]**

| # | Recipe | P1 (capture) | P2 (noise %) | P3 (Completeness) | P4 (Homogeneity) | ARI | AMI | Sil |
|---|--------|--------------|--------------|-------------------|------------------|-----|-----|-----|
| 1 | B0 Global InfoNCE only | 1.000 | 6.20% | 0.9602 | 0.9290 | 0.823 | 0.929 | 0.582 |
| 2 | + Local DenseCL (LW=0.5) | 1.000 | 3.93% | 0.9665 | 0.9351 | 0.851 | 0.939 | 0.514 |
| 3 | + MoCo Queue 4096 | 1.000 | 1.31% | 0.9828 | 0.9365 | 0.846 | 0.950 | 0.573 |
| 4 | + NV-Retriever NEG 0.72 | 1.000 | 0.52% | 0.9852 | 0.9439 | 0.861 | 0.956 | 0.611 |
| 5 | + NeCo 0.2 (full 구성) | 1.000 | 0.96% | 0.9801 | 0.9403 | 0.8564 | 0.9503 | 0.6104 |
| 6 | 최종 recipe (Local DenseCL 제외 4-tool) | 1.000 | 1.48% | 0.9938 | 0.9424 | 0.859 ± 0.018 | 0.960 | 0.781 |
| 7 | 최종 recipe + 후처리 (noise 임계 τ=0.5) | 1.000 | 0.00% | 0.9938 | 0.9424 | 0.868 ± 0.013 | 0.960 | 0.781 |

컬럼 정의: P1 capture (defect-class recall, ↑) / P2 noise % (defect-only HDBSCAN noise 비율, ↓) / P3 Completeness (sklearn completeness_score, ↑) / P4 Homogeneity (sklearn homogeneity_score, ↑) / 보조 ARI / AMI / Silhouette 점수. 단계별 구성요소 누적으로 보면 noise % 는 6.20% → 3.93% → 1.31% → 0.52% → 0.96% 로 감소하며 (Local DenseCL, MoCo Queue, NV-Retriever NEG 가 주된 기여), Completeness 는 0.9602 → 0.9852 까지 단조 개선됩니다. 최종 recipe 와 후처리 측정값은 3-seed 평균 기준이며, 후속 검증 중입니다.

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
| 1 | 본인 | 개인정보 입력란 | 개인정보 입력란 | FCM-PM 합성 및 손실 마스킹 구조 신규 적용, val_margin 기준 도입, KD 압축 후보 검증, 학습·평가 운영 | 80% |
| 2 | 관리자 | 개인정보 입력란 | 개인정보 입력란 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

P2 의 주요 기여는 FCM-PM 을 본 과제 데이터 특성에 맞게 신규 적용한 점입니다. 본인은 chip 내부 defect 위치를 사전에 알 수 없는 조건에서 일반 CutMix 가 defect signal 을 잘라낼 수 있다는 한계를 인지하고, `CutMix 선정 → CutMix + Pair Mask 로 background loss 제외 → Full-Cover Mixup + Pair Mask 구성` 순서로 방법을 확장했습니다.

알고리즘은 다음 3단계 logic flow 로 데이터 합성 구조를 단계적으로 확장했고, 각 단계마다 본 과제 데이터 특성에 맞춘 선택 사유를 두었습니다.

**(1) CutMix 계열 선정 — Mixup 계열 대신 양자화 의미 보존**

Grade 0-7 양자화 chip 이미지를 다루는 본 과제에서는 픽셀값이 중간 색으로 섞이는 Mixup / Diffusion 계열은 사용할 수 없습니다. 합성 결과의 픽셀값이 실재하지 않는 grade 가 되어 분류기 학습에 노이즈로 작용하기 때문입니다. 영역 단위로 잘라 붙이는 CutMix 계열만이 양자화 의미를 보존하면서 multi-label 학습 신호를 만들 수 있다고 판단해 CutMix 를 baseline 으로 채택했습니다.

**(2) Pair Mask 결합 — background loss 제외로 negative 오학습 차단**

CutMix 단독은 합성된 chip 의 background 영역까지 defect class 로 학습 신호가 흘러 Normal / Invalid / OOD negative 에서 false-positive 가 100% 까지 치솟는 한계가 있었습니다. 이를 해결하기 위해 합성 단계에서 어느 영역이 background 인지 추적하는 Pair Mask 를 결합해, loss 계산 시 background 영역을 제외하는 구조를 적용했습니다. 이로써 background 를 defect 로 오학습하는 문제가 차단됩니다.

**(3) Full-Cover Mixup 확장 — chip 내부 defect 위치 미지 조건 반영**

일반 CutMix 는 chip 의 일부 영역만 잘라 붙이는 방식이라 defect signal 이 잘릴 위험이 있습니다. chip 내부 어느 위치에 defect 가 올지 사전에 알 수 없는 본 과제의 특성을 합성 단계에 반영하기 위해 chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장하고, 위 (2) 의 Pair Mask 와 결합해 FCM-PM (Full-Cover Mixup + Pair Mask) 합성 구조를 본 과제에 신규 적용했습니다.

학습·평가 운영 측면에서는 val_margin 기준을 도입해 작은 validation set 에서 val_f1 plateau 로 checkpoint 선택이 흔들리는 문제를 줄였으며, KD single student 로 1× inference cost 압축 후보를 함께 확인했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | chip 내부 defect 위치를 사전에 알 수 없고, single defect chip 을 조합해 multi-label 평가로 확장해야 합니다. |
| 기존 방식의 한계 | 일반 CutMix 는 일부 영역만 잘라 붙이므로 defect signal 이 잘릴 수 있습니다. background 영역까지 defect 로 학습하면 Normal / Invalid / OOD negative 에서 false-positive 가 증가합니다. |
| 기술적 / 환경적 제약 | multi-label 조합 label 부족, 작은 validation set, OOD / negative false-positive 억제, 압축 후보의 inference cost 제약이 동시에 존재했습니다. |

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

학습 single 4 class 예시 chip (좌측부터 bank_boundary / fork / scratch / scratch_rot):

<p align="left">
  <img src="./figures/chip_eval_bank_boundary_selected.png" width="160" />
  <img src="./figures/chip_eval_fork_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_rot_selected.png" width="160" />
</p>

2-combo 합성 예시 chip 6종 (single 4 class 의 모든 2-조합, 좌측부터 bb+fork / bb+scratch / bb+scratch_rot / fork+scratch / fork+scratch_rot / scratch+scratch_rot):

<p align="left">
  <img src="./figures/chip_combo_bb_fork_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_scratch_scratch_rot_selected.png" width="130" />
</p>

Normal / Invalid / OOD negative 평가셋 예시 (좌측부터 Normal / Invalid / OOD-Starburst / OOD-CenterDonut / OOD-CrossScratch / OOD-DiagonalSmear):

<p align="left">
  <img src="./figures/chip_eval_normal_selected.png" width="130" />
  <img src="./figures/chip_eval_invalid_selected.png" width="130" />
  <img src="./figures/chip_ood_starburst_selected.png" width="130" />
  <img src="./figures/chip_ood_centerdonut_selected.png" width="130" />
  <img src="./figures/chip_ood_crossscratch_selected.png" width="130" />
  <img src="./figures/chip_ood_diagonalsmear_selected.png" width="130" />
</p>

val_margin 은 chip 한 장에서 모델이 출력하는 bit 별 score 를 두 그룹으로 나눠 차이를 본 신호입니다. positive bit (실제 결함이 있는 bit) 의 평균 score 와 negative bit (정상 bit) 의 최대 score 의 차이로 정의했습니다.

```
       [chip image]
            ↓
    [classifier 출력 bit score]
            │
   ┌────────┴────────┐
   ▼                 ▼
positive bits     negative bits
(실제 결함)        (정상 bit)
   │                 │
 평균 score        최대 score  ← false-positive 위험점
   │                 │
   └────────┬────────┘
            ▼
   val_margin = 평균(positive) - 최대(negative)
            ↓
   클수록 결함과 정상 분리가 안정적
```

이렇게 정의한 이유는 다음 두 가지입니다.

첫째, validation set 이 작으면 val_f1 이 여러 epoch 에서 같은 값으로 plateau 가 되어 best epoch 이 흔들립니다. val_margin 은 score 평균과 최대의 차이라 plateau 구간에서도 미세한 변동이 살아 있어 best epoch 식별이 안정됩니다.

둘째, negative 측은 최대값을 사용했기 때문에 정상 bit 중 가장 결함처럼 보이는 케이스 (false-positive 위험점) 가 그대로 신호에 들어옵니다. val_f1 만 봤을 때 놓치는 운영 false-positive 위험을 best-model 선택 단계에서 자동으로 반영하게 됩니다.

운영 적용 시에는 val_f1 best 와 val_margin best 를 함께 보았고, 본 과제 데이터에서는 두 기준이 동일한 epoch 으로 수렴해 정합성을 확인했습니다.

**ㅁ 구현 성과**

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[추가 생성 chip 데이터, PoC]** | 평가셋 | single 4 + 2-combo 6 + Normal + Invalid + OOD 4 = **16+ class × 약 3,850 chip** 추가 생성 chip 데이터 기반 controlled synthetic benchmark |
| **[추가 생성 chip 데이터, PoC]** | FCM-PM 대표 모델 | bit F1 **0.9943**, Normal / Invalid / OOD negative 평가셋에서 false-positive 미검출 |
| **[추가 생성 chip 데이터, PoC]** | Pair Mask 제거 비교 | Pair Mask 미적용 시 Total FAR **100%** 의 운영 부적합 사례 확인. Pair Mask background loss masking 의 false-positive 억제 효과 확인 |
| **[추가 생성 chip 데이터, PoC]** | val_margin 기준 도입 | false-positive 위험까지 반영하는 best-model 선택 기준으로 적용 |
| **[추가 생성 chip 데이터, PoC]** | KD single student | 1× inference cost 압축 후보로 검토 중이나, OOD 포함 Total FAR 리스크가 있어 제출 성과에서는 제외하고 후속 개선 대상으로 분리 관리합니다. |

**Multi-label 합성 학습 recipe 성능표 [추가 생성 chip 데이터, PoC — n=2000/class 평가 / 16+ class 평가셋]**

| # | Recipe | bit_F1 | single | 2combo | FAR | NI-FAR | OOD-FAR | Note |
|---|--------|--------|--------|--------|------|--------|---------|------|
| 1 | Baseline (BCE+LS, no cutmix) | 0.1093 | 0.1662 | 0.0652 | 99.47% | 99.65% | 98.91% | Baseline 단독 학습은 검증 단계에서 수렴 실패 (best val 0.676, bit_F1 chance 수준). CutMix 미적용 시 margin_max 학습 실패 사례 |
| 2 | Focal loss (sigmoid focal, no cutmix) | 0.7980 | 0.7981 | 0.3987 | 45.72% | 35.55% | 77.50% | Focal loss 단독으로도 추가 하이퍼파라미터 조정에 따라 Total FAR 0.08% 까지 도달 가능 (FAR 최저 사례). CutMix 미적용 |
| 3 | ASL (asymmetric, label smoothing 0, no cutmix) | 0.6435 | TBD | TBD | 100.0% | 100.0% | 100.0% | 최신 ladder final 기준 negative rejection 실패. single / 2combo 분해는 후속 검증 중 |
| 4 | CutMix only (random rect, no pair) | 0.9359 | TBD | TBD | 42.05% | 37.00% | 57.81% | CutMix 도입으로 bit_F1 은 회복되나, Pair Mask 미적용 시 background 영역까지 defect 로 오학습되어 FAR 이 운영 부적합 수준으로 남음 |
| 5 | CutMix + Pair (random rect + masked) | 0.9256 | 0.7851 | 0.3221 | 100.0% | 100.0% | 100.0% | bit-level 학습 (bb 0.9848) 은 강화되나 단일 sigmoid 임계 셀로 수렴해 negative rejection signal 부재. Full-Cover Mixup 까지 결합한 FCM-PM 의 필요성 확인 사례 |
| 6 | FCM-PM val_f1 criterion (run116J ep1) | 0.9422 | TBD | TBD | 0.00% | TBD | TBD | 같은 recipe 에서 val_f1 기준 checkpoint 선택 사례 |
| 7 | FCM-PM val_margin criterion (run116J ep6) | 0.9943 | TBD | TBD | 0.00% | 0.00% | 0.00% | val_margin 기준 대표 모델 |
| 8 | 4-bag majority 2/4 ensemble | 0.9167 | TBD | TBD | 4.05% | 4.10% | 3.91% | ensemble 보조 실험. FCM-PM 단일 대표 모델보다 낮아 주 성과로 쓰지 않음 |
| 9 | KD distill 4-bag → student | TBD | TBD | TBD | TBD | TBD | TBD | 1× inference cost 압축 후보. OOD 포함 Total FAR 리스크로 후속 검증 중 |

표는 학습 단계별 비교 측정을 정리한 것입니다. Baseline / Focal 의 single / 2combo 는 추가 측정으로 보강했고, KD distill student 는 제출 성과에서 제외하고 후속 검증 중인 압축 후보로만 관리합니다. 단계별 비교 요약: CutMix 단독은 bit_F1 은 회복되나 FAR 기준으로는 운영 부적합했고, FCM-PM + val_margin 에서 bit_F1 0.9943 / Total FAR 0.00% 로 균형이 개선되었습니다.

추가 보조 확인 [추가 생성 chip 데이터, PoC]: Pair Mask 변형 2종 (Complement + Pair Mask, Single Pair Mask) 도 bit_F1 0.8743 / Total FAR 100% 로 negative false-positive 를 억제하지 못해, Full-Cover Mixup 과 Pair Mask 의 결합 (FCM-PM) 이 필요한 이유를 보조 확인했습니다.

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
| 1 | 본인 | 개인정보 입력란 | 개인정보 입력란 | trend episode 합성 generator 설계, Region / Noise / 일반 trend 4종 + context 1종 코드화, 생성 데이터 학습 가능성 검증 | 80% |
| 2 | 관리자 | 개인정보 입력란 | 개인정보 입력란 | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

P3 의 주요 기여는 데이터 생성입니다. 본인은 BBD/Overlay/CD 현업 경험에서 형성된 trend 도메인 지식을 synthetic trend episode generator 의 parameter 로 코드화했습니다. Binary gate + Type classifier 는 생성 데이터가 정상 / 이상 패턴을 학습 가능하게 담고 있는지 확인하기 위한 검증용 baseline 입니다 (실전 운영 검증과 분리).

먼저 Region 5종으로 계측 밀도 차이를 코드화하고, Noise 3종으로 설비 산포·일시 튐·상관 drift 성격을 통계 noise 로 설계한 뒤, 일반 trend 불량 4종 mean shift / standard deviation change / spike / drift 와 context pattern 1종을 구성했습니다.

생성 데이터의 신뢰도 확보를 위해 fleet/target baseline 통계 기반 enforcement floor 로 이상 강도가 정상 산포에 묻히지 않도록 하한을 보장했고, target_std 를 fleet_within_std × 1.2 이내로 정렬해 합성 normal chart 의 통계 특성이 현업 정상 trend 판단 기준에 가까워지도록 보정했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 함께 봐야 합니다. |
| 기존 방식의 한계 | 실전 trend abnormal data 는 충분한 양과 균형 label 을 확보하기 어렵고, 수작업 chart 판독은 초보자 누락과 시간 소모가 큽니다. |
| 기술적 / 환경적 제약 | 실전 label 부족을 전제로, 먼저 현업 trend domain knowledge 를 학습 가능한 synthetic data 로 만드는 것이 핵심 과제입니다. |

**ㅁ 기술적 해결 방안**

알고리즘은 다음 3단계 logic flow 로 구성했고, 각 단계마다 본 과제 도메인 특성에 맞춘 선택 사유를 두었습니다.

**(1) 합성 generator 코드화 — 실전 label 부족 전제**

trend abnormal 데이터는 실전 운영에서 충분한 양과 균형 라벨을 확보하기 어렵습니다. 본인은 BBD / Overlay / CD 현업에서 형성한 trend 도메인 지식 (Region 별 계측 밀도, 설비 산포 / 헌팅 / drift 등 통계 noise, 일반 trend 불량 4종 + context pattern 1종) 을 episode generator 의 parameter 로 코드화해 학습 가능한 데이터 자산으로 만드는 것을 알고리즘 1단계로 두었습니다. 이 단계가 본 과제의 핵심 알고리즘 기여입니다.

**(2) 정상성 보장 — fleet/target baseline 기반 enforcement floor**

합성 데이터가 실전에 가깝게 보이려면 정상 chart 의 통계 특성이 실재 baseline 과 일치해야 하고, 이상 강도는 정상 산포에 묻혀버리면 안 됩니다. target_std 를 fleet_within_std × 1.2 이내로 정렬해 합성 normal chart 의 통계 분포를 실전에 맞췄고, fleet_std 기반 enforcement floor 로 이상 강도에 하한을 보장해 ABNORMAL 사례가 noise 안에 숨지 않도록 설계했습니다.

**(3) 학습 가능성 검증 — Binary gate + Type classifier baseline**

위 합성 데이터가 정상 / 이상 패턴을 실제로 학습 가능한 형태로 담고 있는지 검증하기 위해 2단계 baseline 분류기를 구성했습니다. 1차 Binary gate 는 정상 / 이상 판정 신호의 명확성을 검증하고, 2차 Type classifier 는 5종 (4 + context) 분류로 세부 패턴까지 분리 가능한지 확인합니다. 두 baseline 은 모델 차별성을 주장하는 운영 후보가 아니라 합성 데이터 학습 가능성을 점검하기 위한 검증 도구로 분리해 보고합니다.

P3는 현업 trend 통계와 불량 발생 양상을 synthetic generator 로 코드화한 과제입니다.

```
[BBD / Overlay / CD 현업 trend 경험]
        ↓
[Region 5종: dense / sparse / very_sparse / thin / missing]
        ↓
[Noise 3종: Gaussian / Laplacian / correlated drift]
        ↓
[일반 trend 불량 4종 + context 1종]
        ↓
[fleet/target baseline 통계 기반 enforcement floor]
        ↓
[224×224 trend chart PNG rendering]
        ↓
[검증용 baseline 학습: Binary gate + Type classifier]
        ↓
[생성 데이터 학습 가능성 확인]
```

합성 trend chart 예시 (정상 + 일반 trend 불량 4종 + context pattern 1종):

| Normal | Mean Shift | Standard Deviation Change |
|:------:|:----------:|:-------------------------:|
| <img src="./figures/trend_normal.png" width="200" /> | <img src="./figures/trend_mean_shift.png" width="200" /> | <img src="./figures/trend_standard_deviation.png" width="200" /> |
| **Spike** | **Drift** | **Context** |
| <img src="./figures/trend_spike.png" width="200" /> | <img src="./figures/trend_drift.png" width="200" /> | <img src="./figures/trend_context.png" width="200" /> |

생성 데이터 검증 파이프라인의 checkpoint 안정화를 위해, 일시적 spike 에 선택이 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 구성했습니다.

**ㅁ 구현 성과**

_데이터 생성 그룹 (주 성과)_

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[합성 trend chart, PoC]** | 시나리오 구성 | train 7,000 + val 1,500 + test 1,500 = 총 10,000 scenarios |
| **[합성 trend chart, PoC]** | test 평가셋 | normal 750 + abnormal 5종 각 150 = 총 **1,500 sample** |
| **[합성 trend chart, PoC]** | Region 코드화 | `dense` 70-100%, `sparse` 40-70%, `very_sparse` 20-35%, `thin` 10-20%, `missing` 0% |
| **[합성 trend chart, PoC]** | Noise 코드화 | Gaussian 0.80, Laplacian 0.15, correlated drift 0.05 |
| **[합성 trend chart, PoC]** | trend 불량 코드화 | mean_shift / std / spike / drift 4종 + context 1종 |
| **[합성 trend chart, PoC]** | chart rendering | 224×224 chart PNG, 12-25 episode mix |

_검증용 baseline 학습 그룹 (생성 데이터 학습 가능성 확인)_

아래 baseline 수치는 위 데이터 생성 그룹이 학습 가능한 자산인지 확인한 부속 검증입니다.

| 라벨 그룹 | 구분 | 성과 |
|-----------|------|------|
| **[합성 trend chart, PoC]** | 1차 Binary gate | test split 1,500건, normal_threshold=0.9 기준 Binary F1 **0.9967**, Abnormal Recall **0.9987**, TN/FN/FP/TP=746/1/4/749. 생성 데이터 학습 가능성 확인용 참고 수치입니다. |
| **[합성 trend chart, PoC, 개발 중]** | 2차 Type classifier | mean_shift ↔ drift 혼동 등으로 type-level accuracy 는 추가 개발 중 (1차 binary 안정성과 분리하여 보고합니다) |

BBD/Overlay/CD trend 판단 기준을 synthetic data generator 로 코드화해, 실전 label 부족 상황에서도 AI 검증을 시작할 수 있는 데이터 기반을 마련했습니다.
