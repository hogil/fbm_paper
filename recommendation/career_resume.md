## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|------------------------|
| Computer Vision | Failbit Map wafer 이미지 처리, chip 이미지 처리, 결함 pattern 인식 |
| Image Classification | ConvNeXtV2 기반 wafer-level single-label classification, chip-level classification, chip multi-label classification |
| Object Detection | ROI YOLO 기반 저신뢰 wafer sample 보정, region-of-interest defect localization |
| Self-Supervised Learning | Unknown pattern detection 을 위한 contrastive representation learning, Task-Adaptive Pre-training (TAPT), InfoNCE, MoCo Queue, hard-negative mining |
| Clustering / Unsupervised Learning | HDBSCAN 기반 unknown 후보 grouping, ARI / class capture / cross-anchor robustness check |
| Synthetic Data Generation | wafer-class 생성 평가셋, chip multi-label synthesis, trend episode synthesis generator |
| Data Engineering | EDS Test raw log → S3 → fail-map → mapviewer 적재, Failbit Map 생성·저장·조회, chip 좌표 / 측정값 JSON 생성 |
| MLOps | FastAPI backend, JavaScript frontend, WebGL2 rendering, RBAC, SAML Single Sign-On, 이미지 분석 AI 결과의 Web App 표시 |
| High-Performance Computing | Cython hex-to-grade conversion, pyvips / Numba 기반 이미지 처리, 32-color palette-indexed PNG encoding, PLTE chunk patch |
| Model Optimization | Bayesian Hyperparameter Optimization (Optuna), Focal Loss, Label Smoothing, Temperature Scaling, val_margin / best-margin checkpoint selection |
| Model Compression | 4-bag ensemble 성능 상한 검증, Knowledge Distillation single-model compression, 1× inference cost 운영 후보 검증 |

## 2. 업무경력

본인의 결정적 차별성은 **반도체 역량을 AI 모델 또는 AI 학습 데이터 생성 체계에 직접 반영해 현업 문제를 개선** 하는 흐름이며, 아래 3개 과제는 모두 이 기준에 맞춰 수행했습니다.

ㅁ **P1. Failbit Map AI 분류 시스템 (Known 2-stage + Unknown contrastive)**

본 과제는 Failbit Map 데이터 파이프라인부터 Web App, Known 2-stage 분류, Unknown 검출까지 하나의 운영 흐름으로 구성한 시스템 과제입니다.

- 과제 개요 및 규모: DRAM 전제품 라인의 Failbit Map 데이터 파이프라인, mapviewer Web App, Known 2-stage AI 분류기, Unknown self-supervised 검출기 통합 시스템입니다.
- 운영 상태: 데이터 파이프라인과 Web App 은 **[양산 운영]**, Known 2-stage 는 **[실전 현업 데이터, 검증 완료]**, Unknown 검출은 **[실전 운영 적용 및 현업 확인]**, chip-CNN object-id map 보정 구조는 **[추가 생성 데이터, 개발 중]** 입니다.
- 담당 역할: 본인 70% / 현업 엔지니어 20% / 관리자 10% 입니다.
- 수행 업무: Cython hex-to-grade 변환, 32-color palette-indexed PNG 저장, mapviewer 운영, ConvNeXtV2 backbone 선정 및 hyperparameter optimization, ROI YOLO 2-stage 보정, Unknown self-supervised embedding 및 HDBSCAN grouping, chip-CNN → wafer 좌표계 object-id map 기반 Stage 2 보정 구조 개발을 수행했습니다.
- 성과: **[실전 현업 데이터]** Known weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split) 를 달성했습니다.
- 성과: **[실전 현업 데이터]** Unknown 은 5일 운영 데이터 10,000장 학습 + 별도 1일 운영 데이터 2,000장 적용 결과 13 후보 중 7개 실제 불량을 현업 확인받았습니다. 이 항목은 정량 metric 이 아니라 실전 운영 확인 근거입니다.
- 성과: **[추가 생성 데이터, 개발 중]** Unknown self-supervised PoC 는 합성 wafer 데이터에서 label 을 학습에 사용하지 않는 contrastive embedding / HDBSCAN 구조로 보조 지표를 확인했습니다. same-anchor 기준 ARI **0.8588±0.018**, class capture **1.000 (43/43)**, cross-anchor 기준 ARI **0.4437** 로 분포 변화에 따른 일반화 risk 도 함께 확인했습니다. 이는 실전 운영 성과가 아니라 추가 생성 데이터 기반 개발 지표입니다.
- 성과: **[양산 운영]** EDS Test → S3 → fail-map → mapviewer 1시간 주기 적재, 일 약 2만 장 wafer 처리, Cython hex-to-grade 약 **100배** 가속, 32-color palette PNG 저장 용량 약 **75%** 절감, 사내 failbitmap 서비스 12일 누적 **2,317 요청** (peak 1,801, 2026-03-07) 을 확인했습니다.
- 성과: **[추가 생성 데이터, 개발 중]** chip 분류기 보조 개발 지표는 추가 생성 chip 데이터 **1.16M** 기준 val_f1 **0.9946** / test_f1 **0.9872** / 5-seed **0.9838±0.0092** 입니다. 이는 2-stage 통합 성과가 아니라 chip 분류기 단독 개발 지표입니다.

