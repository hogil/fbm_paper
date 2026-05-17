## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|------------------------|
| Computer Vision | Image Classification, Object Detection, Multi-label Classification, Feature Representation Learning, Image-based Failure Detection |
| Deep Learning | CNN Backbone Modeling, Transfer Learning, Fine-tuning, Loss Function Design, Regularization |
| Self-Supervised Learning | Contrastive Learning, Self-supervised Representation Learning, Embedding Learning |
| Unsupervised Learning | Clustering, Novelty Detection, Anomaly Detection, Out-of-Distribution Detection |
| Synthetic Data Generation / Data Augmentation | Synthetic Dataset Generation, Data Augmentation, Mixup, CutMix, Noise Injection |
| Model Optimization / Model Selection | Hyperparameter Optimization, Model Selection, Threshold Optimization, Calibration, Ensemble, Knowledge Distillation |
| Data Engineering / MLOps | ETL Pipeline, Batch Processing, Object Storage Integration, Model Evaluation Pipeline, Experiment Tracking |
| AI Systems Engineering | Backend API, Web Application, Data Visualization, Access Control, Single Sign-On |

## 2. 업무경력

본인은 반도체 분석 현장에서 쌓은 이해를 AI 모델 구조 / 학습 데이터 생성 / 손실 함수 설계 / 운영 안전판에 직접 반영해 현업 문제를 줄이는 방향으로 일해 왔습니다. 아래 세 과제는 모두 이 흐름 위에 있습니다.

**※ 제출 대표 성과 기준**

본 문서에서 제출 대표 성과로 읽어야 할 수치는 P1 양산 운영 파이프라인 (일 약 2만 장 / 1시간 주기, Known weighted F1 0.95, Unknown 13 후보 중 7 실제 불량 확인) 과 P2 FCM-PM val_margin 단일 모델 (bit_F1 0.9943 / Total FAR 0.00%) 입니다. Unknown 후속 metric, chip-CNN object-id map, KD는 개발 중 또는 심화 질의 대비 항목으로 분리해 관리합니다.

**핵심 요약**

1. P1은 raw log 를 wafer image, chip coordinate, 운영 뷰어, Known 2-stage, Unknown 후보 group 검토까지 연결한 양산 운영형 AI 시스템입니다.
2. P2는 현업 single failure chip 원천 기반 FCM-PM + Pair Mask loss 로 2-combo label 부족과 false alarm 문제를 같이 줄인 multi-label 방법론입니다.
3. P3는 본인 trend 판정 경험을 synthetic episode generator 로 코드화해, label 부족 환경에서 anomaly 검증을 시작할 수 있게 만든 PoC 입니다.

ㅁ **P1. Failbit Map AI 분류 시스템 (Known 2-stage + Unknown contrastive)**

본 과제는 Failbit Map 데이터 파이프라인부터 운영 뷰어, Known 2-stage 분류, Unknown 검출까지 하나의 운영 흐름으로 묶은 시스템 과제입니다. fail-map 은 데이터 변환 / 저장 흐름, 운영 뷰어는 만들어진 이미지의 검색 / 비교 흐름으로 역할이 갈리고, 본인이 양쪽을 한 줄로 이었습니다.

