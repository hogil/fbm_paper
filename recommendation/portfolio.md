## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2024년 10월 ~ 현재 | P1. Failbit Map AI 분류 시스템 | 3인 협업, 본인 60% 리딩. DRAM 전제품 라인 양산 운영, 일 약 2만 장 wafer 처리 | 본인이 FBM raw log 적재 / Cython 파싱 / palette PNG 와 chip 좌표 JSON 생성을 짜고, 운영 뷰어 쪽과 연결한 뒤 Known 불량 및 Unknown 불량 AI 모델을 설계 / 학습 / 검증까지 끌고 갔습니다. | 20% | 35% | 45% |
| 2025년 3월 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC, 본인 80% 리딩. 16+ class × 약 3,850 chip controlled synthetic benchmark | chip single / 2-combo 합성, Pair Mask loss masking, FCM-PM 설계, val_margin 기반 best-model 선택, 대표 모델 검증까지 본인이 직접 진행. | 20% | 40% | 40% |
| 2026년 1월 ~ 현재 | P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC | 3인 PoC, 본인 70% 리딩. 10,000 scenarios 구성, test 1,500 sample 평가 | 본인이 직접 trend 를 판정해 온 시기에 본 패턴들을 episode generator parameter 로 코드화, 정상성 보정 식 설계, 검증용 baseline 분류기 구성. | 20% | 45% | 35% |

**※ 제출 대표 성과 기준**

본 문서에서 제출 대표 성과로 읽어야 할 수치는 P1 양산 운영 파이프라인 (일 약 2만 장 / 1시간 주기, Known weighted F1 0.95, Unknown 13 후보 중 7 실제 불량 확인) 과 P2 FCM-PM val_margin 단일 모델 (bit_F1 0.9943 / Total FAR 0.00%) 입니다. Unknown 후속 metric, chip-CNN object-id map, KD는 개발 중 또는 심화 질의 대비 항목으로 분리해 관리합니다.

**핵심 요약**

1. P1은 Failbit Map raw log 를 wafer image, chip coordinate, 운영 뷰어, Known 2-stage, Unknown 후보 group 검토까지 연결한 양산 운영형 AI 시스템입니다.
2. P2는 현업 single failure chip 원천 기반 FCM-PM + Pair Mask loss 로 2-combo label 부족과 false alarm 문제를 동시에 줄인 multi-label 방법론입니다.
3. P3는 본인 trend 판정 경험을 synthetic episode generator 로 코드화해 label 부족 환경의 anomaly 검증 기반을 만든 PoC 입니다.

## 2. 대표 과제 상세 기술서

**ㅁ P1. Failbit Map AI 분류 시스템**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Failbit Map 대량 데이터 파이프라인 + single-label Known 2-stage 분류 + Unknown self-supervised 검출 |
| 수행기간 | 2024년 10월 ~ 현재 |
| 참여인원 | 본인 / 현업 엔지니어 / 관리자 |

**양산 파이프라인 핵심 수치 요약**

- Cython hex-to-grade 변환 재구성으로 데이터 처리 속도를 약 **100배** 끌어올렸습니다.
- 32색 palette indexed PNG 저장으로 이미지 저장 용량을 약 **75%** 줄였습니다.
- 기존 1회 약 48매 조회 중심의 흐름을 일 약 **2만 장 wafer / 1시간 주기** 누적 비교 흐름으로 확장했습니다.
- Known 2-stage 는 weighted F1 **0.95**, Unknown 검출은 특정 제품 실전 데이터 기반 13개 후보 group 중 7개 실제 불량 확인으로 분리해 보고합니다.

**P1 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: 일 약 2만 장 wafer / 1시간 주기 처리 가능한 Failbit Map 운영 파이프라인, Known 2-stage weighted F1 0.95, Unknown 13개 후보 group 중 7개 실제 불량 현업 확인입니다.
- **후속 개발**: chip-CNN object-id map 과 Unknown synthetic benchmark metric 은 개발 중 또는 심화 질의 대비 항목으로 분리합니다.
- **한계 및 관리**: Unknown 운영 데이터는 정답 label 이 없으므로 F1 / ARI / recall 로 주장하지 않고, 후보 group 압축 및 현업 확인 결과로만 보고합니다.

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | FBM 데이터 파이프라인, 운영 뷰어 연동, Known CNN → ROI-YOLO 2-stage, Unknown contrastive 학습, 후속 chip-CNN obj-id map 보정 구조의 설계 / 구현 주도 | 60% |
| 2 | 현업 엔지니어 | 개인정보 비공개 | 관련 현업부서 (공식 기록 대조) | 아이디어 발의, Failbit Map 의미 및 불량 분석 교육, Unknown 후보 13개 중 실제 불량 7개 현업 검증 협업 | 20% |
| 3 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

본인은 이전 담당 경력에서 wafer 단위 Grade 판독을 직접 해온 시간이 있어, Failbit Map 의 의미와 분석 흐름을 짧게 익힌 뒤 바로 AI 설계 단으로 들어갈 수 있었습니다. 분석 엔지니어가 평소 wafer 를 어떤 순서로 읽고 어떤 Grade 가 어디서 몰리는지가 이미 머리 안에 잡혀 있었던 점이 모델 구조 결정과 데이터 흐름 설계의 출발점입니다. 그 이해 위에서 raw log 를 wafer 이미지로 풀어내는 변환 / 저장 / 조회 흐름 (fail-map) 과 대량 이미지 검색을 위한 운영 뷰어를 한 줄로 이었고, 그 위에 Known 2-stage 분류와 Unknown self-supervised 검출을 얹어 분석 부담을 줄이는 운영 시스템 모양이 잡혔습니다. fail-map 은 데이터를 만들어내는 쪽, 운영 뷰어는 만들어진 데이터를 사람이 보는 쪽으로 역할이 나뉘고, 본인은 양쪽 모두에 직접 손을 댔습니다.

데이터 처리 단에서 가장 먼저 짚어낸 부분은 hex 그 자체가 아니라 hex → Grade 0-7 해석이 분석 / AI 의 실제 입구라는 점이었습니다. wafer 한 장에 약 1,000만 cell 이 있고, 그 cell 각각의 hex 값을 Grade 0-7 로 풀어내야 분석 엔지니어가 zone 별 결함을 읽을 수 있고, AI 모델 입력으로도 의미가 살아납니다. 즉 이 변환이 막히면 뒤 흐름은 전부 멈춥니다. 본인은 변환 루프를 Cython 으로 다시 짜서 약 100배 가속을 잡았고, 저장 측은 32색 palette indexed PNG 양자화로 용량을 약 75% 줄여 일 약 2만 장 / 1시간 주기 적재 흐름이 양산 운영으로 가능해졌습니다.

AI 모델 단에서는 ConvNeXtV2 wafer-level classifier 와 ROI YOLO 보정 stage 를 cascade 로 묶었습니다. **[실전 현업 데이터]** 16 class / 1,500 labeled samples / 4:1 stratified split 에서 weighted F1 **0.95** 에 도달했고, Unknown 검출은 13 후보 group 가운데 7개가 실제 불량으로 현업 확인되었습니다 (학습 / eval 세부는 §현업 임팩트 박스에 정리).

Unknown 측은 운영 단계에 정답 label 이 없어 별도 보조 metric 으로 분리해 추적하고 있습니다. **[추가 생성 데이터, 개발 중]** WM-811K 공개 셋 분포 기반 추가 anchor 는 심화 질의 대비용으로 별도 관리하며, 실전 Unknown 운영 성과와 섞지 않습니다.

ROI YOLO 측의 class 확장성 / throughput 한계는 별도 후속 구조로 풀고 있습니다. **[추가 생성 chip 데이터, 개발 중]** chip-CNN 결과를 wafer 좌표계에 다시 그리는 object-id map 보정을 본인이 추가 설계 중이고, 본 모듈은 기존 양산 2-stage 의 Stage 2 ROI-YOLO 자리를 대체할 후속 후보입니다. 양산 deploy 여부는 validation 검증 결과 후 운영 절차에 따라 결정합니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | Failbit Map 은 EDS Test 단계에서 wafer 당 약 1,000만 cell 의 Grade 로 표현되는 초고해상도 데이터라, 분석 엔지니어 수작업 판독만으로는 전수 분석이 불가능합니다. |
| 기존 방식의 한계 | 기존 조회는 1회 약 48매 수준에 머물러 제품 / 시간 / lot 단위 누적 비교가 어려웠고, 등록되지 않은 신규 결함 패턴은 known classifier 만으로는 잡히지 않습니다. |
| 기술적 / 환경적 제약 | label 1,500장 / 16 class 의 작은 학습 set, 일 약 2만 장 wafer 처리, 1시간 주기 적재, 운영 뷰어 응답성, 신규 unknown pattern 검출이 한꺼번에 걸려 있었습니다. |

**ㅁ 기술적 해결 방안**

