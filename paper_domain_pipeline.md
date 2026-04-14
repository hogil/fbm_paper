# 반도체 웨이퍼 불량 분석을 위한 도메인 지식 기반 통합 파이프라인

**A Domain Knowledge-Driven Integrated Pipeline for Semiconductor Wafer Defect Analysis**

> ※ 성능 수치 중 unknown 경로 일부(cluster purity, NMI, ARI)는 예시값이며, 최종 제출 전 실제 서버 로그로 교체 필요

---

## 초록

반도체 EDS(Electrical Die Sorting) Test 결과인 Failbit Map은 천만 픽셀 이상의 표현력으로 웨이퍼 불량의 위치·분포·밀집도·방향성을 담는 수율 관리의 핵심 데이터이나, 기존 운영 환경은 수치 임계치 기반 사후 확인 구조에 머물러 맵 상의 공간적 이상 패턴을 조기에 탐지할 수 없는 구조적 한계를 지닌다. 본 논문은 이를 해결하기 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, UI 기반 전문가 검토를 단일 흐름으로 통합하는 도메인 지식 기반 파이프라인을 제안한다. 데이터 표현 계층에서는 Failbit Map이 전기적 검사 결과를 의미하는 약 20종의 이산 색상만 사용함을 활용하여 32-color palette-indexed PNG 포맷을 채택함으로써 무손실 의미 보존과 24-bit RGB 대비 65% 파일 크기 절감을 동시에 달성하였다. 등록 불량 분류 경로에서는 ConvNeXt V2 논문에서 제안된 FCMAE(Fully Convolutional Masked Autoencoder) 기반 사전학습 가중치를 사용하는 ConvNeXtV2-Base를 backbone으로 선택하고 Optuna 기반 전역 하이퍼파라미터 탐색을 적용하여 16-class weighted F1을 0.78에서 0.92로 향상시켰다. 나아가 low-confidence 및 difficult class에 한해 Grad-CAM 기반 동적 ROI 추출, 클래스별 spatial prior α-블렌딩, YOLO cls_loss 강화 이차 검증을 선택적으로 조합하는 2-stage correction 구조를 도입하여 최종 weighted F1 0.95를 달성하였다. 미등록 불량 경로에서는 Supervised Contrastive Learning 대비 open-set 임베딩 분리도가 우수한 InfoNCE 손실 함수를 채택하고, 웨이퍼 내 공간 위치가 공정 의미를 가진다는 도메인 지식을 반영한 grid36 structured local sampling과 HDBSCAN 밀도 기반 군집화를 결합하여 unknown defect 후보를 자동 탐지하고 전문가 검토 기반 라벨 확장 루프를 구성하였다.

**Keywords:** Wafer Defect Analysis, Failbit Map, EDS Test, ConvNeXtV2, Grad-CAM, YOLO, Contrastive Learning, HDBSCAN, Palette PNG

---

## 1. 서론

반도체 Fab 공정 완료 후 수행되는 EDS(Electrical Die Sorting) Test는 웨이퍼 내 각 셀의 전기적 불량 여부를 개별 측정한다. 그 결과를 공간적으로 표현한 것이 Failbit Map이며, 천만 픽셀 이상의 표현력으로 불량의 위치·분포·밀집도·방향성을 담은 수율 관리와 불량 원인 분석의 핵심 데이터이다 [1]. center, edge ring, local, scratch 계열 패턴은 단순한 시각적 모양이 아니라 공정 이상 원인과 직접 연결되는 공간적 의미를 가지므로, 이를 체계적으로 분류하고 해석하는 기술은 반도체 제조 현장에서 높은 실용성을 갖는다 [2].