**과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본 과제 도메인은 Failbit Map, DRAM EDS Test Grade 0-7 양자화 이미지, wafer-level defect zone 해석, 대량 wafer image operating pipeline 입니다. 이 도메인 위에 Computer Vision, Object Detection, Self-Supervised Representation Learning, Clustering, MLOps / Data Pipeline Engineering 을 결합해 하나의 운영 흐름으로 구성했습니다. 핵심 모델·방법론으로는 ConvNeXtV2, ROI YOLO 2-stage refinement, ConvNeXtV2 TAPT, Global InfoNCE, MoCo Queue, hard-negative mining, HDBSCAN grouping, chip-CNN object-id map reconstruction, cross-anchor robustness check 를 채택했습니다.

Backbone 선정 과정에서는 Transformer 계열이 wafer 전체 구조를 보는 데 강점이 있으나, 본 과제의 결함이 특정 zone 또는 국소 영역에 나타나는 경우가 많다는 점을 고려해 CNN 계열 ConvNeXtV2 의 sliding-window 기반 지역 특징 추출이 더 적합하다고 판단했습니다. 실제 비교 (ViT 0.81 / Swin 0.84 / EffNetV2 0.85 / MaxViT 0.87 / ConvNeXtV2 0.87 / +Optuna 0.92 / +ROI 0.95) 에서 ConvNeXtV2 는 MaxViT 와 동일한 weighted F1 0.87 을 보이면서 파라미터 **26% 감소 (119.5M → 88.6M)** 와 FLOPs **39% 감소 (74.2G → 45.1G)** 로 효율이 높아 최종 backbone 으로 선정했습니다.

ㅁ **P2. Chip Multi-label Classification (CutMix → CutMix + Pair Mask → FCM-PM)**

본 과제는 chip 단위 multi-label classification 의 합성 데이터 한계를 단계적으로 풀어가며 FCM-PM 합성 및 손실 마스킹 구조를 본 과제에 맞게 신규 적용한 PoC 입니다.

- 과제 개요 및 규모: chip multi-label classification PoC 입니다. 학습은 single 4 class 에서 시작하고, 평가는 single 4 + 2-combo 6 + Normal + Invalid + OOD 4 로 구성한 **16+ class × 약 3,850 chip** 생성 평가셋으로 수행했습니다. 실전 양산 데이터 검증이 아니라 controlled synthetic benchmark 입니다.
- 운영 상태: **[추가 생성 chip 데이터, PoC, 양산 적용 후보 검증 중]** 입니다.
- 담당 역할: 본인 90% / 관리자 10% 입니다.
- 수행 업무: CutMix 계열 선정, CutMix + Pair Mask background loss masking, FCM-PM (Full-Cover Mixup + Pair Mask) 합성 및 손실 마스킹 구조의 본 과제 신규 적용, val_margin / best-margin checkpoint selection, Label Smoothing, Temperature Scaling, 4-bag ensemble 성능 상한 검증, Knowledge Distillation single-model compression 을 수행했습니다.
- 성과: **[추가 생성 chip 데이터, PoC]** FCM-PM 대표 모델 bit F1 **0.9943**, Normal / Invalid / OOD negative false-positive **0건**을 확인했습니다.
- 성과: Pair Mask 제거 시 FAR **100%** 로 전면 오판되어, FCM-PM 의 background loss masking 이 성패를 가르는 핵심 장치임을 확인했습니다.
- 성과: val_margin 은 eval bit F1 과 Spearman ρ **+0.56** 으로 정렬되어 val_f1 (ρ **-0.10**) 대비 best-model 선택 신호를 개선했습니다.
- 성과: 4-bag ensemble 은 bit F1 **0.9953** / FAR **0.00%** 로 성능 상한을 확인했고, KD single student 는 bit F1 **0.9872** / FAR **0.5%** 로 1× inference cost 운영 후보를 확보했습니다.