**[데이터]** 본인이 직접 잡은 end-to-end 흐름은 raw log → wafer 이미지 변환 → 좌표 JSON → 운영 뷰어 노출 → Known 분류 / Unknown 검출 → 현업 검증 까지입니다. 단계별 모듈은 아래와 같습니다.

```
[EDS Test raw log]
        ↓
[원본 적재 / 압축 해제]
        ↓
[fail-map 변환: Cython hex-to-grade + palette PNG + chip 좌표 JSON]
        ↓
[운영 뷰어 (사내 인증 시스템 연동, 대량 wafer 이미지 조회 / 비교, 운영 기여)]
        ↓
[Known 2-stage 분류]
        ├─ Stage 1: ConvNeXtV2 wafer-level classification
        └─ Stage 2: ROI YOLO refinement
        ↓
[Unknown self-supervised 후보 grouping]
        ↓
[운영 뷰어 결과 표시 및 현업 검증]
```

**[알고리즘]** 모델 선택과 결합 구조는 본 과제 데이터 특성에 맞춰 다음과 같이 결정했습니다.

**(1) Stage 1 Backbone — ConvNeXtV2 선택과 fine-tune 설계**

먼저 Transformer 와 CNN 을 같은 split 에서 비교했습니다.

- **도메인 판단**: ViT, Swin 같은 전역 attention 기반 backbone 은 wafer 전체 구조를 보는 데 강합니다. 다만 본 과제의 결함은 특정 zone 이나 국소 chip 영역에 몰리는 경우가 많아, CNN 계열의 local receptive field 와 계층적 feature extraction 이 더 어울린다고 판단했습니다.
- **비교 결과**: 동일 4:1 stratified split 에서 Optuna sweep 으로 hyperparameter 를 정렬한 뒤 측정했습니다. 결과는 ViT 0.81 / Swin 0.84 / EffNetV2 0.85 / MaxViT 0.87 / ConvNeXtV2 0.87 입니다.
- **최종 선택**: ConvNeXtV2 는 MaxViT 와 동일한 F1 0.87 을 유지하면서 파라미터 26% (119.5M → 88.6M), FLOPs 39% (74.2G → 45.1G) 감소가 따라와 양산 inference 비용 측면에서 최종 backbone 으로 채택했습니다 (자문: 연세대학교 인공지능학과 전해곤 교수).
- **과적합 제어**: 본 과제는 label 이 1,500장 / 16 class 로 작은 편입니다. backbone 전체를 풀 미세조정하면 좁은 class 분포에 빠르게 과적합될 수 있어, ConvNeXt block 본체의 학습률은 낮게 두고 분류 head 와 마지막 stage 만 분리해 올렸습니다.
- **fine-tune 비율**: 실 적용 비율은 block 본체 대비 분류 head 약 10×, 마지막 stage 약 3× 수준입니다. 이 비율 분리가 backbone 사전학습 특성을 보존하면서 분류층만 본 과제 분포에 맞춰 적응시키는 결정 포인트였습니다.

**(2) Stage 2 ROI 보정 — cascade gate 와 보정 결정 로직**

Stage 1 만으로는 center 영역 chip 분포가 비슷한 class (center scratch ↔ center scratch_rot 등) 가 헷갈리는 한계가 남았습니다. 본인이 잡은 보완 구조는 wafer-level confidence 뿐 아니라 class별 precision / recall 로 식별한 difficult class 기준을 함께 보며, 필요한 경우에만 ROI YOLO 가 chip 단위 bounding box 와 class 라벨을 다수 출력하고 그 분포로 wafer class 를 다시 추정하는 cascade gate 입니다. confidence ≥ gate 인 wafer 는 Stage 2 를 건너뛰므로 throughput 손실이 거의 발생하지 않고, 헷갈리는 class 의 분리력만 선택적으로 보강할 수 있습니다. cascade gate 가 한 번 흘려보낸 wafer 가 영구적으로 빠지지 않도록, skip 된 wafer 중 일정 비율을 일일 sampling 으로 Stage 2 에 다시 흘려 false-negative rate 를 후행 측정하고, Stage 1 의 Normal / 고신뢰도 class prediction 누적 분포 drift 를 별도 monitoring 으로 추적해 gate 자체를 주기적으로 재조정합니다. 단계별 ladder 는 [구현 성과] 기술 지표에 모았습니다.

**(3) 후속 보정 — chip-CNN object-id map 재구성 (개발 중)**

ROI YOLO 경로는 class 추가 시마다 annotation 과 재학습 비용이 같이 누적되어 운영 확장이 점점 무거워지는 구조였습니다. 반대로 chip-CNN 경로는 chip-level confusion matrix 로 어느 class 가 어느 위치에서 헷갈리는지를 분리해 볼 수 있어 운영 개선 cycle 이 짧아진다는 점이 본인이 본 가장 큰 차이였습니다. 그래서 다음 후속 구조로 chip 단위 classification 결과를 wafer 좌표계에 다시 그리는 object-id map 보정 모듈을 개발 중입니다. 본 모듈은 기존 양산 2-stage 의 Stage 1 wafer-level CNN 은 그대로 두고, Stage 2 의 ROI-YOLO 자리를 chip-CNN object-id map 으로 대체하는 후속 후보입니다. 어느 모듈을 deploy 할지는 validation 검증 결과 후 운영 절차에 따라 결정합니다.

근본적 변별점은 두 모듈이 푸는 문제 자체가 다르다는 점입니다. ROI-YOLO 는 wafer 전체 이미지에서 chip 위치를 알 수 없다는 전제 위에서 detection 을 푸는 모듈이라, 수많은 candidate bounding box 를 두고 각 box 가 failure 인지, 위치가 어디인지 (좌표 회귀), 어느 class 인지 — 세 가지를 동시에 추론해야 합니다. small grid 단위에 결함이 빽빽하게 몰리는 fail-map 특성에서는 box 회귀 오차와 class 분류 오차가 누적되어 정확도가 흔들립니다. 반대로 chip-CNN object-id map 은 chip 좌표가 fail-map 파이프라인에서 이미 확정된 상태에서 시작하므로, 모델은 chip crop 한 장만 받아 classification 만 수행합니다. detection 의 candidate box 생성 + 좌표 회귀 + NMS 단계가 사라져 푸는 문제가 단순해진 만큼 정확도 천장이 높아 V3 obj-only chipgrid 32×32×5 one-hot 기준 val_f1 **0.9946** / test_f1 0.9872 / 5-seed 평균 0.9838 ± 0.0092 까지 도달했고, latency 도 함께 짧아집니다. 이 정량 + 구조 변별이 Stage 2 모듈 교체 개발의 동기입니다. raw map 만 봐서는 비슷해 보이는 wafer 도 chip 단위 failure grid (32×32 one-hot) 로 옮겨 놓으면 center 영역 결함이 즉시 식별되어, 헷갈리는 class 분리력을 한 번 더 끌어올리는 방향으로 잡혀 있습니다.

chip-CNN object-id map 의 내부 흐름은 아래 식으로 정리했습니다.

```
c_{u,v} = crop(x, pos_{u,v})
q_{u,v} = softmax(h_phi(c_{u,v}))
M_obj(u,v) = argmax_k q_{u,v,k}
```

`c_{u,v}` 는 wafer 내 (u,v) 위치의 chip crop (256×256 입력), `h_phi` 는 chip-CNN, `M_obj` 는 chip 위치별 failure family map 입니다. 이 map 이 Stage 2 의 posterior p_chip_obj(y | crop(x)) 로 들어가, 기존 Stage 2 ROI-YOLO 자리를 대체할 수 있는 모듈 형태로 구성됩니다.

**[최적화]** Known 2-stage ladder 와 Unknown 보조 metric ladder 는 [구현 성과] 에 정리했고, label 부족 조건에서 결정적이었던 두 step 은 backbone 교체 (0.78 → 0.87) 와 cascade 결합 (0.92 → 0.95) 입니다. Unknown contrastive 측은 global InfoNCE 만으로는 patch-level 분리력이 부족해 DenseCL 의 patch-level positive matching 을 추가했고, large batch 에서 false negative 가 metric 을 흔드는 부분은 MoCo Queue (4096) 와 NV-Retriever 의 hard-negative 임계 0.72 를 누적으로 잡았습니다. 임계 자체는 0.6 / 0.72 / 0.8 sweep 에서 noise 비율 감소와 cluster 분리력이 둘 다 살아나는 지점이 0.72 라 그 값에서 멈춘 결과입니다. noise % 가 6.20% → 0.52% 까지 떨어진 흐름은 이 누적 결과이며, 이후 Local DenseCL 을 빼고 4-tool 로 재구성한 recipe (noise 1.48%, τ=0.5 후처리 시 0.00%) 가 안정성 / 분리력 균형이 더 좋아 최종 안으로 잡았습니다. Local DenseCL 제거 판단의 근거는, 본 과제처럼 large batch + MoCo Queue 가 같이 들어가는 구성에서는 patch-level positive matching 이 false negative 와 동시에 누적되어 분리력 이득보다 patch matching 잡음 비용이 커지는 구간으로 넘어간다고 본 부분이었습니다.