- 과제 개요 및 규모: DRAM 전제품 라인의 Failbit Map 데이터 파이프라인 (fail-map), 뷰어 Web App, Known single-label 2-stage AI 분류기, Unknown self-supervised 검출기를 결합한 운영 시스템.
- 수행기간: 2024년 10월 ~ 현재
- 운영 상태: 데이터 파이프라인 / 운영 뷰어 **[양산 운영]**, Known 2-stage 분류와 Unknown 검출 **[실전 현업 데이터, 검증 완료]**, chip-CNN object-id map 보정 구조 **[추가 생성 chip 데이터, 개발 중]**.
- 담당 역할: 본인 60% / 현업 엔지니어 20% / 관리자 20%
- 수행 업무:
  - 데이터 처리: wafer 당 약 1,000만 cell 의 hex 표현을 Grade 0-7 로 풀어내는 변환 루프를 Cython 으로 다시 짜 약 100배 가속을 잡았고, 저장 측은 32색 palette indexed PNG 양자화로 용량 약 75% 감소를 같이 묶었습니다. 운영 뷰어 쪽은 대용량 이미지 병렬 처리와 사내 인증 시스템 연동을 같이 진행했습니다.
  - Stage 1 / Stage 2 AI: ConvNeXtV2 backbone 선정과 fine-tune LR 분리 (block 본체 대비 head 약 10× / 마지막 stage 약 3× 비율) 를 잡았고, ROI YOLO cascade gate 는 wafer-level confidence 뿐 아니라 class별 precision / recall 로 식별한 difficult class 기준을 함께 보도록 설계했습니다. Stage 2 skip wafer 는 일일 sampling 재검증과 Normal 분포 drift 추적으로 false-negative 누적을 차단했습니다.
  - Unknown 검출: self-supervised embedding + HDBSCAN grouping 으로 운영 13 후보 → 7 실제 불량 confirm 흐름을 잡았습니다.
  - 후속 보정: chip-CNN 결과를 wafer 좌표계로 재구성하는 object-id map 보정 모듈 (Stage 2 ROI-YOLO 자리 대체 후보) 까지 본인이 직접 설계 / 구현했습니다.
- 성과: **[실전 현업 데이터]** Known weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split). 단계별 ladder 는 0.78 → 0.87 → 0.92 → 0.95 로 누적되었고, label 부족 조건에서 결정적이었던 두 step 은 backbone 교체 (0.78 → 0.87) 와 cascade 결합 (0.92 → 0.95) 입니다.
- 추가로 **[실전 현업 데이터]** Unknown 검출은 13 후보 group 중 7개가 실제 불량으로 현업 확인되었습니다 (학습 / eval 분리 세부는 §현업 임팩트 박스에 정리).
- **[양산 적용 단계]** 2025년 5월부터 DRAM 전제품 라인 Failbit Map 을 120일치씩 누적 처리 중이며, 일 약 2만 wafer 규모로 가동됩니다.
- **[현업 데이터 평가 완료]** Known 2-stage 분류는 16-class / 1,500 labeled / weighted F1 **0.95** 평가 완료, Unknown 검출은 특정 제품 실전 데이터 1만 장 학습 + 2천 장 eval 에서 13 후보 group 중 **7개 실제 불량 현업 확인** 완료입니다.
- **[전수 자동 적용 단계 확장 계획]** 전제품 / 전수 wafer 상시 자동 추론으로 확장하려면 추가 GPU 자원이 필요하며, AI 센터 GPU 할당 담당자 안내 기준 **2026년 9월** GPU 제공이 예정되어 있습니다. GPU 할당 이후에는 현재 검증된 Known / Unknown 모델을 전수 자동 추론 흐름으로 단계 확장할 계획입니다.
- **[추가 생성 데이터 / 공개 anchor 기반 후속 방법론 개발 중]** (1) Stage 2 ROI-YOLO 대체 후보: 기존 양산 2-stage 의 Stage 1 wafer-level CNN 은 그대로 두고, Stage 2 의 ROI-YOLO 자리를 chip-CNN object-id map 으로 대체할 후속 모듈을 개발 중입니다. 어느 모듈을 deploy 할지는 validation 검증 결과 후 운영 절차에 따라 결정합니다. chip 단위 결과를 wafer 좌표계로 재구성하는 흐름은 `c_{u,v}=crop(x,pos_{u,v})` (256×256 입력), `q_{u,v}=softmax(h_phi(c_{u,v}))`, `M_obj(u,v)=argmax_k q_{u,v,k}` 로 정리되며, M_obj 가 Stage 2 의 posterior p_chip_obj(y | crop(x)) 로 들어갑니다. ROI-YOLO 는 chip 위치를 알 수 없다는 전제 위에서 detection 을 푸는 모듈이라 candidate bounding box 다수에 좌표 회귀와 class 분류를 동시에 학습해야 하지만, chip-CNN object-id map 은 chip 좌표가 fail-map 파이프라인에서 이미 확정된 상태에서 classification 만 수행합니다. 푸는 문제가 단순해진 만큼 chip-level 정확도가 더 높고 (val_f1 **0.9946**) latency 도 짧다는 점이 교체 동기입니다. (2) Unknown 신규 recipe: 추가 anchor 셋 기반 contrastive recipe (MoCo Queue / NV-Retriever / NeCo 등) 와 cross-anchor 일반화 개선을 별도 트랙으로 개발 중입니다. 본 후속 트랙의 정량 metric (chip-CNN obj-id map val_f1 **0.9946** / test_f1 0.9872 / 5-seed 평균 0.9838 ± 0.0092, Unknown cross-anchor ARI 0.4437 등) 은 위 현업 데이터 평가 성과와 섞지 않고 분리 관리합니다.

