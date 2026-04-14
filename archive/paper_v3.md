# 반도체 웨이퍼 불량 분석을 위한 도메인 지식 기반 등록/미등록 통합 파이프라인

**A Domain-Knowledge-Driven Unified Pipeline for Registered and Unregistered Wafer Defect Analysis**

---

## 초록

반도체 제조 공정에서 Failbit Map 기반 웨이퍼 불량 분석은 수율 관리와 이상 원인 추적의 핵심 과제이다. 초기에는 기등록 불량을 대상으로 단일 CNN 분류기를 구축하는 접근에서 출발하였으나, 실제 현업에서는 라벨 노이즈, 신규 불량의 돌발 발생, 칩 단위 계측값 연계, 분석 UI 기반 검토가 동시에 요구됨을 확인하였다. 이에 본 연구에서는 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, 사용자 검토를 하나의 흐름으로 연결하는 도메인 지식 기반 복합 파이프라인을 제안한다. 등록 불량 경로에서는 Optuna 기반 하이퍼파라미터 탐색과 ConvNeXtV2 기반 학습 최적화를 통해 weighted F1를 0.78에서 0.92까지 향상시켰고, 이후 Grad-CAM 기반 ROI 추출, 클래스별 spatial prior, YOLO 이차 검증을 결합한 2단계 구조를 통해 최종 0.95를 달성하였다. 미등록 불량 경로에서는 자기지도 대조 학습과 HDBSCAN을 결합하여 unknown defect 후보를 자동 군집화하고, 대표 이미지 및 cluster summary를 생성하여 전문가 검토와 신규 라벨 등록을 지원하였다. 또한 dual-bucket 데이터 수집, Cython 기반 초고속 설비 로그 가공, palette-indexed PNG 생성, positions JSON 기반 칩 좌표 및 FTN/QTN 계측값 정합, BIN/FBT/QVL 시각화 UI를 구축함으로써 향후 이미지-계측 융합 기반 multimodal 불량 분석으로 확장 가능한 운영형 데이터 기반을 마련하였다.

---

## 1. 서론

웨이퍼 Failbit Map은 메모리 테스트 결과를 공간적으로 표현한 데이터로서, 불량의 위치, 분포, 방향성, 밀집도와 같은 정보를 직접적으로 담고 있다. center, edge_ring, donut, scratch와 같은 대표 패턴은 단순한 시각적 모양이 아니라 공정 이상 원인과 연결되는 공간적 의미를 가지므로, 이를 자동 분류하는 기술은 반도체 제조 현장에서 높은 실용성을 가진다.

본 연구는 처음에 기등록 불량 클래스만을 대상으로 CNN 기반 자동 분류기를 구축하는 문제로 시작하였다. 그러나 실제 현업 적용 과정에서 세 가지 한계가 분명히 드러났다. 첫째, 라벨 등록과 유지가 전문가 의존적이어서 학습 데이터에 라벨 오류와 라벨 지연이 누적된다. 둘째, 신규 제품 및 공정 변화로 인해 기존 라벨 체계에 없는 unknown 불량이 발생하며, closed-set classifier는 이를 기존 클래스 중 하나로 강제 분류한다. 셋째, 실제 분석 업무는 분류 결과만 확인하는 것이 아니라 웨이퍼 맵, 칩 좌표, 계측값, 시각화 UI, 수동 라벨링과 결합된 운영 workflow로 수행된다.

이에 따라 본 연구는 단일 분류 모델의 성능 개선을 넘어서, 데이터 생성부터 등록 불량 분류, 미등록 불량 군집화, UI 기반 검토와 라벨 확장까지 연결되는 통합 파이프라인으로 범위를 확장하였다. 특히 본 시스템은 도메인 지식의 구조적 반영을 핵심 설계 원칙으로 삼았다. 웨이퍼 불량은 일반 자연영상과 달리 절대 위치와 방향이 중요한 경우가 많으므로, ROI 추출, 증강 전략, cluster filtering, palette 표현, 칩 좌표 정합에 모두 이러한 제약을 반영하였다.

본 논문의 기여는 다음과 같다.

1. Optuna 기반 학습 최적화와 도메인 지식 기반 ROI 보정을 결합하여 등록 불량 분류 성능을 `0.78 -> 0.92 -> 0.95`로 향상시킨다.
2. Contrastive Learning과 HDBSCAN을 이용해 미등록 불량을 자동 군집화하고, 전문가 검토 기반 라벨 확장 루프를 제안한다.
3. Dual-bucket 수집, Cython 기반 로그 가공, palette-indexed PNG, positions JSON, FTN/QTN 및 LT/TM/yield/sys 저장 구조를 통해 multimodal 확장을 위한 운영형 데이터 파이프라인을 구축한다.