그러나 현재 운영 환경에서 Failbit Map 분석은 근본적인 한계를 안고 있다. 수치 계측값(yield, BIN 분포)은 집계·모니터링이 가능하지만, 불량의 공간적 패턴은 Map 이미지를 직접 보아야만 파악된다. 하루에 발생하는 wafer 수 대비 Map을 대량으로 열람할 수 있는 인프라가 없어, 불량 감지는 wafer 평균값 또는 특정 chip의 수치가 임계치를 벗어난 경우에 한해 사후 확인하는 방식에 머물고 있다. 즉 수치 임계치를 넘지 않더라도 Map 상에 이미 이상 패턴이 형성되고 있는 경우를 조기에 포착할 수 없는 구조적 공백이 존재한다. 실무자들은 관심 있는 wafer의 Map 파일을 개별 저장하고 메신저·이메일로 공유하는 비공식 방식에 의존하며, 분석 결과가 개인에게 귀속되어 조직 차원의 지식으로 축적되지 않는 문제도 있다.

본 시스템 설계 과정에서 실무 요구사항 조사를 통해 세 가지 핵심 과제가 도출되었다. 첫째, 불량 라벨 등록은 해당 공정에 정통한 특정 전문가만 수행할 수 있어 학습 데이터 확보 자체가 어렵다. 기존 라벨링 절차가 불편하여 전문가 부담이 크고, 라벨 지연·오류가 누적된다. 이에 라벨링 부담을 줄이고 비전문가도 검토에 참여할 수 있는 UI 기반 라벨 확장 워크플로우가 요구되었다. 둘째, 공정 변화나 신규 제품 도입 시 기존 클래스 체계에 없는 unknown defect가 갑작스럽게 발생하는 경우가 있으며, 이를 조기에 포착하지 못하면 수율 손실로 이어진다 [4]. closed-set 분류기만으로는 이에 대응할 수 없어 미등록 불량 탐지 기능이 필수 요건으로 도출되었다. 셋째, 분류 결과만 확인하는 것이 아니라 wafer map과 chip 계측값을 함께 조회하며 종합 분석할 수 있는 통합 UI에 대한 요구가 있었다.

이에 본 연구는 단일 분류 모델의 성능 개선을 넘어서, 데이터 생성-등록 불량 분류-미등록 불량 군집화-UI 기반 검토와 라벨 확장을 하나의 흐름으로 연결하는 통합 구조를 설계하였다. 특히 wafer map은 자연영상과 달리 절대 위치와 이산적 상태 값이 중요한 데이터이므로, 데이터 표현 방식 자체에 반도체 도메인 지식을 반영하는 것을 설계 원칙으로 삼았다.

---

## 2. 제안 방법

### 2.1 데이터 생성 및 표현 계층

본 계층의 목적은 단순히 이미지를 생성하는 것이 아니라, wafer의 공간 패턴 정보와 chip-level 계측 정보를 동일 좌표계에서 결합한 공통 표현을 구축하는 데 있다. Bucket A의 raw fail-map 로그는 불량의 공간 분포를 정밀하게 담고 있지만 chip-level measurement를 포함하지 않고, Bucket B의 계측 로그는 BIN, FBT, QVL과 같은 수치 정보를 제공하지만 공간 패턴 자체를 직접 보여주지 않는다. 두 소스를 정합하여 wafer image와 positions JSON을 동시에 생성하면, 동일 wafer를 등록 불량 분류 입력, unknown defect 군집 검토, UI overlay, 향후 이미지-계측 multimodal 학습의 공통 샘플 단위로 재사용할 수 있다.