**P1 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: 일 약 2만 장 wafer / 1시간 주기 처리 가능한 Failbit Map 운영 파이프라인, Known 2-stage weighted F1 0.95, Unknown 13 후보 group 중 7개 실제 불량 현업 확인입니다.
- **후속 개발**: chip-CNN object-id map 보정과 Unknown synthetic benchmark metric 은 심화 질의 대비용 개발 항목으로 분리합니다.
- **한계 및 관리**: Unknown 운영 데이터는 정답 label 이 없어 F1 / ARI 로 주장하지 않고, 후보 group 압축 및 현업 확인 결과로만 보고합니다.

**과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본 과제 도메인은 Failbit Map, DRAM EDS Test Grade 0-7 양자화 이미지, wafer-level failure zone 해석, 대량 wafer 이미지 양산 운영 파이프라인입니다. 이 위에 wafer 분류, ROI 보정, unknown 후보 grouping, 운영 뷰어 표시를 결합했습니다. 핵심은 AI 모델이 신규 불량 후보를 현업 검토 대상으로 올려주고, 엔지니어가 대량 Failbit Map 을 빠르게 조회 / 비교 / 확인할 수 있게 한 부분입니다.

Backbone 선정 측은 본 과제 결함이 특정 zone 이나 국소 영역에 몰리는 경우가 많아 CNN 계열의 local receptive field 와 계층적 feature extraction 이 더 어울린다고 판단했습니다 (자문: 연세대학교 인공지능학과 전해곤 교수). ConvNeXtV2 는 MaxViT 와 동일 F1 0.87 을 유지하면서 파라미터 **26%** / FLOPs **39%** 감소가 따라와 양산 inference 비용에서 유리해 최종 backbone 으로 채택했습니다. cascade 구조는 wafer-level confidence 가 gate 보다 낮을 때만 Stage 2 ROI YOLO 로 넘기는 식이라 throughput 손실은 거의 두지 않으면서 헷갈리는 class 분리력만 선택적으로 보강할 수 있도록 잡았습니다.

ㅁ **P2. Chip Multi-label Classification (CutMix → CutMix + Pair Mask → FCM-PM)**

P2 는 현업의 근본적 제약인 '2-combo 결함 데이터 부족' 을 해결하기 위해, 반도체 도메인 확률분포를 AI 학습에 직접 이식한 '도메인 특화 합성 방법론' 입니다. 본 과제의 핵심 기술적 성과는 단순한 BCE 손실 함수 적용을 넘어, 본 과제 데이터 구조에 맞는 학습 / 평가 파이프라인을 직접 설계한 것입니다.

- **데이터 합성**: FCM-PM 으로 2-combo 결함 학습 신호를 구성했습니다.
- **손실 통제**: Pair Mask 로 합성 background 의 오학습 경로를 분리했습니다.
- **모델 선택**: `val_margin` 기준으로 false-alarm 위험까지 checkpoint 선택에 반영했습니다.
- **추론 최적화**: I13 max-prob gate, 4-bag ensemble 보조 안정성 검토, KD_v7 skip-on-cutmix single student (1× cost) 압축 후보 검토를 대표 성과와 분리해 관리했습니다.

