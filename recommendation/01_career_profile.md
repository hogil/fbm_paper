## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|----------------|
| Computer Vision | Image Classification, Object Detection, Multi-label Classification, Feature Representation Learning, Image-based Defect Detection |
| Deep Learning | CNN Backbone Modeling, Transfer Learning, Fine-tuning, Loss Function Design, Regularization |
| Self-Supervised Learning | Contrastive Learning, Self-supervised Representation Learning, Embedding Learning |
| Unsupervised Learning | Clustering, Novelty Detection, Anomaly Detection, Out-of-Distribution Detection |
| Synthetic Data Generation / Data Augmentation | Synthetic Dataset Generation, Data Augmentation, Mixup, CutMix, Noise Injection |
| Model Optimization / Model Selection | Hyperparameter Optimization, Model Selection, Threshold Optimization, Calibration, Ensemble, Knowledge Distillation |
| Data Engineering / MLOps | ETL Pipeline, Batch Processing, Object Storage Integration, Model Evaluation Pipeline, Experiment Tracking |
| AI Application Engineering | Backend API, Web Application, Data Visualization, Access Control, Single Sign-On |

---

## 2. AI 주요 과제

> 본인의 결정적 차별성은 **반도체 역량을 AI 모델 또는 AI 학습 데이터 생성 체계에 직접 반영해 현업 문제를 개선** 하는 흐름이며, 아래 3개 과제 모두 같은 흐름으로 진행되었습니다.

| 과제명 | 과제 개요 및 규모 | 담당 역할 | 수행 업무 | 성과 / 검증 근거 | 과제 관련 도메인 / AI 기술 / 모델 / 방법론 |
|--------|---------------|-----------|----------|----------|-----------------------------------|
| **P1. Failbit Map AI 분류 시스템** | Failbit Map 파이프라인 / Web App [양산 운영], Known ROI YOLO 2-stage [실전 검증], Unknown 후보 검출 [실전 확인], chip-CNN obj-id map 보정 [추가 생성 데이터, 개발 중] | 본인 70% (데이터·Web App·Known/Unknown AI 모델 직접 설계·개발·검증) / 현업 엔지니어 20% (불량 교육·Unknown 7건 확인) / 관리자 10% | Cython hex-to-grade 변환, 32-color palette PNG 저장, mapviewer 운영, ConvNeXtV2 backbone 선정 및 HPO, ROI YOLO 2-stage 보정, Unknown self-supervised embedding 및 HDBSCAN grouping, chip-CNN → wafer 좌표계 obj-id map 기반 Stage 2 보정 구조 개발 | **[실전 현업 데이터]** Known weighted F1 0.95.<br>**[실전 현업 데이터]** Unknown 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 7개 실제 불량 현업 확인 (정량 metric 없음).<br>**[양산 운영]** 사내 failbitmap 서비스 12일 누적 2,317 요청.<br>**[추가 생성 데이터, 개발 중]** chip 분류기 보조 개발 지표 (2-stage 통합 성과 아님): val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838±0.0092 | ConvNeXtV2, ROI YOLO 2-stage, chip-CNN obj-id map 재구성, self-supervised pretraining, Global InfoNCE, MoCo Queue, NV-Retriever, NeCo, HDBSCAN, Cython |
| **P2. Chip multi-label classification** | FCM-PM (Full-Cover Mixup + Pair Mask) 합성 및 손실 마스킹 구조를 본 과제에 신규 적용한 chip multi-label 과제입니다. chip 내부 불량 위치를 사전에 알 수 없는 현업 특성을 반영해, 일부 영역만 자르는 기존 CutMix 한계를 보완하고 chip 전체 grid 를 cover 하는 Full-Cover Mixup + 합성 background loss 를 제외하는 Pair Mask 를 결합했습니다 (Pair Mask 제거 시 FAR 100%). 이후 val_margin checkpoint 선택, ensemble/KD 압축으로 운영 후보를 검증했습니다. **[추가 생성 데이터, PoC, 양산 적용 후보 검증 중]** | 본인 90% / 관리자 10% | CutMix 계열 선정, CutMix + Pair Mask background loss masking, FCM-PM 합성 및 손실 마스킹 구조의 본 과제 신규 적용, single 4 → 16+ multi-label / OOD 평가 구성, val_f1 → val_margin / best-margin checkpoint 선택 기준 전환, Label Smoothing 및 Temperature scaling 적용, 비대칭 pos/neg target (pt=0.95 / nt=0.30) sweep, 4-bag ensemble 성능 상한 확인, KD single-model 압축 | **[추가 생성 chip 데이터, PoC]** FCM-PM 대표 모델은 bit F1 **0.9943** (기존 요약 평가) / **0.9964** (per-class 2,000 갱신 평가)이며, Normal/Invalid/OOD negative 평가에서 false-positive **0건**을 확인했습니다. Pair Mask 제거 시 FAR **100%** 로 negative 전체 오탐이 발생해 background loss masking 이 주요 개선 요인임을 확인했습니다. val_margin 은 eval bit F1 과 Spearman ρ **+0.56** 으로 정렬되어 val_f1 (ρ **-0.10**) 대비 best-model 선택 신호를 개선했습니다. 4-bag ensemble 은 bit F1 **0.9953** / FAR **0.00%** 로 성능 상한을 확인했고, KD single 은 bit F1 **0.9872** / FAR **0.5%** 에서 1× 추론 후보를 확보했습니다. | Multi-label chip classification, CutMix, CutMix + Pair Mask, FCM-PM, Pair Mask background loss masking, val_margin / best-margin checkpoint 선택, asymmetric pos/neg target, Label Smoothing, Temperature scaling, 4-bag ensemble, Knowledge Distillation |
| **P3. Trend episode 데이터 생성 기반 Anomaly-detection** | **데이터 생성이 주 성과인 과제**입니다. BBD/Overlay/CD 현업 경험에서 형성된 trend 도메인 지식을 episode 합성 generator 로 코드화하고, Region 5종 / Noise 3종 / 일반 trend 불량 4종 + context 1종 / Fleet enforcement floor 를 직접 설계했습니다. **[합성 trend chart, PoC]** | 본인 90% / 관리자 10% | Region 5종, Noise 3종, 불량 5종 trend 합성 generator 설계, fleet_std 비례 anomaly 강도 하한 보정, 정상/이상 trend episode 생성, 생성 데이터 검증용 baseline 학습 안정화 (val-F1 median smoothing + val-loss spike guard), 생성 데이터 학습 가능성 확인용 Binary gate + Type classifier 검증 | **[합성 trend chart, PoC]** normal 750 + abnormal 5종 각 150 = 총 1,500 sample 합성 trend chart 평가셋을 생성했습니다. Binary F1 0.9967, Abnormal Recall 0.9987, 5-seed sweep 0.9944~0.9988 은 모델 차별성이 아니라 **생성 데이터가 이상/정상 패턴을 학습 가능하게 담고 있는지 확인한 참고 수치**입니다. 실전 현업 데이터 검증 미실시입니다. | Region 5종 계측 밀도 코드화, Noise 3종 설비 모드 매핑 (Gaussian(산포) / Laplacian(헌팅) / corr(drift)), 불량 5종 trend 형상 카탈로그, Fleet enforcement floor, 생성 데이터 검증용 baseline 학습 안정화 |

