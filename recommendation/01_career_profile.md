## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|----------------|
| Computer Vision | Image Classification, Object Detection, Multi-label Classification, Feature Representation Learning, Image-based Defect Detection |
| Deep Learning | CNN Backbone Modeling, Transfer Learning, Task-specific Fine-tuning, Loss Function Design, Regularization |
| Self-Supervised Learning | Contrastive Learning, Self-supervised Representation Learning, Embedding Learning |
| Unsupervised Learning | Clustering, Novelty Detection, Anomaly Detection, Out-of-Distribution Detection |
| Synthetic Data Generation / Data Augmentation | Synthetic Dataset Generation, Data Augmentation, Mixup, CutMix, Noise Injection |
| Model Optimization / Model Selection | Hyperparameter Optimization, Model Selection, Threshold Optimization, Calibration, Ensemble, Knowledge Distillation |
| Data Engineering / MLOps | ETL Pipeline, Batch Processing, Object Storage Integration, Model Evaluation Pipeline, Experiment Tracking |
| Software Engineering / API Service | Backend API, Web Application, Data Visualization, Access Control, Single Sign-On |

---

## 2. AI 주요 과제

> 본인은 반도체 현장에서 익힌 문제 이해를 AI 모델과 학습 데이터 설계에 옮겨, 실제 현업 부담을 줄이는 방향으로 과제를 진행해 왔습니다.

**ㅁ P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

Failbit Map 변환 파이프라인과 Web App 은 양산에서 운영 중입니다. Known 분류는 ROI YOLO 2-stage 를 붙여 16 class / 1,500 labeled samples / 4:1 stratified split 의 평가용 hold-out set 에서 weighted F1 0.95까지 확인했습니다. 이 수치는 운영 적용 결과와 분리한 분류 성능 지표입니다. Unknown 쪽은 같은 모양의 패턴도 wafer 안에서 어디에 생겼는지에 따라 다른 불량으로 봐야 하는 경우가 있어, 전체 map embedding 만 쓰지 않고 6×6 grid structured local sampling 과 Local InfoNCE loss 를 함께 넣었습니다. 실전 운영 데이터에서는 후보 13건 중 현업이 실제 불량으로 확인한 건이 7건이었고, capture ratio / ARI 같은 수치는 후속 생성 데이터 benchmark 로 따로 관리하고 있습니다. chip-CNN 기반 object-id map(chip 위치별 불량 chip id로 제작한 map)은 아직 추가 생성 데이터 기준의 개발 단계입니다.

- **담당 역할**: 본인 60% (서버 환경 구축, 데이터 처리, Web App 운영, Known/Unknown AI 모델 설계, 개발 및 검증) / 현업 엔지니어 20% (현업 문제정의 및 불량 교육) / 관리자 20% (방향성, 일정 및 리뷰 매니징)
- **수행 업무**: fine-tuned ConvNeXtV2 checkpoint 선정, Failbit Map task-specific fine-tuning 및 HPO, ROI YOLO 2-stage 보정, Unknown self-supervised embedding, 6×6 grid structured local sampling 및 Local InfoNCE loss 적용, HDBSCAN grouping, chip-CNN → object-id map 기반 Stage 2 보정 구조 개발, Web App 운영, Cython hex-to-grade 변환, 32-color palette PNG 저장
- **모델 선택 이유**: wafer 전체 분포는 ConvNeXtV2 로 먼저 보고, center scratch / scratch_rot 처럼 map-level 에서 헷갈리는 class 는 ROI YOLO 로 chip evidence 를 다시 확인했습니다. 등록 class 밖 패턴은 SimCLR 계열 embedding + Local InfoNCE + HDBSCAN 으로 후보화했고, class 가 더 늘어날 때의 부담은 chip-CNN → object-id map 구조로 줄이는 방향을 잡았습니다.
- **성과 / 검증 근거**: **[실전 현업 데이터]** Known weighted F1 0.95(16 class / 1,500 labeled samples / 4:1 stratified split 의 평가용 hold-out set 기준, 운영 적용 결과와 별도), Unknown 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 현업 확인 실제 불량 7건(후보 발굴 / 현업 확인값), **[양산 운영]** 사내 failbitmap 서비스 12일 누적 2,317 요청
- **추가 개발**: **[추가 생성 데이터, 개발 중]** 실전 운영 성과와 분리해 Unknown metric benchmark 를 운영하고 있습니다. 현재 same-anchor defect-class capture 43/43(capture ratio 1.000), ARI 0.859±0.018, Completeness 0.994, Homogeneity 0.942 를 확인했고, object-id map용 chip 분류기 보조 지표는 val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838±0.0092 입니다.
- **관련 기술**: fine-tuned ConvNeXtV2 checkpoint 기반 task-specific fine-tuning, ROI YOLO 2-stage, chip-CNN 기반 object-id map, self-supervised pretraining, Global InfoNCE, Local InfoNCE, 6×6 grid structured local sampling, MoCo Queue, NV-Retriever, NeCo, HDBSCAN, Cython