```
[Input wafer image]
        ↓
[ConvNeXtV2 wafer classifier]
        ↓ confidence < gate
[ROI YOLO refinement]
        ↓
[Known class prediction]
```

학습 / 평가에 사용된 실제 wafer 이미지 예시 (2행 3열):

| Edge-Top Scratch | Edge-Ring Scratch_rot | Center Bank-Boundary (신규) |
|:----------------:|:---------------------:|:---------------------------:|
| <img src="./figures/wafer_edge_top_scratch.png" width="180" /> | <img src="./figures/wafer_edge_ring_scratch_rot.png" width="180" /> | <img src="./figures/wafer_center_bank_boundary.png" width="180" /> |
| **BrokenRing** | **RingDots** | **CrescentArc (신규)** |
| <img src="./figures/wafer_brokenring.png" width="180" /> | <img src="./figures/wafer_ringdots.png" width="180" /> | <img src="./figures/wafer_crescentarc.png" width="180" /> |

Stage 1 만으로 헷갈리는 사례를 Stage 2 ROI YOLO 가 보정하는 흐름:

| Stage 1 (raw wafer) | Stage 2 ROI 영역 | Stage 2 chip 단위 box + class |
|:-------------------:|:----------------:|:-----------------------------:|
| <img src="./figures/wafer_center_scratch.png" height="280" /> | <img src="./figures/p1_roi_crop_real.png" height="280" /> | <img src="./figures/p1_chip_yolo_box_real.png" height="280" /> |

좌측 raw wafer 는 GT 가 center scratch 인데 Stage 1 wafer-level CNN 만 보면 center scratch_rot 으로 오인됩니다. Stage 2 ROI YOLO 가 chip 단위 box 와 class 라벨을 다수 출력하고, 그 분포 majority 로 다시 center scratch 로 잡아주는 구조입니다.

후속 chip-CNN object-id map 재구성 흐름은 다음과 같이 두었습니다.

```
[Wafer image]
        ↓
[chip crop / chip-CNN failure classification]
        ↓
[chip별 failure id]
        ↓
[wafer 좌표계 object-id map 재구성]
        ↓
[Stage 2 모듈 대체 구조 (ROI-YOLO → chip-CNN obj-id map)]
        ↓
[최종 보정 classifier 입력]
```

**[chip-CNN obj-id map 정식 수식]**

위 흐름을 식으로 풀면 다음과 같습니다.

- chip crop: c_{u,v} = crop(x, pos_{u,v})
- chip-CNN posterior: q_{u,v} = softmax(h_φ(c_{u,v}))
- object-id map: M_obj(u,v) = arg max_k q_{u,v,k}

여기서 (u,v) 는 wafer 내 chip 좌표, c_{u,v} 는 256×256 chip crop 입력, h_φ 는 chip-CNN, M_obj 는 wafer 위에 다시 올라가는 chip-level object-id map 입니다. 이 M_obj 가 Stage 2 의 posterior p_chip_obj(y | crop(x)) 로 들어가, 기존 Stage 2 ROI-YOLO 자리를 대체하는 모듈로 운영됩니다. 어느 모듈을 적용할지는 validation 검증 결과 후 운영 절차에 따라 결정합니다.

raw wafer map (좌측 2칸) 과 동일 wafer 의 chip-CNN object-id map (우측 2칸) 비교:

<table>
  <thead>
    <tr>
      <th colspan="2" align="center">raw wafer map</th>
      <th colspan="2" align="center">chip-CNN obj-id map</th>
    </tr>
    <tr>
      <th align="center">center bank-boundary</th>
      <th align="center">center scratch_rot</th>
      <th align="center">center bank-boundary</th>
      <th align="center">center scratch_rot</th>
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

**[정량적/정성적 성과]**

- **기술 지표**
  - **[실전 현업 데이터]** Known 2-stage weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split). 단계별 ladder 는 0.78 (baseline) → 0.87 (ConvNeXtV2 backbone 교체) → 0.92 (+Optuna hyperparameter optimization) → **0.95** (+ROI YOLO 2-stage 보정) 로 누적되었습니다. label 부족 조건에서 backbone 교체와 cascade 결합이 결정적이었습니다.
  - **[실전 현업 데이터]** Unknown 검출은 특정 제품 실전 데이터 1만 장 학습 후, 학습에 쓰지 않은 별도 2,000장에 적용해 13 후보 group 중 7개가 실제 불량으로 현업 확인되었습니다. 정답 label 이 없는 환경이라 정량 metric 대신 현업 확인 결과로 보고합니다.
  - **[추가 생성 데이터, 개발 중 / WM-811K 공개 셋 분포 기반]** Unknown 후속 보조 metric 은 추가 anchor 셋으로 별도 관리합니다. cross-anchor 평가에서는 학습 분포 바깥에서 분리력이 낮아지는 도메인 shift 영향이 보여, 신규 anchor 학습과 분포 보완을 추가 점검 중입니다. 이 항목은 실전 Unknown 운영 성과와 분리한 심화 질의 대비용 근거입니다.
  - **[추가 생성 chip 데이터, 개발 중]** chip-CNN object-id map 보정 구조는 Stage 2 ROI-YOLO 자리를 대체할 수 있는 후속 모듈로 개발 중인 항목입니다. 양산 deploy 결정은 validation 검증 결과 후 운영 절차에 따라 진행됩니다. 아래 수치는 P1 대표 성과가 아니라 ROI-YOLO 이후 class 확장 비용과 annotation 부담을 줄이기 위한 후속 개발 보조 지표입니다.

| chip-CNN object-id map 후속 개발 보조 지표 | 값 |
|----------------------------------|----|
| chip crop 입력 크기 | **256×256** |
| V3 obj-only chipgrid | 32×32×5 one-hot |
| val_f1 | **0.9946** |
| test_f1 | **0.9872** |
| 5-seed 평균 val_f1 | **0.9838** |
| 5-seed val_f1 표준편차 | **± 0.0092** |

- **현업 임팩트**
  - **[양산 적용 단계]** 2025년 5월부터 DRAM 전제품 라인 Failbit Map 을 120일치씩 누적 처리 중이며, 일 약 2만 wafer 규모입니다.
  - **[현업 데이터 평가 완료]**
    - Known 2-stage 분류: 16-class / 1,500 labeled / weighted F1 **0.95** 평가 완료.
    - Unknown 검출: 특정 제품 실전 데이터 1만 장 학습 + 2천 장 eval 에서 13 후보 group 중 **7개 실제 불량 현업 확인** 완료.
  - **[전수 자동 적용 단계 확장 계획]**
    - 전제품 / 전수 wafer 상시 자동 추론으로 확장하려면 추가 GPU 자원이 필요하며, AI 센터 GPU 할당 담당자 안내 기준 **2026년 9월** GPU 제공이 예정되어 있습니다.
    - GPU 할당 이후에는 현재 검증된 Known / Unknown 모델을 전수 자동 추론 흐름으로 단계 확장할 계획입니다.
  - **[추가 생성 데이터 / 공개 anchor 기반 후속 방법론 개발 중]**
    - 현재 P1 대표 성과 weighted F1 **0.95** 는 실제 현업 데이터에서 검증한 **ROI-YOLO 기반 2-stage 결과** 입니다. chip-CNN object-id map 은 추가 생성 chip 데이터 기반으로 개발 중인 **Stage 2 구조적 대체 모듈** 이며, validation 검증 결과와 운영 절차에 따라 deploy 여부를 결정합니다. 이 수치는 P1 대표 성과와 섞지 않고 후속 개발 보조 지표로 별도 관리합니다.
    - ROI-YOLO 는 chip 위치를 모른다는 전제에서 candidate box 생성, 좌표 회귀, class 분류, NMS 를 동시에 풀어야 하지만, chip-CNN object-id map 은 chip positions JSON 으로 chip 좌표가 확정된 상태에서 chip crop classification 만 수행합니다. 문제 정의가 단순해지면서 class 확장 시 annotation 과 재학습 부담을 크게 줄일 수 있어 Stage 2 구조적 대체 모듈로 개발 중입니다.
    - Unknown 검출은 추가 anchor 셋 기반 contrastive recipe (MoCo Queue / NV-Retriever / NeCo 등) 와 cross-anchor 일반화 개선을 별도 트랙으로 개발 중입니다.
    - 본 후속 개발 트랙의 정량 metric (chip-CNN obj-id map val_f1 **0.9946** 등, Unknown cross-anchor ARI 0.4437 등) 은 위 현업 데이터 평가 성과와 섞지 않고 분리 관리합니다.