---

## 2. 제안 시스템

### 2.1 데이터 생성 파이프라인: Dual Bucket + Cython + Palette PNG

본 시스템의 입력 데이터는 단일 이미지 파일이 아니라, 서로 다른 소스에서 수집되는 공정 로그와 계측 로그의 결합 결과이다. Bucket A에는 primary fail map raw 파일이 저장되고, Bucket B에는 칩 단위 계측 정보가 저장된다. 두 bucket의 파일명 규칙과 시간 차이를 이용해 동일 wafer를 매칭한 뒤, 병렬 다운로드 및 압축 해제를 수행하고, Cython 기반 hex 변환 및 로그 파싱을 거쳐 PNG 이미지와 positions JSON을 동시에 생성한다.

```text
          Bucket A (.Z)                    Bucket B (.gz)
     fail map raw / header              chip-level measurement
                |                               |
                +----------- filename/time ------+
                            matching
                                |
                                v
                  Parallel download + decompress
                                |
                                v
                    Cython-based fast log parsing
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
      Palette-indexed wafer PNG         positions JSON
      (grade / border / BIN color)      (rect / grid / f/q / meta)
                 |                             |
                 +--------------+--------------+
                                |
                                v
                     Training / UI / Analysis
```

**Figure 1.** Dual-bucket 기반 데이터 생성 파이프라인. Bucket A와 Bucket B를 파일명 및 시간 정보로 매칭한 뒤, 병렬 다운로드와 Cython 기반 파싱을 통해 palette PNG와 positions JSON을 생성한다.

Palette PNG는 색 자체보다 인덱스 의미가 중요한 `32-color 8-bit indexed PNG` 구조를 사용한다. grade 0~7, 배경, 텍스트, 기본 border, BIN-specific border를 고정 인덱스로 관리함으로써, UI에서는 `IDAT`의 인덱스 기반 픽셀 구조를 유지한 채 `PLTE` 청크만 교체하여 색상 scheme, composite, measure overlay를 빠르게 전환할 수 있다. 이 방식은 RGB full-color PNG 대비 wafer map 형태 정보를 유지하면서 저장 용량을 줄일 수 있고, 무엇보다 현업 사용자마다 defect별 선호 색상이 다르다는 요구를 반영해 사용자별 개인 색상 scheme을 동일 원본 이미지에 즉시 적용할 수 있다는 장점이 있다. positions JSON에는 칩별 `rect`, `grid_edges`, `b`, `f`, `q` 정보와 웨이퍼 레벨 `yield`, `sys`, `gd`, `lt`, `tm`이 함께 저장되며, 이 구조는 이후 분류기, UI, 통계 분석이 동일한 좌표계를 공유하도록 만든다.

여기서 이미지 포맷 선택 자체가 중요한 도메인 설계가 된다. JPEG는 자연영상에 적합한 손실 압축 방식이므로 wafer map의 sharp한 경계와 discrete semantic pattern을 손상시킬 수 있다. 일반 RGB PNG는 무손실이지만 각 픽셀에 RGB가 직접 고정되어 있어 사용자별 색상 변경이나 grade/bin 의미 유지 측면에서 비효율적이다. 반면 palette-indexed PNG는 픽셀에 `색`이 아니라 `의미 인덱스`를 저장하므로, wafer map을 사진이 아니라 `grade/bin 상태 지도`로 다룰 수 있게 한다. 즉 본 연구의 palette PNG 채택은 단순한 저장 포맷 선택이 아니라, 반도체 wafer map의 본질이 연속 톤 영상이 아니라 이산적 상태의 공간 배치라는 도메인 지식을 표현 계층에 반영한 결과이다.

아래는 palette PNG의 개념 구조이다.

```text
Palette PNG
 ├─ index 0~7   : grade colors
 ├─ index 8     : background
 ├─ index 9     : text
 ├─ index 10~11 : default / invalid border
 ├─ index 12~23 : BIN-specific border colors
 └─ pixel data  : chip fill + border encoded by index

positions JSON
 ├─ chips[i].rect / grid_edges
 ├─ chips[i].b
 ├─ chips[i].f / chips[i].q   <- FTN/QTN
 ├─ wafer meta: yield / sys / gd / lt / tm
 └─ bucket_b_match summary
```