설계 근거는 다음 네 줄로 압축됩니다.

- **기존 loss 변경 한계**: BCE / Focal / ASL 만으로는 2-combo recall 과 false alarm 억제를 동시에 만족시키기 어려움.
- **본 과제 chip Grade 이미지 조건**: 결함 픽셀 의미 보존, failure signal coverage 보장, background 오학습 억제가 동시 필요.
- **본인 결합 (FCM-PM + val_margin selection)**: 세 축을 한 학습 구조에 묶은 결합 설계.
- **내부 ablation 근거**: BCE-only / Focal / ASL / CutMix only 가 bit_F1 과 FAR 균형 동시 만족 실패, Pair Mask 제거 시 Total FAR 100% 까지 치솟아 FCM-PM 유지 근거 확보.

- 과제 개요 및 규모: chip multi-label classification. 학습 원천은 실전 현업 chip failure single 4 class, 2-combo 6 종은 FCM-PM 으로 도메인 분포에 맞춰 합성, Normal / Invalid / OOD negative 4 종은 현업 분포에 가깝게 설계한 controlled benchmark. 합쳐 **16+ class × 약 3,850 chip** 규모.
- 수행기간: 2025년 3월 ~ 현재
- 운영 상태: **[현업 failure chip 원천 + 도메인 확률분포 기반 생성/검증]**, 양산 적용 후보 검증 단계.
- 담당 역할: 본인 80% / 관리자 20%
- 수행 업무:
  - **합성**: CutMix 계열 채택 → chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장.
  - **손실 (Pair Mask)**: binary mask M (M_ij ∈ {0, 1}) 으로 background bit 를 loss 에서 제외하도록 `L = Σ_ij M_ij · BCE(y_ij, ŷ_ij)` 로 재정의.
  - **선택 (val_margin)**: positive bits 평균 score − negative bits 최대 score 차이로 best epoch 결정. 인접 epoch 변동 폭과 4-bag ensemble 안정성 비교로 단일 checkpoint 우연성도 같이 점검.
  - **추론**: I13 (max-prob<0.55 → Normal 강제), pos=0.95 / neg=0.30 비대칭 target, Temperature Scaling, 4-bag (g=2/2/3/4) ensemble 검증.
  - **KD**: KD_v7 skip-on-cutmix single student 는 CutMix 활성 25% batch 에서 KD loss 를 제외해 이전 6개 KD run 의 collapse 를 막았고, I10 기준 bit_F1 0.9265 / Total FAR 0.00% 로 후속 압축 후보성을 확인했습니다.