**P1 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: 일 약 2만 장 wafer / 1시간 주기 처리 가능한 Failbit Map 운영 파이프라인, Known 2-stage weighted F1 **0.95**, Unknown 13 후보 group 중 **7 실제 불량 현업 확인**.
- **후속 개발**: chip-CNN object-id map 보정 구조 (Stage 2 ROI-YOLO 대체 후보), Unknown synthetic benchmark metric 관리, KD / 모델 경량화 후보 검토.
- **한계 및 관리**: Unknown 운영 데이터는 정답 label 이 없어 F1 / ARI 로 주장하지 않고 후보 group 압축과 현업 확인 결과로만 보고합니다. ROI YOLO class 확장성 한계는 Stage 2 대체 후보인 chip-CNN obj-id map 으로 풀고 있으며, 어떤 모듈을 deploy 할지는 validation 검증 결과 후 운영 절차에 따라 결정합니다.

**Unknown contrastive 구성요소 성능표 [심화 질의 대비용 / 추가 생성 데이터, 개발 중]**

| # | Recipe | M1 (capture) | M2 (noise %) | M3 (Completeness) | M4 (Homogeneity) | ARI | AMI | Sil |
|---|--------|--------------|--------------|-------------------|------------------|-----|-----|-----|
| 1 | B0 Global InfoNCE only | 1.000 | 6.20% | 0.9602 | 0.9290 | 0.823 | 0.929 | 0.582 |
| 2 | + Local DenseCL (LW=0.5) | 1.000 | 3.93% | 0.9665 | 0.9351 | 0.851 | 0.939 | 0.514 |
| 3 | + MoCo Queue 4096 | 1.000 | 1.31% | 0.9828 | 0.9365 | 0.846 | 0.950 | 0.573 |
| 4 | + NV-Retriever NEG 0.72 | 1.000 | 0.52% | 0.9852 | 0.9439 | 0.861 | 0.956 | 0.611 |
| 5 | + NeCo 0.2 (B5 5-tool full) | 1.000 | 0.96% | 0.9801 | 0.9403 | 0.8564 | 0.9503 | 0.6104 |
| 6 | 최종 recipe (Local DenseCL 제외 4-tool) | 1.000 | 1.48% | 0.9938 | 0.9424 | 0.859 ± 0.018 | 0.960 | 0.781 |
| 7 | 최종 recipe + 후처리 (noise 임계 τ=0.5) | 1.000 | 0.00% | 0.9938 | 0.9424 | 0.868 ± 0.013 | 0.960 | 0.781 |

이 표는 P1 Unknown 의 실전 현업 확인 성과 (13 후보 중 7 실제 불량 현업 확인) 와는 분리된, 후속 개발 / metric 관리용 synthetic benchmark 결과입니다. 실전 Unknown 에는 정답 label 이 없어 F1 / ARI / recall 같은 정량 metric 이 성립하지 않고, 13/7 현업 확인은 후보 압축 결과이지 분류 metric 이 아닙니다.

DenseCL / MoCo Queue / NV-Retriever / τ=0.5 후처리는 운영 대표 성과가 아니라 embedding recipe 개선을 위한 후속 metric 관리 항목입니다. noise % 가 6.20% → 0.52% 로 떨어진 흐름은 patch-level matching 과 hard-negative 제어를 누적으로 조합한 결과이고, 최종 recipe 는 Local DenseCL 을 제외한 4-tool 구성이 안정성 / 분리력 균형이 더 좋아 별도 관리 중입니다.

**Cross-anchor 일반화 평가 [심화 질의 대비용 / WM-811K 공개 셋 분포 기반 추가 anchor]**

| 지표 | Same-anchor (학습 분포) | Cross-anchor (WM-811K 기반 E set) | 변동 |
|---|---|---|---|
| ARI | 0.859 ± 0.018 | **0.4437** | −0.415 |
| AMI | 0.961 | **0.8507** | −0.110 |
| Completeness | 0.994 | **0.9358** | −0.058 |
| Homogeneity | 0.942 | **0.7859** | −0.156 |
| P1 capture (38 class 발견) | 1.000 | **1.000** | 유지 |
| Noise (failure) | 1.48% | 4.73% | +3.25pp |

학습 분포 바깥 (cross-anchor) 에서는 cluster 분리력 (ARI / Homogeneity) 이 크게 떨어지지만 P1 capture 1.000 은 그대로 유지됩니다. 즉, 후보 group 압축은 계속 작동하나 cluster 내부 정밀도는 도메인 shift 영향을 받는 구조입니다. 본 항목은 실전 Unknown 운영 성과 (13 후보 → 7 실제 불량 confirm) 와 분리한 심화 질의 대비용 근거이며, 신규 anchor 학습과 분포 보완을 후속 개선 항목으로 관리 중입니다.

**ㅁ P2. Chip Multi-label Classification**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Chip multi-label classification — CutMix → CutMix + Pair Mask → FCM-PM |
| 수행기간 | 2025년 3월 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | chip single / 2-combo 합성, CutMix 계열 선정, Pair Mask loss masking 설계, FCM-PM 본 과제 신규 적용, val_margin 기반 best-model selection, Temperature Scaling, pos/neg target asymmetry sweep, I13 inference variant, 4-bag ensemble, KD 압축 후보 검토 | 80% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

P2 는 현업의 근본 제약인 2-combo 결함 데이터 부족을 풀기 위해, 실제 single failure chip 원천을 multi-label 학습 신호로 확장한 과제입니다.

- single failure 원천 데이터는 Grade 의미와 결함 분포를 유지했습니다.
- 2-combo label 부족은 FCM-PM 으로 도메인 분포에 맞춰 보완했습니다.
- Normal / Invalid / OOD negative 평가셋은 현업 분포에 가깝게 직접 설계했습니다.
- 목표는 bit_F1 만 올리는 것이 아니라, false-positive 리스크를 사전에 확인하는 구조를 만드는 것이었습니다.

본 과제의 핵심 기술적 성과는 단순한 BCE 손실 함수 적용을 넘어, 본 과제 데이터 구조에 맞는 학습 / 평가 파이프라인을 직접 설계한 것입니다.

- **데이터 합성**: FCM-PM 으로 2-combo 결함 학습 신호를 구성했습니다.
- **손실 통제**: Pair Mask 로 합성 background 의 오학습 경로를 분리했습니다.
- **모델 선택**: `val_margin` 기준으로 false-alarm 위험까지 checkpoint 선택에 반영했습니다.
- **추론 최적화**: I13 max-prob gate, 4-bag ensemble 보조 안정성 검토, KD_v7 skip-on-cutmix single student (1× cost) 압축 후보 검토를 대표 성과와 분리해 관리했습니다.

기존 BCE, Focal, ASL 같은 loss 변경만으로는 2-combo recall 과 false alarm 억제를 동시에 만족시키기 어려웠습니다. 본인은 아래 세 조건이 같이 필요하다고 봤고, 이를 FCM-PM 과 val_margin checkpoint selection 으로 묶었습니다.

- Grade 0-7 결함 픽셀 의미 보존
- chip 내부 failure signal coverage 보장
- 합성 background 의 오학습 억제

여기에 추가로 4-bag ensemble 과 KD 를 후속 운영성 검토 항목으로 분리했습니다.

- **4-bag (g=2/2/3/4) ensemble**: seed / cover grid 강도 차이에 따른 checkpoint 흔들림을 확인하는 보조 안정성 실험. 단일 FCM-PM val_margin 대표 모델보다 bit_F1 이 낮은 구간이 있어 대표 성능 향상 근거로는 쓰지 않습니다.
- **KD_v7 skip-on-cutmix single student**: single model 수준의 추론 비용으로 압축 가능성을 보는 후보. CutMix 활성 25% batch 에서 KD loss 를 제외해 이전 6개 KD run 의 collapse 를 막았고, I10 기준 bit_F1 0.9265 / Total FAR 0.00% 까지 확인했지만 대표 모델보다 낮아 제출 성과에서는 분리.
- **제출 대표 성과 고정**: FCM-PM val_margin 단일 모델 bit_F1 **0.9943** / Total FAR **0.00%**.

**P2 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: FCM-PM val_margin 단일 모델 bit_F1 **0.9943** / Total FAR **0.00%** 입니다.
- **후속 개발**: KD_v7 skip-on-cutmix single student (bit_F1 0.9265 / Total FAR 0.00%), 4-bag ensemble 안정성 비교, 운영 threshold calibration 은 대표 성과와 분리해 관리합니다.
- **한계 및 관리**: P2 결과는 controlled benchmark 기준으로 해석합니다. 본 P2 의 failure class 는 실제 EDS Failbit Map 에서 관찰되는 failure 형태를 기준으로 구성했습니다. EDS Failbit Map 은 Test 결과가 0~7 Grade 로 표현된 map 이며, **Grade 0 은 양호, Grade 7 은 가장 강한 failure 상태**입니다. 본 P2 benchmark 는 이번 생성 데이터 기준으로 정의한 **single failure 4 class (bank_boundary / fork / scratch / scratch_rot)** 에서 가능한 **2-combo 6종 (bank_boundary+fork / bank_boundary+scratch / bank_boundary+scratch_rot / fork+scratch / fork+scratch_rot / scratch+scratch_rot)** 을 모두 포함하도록 구성했습니다. 따라서 해당 benchmark 범위 안에서는 2-combo 조합 누락 없이 평가했으며, 실제 운영에서 추가될 수 있는 신규 failure class 와 장기 운영 분포 변화는 후속 확장 및 검증 대상으로 분리합니다.