**Figure 2.** 32색 palette PNG와 positions JSON의 역할 분담. PNG는 PLTE 교체 기반의 빠른 recolor와 용량 효율을, JSON은 좌표 및 계측 정합을 담당한다.

### 2.2 등록 불량 분류 경로: baseline 0.78에서 optimized 0.92까지

등록 불량 분류는 초기 baseline CNN에서 시작하여, 고성능 backbone 도입과 학습 최적화를 통해 성능을 단계적으로 향상시켰다. 특히 서버 환경에서는 Optuna 기반 하이퍼파라미터 탐색을 수행하여 learning rate, weight decay, scheduler, dropout, augmentation 강도, label smoothing, batch size, optimizer 조합 등을 폭넓게 실험하였다. 이러한 탐색은 수동 실험보다 훨씬 빠르게 유효 설정을 좁히는 데 기여했으며, 최종적으로 등록 불량 1-stage classifier의 weighted F1를 0.78에서 0.92까지 끌어올리는 데 핵심 역할을 했다.

**Table 1. 등록 불량 분류 성능 향상 단계**

| 단계 | 구성 | Weighted F1 | 핵심 변화 |
|------|------|-------------|-----------|
| Step 0 | 초기 baseline CNN | 0.78 | 기본 CNN 기반 시작점 |
| Step 1 | 고성능 backbone + 입력/전처리 개선 | [server log 값] | ConvNeXtV2 계열 전환, 해상도/입력 구조 개선 |
| Step 2 | Optuna 기반 하이퍼파라미터 탐색 | 0.92 | LR, WD, scheduler, dropout, augmentation, smoothing 등 최적화 |
| Step 3 | ROI + YOLO 2단계 보정 | 0.95 | difficult class 중심 재검증, spatial prior, 라벨 오류 보정 |

논문 본문에서는 Step 1과 Step 2를 자세히 분리해 설명하되, 최종 제출 시에는 서버 실험 로그를 기준으로 Step 1의 실제 F1을 기입하는 것을 권장한다. 만약 단계별 수치가 더 세밀하게 존재한다면, backbone 변경, 고해상도 입력, pretraining 적용, Optuna tuning의 순서대로 4~5단계로 세분화할 수 있다.

Optuna 기반 튜닝 항목은 Table 2와 같이 정리할 수 있다.

**Table 2. Optuna 기반 주요 탐색 항목**

| 범주 | 탐색 항목 | 목적 |
|------|-----------|------|
| Optimizer | learning rate, weight decay, optimizer 종류 | 수렴 안정성 및 일반화 성능 향상 |
| Scheduler | cosine / step / warmup 여부 | 학습 후반 성능 안정화 |
| Regularization | dropout, label smoothing | 라벨 노이즈와 과적합 완화 |
| Augmentation | augmentation intensity, crop/resize 전략 | 웨이퍼 패턴 변동성 대응 |
| Batching | batch size, accumulation, sampling 전략 | 클래스 편향 완화 및 학습 효율 개선 |
| Input | image size, normalization | 미세 패턴 보존과 backbone 적합성 확보 |

### 2.3 등록 불량 분류 경로: ROI enhancement로 0.92에서 0.95까지

1-stage classifier 위에는 ROI enhancement 기반 2단계 보정 경로를 추가하였다. 1차 분류 결과와 confidence를 바탕으로 difficult class 또는 low-confidence 샘플만 선별하고, 해당 샘플에 대해서만 Grad-CAM 기반 ROI 추출과 YOLO 이차 검증을 수행한다. 이때 dynamic ROI는 클래스별 평균 ROI 패턴과 `alpha` 블렌딩되어 공간적 안정성을 높이며, 최소 ROI 크기 보정과 class-object mapping을 통해 객체 검증이 도메인 의미와 맞도록 설계하였다.

이 구조의 중요한 특징은 단순한 후단 ensemble이 아니라, 라벨 오류 후보를 드러내는 검증 장치로도 동작한다는 점이다. 실제 서버 실험에는 다음 두 종류의 증거가 존재한다.

1. `original prediction != true`였지만 `ROI-enhanced prediction == true`로 교정된 대표 샘플 이미지
2. original confusion matrix와 ROI-enhanced confusion matrix를 각각 비교한 결과

따라서 논문에는 아래와 같은 그림 구성을 권장한다.