**과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본 과제 도메인은 Grade 양자화 chip image, chip 내부 defect 위치를 사전에 알 수 없는 특성, multi-label defect co-occurrence 입니다. 이에 따라 Multi-label Image Classification, Synthetic Data Engineering, Machine Learning Optimization, Knowledge Distillation 을 결합했고, 구체 모델·방법론으로 CutMix 와 CutMix + Pair Mask 를 거쳐 FCM-PM (Full-Cover Mixup + Pair Mask) 을 본 과제에 신규 적용했으며, Pair Mask background loss masking, val_margin / best-margin checkpoint selection, Label Smoothing, Temperature Scaling, 4-bag ensemble, single student distillation 까지 함께 구성했습니다.

기술 판단으로는 일반 CutMix 가 일부 영역만 잘라 붙이는 방식이라 chip 내부 defect 위치를 사전에 알 수 없는 본 과제에서는 defect signal 이 잘릴 수 있다는 점을 인지했고, chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장하면서 합성 background 를 loss 에서 제외하는 Pair Mask 를 결합해 multi-label 오탐을 억제했습니다.

ㅁ **P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

본 과제는 BBD/Overlay/CD 현업에서 형성한 trend 도메인 지식을 합성 episode generator 로 코드화하여 AI 학습이 가능한 데이터 자산으로 만드는 데이터 생성 중심 과제입니다.

- 과제 개요 및 규모: **데이터 생성이 주 성과인 과제**입니다. BBD/Overlay/CD 현업 경험에서 형성된 trend 도메인 지식을 episode synthesis generator 로 코드화하고, Region 5종 / Noise 3종 / 일반 trend 불량 4종 + context 1종 / Fleet enforcement floor 를 직접 설계했습니다.
- 운영 상태: **[합성 trend chart, PoC]** 이며, 실전 현업 데이터 검증은 미실시입니다.
- 담당 역할: 본인 90% / 관리자 10% 입니다.
- 수행 업무: Region 5종 계측 밀도 코드화, Noise 3종 설비 모드 매핑, trend 불량 5종 형상 카탈로그, fleet_std 비례 anomaly 강도 하한 보정, 정상 / 이상 trend episode 생성, 생성 데이터 검증용 baseline 학습 안정화를 수행했습니다.
- 성과: **[합성 trend chart, PoC]** normal 750 + abnormal 5종 각 150 = 총 **1,500 sample** 합성 trend chart 평가셋을 생성했습니다.
- 성과: 1차 Binary gate 는 Binary F1 **0.9967**, Abnormal Recall **0.9987**, 5-seed sweep **0.9944~0.9988** 로 안정 수렴 (TN 746 / FN 1 / FP 4 / TP 749). 2차 Type classifier 는 mean_shift ↔ drift 혼동 등으로 type-level accuracy 가 추가 개발 중이며, 1차 / 2차 단계를 분리해 보고합니다. 위 수치는 모델 차별성 주장이 아니라 **생성 데이터가 정상 / 이상 패턴을 학습 가능하게 담고 있는지 확인한 참고 수치**입니다.

**과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본 과제 도메인은 BBD/Overlay/CD trend 해석 경험, 설비 산포, 설비 hunting, 미세 drift, baseline 평탄도, spec-in 변동 사고 가능성입니다. 이에 맞춰 Synthetic Data Engineering, Time-series / Trend Episode Simulation, Baseline Model Validation 을 결합했습니다. 구체적으로는 계측 밀도를 `dense` / `sparse` / `very_sparse` / `thin` / `missing` 5단계로 코드화하고, 설비 산포 / hunting / drift 를 `Gaussian` / `Laplacian` / `correlated drift` 3 가지 통계 분포로 매핑한 뒤, `mean_shift` / `std` / `spike` / `drift` / `context` 5종 trend 불량 형상을 구성했습니다. 여기에 fleet_std 기반 enforcement floor 로 이상 강도 하한을 보장했고, 검증용 baseline 학습은 val-F1 median smoothing 과 val-loss spike guard 로 수렴을 안정화했습니다.

P3의 본질은 특별한 anomaly detection model 이 아니라, 현업 trend 이상 양상을 AI 학습 데이터로 만들 수 있게 한 domain-knowledge-driven synthetic data generation 이라는 점을 기술 판단의 출발점으로 잡았습니다.