출발점은 CutMix 였습니다. 다만 일반 CutMix 는 본 과제에서 두 가지 문제가 같이 생겼습니다.

- 일부 직사각형만 잘라 붙이면 failure signal 이 잘려 학습 신호가 사라질 수 있습니다.
- 잘라 붙인 영역 바깥 background 까지 failure 로 오학습되어 Normal / Invalid / OOD negative 에서 false-positive 가 폭증할 수 있습니다.

본인은 이를 Full-Cover Mixup 과 Pair Mask 로 나누어 풀었습니다.

- **Full-Cover Mixup**: pixel-level MIN-BLEND (`np.minimum(a, b)`) 로 Grade 원값을 보존하면서 chip 전체 grid 를 cover 합니다. 합성 sanity 는 `failure_pixel_ratio(blended) ≥ max(d_i) - 0.01` 로 두어 입력 chip 의 failure signal 이 잘리지 않도록 잡았습니다.
- **Pair Mask**: 합성 영역과 background 를 구분하는 binary mask M (M_ij ∈ {0, 1}) 으로 loss 를 `L = Σ_ij M_ij · BCE(y_ij, ŷ_ij)` 에 제한해 background 픽셀 / bit 를 학습에서 제외합니다.
- **Pair Mask 제거 ablation**: Total FAR 이 **100%** 까지 치솟아, background loss 가 false-positive 의 핵심 원인임이 정량으로 확인됐습니다.

마지막 쟁점은 best epoch 선택이었습니다. 작은 validation set 에서는 val_f1 이 여러 epoch 에서 같은 값으로 붙어 선택이 흔들렸습니다. 그래서 본인은 `val_margin = mean(score over positive bits) - max(score over negative bits)` 를 기준으로 잡았습니다.

- positive bit 평균은 결함 신호가 충분히 살아 있는지 봅니다.
- negative bit 최대값은 가장 위험한 false-positive 후보를 직접 봅니다.
- epoch-vs-test_f1 Spearman ρ 는 val_margin +0.56, val_f1 -0.10 으로 갈렸습니다.
- run116J val_margin best 자체의 단일 checkpoint 우연성은 인접 epoch (ep5 / ep6 / ep7) bit_F1 변동 폭과 4-bag (g=2/2/3/4) ensemble 보조 실험의 일관성을 같이 두고 점검해 한 epoch 의 운 좋은 결과가 아니라는 것을 확인했습니다.

이후 운영 환경 약 80% Normal 분포에 대응하는 추론 단계를 같이 검토했습니다.

- **I13 inference variant**: max-prob<0.55 → Normal 강제 (80% Normal 분포 사전 정보가 임계 근거).
- **pos=0.95 / neg=0.30 비대칭 target sweep**: 39-cell grid 위에서 negative 측 보수성을 가장 안정적으로 확보한 조합.
- **4-bag (g=2/2/3/4) ensemble**: 보조 안정성 실험 (대표 성과 후보 아님).
- **KD_v7 skip-on-cutmix single student**: 1× inference cost 압축 후보. I10 기준 bit_F1 0.9265 / Total FAR 0.00% 로 collapse 없이 동작했지만 대표 모델보다 낮아 제출 성과에서는 분리.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | chip 내부 failure 위치를 사전에 알 수 없고, single failure chip 만 가지고 multi-label 평가로 확장해야 합니다. |
| 기존 방식의 한계 | 일반 CutMix 는 일부 영역만 잘라 붙여 failure signal 누락과 background 의 failure 오학습이 같이 발생하고, 그 결과 Normal / Invalid / OOD negative 에서 false-positive 가 운영 부적합 수준으로 치솟습니다. |
| 기술적 / 환경적 제약 | 2-combo label 부족, 작은 validation set 의 best epoch plateau, OOD / negative false-positive 억제, 압축 후보의 1× inference cost 제약이 한꺼번에 묶여 있습니다. |

**ㅁ 기술적 해결 방안**

**[데이터]** 학습 원천은 **[실전 현업 chip failure 원본]** single 4 class (bank_boundary / fork / scratch / scratch_rot) 입니다. 그 위에 **[FCM-PM 합성, 실전 chip 원천 결합]** 2-combo 6 종을 반도체 도메인 분포에 맞춰 만들어 multi-label 학습 신호를 확보했고, 평가 측은 여기에 **[현업 분포 기반 합성 평가셋]** Normal + Invalid + OOD 4 종을 더해 single 4 + 2-combo 6 + negative 6 = 16+ class × 약 3,850 chip 규모의 controlled benchmark 를 구성했습니다. 합성 detail 은 다음 세 축으로 잡았습니다. (1) **2-combo 6 종**: bank_boundary+fork / bank_boundary+scratch / bank_boundary+scratch_rot / fork+scratch / fork+scratch_rot / scratch+scratch_rot — 4 single failure class 의 모든 조합을 포함. (2) **Normal 합성**: per-chip Beta(2, 10) noise 확률분포 (평균 ~0.17) 로 palette Grade 0~2 만 사용해 실전 정상 chip 분포를 모사. (3) **Negative 평가셋**: Invalid 는 white interior + orange border + black text, OOD wafer-pattern 은 DiagonalSmear / CenterDonut / CrossScratch / Starburst 4 종, OOD synthetic 은 trained 2 종 + untrained 1 종 결합 4 종으로 설계해 신규 failure family 모사까지 포함했습니다. 실전 평가 환경을 얻기 어려운 조건에서 현업 분포에 맞춰 평가셋까지 직접 설계한 부분이 본 과제 데이터 전략의 핵심입니다.

data leakage 방지를 위해 single failure chip 원천을 chip 단위로 먼저 train / test 로 split 한 뒤, 2-combo 와 Pair Mask 합성은 train 원천 chip 만 사용했습니다. test 원천 chip 은 합성 과정에서 완전히 배제되어 train / test 사이 chip 단위 누수가 없도록 잡았습니다.

**[P2 수식 요약]**

```
p_k = sigmoid(z_k),  k = 1..K

L_BCE = -Σ_k [y_k log p_k + (1-y_k) log(1-p_k)]

x_tilde = Σ_r M_r ⊙ T_r(x_r)
y_tilde = OR_r y_r

L_PM = Σ_{i,k} M_{i,k} · BCE(y_{i,k}, p_{i,k})
       / (Σ_{i,k} M_{i,k} + ε)

val_margin = mean_{k in P+}(p_k) - max_{j in P-}(p_j)

FAR = FP_negative / N_negative
```