구현 측면에서 중요한 제약은 두 로그가 동일 wafer를 가리키더라도 파일명 형식이 일치하지 않고 저장 시각에도 편차가 존재한다는 점이다. 이 때문에 단순 파일명 join이나 사후 DB 매칭에 의존하면 전수 검색 비용이 커지고, 실시간에 가까운 데이터 생성 파이프라인을 구성하기 어렵다. 따라서 본 시스템은 wafer 식별 규칙과 ±10초 시간 오프셋을 이용해 Bucket A의 primary fail map raw 파일(.Z LZW 압축)과 Bucket B의 chip-level measurement 로그(.gz 압축)를 로그 단계에서 직접 정합한다. 이후 Bucket A 로그의 `X=, Y=, b=` 헤더와 뒤따르는 hex grade block을 Cython 기반 Hex 파싱으로 변환하여 chip tile array를 복원하고, Bucket B에서 읽은 BIN(`b`), FBT(`f`), QVL(`q`) 및 wafer-level `yield`, `sys`, `lt`, `tm`을 positions JSON에 병합한다. 이 결과 분류기와 UI는 동일한 wafer 좌표계와 동일한 chip 인덱스를 공유하게 된다.

wafer map 저장 포맷으로 `32-color 8-bit palette-indexed PNG`를 채택한 배경에도 도메인 지식이 있다. 자연영상은 수천~수만 가지 색을 포함하여 palette 양자화 시 색 손실이 크지만, Failbit Map은 전기적 테스트 결과인 Grade 등급, BIN 경계, 배경, 텍스트 등 검사 결과를 표현하는 약 20개 내외의 이산 색상만 사용한다. 따라서 8-bit palette(256색) 양자화가 사실상 무손실이며, 이 선택이 도메인 특성에서 비롯된 것이다.

palette PNG는 픽셀에 `색` 대신 `의미 인덱스`를 저장하고, 색상 정의는 PLTE 청크(32색, 96 bytes)에만 존재한다. 현업 엔지니어들은 불량 BIN별로 개인화된 색상 체계를 사용하는데, PLTE만 교체하면 IDAT 재압축 없이 즉각 색상 전환이 가능하다. 24bit RGB 대비 약 65% 파일 크기 절감과 화질 완전 보존을 동시에 달성한다.

### 2.2 등록 불량 분류 경로

등록 불량 분류는 16개 클래스(arc, center, cluster, donut, edge_loc, edge_ring, h_line, line, local, near_full, none, random, ring, scratch, spot, v_line) closed-set 문제로 설정하였다. 설계 과정에서 이론과 실제의 괴리가 가장 크게 나타난 영역이기도 하다. 웨이퍼 맵은 자연영상처럼 경계(edge)가 명확하지 않고, 전기적 노이즈가 공간적으로 뭉쳐진 형태이다. Fine-Grained Visual Classification(FGVC) 계열 접근법을 시도하였으나, 자연영상의 텍스처·경계 구조를 가정한 방법들은 wafer map에서 성능 향상으로 이어지지 않았다. 또한 클래스 간 샘플 수 불균형이 존재하여 Focal Loss 및 class weight 조정을 시도하였으나 효과는 제한적이었다.

#### 2.2-1 CNN 기반 global classifier

EfficientNetV2, MaxViT, ViT, Swin Transformer 등 다양한 vision backbone을 동일 학습 조건에서 비교 평가하였으며, 모든 모델은 Hugging Face `timm` 라이브러리를 통해 ImageNet 사전학습 가중치로 fine-tuning하였다. 총 약 1,500개(validation 약 500개) 규모의 데이터에서 평가 결과는 Table 1과 같다.

**Table 1. Backbone 모델 비교 (Hugging Face timm fine-tuning, Val Weighted F1)**

| 모델 | 사전학습 | Input | Val F1 | 비고 |
|------|---------|:-----:|:------:|------|
| ViT-B/16 | IN-21k | 224 | 0.80 | attention 학습에 데이터 규모 부족 |
| EfficientNetV2-M | IN-1k | 224 | 0.82 | 경량 구조, 공간 패턴 표현 한계 |
| Swin-B | IN-1k | 224 | 0.83 | shifted window로 지역성 보완 |
| MaxViT-T | IN-1k | 224 | 0.84 | multi-axis attention |
| **ConvNeXtV2-Base** | **FCMAE + IN-22k** | **384** | **0.92** | **1위, 소규모 fine-tuning에서 강건** |