**ㅁ P2. Chip multi-label classification**

실제 환경에서는 multi-label 불량 조합 label 을 충분히 모으기 어렵고, 먼저 쌓이는 데이터는 대부분 single-label defect chip 입니다. 그래서 single-label chip 두 개를 조합하고, 조합 안에 들어간 각 불량 class 를 빠짐없이 맞히도록 학습 구조를 잡았습니다. 일반 CutMix 와 Pair Mask 만으로는 negative false-positive 가 충분히 잡히지 않아, chip 전체 grid 를 cover 하는 Full-Cover Mixup 과 Pair Mask 를 함께 쓰는 FCM-PM 구조로 정리했습니다.

- **담당 역할**: 본인 80% / 관리자 20%
- **수행 업무**: CutMix 계열 선정, CutMix + Pair Mask background loss masking, FCM-PM 합성 및 손실 마스킹 구조 신규 적용, single 4 → 16+ multi-label / OOD 평가 구성, val_f1 → val_margin checkpoint 선택 기준 전환, Label Smoothing, Temperature scaling, 비대칭 pos/neg target sweep, 4-bag ensemble, KD single-model 압축 검증
- **모델 선택 이유**: multi-label label 을 새로 많이 만들 수 없는 조건이라 single-label defect chip 을 조합하는 쪽을 선택했습니다. Grade 0~7 의미를 보존하려면 픽셀값을 섞는 방식보다 CutMix 계열이 맞았고, random crop 이 defect 를 자르는 문제는 Full-Cover Mixup 으로, background 오학습은 Pair Mask 로 줄였습니다.
- **성과 / 검증 근거**: **[추가 생성 chip 데이터, PoC]** FCM-PM 대표 모델은 기존 요약 평가에서 bit F1 0.9943, Normal/Invalid/OOD negative false-positive 0건을 확인했습니다. per-class 2,000 갱신 평가에서는 bit F1 0.9964, Total FAR 0.83% 로 확인해 평가 기준을 분리해 관리하고 있습니다.
- **주요 확인**: FCM-PM 구조에서 Pair Mask 제거 시 FAR 100% 로 negative 전체 오탐이 발생했습니다. val_margin 은 `정답 class score 평균 - 오답 class score 최대값` 으로 본 여유폭이며, eval bit F1 과 Spearman ρ +0.56 으로 정렬되어 val_f1 (ρ -0.10) 대비 best-model 선택 신호가 더 안정적이었습니다.
- **운영 검토**: 4-bag ensemble 은 per-class 2,000 갱신 평가 기준 bit F1 0.9909 / FAR 0.00% 로 negative 안정성을 확인했습니다. KD single 은 bit F1 0.9872 로 압축 가능성은 봤지만, stress 평가에서 FAR 12.86% 가 나와 바로 운영하기보다 추가 보정 대상으로 두었습니다.
- **관련 기술**: Multi-label chip classification, CutMix, CutMix + Pair Mask, FCM-PM, Pair Mask background loss masking, val_margin / best-margin checkpoint 선택, asymmetric pos/neg target, Label Smoothing, Temperature scaling, 4-bag ensemble, Knowledge Distillation

**ㅁ P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 검증 PoC**