softmax 대신 sigmoid multi-label head 를 쓴 이유는 single failure 와 2-combo failure 가 mutually exclusive 가 아니기 때문입니다. FCM-PM 합성은 포함된 failure label 의 union 을 target 으로 두고, Pair Mask loss 는 합성 background 가 failure negative 로 과도하게 학습되는 경로를 끊습니다. FAR 는 Normal / Invalid / OOD negative set 에서 별도로 계산해 운영 false-positive 위험을 직접 보게 했습니다.

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
[I13 inference variant + 4-bag 보조 안정성 / KD 후보 보조 검증]
```

학습 single 4 class 예시 chip (bank_boundary / fork / scratch / scratch_rot):

<p align="left">
  <img src="./figures/chip_eval_bank_boundary_selected.png" width="160" />
  <img src="./figures/chip_eval_fork_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_rot_selected.png" width="160" />
</p>

single 4 class 의 모든 2-조합으로 만든 2-combo 평가 chip 6종:

<p align="left">
  <img src="./figures/chip_combo_bb_fork_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_scratch_scratch_rot_selected.png" width="130" />
</p>

Normal / Invalid / OOD negative 평가셋 예시:

<p align="left">
  <img src="./figures/chip_eval_normal_selected.png" width="130" />
  <img src="./figures/chip_eval_invalid_selected.png" width="130" />
  <img src="./figures/chip_ood_starburst_selected.png" width="130" />
  <img src="./figures/chip_ood_centerdonut_selected.png" width="130" />
  <img src="./figures/chip_ood_crossscratch_selected.png" width="130" />
  <img src="./figures/chip_ood_diagonalsmear_selected.png" width="130" />
</p>

**[알고리즘]** 합성 / 손실 / 선택 / 추론 네 단계로 본 과제 데이터 특성에 맞춰 본인이 직접 설계했습니다.

**(1) 합성 — CutMix 계열 채택과 Full-Cover Mixup 확장**

Grade 0-7 양자화 chip 이미지를 다루는 본 과제에서는 생성 방식 선택이 곧 label 의미 보존 문제였습니다.

- **Mixup 배제**: 입력과 label 을 함께 보간하면 Grade 0-7 사이에 실재하지 않는 중간 grade 가 만들어져 분류기가 그 값을 noise 로 학습할 위험이 있습니다.
- **Diffusion 보류**: 충분한 실제 2-combo 분포 없이 쓰면 생성 품질과 label 의미 검증 부담이 커서, 본 과제의 label 부족 조건에서는 운영 적용 후보로 두지 않았습니다.
- **CutMix 계열 채택**: 영역 단위로 원값을 보존해 붙이는 CutMix 계열을 양자화 의미 보존 측면에서 추천받았고, 본 과제 데이터에 맞춰 채택했습니다 (자문: 연세대학교 인공지능학과 박은병 교수).
- **Full-Cover Mixup 확장**: 일반 CutMix 는 일부 직사각형 영역만 잘라 붙입니다. chip 내부 어디에 failure 가 올지 모르는 본 과제에서는 failure signal 이 잘릴 위험이 남아, chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장했습니다.

**(2) 손실 — Pair Mask 와 background loss 제외**

합성 단계에서 잘라 붙인 영역 / background 영역을 구분하는 binary mask M (M_ij ∈ {0, 1}) 를 같이 만들고, 학습 loss 를 다음과 같이 정의했습니다.

```
L = Σ_ij M_ij · BCE(y_ij, ŷ_ij)
```

M_ij = 1 인 영역만 loss 에 들어가므로 background 픽셀 / bit 는 학습에서 제외되고, Normal / Invalid / OOD negative 에서 background 가 failure 로 오학습되는 경로가 끊깁니다. Pair Mask 를 빼면 Total FAR 이 100% 까지 치솟는 PoC 결과가 본 설계의 직접 근거입니다.

**(3) checkpoint 선택 — val_margin 정의**

val_margin = mean(score over positive bits) − max(score over negative bits)

평균과 최대의 차이로 정의했기에 val_f1 plateau 구간에서도 미세 변동이 남아 best epoch 이 흔들리지 않습니다. negative 측 최대를 쓴 정의 근거는 §개인별 기여 서술 에서 풀어 적었습니다. epoch-vs-test_f1 Spearman ρ 는 val_margin +0.56 / val_f1 −0.10 으로, val_margin 이 ground-truth test_f1 과 양의 일관성을 보였습니다.

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
   val_margin = mean(positive) − max(negative)
            ↓
   클수록 결함과 정상 분리가 안정적
```

**(4) inference / 후속 — I13 variant, ensemble, KD**

운영 환경은 약 80% Normal 분포라서, max-prob<0.55 인 입력을 Normal 로 강제하는 I13 inference variant 를 두어 운영 false-positive 를 추가로 억제했습니다. Normal 분포 80% 라는 운영 사전 정보가 max-prob 임계 0.55 의 직접 근거입니다. pos=0.95 / neg=0.30 비대칭 target sweep 으로 negative 측 보수성을 강화했고, 4-bag (g=2/2/3/4) ensemble 은 부속 실험으로 검증했습니다. g 를 2/2/3/4 로 펼친 이유는 bag 별로 cover grid 강도가 달라 실수 패턴이 겹치지 않게 하기 위함입니다. 그 결과 4-bag majority vote 의 분산이 줄어드는 효과까지 따라옵니다. KD_v7 skip-on-cutmix single student 는 CutMix 활성 25% batch 에서 KD loss 를 제외해 이전 KD collapse 를 막았고, I10 기준 bit_F1 0.9265 / Total FAR 0.00% 로 동작했지만 대표 모델보다 낮아 압축 후보로만 두었습니다.

**[최적화]** 합성 단계에서는 CutMix → CutMix + Pair → FCM-PM 순서로 단계별 효과를 직접 측정했고, false-positive 와 bit_F1 의 trade-off 가 어디서 깨지는지를 아래 ablation 표로 추적했습니다.

- **cover grid sweep**: FCM-PM 의 분할 파라미터는 `g ∈ {2..6}`, `n ∈ {1..8}` 범위에서 sweep 했습니다. eval I3 기준 g=3 / n=1 조합이 bit_F1 0.9960 으로 가장 높았고, g=3 부근에서는 n 변화에 둔감했습니다.
- **g 선택 근거**: g 를 키우면 chip 한 장이 더 잘게 쪼개져 공간 다양성은 올라갑니다. 다만 본 데이터에는 fork 처럼 좁고 긴 결함이 있어 g≥4 부터 fork bit 분리력이 떨어졌고, g=3 부근에서 멈추는 것이 본 과제 데이터에 맞다고 판단했습니다.
- **pos / neg target sweep**: pos=0.95 / neg=0.30 비대칭 target 은 39-cell asymmetric target grid sweep 에서 bit_F1 0.9795 / Total FAR 0.00% 를 가장 안정적으로 동시에 달성한 조합이었습니다. neg target 을 0~0.10 으로 낮추면 OOD FAR 가 다시 올라갔고, pos=1.0 을 유지한 채 neg 만 0.30 이상으로 올리면 bit_F1 자체가 빠졌습니다.
- **checkpoint 선택**: val_f1 best 와 val_margin best 를 같이 보았고, 본 데이터에서는 두 기준의 best epoch 이 인접 구간에 모여 있어 큰 충돌 없이 같이 관리하고 있습니다.

**ㅁ 구현 성과**

**[정량적/정성적 성과]** (P2 성과는 **[현업 failure chip 원천 + 도메인 확률분포 기반 생성/검증]** 위에서 측정한 값입니다. 아래 성과 항목별 데이터 출처는 inline 라벨로 분리 표기합니다.)

- **기술 지표**
  - **[실전 현업 chip failure 원본]** single 4 class (bank_boundary / fork / scratch / scratch_rot) 를 학습 원천으로 두고, **[FCM-PM 합성, 실전 chip 원천 결합]** 2-combo 6 종 + **[현업 분포 기반 합성 평가셋]** Normal / Invalid / OOD 4 종을 합쳐 **16+ class × 약 3,850 chip** 규모의 controlled benchmark 를 구성했습니다.
  - FCM-PM 대표 모델은 bit F1 **0.9943**, Normal / Invalid / OOD negative 평가셋에서 false-positive 미검출 (Total FAR 0.00%) 입니다.
  - Pair Mask 를 제거하면 Total FAR 이 **100%** (Normal / Invalid / OOD negative 평가셋 합산 기준) 로 치솟는 운영 부적합 사례가 PoC 에서 확인되었습니다. background loss 를 masking 한 것이 false-positive 억제의 핵심 요인이라는 직접 근거입니다.
  - val_margin 기반 best-model selection 은 epoch-vs-test_f1 Spearman ρ val_margin +0.56, val_f1 −0.10 으로, false-positive 위험까지 반영하는 best epoch 선택 기준으로 정착되었습니다.
  - I13 inference variant 와 4-bag ensemble 보조 실험을 검증했고, KD_v7 skip-on-cutmix single student 는 I10 기준 bit_F1 0.9265 / Total FAR 0.00% 로 collapse 없이 동작했지만 대표 모델보다 낮아 제출 성과에서 분리해 후속 압축 후보로 관리합니다.

- **현업 임팩트**
  - 실전 single failure chip 원천 위에 부족한 2-combo 결함을 도메인 분포로 합성해 multi-label 학습 / 평가가 가능해졌습니다. 현업에서는 2-combo label 수와 균형을 얻기 어려워 사실상 막혀 있던 분류 문제를, 반도체 도메인 (Grade 0-7 의미와 failure 위치 / 강도 / 조합 분포) 위에서 다시 푼 방법론입니다.
  - 현업 eval 환경을 얻기 어려운 상황에서 Normal / Invalid / OOD negative 평가셋을 현업 분포에 가깝게 직접 설계한 점도 본 과제 변별 포인트입니다. 현업 평가 환경 부재를 도메인 분포 합성과 multi-label 학습 설계로 풀어낸 사례에 해당합니다.
  - 정량으로는 bit F1 0.9943, Normal / Invalid / OOD negative Total FAR 0.00% 로 양산 적용 전 false-positive 리스크 검증을 마쳤습니다.
  - val_margin 기반 best-model 선택은 작은 validation set 의 plateau 흔들림을 제어하는 안전판으로 같이 들어 있습니다.
  - 이 구조는 P1 의 wafer-level 판단을 chip 좌표계로 정밀화하는 후속 기반으로도 이어집니다.
  - 본 방법론의 변별 포인트는 실전 single failure chip 원천 + 반도체 도메인 분포 기반 결합 합성 + multi-label 학습 / 평가 설계 결합이라는 한 줄 흐름입니다.