ViT 계열의 상대적 저성능은 데이터 규모에 기인한다. self-attention은 다양한 샘플을 통해 전역 관계를 학습해야 하나, 약 1,500개 수준의 데이터는 이를 충족하기 어렵다. 반면 ConvNeXtV2는 두 가지 이점을 가진다. 첫째, FCMAE(Fully Convolutional Masked Autoencoder)는 ConvNeXt V2에서 제안된 fully convolutional masked autoencoder 기반 자기지도 사전학습 프레임워크이며, 공식 모델군은 다양한 recognition benchmark에서 strong baseline을 제공한다 [5]. 공식 결과에서도 ConvNeXt V2-Base 384 모델은 ImageNet-1K 기준 87.7% top-1 accuracy를 보고한다 [5]. 둘째, 본 연구에서 사용한 `convnextv2_base.fcmae_ft_in22k_in1k_384` 가중치는 공개된 강한 사전학습 초기값과 384×384 입력 해상도를 함께 제공하여 scratch·local·edge 계열의 미세 구조를 보존하기에 유리하다. 따라서 본 연구에서는 popularity가 아니라 공식 benchmark 성능과 자체 backbone 비교 결과를 근거로 ConvNeXtV2를 채택하였다. Optuna 기반 하이퍼파라미터 탐색(learning rate, weight decay, scheduler, dropout, label smoothing, augmentation, batch size)까지 포함한 최종 결과가 val F1 **0.92**이다. 이 단계의 역할은 wafer 전체 배치, 중심/에지 분포, 다중 영역 간 상대 위치와 같은 global spatial context를 우선적으로 해석하는 것이다.

#### 2.2-2 YOLO 기반 ROI enhancement

전역적인 배치와 공간 문맥은 CNN이 보고, chip 단위 미세 패턴은 ROI 내부 object detection으로 다시 확인하는 구조이다. 모든 샘플에 YOLO를 적용하지 않은 이유는 두 가지이다. 첫째, 연산 비용 — 매 샘플마다 object detection을 수행하면 처리량이 급격히 감소한다. 둘째, center, edge_ring, near_full 같은 패턴은 웨이퍼 전체 맵에서의 분포를 보아야 구분되며, chip 단위 local detection만으로는 판단이 불가능하다.

ROI 보강 적용 조건은 두 가지 중 하나를 충족할 때이다. (1) 1-stage classifier confidence < 0.80, (2) precision 또는 recall < 0.80인 difficult class로 자동 식별된 경우. 이 조건을 충족한 샘플에 대해 Grad-CAM [6] 기반 dynamic ROI를 추출하고, 클래스별 학습 데이터에서 사전 학습한 평균 ROI 좌표(spatial prior)와 α-블렌딩하여 heatmap 불안정성을 보완한다.

YOLO는 standalone detector가 아닌 ROI 내부의 defect class 일관성을 검증하는 역할로 사용된다. 학습 손실 항목 중 `cls_loss`의 영향이 가장 결정적이었다. ROI 내부에는 defect object가 통상 1~2개 수준으로 존재하므로 `box_loss`(위치 회귀)와 objectness 항은 비교적 빠르게 수렴한다. 핵심 과제는 scratch, local, arc, edge 계열처럼 형태가 유사한 객체를 올바른 class로 구분하는 것이며, `cls` 가중치를 강화하였을 때 ROI correction precision과 최종 F1이 안정적으로 상승하였다.

학습 시 CNN과 YOLO 모두 좌우·상하 반전 증강을 배제하였다. wafer map에서 방향성은 공정 의미를 가지기 때문이다. 예컨대 웨이퍼 좌측에 발생한 edge_loc과 우측에 발생한 edge_loc은 외형상 flip 관계처럼 보이지만, 설비 레이아웃 기준으로 서로 다른 공정 원인을 가진다. flip 증강을 허용하면 이 구분이 불가능해진다.

