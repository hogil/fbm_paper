## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|------------------------|
| Computer Vision | Image Classification, Object Detection, Multi-label Classification, Feature Representation Learning, Image-based Failure Detection |
| Deep Learning | CNN Backbone Modeling, Transfer Learning, Fine-tuning, Loss Function Design, Regularization |
| Self-Supervised Learning | Contrastive Learning, InfoNCE, Hard Negative Mining, Task-Adaptive Pretraining, Embedding Learning |
| Unsupervised Learning | Clustering, Novelty Detection, Anomaly Detection, Out-of-Distribution Detection |
| Synthetic Data Generation / Data Augmentation | Synthetic Dataset Generation, Data Augmentation, CutMix, Region-based Mixing Augmentation, Loss Masking, Noise Injection |
| Model Optimization / Model Selection | Hyperparameter Optimization, Model Selection, Margin-based Checkpoint Selection, Threshold Optimization, Calibration, Ensemble, Knowledge Distillation |
| Data Engineering / MLOps | ETL Pipeline, Batch Processing, Object Storage Integration, Model Evaluation Pipeline, Experiment Tracking |
| High-Performance Computing | Cython Acceleration, Numba, pyvips, Large-scale Image Encoding, Palette-indexed PNG Compression |
| AI Systems Engineering | FastAPI Backend, Vanilla JavaScript Frontend, WebGL2 Visualization, Role-Based Access Control (RBAC), SAML Single Sign-On |

## 2. 업무경력

ㅁ **P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요: DRAM 전제품 라인 Failbit Map raw log 변환 파이프라인 + 사내 운영 뷰어 web app + Known 2-stage 분류 + Unknown self-supervised 검출을 결합한 AI 시스템 (운영 뷰어는 일 약 2만 wafer / 1시간 주기 양산 운영, Known / Unknown 모델은 GPU 할당 대기 단계).
- 수행기간: 2024년 10월 ~ 현재
- 담당 역할: 본인 60% / 현업 엔지니어 20% / 관리자 20%
- 수행 업무 및 성과: raw log → wafer image 변환 파이프라인과 사내 인증 연동 운영 뷰어 web app 을 직접 구현해 운영 뷰어는 2025년 5월부터 DRAM 전제품 라인에서 양산 운영 중입니다. Known 2-stage (CNN 분류 + ROI YOLO 보정) 로 실전 16 class weighted F1 **0.95** 까지 도달했고, Unknown 은 self-supervised embedding + HDBSCAN 으로 13개 후보 group 중 **7개 실제 불량**을 현업 검토로 확인했습니다. Known / Unknown 모델의 전수 자동 추론 적용은 AI 센터 GPU 할당 일정 (2026년 9월) 에 맞춰 단계 확장할 계획입니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

Failbit Map / DRAM EDS Test Grade 이미지 / wafer-level failure zone 해석 도메인 위에 ConvNeXtV2 분류 + ROI YOLO 2-stage 보정 + self-supervised contrastive embedding + HDBSCAN grouping + chip-CNN object-id map 후속을 결합했습니다. backbone 은 결함이 국소 영역에 몰리는 특성을 고려해 CNN 계열을 채택했고 (자문: 연세대학교 인공지능학과 전해곤 교수), 신뢰도가 낮은 wafer 만 Stage 2 로 보내는 cascade 구조로 운영 부담을 늘리지 않으면서 정확도를 끌어올렸습니다.

ㅁ **P2. Chip Multi-label Classification (FCM-PM, val_margin)**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요: 한 chip 안에 결함이 동시에 여러 개 나타나는 multi-label 분류. 현업 single failure chip 을 원천으로 두고 부족한 2-combo 조합을 도메인 분포에 맞춰 합성해 학습 / 평가 가능한 형태로 만든 방법론.
- 수행기간: 2025년 3월 ~ 현재
- 담당 역할: 본인 80% / 관리자 20%
- 수행 업무 및 성과: chip 전체 격자를 cover 하는 Full-Cover Mixup 과, 합성된 영역을 paired mask 로 보강해 background false-positive 를 차단하는 Pair Mask 를 결합한 FCM-PM 을 설계 / 학습 / 검증했습니다. 단일 모델 **bit_F1 0.9943 / Total FAR 0.00%** 으로 다중 결함 검출과 정상 / 잡음 wafer 에서의 false alarm 억제를 동시에 잡았습니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

chip Grade 이미지, chip 내부 failure 위치 미상, multi-label co-occurrence, 2-combo label 부족 제약 도메인 위에 Multi-label Image Classification + Synthetic Data Engineering (FCM-PM) + margin-based checkpoint selection 을 결합했습니다. CutMix 계열은 원값을 보존하는 특성이 Grade 이미지 의미 보존에 맞다고 판단해 채택했습니다 (자문: 연세대학교 인공지능학과 박은병 교수).

ㅁ **P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요: 실전 abnormal label 이 부족한 trend chart 영역에서, 본인 trend 판정 경험을 generator parameter 로 옮겨 학습 가능한 합성 trend 데이터를 만든 PoC.
- 수행기간: 2026년 1월 ~ 현재
- 담당 역할: 본인 70% / 관리자 20% / 동료 엔지니어 (공동 연구자) 10%
- 수행 업무 및 성과: 본인 BBD / Overlay / CD 담당 9년 경험을 바탕으로 계측 밀도 Region, Noise 분포, Anomaly 5종을 generator parameter 에 반영해 normal / abnormal 합쳐 약 7,000개 trend sample 을 만들었고, 1차 Binary gate baseline 으로 **Binary F1 0.9967** 까지 확인했습니다. 동료 엔지니어는 AI 모델 실행, 데이터 정리, 실험 결과 취합을 공동 수행했습니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본인이 BBD담당 / Overlay담당 / CD담당으로 9년간 trend chart 를 직접 판정해 온 경험에서 어떤 강도의 mean shift / standard deviation / spike / drift / context 가 실제 불량으로 이어지는지 기준을 가지고 있었고, 이 판단 기준을 직접 generator parameter 로 옮겨 합성 trend 데이터를 만들었습니다. 그 위에 Synthetic Data Engineering + Time-series Episode Simulation + Baseline Model Validation 을 결합했고, 다음 단계는 실제 현업 trend chart 기반 검증입니다.