**P2 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: FCM-PM val_margin 단일 모델 bit_F1 **0.9943** / Normal / Invalid / OOD negative Total FAR **0.00%**.
- **후속 개발**: KD_v7 skip-on-cutmix single student 1× cost 압축 후보 (bit_F1 0.9265 / Total FAR 0.00% 로 collapse 방지 확인), 4-bag ensemble seed / cover-grid 안정성 보조 실험, 운영 threshold calibration.
- **한계 및 관리**: 본 결과는 controlled synthetic benchmark 기준이며 실전 장기 운영 전체 2-combo 분포를 완전히 대표한다고 주장하지 않습니다. label 부족 조건에서 2-combo 학습 신호와 false alarm 억제 구조를 검증한 결과로 해석합니다. 4-bag ensemble 은 보조 안정성 실험으로만 두고 대표 성과 후보에서 분리합니다.

**Multi-label 학습 recipe 성능표 [현업 failure chip 원천 + 도메인 확률분포 기반 생성/검증]**

| # | Recipe | bit_F1 | Total FAR | Latency | Throughput | Params | 핵심 해석 |
|---|--------|--------|-----------|---------|------------|--------|-----------|
| 1 | Baseline (BCE+LS, no cutmix) | 0.1093 | 99.47% | 1x | 1x | 1x | 2-combo 신호를 거의 학습하지 못해 기본 multi-label 구조만으로는 운영 후보가 되기 어렵습니다. |
| 2 | Focal loss (sigmoid focal, no cutmix) | 0.7980 | 45.72% | 1x | 1x | 1x | hard sample 대응은 됐지만 Normal / Invalid / OOD false-positive 가 남았습니다. |
| 3 | ASL (asymmetric, LS 0, no cutmix) | 0.6435 | 100.0% | 1x | 1x | 1x | class imbalance 손실만으로는 negative rejection 이 무너졌습니다. |
| 4 | CutMix only (random rect, no pair) | 0.9359 | 42.05% | 1x | 1x | 1x | bit_F1 은 회복됐지만 background 까지 failure 로 오학습되어 FAR 이 운영 부적합 수준에 남았습니다. |
| 5 | CutMix + Pair (random rect + masked) | 0.9256 | 100.0% | 1x | 1x | 1x | mask 만 붙이면 임계 수렴으로 흔들렸고, failure signal coverage 보장이 같이 필요했습니다. |
| 6 | FCM-PM val_f1 criterion (run116J ep1) | 0.9422 | 0.00% | 1x | 1x | 1x | 같은 FCM-PM recipe 에서 val_f1 기준으로 고른 checkpoint 입니다. |
| 7 | FCM-PM val_margin criterion (run116J ep6) | 0.9943 | 0.00% | 1x | 1x | 1x | 제출 대표 모델입니다. bit_F1 과 false-positive 억제가 동시에 맞았습니다. |
| 8 | 4-bag majority 2/4 ensemble※ | 0.9167 | 4.05% | 4x | 1/4x | 4x | 단일 FCM-PM val_margin 대표 모델 대비 bit_F1 / FAR 두 지표가 다 좋지 못한 보조 안정성 실험입니다. bag 별 cover-grid 강도 (g=2/2/3/4) 를 달리해 실수 패턴 겹침을 확인했고, 4x latency / 1/4x throughput 이라 운영 후보는 단일 FCM-PM val_margin 모델로 고정했습니다. |
| 9 | KD_v7 skip-on-cutmix single student | 0.9265 | 0.00% | 1x | 1x | 1x | CutMix 활성 25% batch 에서 KD loss 를 제외해 이전 6개 KD run 의 collapse 를 막았습니다. 단일 FCM-PM val_margin 대표 모델보다 bit_F1 이 낮아 후속 압축 후보로만 관리합니다. |

※ 4-bag ensemble row 는 seed / cover-grid / checkpoint 조건이 다른 보조 안정성 실험이며, 다른 요약 자료(01_career_profile.md / 02_ai_portfolio.md)에 기재된 ensemble 수치와는 동일 실험이 아닙니다. 제출 대표 성과는 단일 FCM-PM val_margin 모델 bit_F1 0.9943 / Total FAR 0.00% 로 고정합니다.

row 9 KD_v7 skip-on-cutmix 는 1× inference cost 압축 후보의 측정값으로, 이전 KD collapse 를 해소했지만 row 7 대표 모델보다 bit_F1 이 낮아 제출 대표 성과에서 제외합니다. 표 row 1~7 을 같이 보면 CutMix 단독은 bit_F1 회복은 되어도 FAR 기준에서 운영 부적합이었고, FCM-PM + val_margin 으로 와서야 bit_F1 0.9943 / Total FAR 0.00% 의 균형이 맞춰졌습니다.

본 P2 benchmark 는 이번 생성 데이터 기준으로 정의한 single failure 4 class 에서 가능한 2-combo 6종을 모두 포함하도록 구성했습니다. 따라서 해당 benchmark 범위 안에서는 2-combo 조합 누락 없이 평가했으며, 실제 운영에서 추가될 수 있는 신규 failure class 와 장기 운영 분포 변화는 후속 확장 및 검증 대상으로 분리합니다. 본 결과는 현업 single failure chip 원천에서 출발해 도메인 확률분포 기반으로 구성한 controlled benchmark 기준이며, label 부족 조건에서 2-combo 학습 신호와 false alarm 억제 구조를 검증한 결과로 해석합니다.

이 흐름이 가리키는 본인 결론은 분명합니다.

- Focal 이나 ASL 처럼 loss 만 바꾸는 접근은 2-combo recall 과 false-positive 억제를 동시에 만족시키지 못했습니다.
- 단순 CutMix 도 chip 내부 failure 위치를 사전에 모르는 Grade 0-7 양자화 이미지에서는 충분하지 않았습니다.
- 결정적 두 축은 failure signal coverage 보장 (Full-Cover Mixup) 과 합성 background 의 loss 분리 (Pair Mask) 였습니다.
- 그 두 축을 한 학습 구조에 결합한 것이 FCM-PM 이고, val_margin 으로 운영 false-positive 위험까지 selection 기준에 넣어 운영 적용 후보로 가져갔습니다.

추가 보조 [추가 생성 chip 데이터, PoC]: Pair Mask 변형 2종 (Complement + Pair Mask, Single Pair Mask) 도 bit_F1 0.8743 / Total FAR 100% 로 negative false-positive 를 억제하지 못해, Full-Cover Mixup 과 Pair Mask 결합 (FCM-PM) 이 필요한 이유를 보조로 확인했습니다.

**ㅁ P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Trend episode 데이터 생성 기반 Anomaly-detection 검증 PoC |
| 수행기간 | 2026년 1월 ~ 현재 |
| 참여인원 | 본인 / 관리자 / 동료 엔지니어 (공동 연구자) |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | trend episode 합성 generator 설계, Region 5종 / Noise 3종 / trend 불량 4종 + context 1종 parameter 코드화, 정상 산포 기준 enforcement floor 식 설계, 1차 Binary gate 검증 PoC 설계 / 구현 | 70% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |
| 3 | 동료 엔지니어 (공동 연구자) | 개인정보 비공개 | 관련 엔지니어 조직 (공식 기록 대조) | AI 모델 실행, 데이터 정리, 실험 결과 취합 | 10% |

**ㅁ 개인별 기여 서술**

P3 의 본인 기여는 데이터를 만들어 내는 쪽입니다. 본인이 BBD담당 / Overlay담당 / CD담당 으로 직접 trend chart 를 판정해 온 업무 경험에서, 특정 설비의 산포가 fleet 평균 산포보다 약간만 커져도 lot 단위로 spec-in 변동이 이어지는 패턴, 일시 튐 한두 점이 후공정 정렬에 영향을 주는 패턴, 미세 drift 가 baseline 평탄도를 흔들어 후반에 spec-in 으로 넘어가는 패턴을 반복해서 봐 왔습니다. 그래서 정상 chart 의 통계 분포와 설비 산포 / 일시 튐 / drift 가 어느 강도에서 실제 spec-in 변동을 일으키는지 알고 있었고, 그 판단 기준을 synthetic trend episode generator 의 parameter 로 직접 옮겨 코드화했습니다. Binary gate + Type classifier 는 만들어 낸 데이터가 정상 / 이상 패턴을 학습 가능한 형태로 담고 있는지 확인하기 위한 검증용 baseline 으로 두었습니다 (실전 현업 검증과 분리). 동료 엔지니어는 AI 모델 실행, 데이터 정리, 실험 결과 취합을 공동 수행했습니다.

