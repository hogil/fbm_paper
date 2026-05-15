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

Failbit Map 을 대량 변환, 조회하고 Known/Unknown 불량 후보를 현업 검토로 연결한 양산 운영 과제입니다. wafer 전체 분포, chip 내부 evidence, 발생 위치 정보를 나눠 보도록 모델 구조를 잡았습니다.

(1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과

- 과제 개요 및 규모: 2024년부터 DRAM 전제품 라인에서 운영 중이며, 일 약 2만 장 wafer 를 1시간 주기로 적재합니다.
- 담당 역할: 본인 60% (서버 환경 구축, 데이터 처리, Web App 운영, Known/Unknown 모델 설계, 개발 및 검증) / 현업 엔지니어 20% (현업 문제정의 및 불량 교육) / 관리자 20% (방향성, 일정 및 리뷰 매니징)
- 수행 업무: Failbit Map 변환 파이프라인, Web App, ConvNeXtV2 task-specific fine-tuning 및 HPO, ROI YOLO 2-stage 보정, Unknown self-supervised embedding, Local InfoNCE, HDBSCAN grouping, chip-CNN 기반 object-id map 구조 개발
- 성과: Known은 평가용 hold-out set 기준 weighted F1 0.95(16 class / 1,500 labeled samples, 운영 적용 결과와 별도), Unknown은 운영 데이터 후보 13건 중 현업 확인 실제 불량 7건, Web App은 12일 누적 2,317 요청을 확인했습니다.
- 추가 개발: object-id map용 chip 분류기 보조 지표 val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838±0.0092, Unknown 후속 benchmark same-anchor defect-class capture 43/43, ARI 0.859±0.018

(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론

- 도메인: EDS Failbit Map, wafer 불량 패턴 분석, 현업 불량 검토 Web App
- AI 기술: ConvNeXtV2 fine-tuning, ROI YOLO 2-stage, contrastive embedding, Local InfoNCE, HDBSCAN, chip-CNN 기반 object-id map(chip 위치별 불량 chip id로 제작한 map)
- 방법론: wafer-level classifier 로 전체 분포를 먼저 보고, center scratch / scratch_rot 처럼 헷갈리는 class 는 ROI YOLO 로 chip evidence 를 재확인했습니다. 등록 class 밖 패턴은 contrastive embedding 과 HDBSCAN 으로 후보화했습니다.

**ㅁ P2. Chip multi-label classification**

multi-label 조합 label 을 충분히 모으기 어려운 실제 조건을 가정하고, single-label defect chip 을 조합해 multi-label 불량을 예측하도록 만든 PoC 입니다. 핵심은 모델보다 학습 데이터 조합과 background loss 처리였습니다.

(1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과

- 과제 개요 및 규모: single 4 class 기반으로 2-combo, Normal, Invalid, OOD 를 포함한 16+ class × 약 3,850 chip controlled synthetic benchmark 를 구성했습니다.
- 담당 역할: 본인 80% / 관리자 20%
- 수행 업무: CutMix 계열 선정, FCM-PM(Full-Cover Mixup + Pair Mask) 합성 구조 적용, single 4 → 16+ multi-label / OOD 평가 구성, val_margin checkpoint 선택 기준 도입, Label Smoothing, Temperature scaling, 4-bag ensemble, KD single-model 압축 검토
- 성과: 최신 per-class 2,000 갱신 평가 기준 bit F1 0.9964, Total FAR 0.83% 입니다. 기존 요약 평가에서는 bit F1 0.9943, Normal/Invalid/OOD negative false-positive 0건을 확인했습니다.
- 추가 확인: Pair Mask 제거 시 FAR 100% 로 negative 전체 오탐이 발생했습니다. 4-bag ensemble 은 bit F1 0.9909 / FAR 0.00%, KD single 은 bit F1 0.9872 이지만 stress 평가 FAR 12.86% 로 추가 보정 대상입니다.

(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론

- 도메인: chip 단위 불량 이미지, Grade 0~7 양자화 이미지, single-label 기반 multi-label defect 조합
- AI 기술: Multi-label chip classification, CutMix, CutMix + Pair Mask, FCM-PM, Pair Mask background loss masking, val_margin / best-margin checkpoint 선택, asymmetric pos/neg target, Label Smoothing, Temperature scaling, 4-bag ensemble, Knowledge Distillation
- 방법론: Grade 값을 보존하기 위해 CutMix 계열을 선택했고, defect 위치를 미리 알 수 없는 조건은 Full-Cover Mixup 으로 반영했습니다. 합성 background 가 defect 로 학습되는 문제는 Pair Mask 로 loss 에서 제외했습니다.

**ㅁ P3. Domain Knowledge 기반 Trend Anomaly 데이터 생성 및 검증 PoC**

BBD, Overlay, CD 업무에서 보던 trend 판단 기준을 synthetic trend episode 로 옮긴 데이터 생성 PoC 입니다. 실전 abnormal label 이 부족한 상태에서 detector 를 먼저 키우기보다, 학습 가능한 trend abnormal 데이터를 만드는 쪽을 먼저 선택했습니다.

(1) 과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과

- 과제 개요 및 규모: normal 750 + abnormal 5종 각 150, 총 1,500 sample 합성 trend chart 평가셋을 만들었습니다.
- 담당 역할: 본인 80% / 관리자 20%
- 수행 업무: Region 5종(정상 / 희소 / 공핍 / 얇은 계측 / 결핍), Noise 3종(Gaussian noise=설비 산포 / Laplacian noise=hunting / correlation noise=drift), 불량 5종 trend 합성 generator, 정상 산포 기준 anomaly 강도 하한 보정, 1단계 정상/이상 분류와 2단계 5개 불량 type 분류 기준 모델 검증
- 성과: 1단계 정상/이상 분류에서 Binary F1 0.9967, Abnormal Recall 0.9987, 5-seed sweep 0.9944~0.9988 을 확인했습니다. 이 수치는 실전 성능이 아니라 생성 데이터에 정상/이상 구분 신호가 있는지 확인한 참고 수치입니다.
- 상태: 아직 실전 현업 데이터 검증 단계는 아니며, 생성 데이터와 기준 모델 결과를 분리해 관리하고 있습니다.

(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론

- 도메인: BBD / Overlay / CD trend chart, 계측 밀도 차이, 설비 산포, hunting, drift, context pattern
- AI 기술: synthetic trend episode generation, 계측 밀도 코드화, statistical noise injection, trend anomaly shape catalog, 정상 산포 기준 anomaly strength calibration, 생성 데이터 확인용 기준 모델 학습 안정화
- 방법론: 실제 운영 chart 처럼 결핍 영역, 희소 영역, 공핍 영역을 만들고, Gaussian noise / Laplacian noise / correlation noise 로 설비 산포, hunting, drift 를 분리했습니다. 정상 산포에 묻히는 약한 이상은 최소 anomaly 강도를 보정했습니다.

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