이 과제는 모델을 먼저 복잡하게 만들기보다, 실제 운영 trend chart 와 비슷한 학습 데이터를 만들 수 있는지 확인한 작업입니다. BBD, Overlay, CD 업무에서 보던 계측 밀도 차이, 설비성 noise, trend 불량 shape, 정상 산포 기준 anomaly 강도를 각각 생성 조건으로 나눠 설계했습니다.

- **담당 역할**: 본인 80% / 관리자 20%
- **수행 업무**: Region 5종(정상 / 희소 / 공핍 / 얇은 계측 / 결핍), Noise 3종(Gaussian noise=설비 산포 / Laplacian noise=hunting / correlation noise=drift), 불량 5종 trend 합성 generator 설계, 정상 산포 기준 anomaly 강도 하한 보정, 정상/이상 trend episode 생성, 생성 데이터 확인용 기준 모델 학습 안정화, Binary gate + Type classifier 검증
- **모델 선택 이유**: 실전 abnormal trend label 이 부족했기 때문에 detector 고도화보다 generator 설계를 먼저 잡았습니다. 계측 영역, noise, trend type 을 따로 조절하고, 정상 산포에 묻히는 약한 이상은 강도를 보정한 뒤 기준 모델로 정상/이상 구분 신호를 확인했습니다.
- **성과 / 검증 근거**: **[합성 trend chart, PoC]** normal 750 + abnormal 5종 각 150 = 총 1,500 sample 합성 trend chart 평가셋을 만들었습니다. Binary F1 0.9967, Abnormal Recall 0.9987, 5-seed sweep 0.9944~0.9988 은 실전 성능이 아니라 생성 데이터가 정상/이상 구분 신호를 담고 있는지 본 참고 수치입니다.
- **상태 구분**: 아직 실전 현업 데이터 검증 단계는 아니며, 생성 데이터와 기준 모델 결과를 분리해 관리하고 있습니다.
- **관련 기술**: synthetic trend episode generation, 계측 밀도 코드화, statistical noise injection, trend anomaly shape catalog, 정상 산포 기준 anomaly strength calibration, 생성 데이터 확인용 기준 모델 학습 안정화

---

## 3. 포트폴리오

**P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

- 기간: 2024년 ~ 현재
- 내용: fail-map 파이프라인, Web App, Known 2-stage, Unknown self-supervised 검출, chip-CNN → object-id map 기반 Stage 2 보정 구조
- 리딩 규모: DRAM 전제품 라인 운영, 12일 누적 2,317 요청, single-label 이미지 처리 AI 모델 PoC
- 담당 업무: 데이터 파이프라인 구축, Web App 운영, AI 모델 설계, 개발 및 검증
- 비중: 관리 10% / 설계 40% / 개발 50%

**P2. Chip multi-label classification (CutMix → CutMix + Pair Mask → FCM-PM)**

- 기간: 2025년 ~ 현재
- 내용: FCM-PM 신규 적용, multi-label 평가셋 구성, Pair Mask 제거 비교, val_margin 기준 도입, ensemble negative 안정성 및 KD 압축 가능성 검토
- 리딩 규모: single 4 학습 → 16+ multi-label / OOD 평가, FCM-PM 대표 모델 / 4-bag ensemble / KD 성능-비용 비교
- 담당 업무: 합성 및 손실 마스킹 구조 구성, 학습 및 평가 체계 구축, 모델 선택 기준 및 운영 가능성 검토
- 비중: 관리 20% / 설계 40% / 개발 40%

**P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 검증 PoC**

- 기간: 2025년 ~ 현재
- 내용: trend episode 합성, Region/Noise/불량 type 코드화, 정상 산포 기준 anomaly 강도 하한 보정, 생성 데이터 확인용 기준 모델 학습 안정화
- 리딩 규모: normal 750 + abnormal 5종 각 150 = 총 1,500 sample 합성 trend chart 평가셋 (데이터 생성 중심, 양산 미실시)
- 담당 업무: 합성 generator 설계, 도메인 자산 코드화, 생성 데이터의 정상/이상 구분 신호 확인
- 비중: 관리 5% / 설계 55% / 개발 40%