**Figure 3.** ROI enhancement로 오분류가 정분류로 교정된 대표 샘플  
구성 예시: `원본 웨이퍼 맵`, `Grad-CAM heatmap`, `ROI crop`, `YOLO 검증 결과`, `최종 예측`

**Figure 4.** Original classifier와 ROI-enhanced classifier의 confusion matrix 비교  
설명 문장 예시: `edge_loc`, `edge_ring`, `local`과 같이 상호 혼동이 잦은 클래스에서 ROI-enhanced 경로가 confusion을 감소시켰다.

문서에는 이 내용을 정량적으로 다음과 같이 기술할 수 있다.

> 서버 실험에서 ROI enhancement는 단순 평균 성능 향상뿐 아니라, baseline classifier가 오분류한 샘플 중 일부를 정답 클래스로 복원하는 효과를 보였다. 특히 confusion matrix 비교 결과, 공간적으로 유사한 패턴 간의 혼동이 감소하였으며, 이는 Grad-CAM 기반 ROI local evidence와 클래스별 spatial prior, YOLO 이차 검증이 상호 보완적으로 작용한 결과로 해석된다.

### 2.4 미등록 불량 경로: Contrastive Learning + HDBSCAN

미등록 불량은 사전 라벨이 존재하지 않으므로, supervised classifier만으로는 적절히 다루기 어렵다. 본 시스템에서는 ConvNeXtV2 backbone을 재사용하되 backbone은 고정하고 projection head만 학습하여, 기존 웨이퍼 표현을 유지하면서 unknown 분리를 위한 임베딩 공간을 구축하였다.

현재 코드 기준으로 unknown 성능을 높이기 위해 사용된 핵심 요소는 다음과 같다.

1. **도메인 제약 증강**: flip을 제거하고 소규모 회전, 이동, 스케일, 노이즈만 사용하여 위치 의미를 보존
2. **Global InfoNCE + Queue**: queue-based negative bank로 배치 한계를 넘는 negative 확보
3. **False negative 억제**: 지나치게 유사한 negative를 제외하여 유사 불량 간 과도한 분리 방지
4. **Local InfoNCE**: 국소 결함 구조 보존
5. **HDBSCAN keep/ignore filtering**: cluster size, median probability, persistence 기준으로 안정적인 cluster만 유지
6. **Medoid representative 저장**: 전문가 검토 효율 향상

**Table 3. unknown defect 군집화 품질 향상 요소**

| 요소 | 코드 기반 설정 | 기대 효과 |
|------|----------------|-----------|
| no-flip augmentation | small rotate/translate/scale + noise only | 웨이퍼 위치/방향 의미 보존 |
| projection head 학습 | backbone freeze | 소규모 unknown 데이터에서도 안정적 학습 |
| queue-based negative bank | USE_QUEUE, QUEUE_SIZE=16384 | 임베딩 분리도 향상 |
| local contrastive term | USE_LOCAL, LOCAL_WINDOW, POS_TOPK | 국소 결함 패턴 보존 |
| keep filter | KEEP_MIN_SIZE, KEEP_MIN_MEDIAN_PROB, KEEP_MIN_PERSIST | 약한 cluster와 noise 제거 |
| medoid summary | cluster_summary/ 저장 | 전문가 검토 부담 감소 |

### 2.5 unknown defect 성능은 어떻게 평가할 것인가

unknown defect는 일반 분류와 달리 정답 레이블이 미리 고정되어 있지 않으므로, 정확도 하나로 평가하기 어렵다. 본 연구에서는 세 층위의 평가 방식을 권장한다.

**1) Pseudo-open-set 정량 평가**  
이미 등록된 일부 클래스를 의도적으로 training에서 제외하고 unknown set으로 보내는 방식이다. 이 경우 cluster purity, NMI, ARI, noise ratio, kept cluster coverage를 계산할 수 있다. 논문용 정량 결과가 필요하다면 가장 설득력이 높은 방법이다.

**2) 내부 cluster quality 지표**  
현재 코드가 이미 저장하는 median membership probability, persistence, cohesion, margin은 label-free한 군집 품질 지표로 활용할 수 있다. 이는 HDBSCAN 결과의 안정성을 보여주는 정량 근거가 된다.

**3) 현업 검토 효율 지표**  
실사용 관점에서는 다음이 중요하다.