- data leakage 방지: single failure chip 원천을 chip 단위로 먼저 train / test 로 split 한 뒤 2-combo 와 Pair Mask 합성은 train 원천 chip 만 사용했고, test 원천 chip 은 합성 과정에서 완전히 배제했습니다. 같은 원천 chip 이 train / test 양쪽에 들어가는 경로가 없도록 잡은 부분입니다.
- 수식 요약: multi-label head 는 `p_k = sigmoid(z_k)` 로 두고, FCM-PM 합성은 `x_tilde = Σ_r M_r ⊙ T_r(x_r)`, `y_tilde = OR_r y_r` 로 failure label union 을 만듭니다. Pair Mask loss 는 `L_PM = Σ_{i,k} M_{i,k} · BCE(y_{i,k}, p_{i,k}) / (Σ_{i,k} M_{i,k} + ε)` 로 background bit 를 학습에서 제외했고, checkpoint 는 `val_margin = mean_{k in P+}(p_k) - max_{j in P-}(p_j)` 로 골랐습니다. 운영 false alarm 은 `FAR = FP_negative / N_negative` 로 Normal / Invalid / OOD negative set 에서 따로 봤습니다.
- 성과: **[실전 현업 chip failure 원본]** single 4 class 학습 원천 위에 **[FCM-PM 합성, 실전 chip 원천 결합]** 2-combo 6 종을 도메인 분포로 합성해 학습 / 평가 가능화. FCM-PM 대표 모델 bit F1 **0.9943**, **[현업 분포 기반 합성 평가셋]** Normal / Invalid / OOD negative 에서 false-positive 미검출 (Total FAR 0.00%).
- 이어 Pair Mask 를 제거하면 Total FAR 이 **100%** 로 치솟는 운영 부적합 사례가 확인되어 (background loss masking 이 false-positive 억제의 핵심 요인이라는 직접 근거), FCM-PM 의 손실 마스킹 자체가 결정적 설계 요소임이 정량으로 드러났습니다.
- 추가로 KD_v7 skip-on-cutmix single student 는 1× inference cost 압축 후보로 검토했고, I10 기준 bit_F1 **0.9265** / Total FAR **0.00%** 로 collapse 없이 동작함을 확인했습니다. 다만 단일 FCM-PM val_margin 대표 모델보다 bit_F1 이 낮아 제출 성과가 아니라 후속 압축 후보로 분리합니다. 4-bag ensemble 은 seed / checkpoint 안정성을 확인하기 위한 보조 실험으로만 두고, 제출 대표 성과는 FCM-PM val_margin 단일 모델 bit F1 **0.9943** / Normal / Invalid / OOD negative Total FAR **0.00%** 로 고정했습니다. P2 는 실전 single failure chip 원천 위에 부족한 2-combo 결함을 반도체 도메인 (Grade 0-7 의미, failure 위치 / 강도 / 조합 분포) 으로 합성하고 multi-label 학습 / 평가 설계까지 결합한 방법론입니다.

**P2 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: FCM-PM val_margin 단일 모델 bit_F1 0.9943 / Total FAR 0.00% 입니다.
- **후속 개발**: KD_v7 skip-on-cutmix single student (bit_F1 0.9265 / Total FAR 0.00%), 4-bag ensemble 안정성 비교, 운영 threshold calibration 은 대표 성과와 분리해 관리합니다.
- **한계 및 관리**: P2 결과는 현업 single failure chip 원천에서 출발해 도메인 확률분포 기반으로 구성한 controlled benchmark 기준입니다. 본 P2 의 failure class 는 실제 EDS Failbit Map 에서 관찰되는 failure 형태를 기준으로 구성했습니다. EDS Failbit Map 은 Test 결과가 0~7 Grade 로 표현된 map 이며, **Grade 0 은 양호, Grade 7 은 가장 강한 failure 상태**입니다. 본 P2 benchmark 는 이번 생성 데이터 기준으로 정의한 **single failure 4 class (bank_boundary / fork / scratch / scratch_rot)** 에서 가능한 **2-combo 6종** 을 모두 포함하도록 구성했고, 합성 측은 pixel-level MIN-BLEND 로 Grade 원값을 보존하면서 Full-Cover Mixup 으로 chip 전체 grid 를 cover 했고 Normal 은 per-chip Beta(2, 10) noise 확률분포로 실전 정상 chip 분포를 모사했습니다. 실제 운영에서 추가될 수 있는 신규 failure class 와 장기 운영 분포 변화는 후속 확장 및 검증 대상으로 분리합니다. label 부족 조건에서 2-combo 학습 신호와 false alarm 억제 구조를 검증한 결과로 해석합니다.

**과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본 과제 도메인은 실제 현업 chip 의 Grade 0-7 양자화 이미지, chip 내부 failure 위치를 사전에 알 수 없다는 특성, multi-label failure co-occurrence, 그리고 2-combo failure 사례 수와 label 균형이 부족한 제약입니다. 본인은 이 제약을 아래 구조로 풀었습니다.