판단 근거 측에서는 Region 별 계측 밀도 차이, 설비 산포 / 일시 튐 / 상관 drift 의 성격 차이, 일반 trend 불량 4종과 context 1종이 실재 spec-in 변동을 일으키는 강도 구간을 본인이 미리 알고 있었고, 합성 normal 이 실전 baseline 통계 안에 있으면서도 abnormal 강도는 정상 산포에 묻히지 않아야 한다는 두 조건도 같은 경험에서 나왔습니다. 구체 parameter / 식 / 단계 흐름은 [기술적 해결 방안] 과 다이어그램에 모았습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 같이 봐야 합니다. |
| 기존 방식의 한계 | 실전 abnormal data 는 양과 label 균형 확보가 어려운 위에 수작업 chart 판독까지 의존하다 보니 초보자 누락과 모니터링 시간 부담이 같이 누적됩니다. |
| 기술적 / 환경적 제약 | 실전 label 부족을 전제로 trend domain knowledge 를 합성 데이터 parameter 로 옮기는 단계가 먼저 풀려야 뒤 단계 검증이 가능합니다. |

**ㅁ 기술적 해결 방안**

본인이 잡은 흐름은 도메인 지식의 코드화 → 정상성 보장 → 학습 가능성 검증 세 단계입니다.

먼저 위 담당 경험에서 쌓은 trend 분석 기준 — Region 별 계측 밀도, 설비 산포 / 헌팅 / drift 등 통계 분포, 일반 trend 불량 4종 + context pattern 1종 — 을 episode generator 의 parameter 로 직접 옮겨, 실전 label 부족 상황에서도 학습이 가능한 데이터 자산을 확보하는 것을 1단계로 두었습니다. P3 의 핵심 가치는 현업 도메인 지식을 AI 데이터 generator 의 parameter 로 코드화한 데 있고, 이를 통해 실전 abnormal 데이터가 부족한 조건에서도 정상 / 이상 패턴을 학습 가능한 형태로 만들었습니다.

이어 합성 데이터가 실전 baseline 과 통계 분포가 일치하면서도 이상 강도가 정상 산포에 묻히지 않도록 두 통계 조건 (`target_std ≤ fleet_within_std × 1.2`, `target_baseline_std = max(baseline_std, 0.01)`) 을 enforcement floor 로 결합했습니다. fleet 평균 산포 안에 normal chart 를 가두고, abnormal 강도는 0.01σ 하한으로 lift 되도록 동시에 잡아준 식입니다.

마지막으로 위 합성 데이터가 학습 가능한 자산인지 확인하기 위해 1차 Binary gate (정상 / 이상) 와 2차 Type classifier (4 + context) 를 baseline 으로 같이 돌렸습니다. 두 baseline 은 모델 차별성을 주장하는 운영 후보가 아니라, generator 가 만든 데이터의 학습 가능성을 점검하기 위한 검증 도구입니다.

전체 흐름을 도식으로 정리하면 다음과 같습니다.

```
[본인 trend 판정 경험을 generator parameter 로 코드화]
        ↓
[Region 5종: dense / sparse / very_sparse / thin / missing]
        ↓
[Noise 3종: Gaussian / Laplacian / Correlated]
        ↓
[일반 trend 불량 4종 + context 1종]
        ↓
[fleet/target baseline enforcement floor]
[target_baseline_std = max(baseline_std, 0.01) 최소 0.01σ 보장]
[target_std ≤ fleet_within_std × 1.2 정렬]
        ↓
[224×224 trend chart PNG rendering]
        ↓
[검증용 baseline: 1차 Binary gate + 2차 Type classifier]
        ↓
[생성 데이터 학습 가능성 확인]
```

합성 trend chart 예시 (정상 + 일반 trend 불량 4종 + context 1종):

| Normal | Mean Shift | Standard Deviation Change |
|:------:|:----------:|:-------------------------:|
| <img src="./figures/trend_normal.png" width="200" /> | <img src="./figures/trend_mean_shift.png" width="200" /> | <img src="./figures/trend_standard_deviation.png" width="200" /> |
| **Spike** | **Drift** | **Context** |
| <img src="./figures/trend_spike.png" width="200" /> | <img src="./figures/trend_drift.png" width="200" /> | <img src="./figures/trend_context.png" width="200" /> |

검증 baseline 학습 측의 checkpoint 안정화에는 일시 spike 에 선택이 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 같이 두었습니다.

**ㅁ 구현 성과**

**[정량적/정성적 성과]** (P3 성과는 모두 **[합성 trend chart, PoC]** 기반이며, 주 성과는 데이터 생성 자체입니다.)

- **기술 지표**
  - 시나리오 구성: train 7,000 + val 1,500 + test 1,500 = 총 10,000 scenarios. test 평가셋은 normal 750 + abnormal 5종 각 150 = 총 **1,500 sample** 입니다.
  - 도메인 코드화: Region 5단계 (`dense` 70-100%, `sparse` 40-70%, `very_sparse` 20-35%, `thin` 10-20%, `missing` 0%), Noise 3분포 (Gaussian 0.80 / Laplacian 0.15 / Correlated 0.05). 0.80 / 0.15 / 0.05 비율은 본인이 담당 업무에서 자주 본 형태부터 잡은 결과입니다. Noise 분포 의미는 Gaussian 이 설비 chamber 의 thermal / mechanical 정상 산포, Laplacian 이 설비 hunting 에서 종종 보이는 두꺼운 꼬리 형태, Correlated 가 후공정 align 영향이 시간축으로 이어지면서 누적되는 drift 형태에 각각 대응합니다. 일반 trend 불량 4종 (mean_shift / std / spike / drift) + context 1종, 224×224 chart PNG 12-25 episode mix.
  - 정상성 보정: `target_baseline_std = max(baseline_std, 0.01)` 와 `target_std ≤ fleet_within_std × 1.2` 두 식을 enforcement floor 로 같이 적용해, 합성 normal 의 통계 분포는 실전 baseline 에 맞추고 이상 강도는 정상 산포 안에 묻히지 않도록 하한을 두었습니다.
  - 1차 Binary gate baseline: test 1,500건, normal_threshold=0.9 기준 Binary F1 **0.9967**, Abnormal Recall **0.9987**, TN/FN/FP/TP=746/1/4/749. 생성 데이터가 정상 / 이상 패턴을 학습 가능한 형태로 담고 있는지 확인한 참고 수치입니다. 판정식은 `p_anom = sigmoid(f_theta(x))`, `y_hat = 1 if p_anom >= 0.9 else 0` 입니다. 5-seed 안정성 검증에서도 pc600_s1 / pc700_s2 기준 F1 **0.9987** (TN=748 / FN=0 / FP=2 / TP=750) 으로 일관된 분리 성능을 확인했고, normal_threshold sweep (0.5 / 0.9 / 0.99 / 0.999) 에서도 F1 0.9987 로 임계에 둔감한 결과였습니다.
  - 2차 Type classifier 는 binary TP subset (n=749) 기준 type-level accuracy **0.7303** 수준으로, type 별 분리력이 갈립니다 [합성 trend chart, PoC, 개발 중].
    - context: 150/150 (100%, 분리 양호)
    - spike: 99/150 (66%, standard_deviation 로 51건 흘려)
    - drift: 42/150 (28%, mean_shift 로 97건 혼동)
    - 주 혼동 쌍은 drift ↔ mean_shift (97건) / spike ↔ standard_deviation (51건) 이며, 1차 binary 안정성과 분리해 보고합니다.

- **현업 임팩트**
  - 본인 담당 경력에서 쌓은 trend 분석 경험을 synthetic generator parameter 로 직접 옮긴 덕에, 실전 abnormal label 부족 상황에서도 AI 검증을 시작할 수 있는 데이터 자산이 마련된 상태입니다. L1 trend 모니터링의 수작업 부담과 초보자 누락, spec-in 변동 위험을 완화하는 1차 스크리닝 기반이 됩니다.
  - 본 baseline 수치는 생성 데이터의 학습 가능성을 보는 1차 PoC 지표이며, 양산 적용 후보 모델은 PoC 이후 단계에서 다시 잡습니다.
  - 이 수치는 실제 현업 trend log 일반화 성능과 분리해 해석합니다. 본인이 만든 generator rule 이 정상 / 이상 구분 신호를 학습 가능한 형태로 담고 있는지 확인한 PoC 결과이며, 다음 단계는 generator 가 만들지 않은 실전 abnormal log 를 parameter 재보정 trigger 로 흘려 unseen 영역 일반화 검증으로 이어가는 흐름입니다.

**P3 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: 본인 trend 판정 경험을 Region / Noise / anomaly parameter 로 코드화해 총 10,000 scenarios 의 합성 trend chart 데이터 자산을 만들었습니다.
- **후속 개발**: 2차 Type classifier 와 실전 abnormal log 기반 parameter 재보정 trigger 는 PoC 이후 단계로 분리합니다.
- **한계 및 관리**: Binary F1 0.9967 은 합성 데이터의 학습 가능성 확인값이며, 실제 현업 trend log 일반화 성능과 분리해 해석합니다.