- 전문가가 유효한 신규 불량으로 승인한 cluster 비율
- cluster당 검토해야 하는 이미지 수 감소율
- 신규 라벨 등록까지 걸리는 시간
- unknown cluster를 등록 후 supervised path에 편입했을 때의 downstream F1 향상

즉 unknown defect의 평가는 `몇 퍼센트 맞췄는가`보다, `신규 불량 후보를 얼마나 잘 압축해서 검토 가능한 구조로 제시했는가`에 더 가깝다.

---

## 3. 결과 및 논의

등록 불량 경로에서는 1-stage optimized classifier가 weighted F1 0.92를 달성하였고, ROI-enhanced 2-stage 구조를 통해 0.95까지 향상되었다. 이 결과는 단순 backbone 교체가 아니라, Optuna 기반 학습 최적화와 difficult class 중심의 후단 보정이 결합된 결과이다. 특히 ROI enhancement는 평균 성능 상승뿐 아니라, true label과 다르게 예측된 샘플을 올바르게 복원하는 사례를 제공하므로, confusion matrix와 대표 교정 샘플을 함께 제시하는 것이 바람직하다.

데이터 인프라 관점에서는 dual-bucket 기반 파일 수집과 Cython 기반 초고속 파싱이 이미지 생성 파이프라인의 실용성을 높였다. 이 구조는 단순 PNG 생성 스크립트가 아니라, raw 로그, 칩 좌표, 계측값, 웨이퍼 메타데이터를 분석 UI와 모델 학습에 동시에 공급하는 기반 계층으로 작동한다. 또한 palette-indexed PNG와 PLTE patch 구조는 색상 변경, composite 생성, BIN/FBT/QVL overlay 전환을 가볍게 처리하게 하므로, 대규모 웨이퍼 맵 시각화에서 응답성 향상에 기여한다.

unknown 경로는 아직 완전한 정량 benchmark보다 운영 검토 중심으로 활용되고 있으나, 현재 구현만으로도 군집 후보 생성, 대표 이미지 요약, cluster filtering, human-in-the-loop 라벨 확장이라는 실용적 기능을 제공한다. 따라서 본 연구는 registered classification과 unknown discovery를 별개 문제로 다루지 않고, 하나의 운영형 분석 시스템 안에서 통합했다는 점에서 의미를 가진다.

---

## 4. 결론

본 연구는 반도체 웨이퍼 불량 분석을 위해 등록 불량 분류, 미등록 불량 군집화, 데이터 생성, 시각화 UI를 하나의 파이프라인으로 통합하였다. 등록 불량 경로에서는 Optuna 기반 학습 최적화로 1-stage classifier 성능을 `0.78 -> 0.92`까지 향상시켰고, ROI enhancement와 YOLO 이차 검증을 통해 최종 `0.95`를 달성하였다. 미등록 불량 경로에서는 Contrastive Learning과 HDBSCAN으로 unknown defect 후보를 자동 군집화하고, 전문가 검토 기반 라벨 확장 구조를 마련하였다. 또한 dual-bucket 로그 수집, Cython 기반 파싱, palette PNG, positions JSON, FTN/QTN 및 LT/TM/yield/sys 메타데이터 저장을 통해 향후 이미지-계측 융합 기반 multimodal defect analysis로 확장 가능한 운영형 데이터 기반을 구축하였다.

향후 연구에서는 pseudo-open-set 기반 unknown 정량 평가 체계를 확립하고, ROI-enhanced confusion matrix와 representative correction 사례를 더 체계적으로 분석할 필요가 있다. 또한 칩 레벨 계측값과 이미지 임베딩을 함께 활용하는 multimodal 모델을 도입함으로써, 신규 불량 조기 탐지와 원인 해석의 정확도를 더욱 향상시킬 수 있을 것으로 기대한다.

---

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," IEEE Transactions on Semiconductor Manufacturing, 2018.

[2] M. B. Alawieh et al., "Wafer Map Defect Patterns Classification Using Deep Neural Networks," DAC, 2019.

[3] S. Woo et al., "ConvNeXt V2: Co-designing and Scaling ConvNets with Masked Autoencoders," CVPR, 2023.

[4] R. R. Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization," ICCV, 2017.

[5] G. Jocher et al., "Ultralytics YOLO," GitHub, 2023.

[6] T. Chen et al., "A Simple Framework for Contrastive Learning of Visual Representations," ICML, 2020.

[7] R. J. G. B. Campello et al., "Density-Based Clustering Based on Hierarchical Density Estimates," PAKDD, 2013.