- **기술 결합**: Multi-label Image Classification, Synthetic Data Engineering, Machine Learning Optimization, Knowledge Distillation 후보 검토를 하나의 실험 흐름으로 묶었습니다.
- **방법론 진화**: CutMix → CutMix + Pair Mask → FCM-PM (Full-Cover Mixup + Pair Mask) 순서로 본 과제에 신규 적용했습니다.
- **핵심 제어**: Pair Mask background loss masking, val_margin 기반 checkpoint selection, Label Smoothing, Temperature Scaling, I13 inference variant, 4-bag ensemble 보조 안정성 검토를 함께 구성했습니다.
- **평가 설계**: Normal / Invalid / OOD negative 평가셋을 현업 분포에 가깝게 직접 설계해 양산 적용 전 false-positive 리스크를 검증할 수 있게 만들었습니다.

**도메인 제약 극복 및 아키텍처 설계 근거**

- **CutMix 계열 채택**: Mixup 은 입력과 label 을 함께 보간하므로 Grade 0-7 사이에 실재하지 않는 중간 grade 를 만들 위험이 있고, Diffusion 은 충분한 실제 2-combo 분포 없이 쓰면 생성 품질과 label 의미 검증 부담이 큽니다. 원값을 보존해 영역 단위로 붙이는 CutMix 계열을 추천받았고, 본 과제 데이터 특성에 맞춰 채택했습니다 (자문: 연세대학교 인공지능학과 박은병 교수).
- **Full-Cover Mixup 확장**: 일반 CutMix 는 일부 직사각형 영역만 잘라 붙입니다. chip 내부 failure 위치를 사전에 알 수 없는 본 과제에서는 failure signal 이 잘릴 위험이 남아, chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장했습니다.
- **Pair Mask 손실 통제**: binary mask `M` 으로 잘라 붙인 영역만 loss 에 들어가도록 식을 다시 잡았습니다. 이 구조로 background 가 failure 로 오학습되는 경로를 끊었습니다.

```text
L = Σ_ij M_ij · BCE(y_ij, ŷ_ij)
```

- **val_margin 통계적 타당성**: `val_margin = mean(positive) - max(negative)` 로 정의해 가장 강한 false-positive 후보가 checkpoint selection 기준에 직접 반영되게 했습니다. epoch-vs-test_f1 Spearman ρ 는 val_margin +0.56, val_f1 −0.10 으로 갈렸습니다.

ㅁ **P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

본인이 직접 trend chart 를 판정해 온 담당 경력을 합성 episode generator 의 parameter 로 옮겨, AI 학습이 가능한 데이터 자산으로 만든 과제입니다. 데이터 생성 자체가 주 성과입니다.

- 과제 개요 및 규모: **데이터 생성이 주 성과인 과제**. 본인이 BBD담당 / Overlay담당 / CD담당 으로 직접 trend chart 를 판정해 온 업무 경험을 바탕으로 Region 5종 (dense / sparse / very_sparse / thin / missing), Noise 3종 (Gaussian / Laplacian / Correlated), 일반 trend 불량 4종 (mean_shift 평균 이동, standard_deviation 산포 변동, spike 순간 이상, drift 점진 이동) + context 1종, fleet enforcement floor 식을 generator parameter 로 직접 설계.
- 수행기간: 2026년 1월 ~ 현재
- 운영 상태: **[합성 trend chart, PoC]**, 실전 label 부족을 전제로 한 합성 데이터 기반 검증 단계.
- 담당 역할: 본인 70% / 관리자 20% / 동료 엔지니어 (공동 연구자) 10%
- 수행 업무: Region 5단계 계측 밀도 코드화, Noise 3분포 (현업의 설비 상태변동 / 산포 / spike 패턴을 통계 분포로 1:1 매핑), 일반 trend 불량 4종 + context 1종 형상 카탈로그, fleet/target baseline 통계 기반 enforcement floor 식 (`target_baseline_std = max(baseline_std, 0.01)` 로 최소 0.01σ 보장, `target_std ≤ fleet_within_std × 1.2` 로 합성 normal 의 산포 상한 정렬), 정상 / 이상 trend episode 생성, 검증용 baseline 학습 안정화 (val-F1 median smoothing, val-loss spike guard) 까지 본인이 직접 코드화했습니다. 0.01σ 하한과 fleet_within_std × 1.2 상한은 담당 업무에서 정상 산포 안에 묻혀 놓치는 케이스와 일시 튐을 정상으로 잡는 케이스 사이 경계가 어디서 갈리는지 봐 온 경험에서 잡은 값입니다. 동료 엔지니어는 AI 모델 실행, 데이터 정리, 실험 결과 취합을 공동 수행했습니다.
- 성과: **[합성 trend chart, PoC]** train 7,000 + val 1,500 + test 1,500 = 총 10,000 scenarios 를 구성했고, PoC metric 은 test 평가셋 normal 750 + abnormal 5종 각 150 = 총 **1,500 sample** 기준으로 보고합니다.
- 추가로 1차 Binary gate baseline 은 test split 1,500건 / normal_threshold=0.9 기준 Binary F1 **0.9967**, Abnormal Recall **0.9987** (TN/FN/FP/TP=746/1/4/749) 로, 생성 데이터가 정상 / 이상 패턴을 학습 가능한 형태로 담고 있음이 PoC 로 확인되었습니다. 판정식은 `p_anom = sigmoid(f_theta(x))`, `y_hat = 1 if p_anom >= 0.9 else 0` 입니다. 2차 Type classifier 의 mean_shift ↔ drift 혼동 같은 type-level accuracy 는 1차 binary 결과와 분리해 **[합성 trend chart, PoC, 개발 중]** 으로 보고합니다.