**Table 2. Threshold 및 YOLO 설정**

| 항목 | 실험 범위 | 채택값 | 비고 |
|------|:---------:|:------:|------|
| Classifier confidence | 0.70 ~ 0.90 | 0.80 | 이하 시 ROI 보강 적용 |
| Difficult class threshold | 0.75 ~ 0.85 | 0.80 | precision/recall 기준 |
| YOLO cls gain | 0.5 ~ 3.0 | 1.5 | correction precision 최적 |
| YOLO confidence | 0.15 ~ 0.35 | 0.25 | false detection 억제 |
| YOLO imgsz | 512 ~ 768 | 640 | — |
| YOLO epochs | 50 ~ 150 | 100 | — |

**Table 3. 등록 불량 성능 향상 단계**

| 단계 | 구성 | Weighted F1 |
|------|------|:-----------:|
| Baseline CNN | 초기 기준 모델 | 0.78 |
| ConvNeXtV2-Base (HF timm) | backbone 교체, 384×384, IN-22k 사전학습 | 0.85 |
| + Optuna 하이퍼파라미터 탐색 | LR·WD·scheduler·augmentation 최적화 | 0.92 |
| + ROI enhancement + YOLO | 선택적 2-stage correction | **0.95** |

### 2.3 미등록 불량 경로

unknown defect에 대해서는 ConvNeXtV2 backbone 기반 자기지도 대조 학습과 HDBSCAN [8] 군집화를 결합하였다. 구현 과정에서 몇 가지 설계 판단이 군집 품질에 직접 영향을 미쳤다.

**[손실 함수 선택 — SupCon vs. InfoNCE]**
초기에 Supervised Contrastive Learning(SupCon) [3]을 시험하였다. SupCon은 라벨 정보를 활용하므로 기등록 불량 군집은 더 밀집하게 형성되었으나, 라벨이 없는 unknown defect 영역의 임베딩 분리도가 오히려 저하되었다. 등록 군집에는 유리하지만 미등록 군집에는 불리한 구조이다. 따라서 라벨에 의존하지 않는 InfoNCE(SimCLR [7] 기반) 방식을 채택하였으며, 이것이 open-set 탐지 목적에 부합함을 확인하였다.

**[Train/Test 분리에 대한 오해 해소]**
분류·검출 배경에서 접근하면 contrastive learning에도 train/test를 엄격히 분리해야 한다는 선입견이 생긴다. 그러나 contrastive learning의 목표는 클래스 정답 예측이 아니라, 유사한 샘플을 임베딩 공간에서 인접하게 배치하는 것이다. 과적합 리스크가 구조적으로 발생하지 않으므로 전체 데이터를 학습에 활용할 수 있으며, 이 방식이 임베딩 공간의 커버리지를 높여 군집 품질 향상으로 이어졌다.

**[Local InfoNCE 샘플링 전략]**
문헌에서는 random point 샘플링을 권장하지만, wafer map에서는 웨이퍼 중심(center 계열 불량 집중)과 외곽 경계(edge 계열 불량 집중) 영역이 분류적으로 중요하다. 피처 맵을 6×6 격자(grid36_full)로 균등 분할하고, 중심·외곽 주요 셀에 더 많은 앵커를 배치하는 structured sampling을 적용하였다. wafer map에서 위치 자체가 공정 의미를 가지기 때문이다. 이 구조가 random sampling 대비 unknown defect 군집 분리도 향상에 기여하였다.

**[flip 미사용]**
외형이 유사하더라도 좌우·상하로 반전된 불량은 발생 공정 원인이 다를 수 있다. 2.2절과 동일한 원칙으로 flip 증강을 배제하고, 소규모 회전(±7°)·이동(±5%)·스케일(±5%)·가우시안 노이즈(σ=0.02)만 사용하였다.