---

## 3. 포트폴리오

| # | 프로젝트 | 기간 | 내용 | 리딩 규모 | 담당 업무 | 관리 / 설계 / 개발 비중 |
|---|----------|------|------|-----------|----------|----------------------|
| P1 | Failbit Map AI 분류 시스템 (single-label Known + Unknown) | 2022년 ~ 현재 | fail-map 파이프라인, mapviewer, Known 2-stage, Unknown self-supervised 검출, chip-CNN → wafer 좌표계 obj-id map 기반 Stage 2 보정 구조 | DRAM 전제품 라인 운영 + 12일 누적 2,317 요청 + single-label 이미지 처리 AI 모델 PoC | 데이터 파이프라인 구축, Web App 운영, AI 모델 설계, 개발, 검증 | 관리 10% / 설계 40% / 개발 50% |
| P2 | Chip multi-label classification (CutMix → CutMix + Pair Mask → FCM-PM) | 2025년 ~ 현재 | FCM-PM 신규 적용, multi-label 평가셋 구성, Pair Mask 제거 비교, val_margin 기준 도입, ensemble/KD 운영화 후보 검증 | single 4 학습 → 16+ multi-label / OOD 평가 + FCM-PM 대표 모델 / 4-bag ensemble / KD 성능-비용 비교 | 합성 및 손실 마스킹 구조 구성, 학습 및 평가 체계 구축, 모델 선택 기준 및 운영 후보 검증 | 관리 20% / 설계 40% / 개발 40% |
| P3 | Trend episode 데이터 생성 (Anomaly-detection 검증 PoC) | 2025년 ~ 현재 | trend episode 합성, Region/Noise/불량 type 코드화, fleet_std 비례 anomaly 강도 하한 보정, 생성 데이터 검증용 baseline 학습 안정화 | normal 750 + abnormal 5종 각 150 = 총 1,500 sample 합성 trend chart 평가셋 **(데이터 생성 main, 양산 미실시)** | 합성 generator 설계, 도메인 자산 코드화, 생성 데이터 학습 가능성 검증 | 관리 5% / 설계 55% / 개발 40% |