**P3 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: 본인 trend 판정 경험을 Region / Noise / anomaly parameter 로 옮겨 총 10,000 scenarios 의 합성 trend chart 데이터 자산을 만들었습니다.
- **후속 개발**: 2차 Type classifier 와 실전 abnormal log 기반 parameter 재보정 trigger 는 PoC 이후 단계로 분리합니다.
- **한계 및 관리**: Binary F1 0.9967 은 합성 데이터의 학습 가능성 확인값이며, 실제 현업 trend log 일반화 성능과 분리해 해석합니다.

**과제 관련 도메인 / AI 기술 / 모델 / 방법론**

본 과제 도메인은 본인 trend 판정 경험으로 자주 본 패턴 (설비 산포, 설비 hunting, 미세 drift, baseline 평탄도 흔들림, spec-in 변동 가능성) 을 합성 데이터 자산으로 옮긴 영역입니다. 그 위에 Synthetic Data Engineering, Time-series / Trend Episode Simulation, Baseline Model Validation 을 결합했습니다. 계측 밀도는 `dense` / `sparse` / `very_sparse` / `thin` / `missing` 5단계로 코드화했고, 설비 상태변동 / 산포 / 일시 튐 / 상관 drift 성격은 `Gaussian` / `Laplacian` / `Correlated` 3분포에 1:1 로 매핑했습니다. 그 위에 `mean_shift` / `std` / `spike` / `drift` 4종 일반 trend 불량과 `context` 1종을 episode parameter 로 구성했고, enforcement floor 두 식 (`max(baseline_std, 0.01)` 와 `target_std ≤ fleet_within_std × 1.2`) 으로 합성 normal 의 통계 분포를 실재 baseline 에 맞추면서 abnormal 강도는 정상 산포에 묻히지 않도록 같이 잡았습니다. 검증 baseline 측은 일시 spike 에 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 checkpoint 안정화 장치로 두었습니다.

이 데이터 자산이 P3 의 주 성과이며, 본인이 도메인 담당 경력을 generator 의 parameter 로 옮긴 부분이 본 과제의 변별점이라고 봅니다. generator parameter 는 본인 담당 경험에서 반복 확인한 trend 분포를 기준으로 정의했습니다. 현재 수치는 실제 현업 trend log 일반화 성능과 분리해 해석하며, generator rule 이 정상 / 이상 구분 신호를 학습 가능한 형태로 담고 있는지 확인한 PoC 결과입니다. 다음 단계는 generator 가 만들지 않은 실전 abnormal log 패턴이 들어왔을 때 그 신호를 parameter 재보정 trigger 로 흘리는 feedback loop 를 설계해 unseen 영역 일반화 검증으로 이어 가는 방향입니다.