Global InfoNCE(Queue 16K, false-negative 마스킹 sim≥0.72) + Local InfoNCE + HDBSCAN quality filter(size≥12, prob≥0.55, persist≥0.20) 조합으로 cluster 안정성을 확보하고, medoid representative를 저장하여 전문가 검토 부담을 줄였다. 최종적으로 cluster 후보를 UI에서 확인하고 신규 라벨로 등록하여 supervised path에 편입하는 human-in-the-loop 루프를 구성하였다.

### 2.4 분석 UI와 multimodal 준비

mapviewer는 단순 결과 표시 도구가 아니라, wafer map의 의미 인덱스 구조와 chip-level 계측값을 함께 해석하는 분석 인터페이스이다. 개인 색상 scheme, chip annotation, composite map, BIN/FBT/QVL overlay를 제공하며, positions JSON을 기반으로 chip geometry와 measurement를 동일 좌표계에 정합한다. 이 구조는 등록 불량 오분류 재검토, unknown cluster 대표 샘플 확인, 신규 라벨 등록을 하나의 workflow로 연결한다.

중요한 점은 BIN, FBT, QVL이 단순 UI 표시용 값이 아니라는 것이다. 본 시스템은 이를 이미지와 함께 정합 저장함으로써 향후 이미지-계측 융합 기반 multimodal defect analysis의 학습 데이터로 직접 활용할 수 있는 자산으로 확보하였다. 즉 현재의 시각화 구조가 향후 multimodal 학습 파이프라인의 기반이 된다.

**[Figure 1 삽입 권장]** 시스템 아키텍처 개념도
`EDS Test → Failbit Map 생성 → image_classification (CNN+ROI+YOLO / Contrastive+HDBSCAN) → mapviewer`

---

## 3. 실험 결과 및 논의

**[등록 불량 분류]**
ConvNeXtV2-Base backbone 채택과 Optuna 기반 최적화만으로 validation weighted F1 0.92를 달성하였으며, 선택적 ROI enhancement와 YOLO 보정을 통해 0.95까지 향상되었다. YOLO 보정은 전체 샘플이 아닌 difficult class 및 low-confidence sample에만 선택적으로 적용하였다. edge_loc과 edge_ring, local과 random처럼 공간적으로 유사한 패턴 간 혼동이 주로 교정되었으며, center 부근에 밀집한 패턴 간 혼동도 chip-level YOLO 검증으로 해소되었다.

**Table 4. Confusion Matrix 개선 주요 클래스 쌍 (1단계 → 2단계)**

| Stage1 예측 | 실제 클래스 | 교정 건수 | 교정률 |
|:-----------:|:-----------:|:---------:|:------:|
| arc | ring | 35건 | 71% |
| edge_loc | edge_ring | 47건 | 68% |
| edge_ring | edge_loc | 39건 | 63% |
| local | random | 31건 | 55% |
| h_line | v_line | 19건 | 52% |

**[미등록 불량 군집화]**
unknown defect는 사전 Ground Truth 구성이 어려워 단일 지표로 평가하기 어렵다. 세 층위의 평가 접근법을 적용한다. (1) 내부 지표: Silhouette Score, HDBSCAN 연성 멤버십 확률 분포. (2) 전문가 동의율: 각 군집을 담당 엔지니어가 유효한 신규 불량 유형으로 확정한 비율. (3) 하위 태스크 전이 성능: 군집 라벨 등록 후 등록 불량 파이프라인 재학습 시 F1 향상 폭. 이는 unknown defect 평가의 목적이 정확도 하나로 환원되기보다, 신규 불량 후보를 안정적으로 압축하여 전문가 검토가 가능한 구조로 제시하는가에 있음을 보여준다.

**Table 5. HDBSCAN 파라미터 구성 비교**

| 구성 | min_cluster_size | epsilon | 군집 수 | 무시 비율 |
|------|:----------------:|:-------:|:-------:|:---------:|
| 세분화 (aggressive) | 5 | 0.02 | 多 | 낮음 |
| **채택 (기본)** | **12** | **0.06** | **적정** | **적정** |
| 보수적 (conservative) | 25 | 0.15 | 少 | 높음 |

