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

**핵심 요약**

1. P1 은 Failbit Map raw log → wafer image 변환, **사내 운영 뷰어 web app 직접 구현**, Known 2-stage 분류, Unknown 후보 group 검토까지 양산 운영 흐름 전체를 한 줄로 연결한 AI 시스템입니다.
2. P2 는 현업 single failure chip 원천 기반 FCM-PM + Pair Mask loss 로 2-combo label 부족을 풀고, **bit_F1 과 false alarm 을 동시에 잡은** multi-label 방법론입니다.
3. P3 는 본인 BBD / Overlay / CD 담당 trend 판정 경험을 generator parameter 로 코드화해, **AI 학습이 가능한 trend 데이터 자산 자체를 만든** 것이 주 성과인 PoC 입니다 (1차 Binary gate 검증까지 확보).

ㅁ **P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요 및 규모: DRAM 전제품 라인 Failbit Map 데이터 파이프라인 + 사내 운영 뷰어 web app + Known 2-stage AI 분류기 + Unknown self-supervised 검출기를 결합한 양산 운영 시스템.
- 수행기간: 2024년 10월 ~ 현재
- 담당 역할: 본인 60% / 현업 엔지니어 20% / 관리자 20%
- 수행 업무: wafer 당 약 1,000만 cell hex → Grade 0-7 변환을 Cython 으로 약 100배 가속, 32색 palette indexed PNG 로 저장 용량 약 75% 절감. 운영 뷰어 web app 은 대용량 병렬 처리 + 사내 인증 시스템 연동까지 직접 구현. Stage 1 ConvNeXtV2 backbone + fine-tune LR 분리, Stage 2 ROI YOLO cascade gate 는 wafer-level confidence 가 낮은 difficult sample 만 Stage 2 로 넘기는 방식 (confidence ≥ gate 인 wafer 는 Stage 2 skip, 일부는 일일 sampling 재검증 + Normal drift 추적으로 false-negative 차단). Unknown 은 self-supervised embedding + HDBSCAN grouping. 후속 chip-CNN object-id map (Stage 2 ROI-YOLO 자리 대체 후보) 직접 설계 / 구현.
- 성과: **[실전 현업 데이터]** Known 2-stage weighted F1 **0.95** (16 class / 1,500 labeled / 4:1 split, ladder 0.78 → 0.87 → 0.92 → 0.95), Unknown 13 후보 group 중 **7개 실제 불량 현업 확인** 완료. **[양산 운영]** 2025년 5월부터 DRAM 전제품 라인 일 약 2만 wafer / 1시간 주기 처리 중. **[추가 생성 chip 데이터, 개발 중]** chip-CNN object-id map val_f1 **0.9946**. **[Unknown 추가 생성 데이터, 개발 중]** Unknown 합성 평가셋 capture **1.000** / noise **0.00%** / Completeness **0.9938** / Silhouette **0.781** 측정 중 (신규 recipe MoCo Queue / NV-Retriever / NeCo 별도 트랙). 양산 deploy 와 전수 자동 추론 확장은 validation + 2026년 9월 GPU 할당 후 단계 진행.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

Failbit Map, DRAM EDS Test Grade 0-7 양자화 이미지, wafer-level failure zone 해석 도메인 위에 ConvNeXtV2 wafer 분류 + ROI YOLO 2-stage 보정 + self-supervised contrastive embedding + HDBSCAN grouping + chip-CNN object-id map 후속을 결합했습니다. backbone 은 본 과제 결함이 국소 영역에 몰리는 특성상 CNN 계열의 local receptive field 가 더 어울린다고 판단해 ConvNeXtV2 채택 (MaxViT 와 동일 F1 0.87 에 파라미터 **26%** / FLOPs **39%** 감소, 자문: 연세대학교 인공지능학과 전해곤 교수). Stage 2 는 wafer-level confidence 가 낮은 difficult sample 에 한해 헷갈리는 영역을 ROI 로 먼저 잘라내고 그 ROI 안에서 YOLO 가 chip 단위 object detection (bbox + class) 으로 다시 분류해, 그 출력 분포의 majority 로 최종 class 를 결정하는 구조입니다. 이 흐름으로 throughput 손실 없이 헷갈리는 sample 의 분리력만 선택적으로 보강합니다.

