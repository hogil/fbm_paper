## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|------------------------|
| Computer Vision | Wafer-level Image Classification, ROI-based Object Detection (YOLO), Chip Multi-label Classification, Trend Chart Classification |
| Deep Learning (Architecture & Training) | Pretrained Backbone Transfer Learning, Loss Function Design (BCE / Focal / Asymmetric Loss / Positive & Negative Target Tuning), LR Scheduling (Warmup + Cosine), EMA, Optuna Hyperparameter Sweep |
| Self-Supervised Learning | Global InfoNCE, Local DenseCL, MoCo Queue, NV-Retriever Negative Similarity Filter, NeCo |
| Unsupervised Learning / Anomaly Detection | HDBSCAN Clustering, Novelty Candidate Grouping, Out-of-Distribution Detection, Trend Anomaly Detection |
| Synthetic Data Generation | Domain-Distribution-based Pixel Sampling, FCM-PM (Full-Cover CutMix + Pair Mask), Trend Episode Simulation |
| Model Selection / Inference Optimization | Margin-based Checkpoint Selection (val_margin), Threshold Gating (max-prob), Temperature Scaling, Bit-level Majority Voting Ensemble, Knowledge Distillation, Cascade Confidence Gate |
| Data Engineering | Image ETL Pipeline, Large-scale Batch Image Processing, Metadata Indexing, Model Evaluation Pipeline |
| High-Performance Computing | Cython JIT Acceleration (~100x speed-up), Numba JIT, pyvips Large-scale Image Encoding, Palette-indexed PNG Compression (~75%) |
| AI Systems Engineering | FastAPI Backend, Vanilla JS Frontend, WebGL2 Visualization, RBAC, SAML SSO |

## 2. 업무경력

ㅁ **P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요: DRAM 전제품 라인 Failbit Map raw log 변환 파이프라인 + 사내 운영 뷰어 web app + Known 2-stage 분류 + Unknown self-supervised 검출을 결합한 AI 시스템 (운영 뷰어는 일 약 2만 wafer / 1시간 주기 양산 운영, Known / Unknown 모델은 GPU 할당 대기 단계).
- 수행기간: 2024년 10월 ~ 현재
- 담당 역할: 데이터 파이프라인 설계 및 구현, Failbit Map 이미지 변환 최적화, 운영 뷰어 연동, Known 2-stage 모델 개발 및 튜닝, Unknown self-supervised 검출 구조 설계, 현업 검증 flow 구축
- 수행 업무 및 성과: Failbit Map 대량 조회 한계와 수작업 판정 부담을 해결하기 위해, 데이터 변환 파이프라인 / 사내 운영 뷰어 web app / Known 분류 + Unknown 신규 패턴 검출 AI 모델을 직접 설계 / 구현 / 검증했습니다. 운영 뷰어는 2025년 5월부터 DRAM 전제품 라인 (**D1a/b/c/d**) 에서 매일 양산 운영 중이며, **공수 약 90% 절감 (연 약 26억 효과)** + **수율 +0.02% 개선 (P3WN 1건 약 97억 효과)** 의 현업 임팩트와 함께 Known weighted F1 **0.95** / Unknown 13 후보 중 **7건 실제 불량** 확인까지 달성했습니다. 본 과제는 **AI 센터 주관 DS AI Best Practice Good Challenger 상** 과 **MTC 고등급 제안 1등급** 수상으로 사내 성과를 인정받았습니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

Failbit Map / DRAM EDS Test Grade 이미지 / wafer-level failure zone 해석 도메인 위에 두 갈래 모델 구조를 적용했습니다. Known 측은 ConvNeXtV2 분류 + ROI YOLO 2-stage cascade 보정 (신뢰도가 낮은 wafer 만 Stage 2 로 보내 운영 부담을 늘리지 않으면서 정확도 향상) 으로 구성했고, backbone 은 결함이 국소 영역에 몰리는 특성을 고려해 CNN 계열을 채택했습니다 (자문: 연세대학교 인공지능학과 전해곤 교수). Unknown 측은 self-supervised contrastive embedding + HDBSCAN grouping 으로 라벨 없는 wafer 에서 신규 결함 후보 group 을 검출했습니다. 후속으로 chip-CNN object-id map 보정 구조도 직접 설계 / 구현 중입니다.

ㅁ **P2. Chip Multi-label Classification (FCM-PM, val_margin)**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요: 한 chip 안에 failure 가 동시에 여러 개 나타나는 multi-label 분류. 현업 EDS Failbit Map 에서 관찰되는 single failure 형태를 기준으로 4 class 를 구성하고, 부족한 2-combo 조합을 도메인 분포에 맞춰 합성해 학습 / 평가 가능한 형태로 만든 방법론.
- 수행기간: 2025년 3월 ~ 현재
- 담당 역할: multi-label 학습 데이터 설계, FCM-PM augmentation 설계, Pair Mask loss masking 구현, val_margin 기반 best-model selection, Normal / Invalid / OOD negative 평가셋 설계, threshold gate / ensemble / Knowledge Distillation 후속 검토
- 수행 업무 및 성과: 한 chip 안에 결함이 여러 개 동시에 나타나는 multi-label 검출이 약했던 한계를 풀기 위해, FCM-PM (Full-Cover CutMix + Pair Mask) 기반 합성 데이터 + 학습 구조를 직접 설계 / 학습 / 검증했습니다. 단일 모델 **bit_F1 0.9927 / Total FAR 0.00%** 로 다중 결함 검출과 false alarm 억제를 동시에 잡았습니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

chip Grade 이미지, chip 내부 failure 위치 미상, multi-label co-occurrence, 2-combo label 부족 제약 도메인 위에 Multi-label Image Classification + Synthetic Data Engineering (FCM-PM) + margin-based checkpoint selection 을 결합했습니다. CutMix 계열은 원값을 보존하는 특성이 Grade 이미지 의미 보존에 맞다고 판단해 채택했습니다 (자문: 연세대학교 인공지능학과 박은병 교수).

ㅁ **P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요: 실전 abnormal label 이 부족한 trend chart 영역에서, 본인 trend 판정 경험을 generator parameter 로 옮겨 학습 가능한 합성 trend 데이터를 만든 PoC.
- 수행기간: 2026년 1월 ~ 현재
- 담당 역할: trend episode generator 설계, 도메인 parameter (Region 5종 / Noise 3종 / Anomaly 5종) 정의, 합성 normal / abnormal sample 생성, 정상 산포 보정 수식 설계, 1차 Binary gate baseline 검증, 현업 적용 전 PoC 검증
- 수행 업무 및 성과: 실전 abnormal label 부족으로 trend anomaly 모델 검증이 막혀 있던 한계를 풀기 위해, 본인 BBD / Overlay / CD 담당 **10년** 경험을 generator parameter 로 옮겨 합성 trend sample 약 **7,000개**를 만들고, 1차 Binary gate baseline 으로 **Binary F1 0.9967** 까지 확인해 학습 가능한 데이터 생성 구조를 갖췄습니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본인이 BBD담당 / Overlay담당 / CD담당으로 10년간 trend chart 를 직접 판정해 온 경험에서 어떤 강도의 mean shift / standard deviation / spike / drift / context 가 실제 불량으로 이어지는지 기준을 가지고 있었고, 이 판단 기준을 직접 generator parameter 로 옮겨 합성 trend 데이터를 만들었습니다. 그 위에 Synthetic Data Engineering + Time-series Episode Simulation + Baseline Model Validation 을 결합했고, 다음 단계는 실제 현업 trend chart 기반 검증입니다.