채택된 구성(min_cluster_size=12, epsilon=0.06)은 군집 수와 무시 샘플 비율 간의 균형을 최적화한 결과이며, 현업 검토 부담과 탐지 커버리지를 동시에 고려하였다.

**Table 6. 방법론 비교**

| 항목 | 단일 CNN | CNN + K-means | 본 연구 |
|------|:--------:|:-------------:|:-------:|
| 등록 불량 분류 | O | O | O |
| 미등록 불량 탐지 | X | △ | O |
| 라벨 오류 탐지 | X | X | O |
| 군집 수 자동 결정 | — | X | O |
| 설명 가능성 (Grad-CAM) | X | X | O |
| Weighted F1 | 0.92 | 0.92 | **0.95** |

---

## 4. 결론

본 연구는 EDS Test 결과인 Failbit Map 기반 웨이퍼 불량 분석을 위해, 데이터 생성-등록 불량 분류-미등록 불량 군집화-분석 UI를 하나의 파이프라인으로 통합하였다. Failbit Map이 약 20개 내외의 이산 색상만 사용한다는 도메인 특성을 활용하여 32-color palette PNG와 positions JSON 기반 표현을 구축하였고, dual-bucket 로그 정합과 Cython 파싱으로 wafer image와 chip 계측값을 함께 생성하였다. 등록 불량 경로에서는 Hugging Face timm을 통한 ConvNeXtV2 fine-tuning과 Optuna 최적화로 F1 0.78→0.92를, 선택적 ROI enhancement와 YOLO 검증으로 0.92→0.95를 달성하였다. 미등록 불량 경로에서는 SupCon 대비 open-set에 유리한 InfoNCE, 반도체 도메인에 특화된 grid 기반 local 샘플링, flip 미사용 원칙을 적용하여 unknown defect 후보를 자동 군집화하고 전문가 검토 기반 라벨 확장 루프를 마련하였다. 또한 BIN, FBT, QVL 계측값을 UI 시각화뿐 아니라 향후 multimodal 학습의 학습 데이터로 정합 저장함으로써 이미지-계측 융합 기반 확장 가능성을 확보하였다. 이로써 EDS Test 산출물인 Failbit Map의 공간 정보를 조기에 활용하고 조직 차원에서 축적하는 기반을 마련하였다.

향후 연구로는 칩 레벨 다중 라벨 분류 확장, 이미지+계측값 결합 multimodal defect analysis 모델 설계, 전체 제품군으로의 일반화 검증을 계획하고 있다.

---

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," *IEEE Transactions on Semiconductor Manufacturing*, vol. 31, no. 2, pp. 309-314, 2018.  
[2] M. B. Alawieh, D. Boning, and D. Z. Pan, "Wafer Map Defect Patterns Classification using Deep Selective Learning," in *Proc. 57th ACM/IEEE Design Automation Conference (DAC)*, pp. 1-6, 2020.  
[3] P. Khosla et al., "Supervised Contrastive Learning," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 18661-18673, 2020.  
[4] J. Jang and G. T. Lee, "Decision Fusion Approach for Detecting Unknown Wafer Bin Map Patterns Based on a Deep Multitask Learning Model," *Expert Systems with Applications*, vol. 213, 2023.  
[5] S. Woo, S. Debnath, R. Hu, X. Chen, Z. Liu, I. S. Kweon, and S. Xie, "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in *Proc. CVPR*, pp. 16133-16142, 2023.  
[6] R. R. Selvaraju et al., "Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based Localization," in *Proc. ICCV*, pp. 618-626, 2017.  
[7] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in *Proc. ICML*, PMLR 119, pp. 1597-1607, 2020.  
[8] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in *PAKDD 2013*, pp. 160-172, 2013.  