ㅁ **P2. Chip Multi-label Classification (FCM-PM, val_margin)**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요 및 규모: chip multi-label classification. 학습 원천은 실전 현업 single failure chip 4 class, 2-combo 6 종은 FCM-PM 으로 도메인 분포에 맞춰 합성, Normal / Invalid / OOD negative 4 종은 현업 분포에 가깝게 직접 설계. 합쳐 **16+ class × 약 3,850 chip** controlled benchmark.
- 수행기간: 2025년 3월 ~ 현재
- 담당 역할: 본인 80% / 관리자 20%
- 수행 업무: CutMix 계열 채택 → chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장, Pair Mask binary mask 로 background bit 를 loss 에서 제외, val_margin = mean(pos bits) − max(neg bits) 로 best epoch 선택 (Spearman ρ +0.56 vs val_f1 −0.10), positive target 0.85 / negative target 0.15 (symmetric) 채택. 추론 단은 max-prob threshold gate (0.55) + Temperature Scaling + bit-level majority voting ensemble (champion `vote_majority_bits`) + Knowledge Distillation α/T sweep. data leakage 방지를 위해 single failure chip 원천을 chip 단위로 먼저 train / test split 후, 2-combo 와 Pair Mask 합성은 train 원천 chip 만 사용하고 test 원천 chip 은 합성 과정에서 완전히 배제했습니다.
- 성과: FCM-PM val_margin 단일 모델 **bit_F1 0.9943 / Total FAR 0.00%** (현업 분포 모사 controlled benchmark 기준). Pair Mask 제거 ablation 에서 Total FAR 100% 로 치솟아 background loss masking 이 결정적 설계 요소임을 정량으로 확인. bit-level majority voting ensemble (champion `vote_majority_bits`) **bit_F1 0.9941 / Total FAR 0.00%** 운영 안전판, KD single student 는 KD_v7 (α=0.3, T=2) bit_F1 **0.9265** 첫 안정 → KD_v12 (α=0.3, T=3) bit_F1 **0.9470** KD sweep 최고점, 모두 대표 성과와 분리한 후속 압축 / 안정성 보조.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

실제 현업 chip Grade 0-7 양자화 이미지, chip 내부 failure 위치 미상, multi-label failure co-occurrence, 2-combo label 부족 제약 도메인 위에 Multi-label Image Classification + Synthetic Data Engineering (FCM-PM = Full-Cover Mixup + Pair Mask) + val_margin checkpoint selection + Temperature Scaling + max-prob threshold gate + bit-level majority voting ensemble + Knowledge Distillation 압축 후보를 결합했습니다. CutMix 계열은 원값을 보존해 영역 단위로 붙이는 특성이 본 과제 Grade 의미 보존에 맞다고 판단해 채택 (자문: 연세대학교 인공지능학과 박은병 교수). Full-Cover Mixup 은 chip 내부 failure 위치 미상 환경에서 wafer 전 영역을 빠짐없이 cover 해야 한다는 현업 Overlay dynamic sampling 경험에서 아이디어를 가져왔습니다.

ㅁ **P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**(1) 과제 개요 / 담당 역할 / 수행 업무 / 성과**

- 과제 개요 및 규모: **데이터 생성 자체가 주 성과인 PoC**. 본인 BBD담당 / Overlay담당 / CD담당 9년 trend 판정 경험을 계측 밀도 Region 5종 (dense / sparse / very_sparse / thin / missing), Noise 3분포 (Gaussian / Laplacian / Correlated), Anomaly 5종 (mean_shift / standard_deviation / spike / drift / context), 같은 설비군의 산포 통계를 기준으로 합성 normal 의 산포에 상한과 하한을 같이 두는 두 가지 수식을 generator parameter 로 직접 코드화. **normal 3,500 + abnormal 3,500 = 총 7,000개** trend sample 생성.
- 수행기간: 2026년 1월 ~ 현재
- 담당 역할: 본인 70% / 관리자 20% / 동료 엔지니어 (공동 연구자) 10%
- 수행 업무: Region 5단계 계측 밀도 코드화, Noise 3분포 (현업 설비 상태변동 / 산포 / spike 패턴을 통계 분포로 1:1 매핑), 일반 trend 불량 4종 + context 1종 형상 카탈로그, 합성 normal 산포에 상한과 하한을 같이 두는 두 가지 수식 (`target_baseline_std = max(baseline_std, 0.01)` 로 최소 0.01σ 하한 보장, `target_std ≤ fleet_within_std × 1.2` 로 같은 설비군 산포에 맞춰 상한 정렬), 정상 / 이상 trend episode 생성, val-F1 median smoothing + val-loss spike guard 검증 baseline 학습 안정화까지 본인이 직접 코드화. 두 식의 임계값은 정상 산포에 묻혀 놓치는 케이스와 일시 튐을 정상으로 잡는 케이스 사이 경계를 봐 온 담당 경험에서 잡은 값입니다. 동료 엔지니어는 AI 모델 실행, 데이터 정리, 실험 결과 취합을 공동 수행.
- 성과: **[합성 trend chart, PoC]** normal 3,500 + abnormal 3,500 = 총 7,000개 trend sample 자산, test split 1,500 (normal 750 / abnormal 5종 각 150) 기준 1차 Binary gate baseline **Binary F1 0.9967 / Abnormal Recall 0.9987** (TN/FN/FP/TP = 746/1/4/749, threshold=0.9). 생성 데이터가 학습 가능한 정상 / 이상 패턴을 담고 있음을 확인한 PoC 단계이며, 실제 현업 trend log 일반화 성능과는 분리해 해석합니다.

**(2) 과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본인 trend 판정 경험에서 자주 본 패턴 (설비 산포, 설비 hunting, 미세 drift, baseline 흔들림, spec out 위험) 을 합성 데이터 자산으로 옮긴 영역 위에 Synthetic Data Engineering + Time-series Episode Simulation + Baseline Model Validation 을 결합했습니다. 도메인 변별점은 본인 BBD / Overlay / CD 담당 경력을 generator parameter 로 코드화한 부분이며, 다음 단계는 실전 abnormal log 를 parameter 재보정 trigger 로 흘리는 feedback loop 설계입니다.
