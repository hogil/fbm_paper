# Failbit Map 기반 웨이퍼 불량 패턴의 등록/미등록 통합 분류를 위한 지도-비지도 복합 파이프라인

**A Hybrid Supervised-Unsupervised Pipeline for Wafer-Level Failbit Map Defect Pattern Classification: Registered and Unregistered Defect Integration**

---

## 초록

반도체 제조 공정에서 웨이퍼 Failbit Map의 불량 패턴을 신속하고 정확하게 분류하는 것은 수율 향상과 공정 이상 원인 분석의 핵심 과제이다. 기존 합성곱 신경망(CNN) 기반 지도학습 방법은 사전에 등록된 불량 유형에 대해 높은 분류 성능을 보이지만, 실제 현업에서는 라벨 오류 누적, 신규 불량 패턴의 돌발 발생, 그리고 이미지만으로 설명되지 않는 전기적 계측값 활용 요구 등 단일 분류기로 대응하기 어려운 문제들이 존재한다.

본 연구에서는 이러한 문제를 통합적으로 해결하기 위해 지도-비지도 복합 파이프라인을 제안한다. 등록 불량에 대해서는 ConvNeXtV2 분류기와 Grad-CAM 기반 ROI 추출, YOLO 이차 검증을 결합한 2단계 구조를 적용하여 weighted F1 0.95를 달성하였으며, 이는 단일 CNN 대비 3%p 향상된 결과이다. 미등록 불량에 대해서는 자기지도 대조 학습(Contrastive Learning)과 HDBSCAN 밀도 기반 군집화를 결합하여 사전 라벨 없이 신규 불량 후보를 자동으로 발굴하고, 전문가 검토를 통한 점진적 라벨 확장이 가능한 구조를 구현하였다. 아울러 Failbit Map 생성 단계에서부터 칩별 전기적 특성 검사 결과(FBT, QVL 등)와 웨이퍼 레벨 수율(yield) 및 systematic 불량률을 이미지와 함께 정합 저장하는 데이터 파이프라인을 구축하여, 향후 이미지와 계측값을 결합한 멀티모달(multimodal) 불량 분석으로의 확장 기반을 마련하였다.

---

## 1. 서론

반도체 제조 공정에서 Failbit Map 분석은 공정 이상의 조기 탐지와 수율 관리에 필수적이다 [1]. Failbit Map은 웨이퍼 내 셀 단위 테스트 결과를 공간적으로 표현한 정보로, center, donut, edge ring, scratch와 같은 불량 패턴은 발생 위치와 형상 자체가 공정 원인에 대한 단서를 제공한다 [2]. 이러한 이유로 웨이퍼 맵 기반 자동 분류는 오래전부터 연구되어 왔으며, 최근에는 CNN 기반 분류기가 기등록 클래스에 대해 높은 정확도를 보이고 있다.

그러나 실제 현업 적용 과정에서 단일 지도학습 모델만으로는 해결되지 않는 세 가지 문제가 확인되었다. 첫째, 신규 제품이나 공정 조건 변화로 인해 기존 라벨 체계에 없는 불량이 지속적으로 유입되며, 기존 CNN은 이를 알려진 클래스 중 하나로 강제 분류하는 폐쇄집합(closed-set) 한계를 가진다. 둘째, 라벨 등록과 유지 자체가 전문가 의존적이어서 학습 데이터에 라벨 누락 및 오류가 축적될 수 있다. 셋째, 실제 분석 업무는 단순 분류 결과 확인에 그치지 않고, 웨이퍼 맵 시각화, 칩 위치 확인, 계측값 오버레이, 군집 검토, 수동 라벨링 등 운영 도구와 결합되어야 한다.

본 연구는 이러한 문제를 해결하기 위해 단순 모델 성능 향상에 머무르지 않고, 데이터 생성-분류-군집화-시각화-검토를 연결하는 통합 파이프라인을 설계하였다. 처음에는 기등록 불량을 CNN으로 분류하는 문제에 집중하였으나, 실제 적용 요구를 반영하면서 unknown 불량 발굴과 후속 라벨 확장을 함께 고려하는 방향으로 시스템을 확장하였다. 특히 도메인 지식을 반영한 공간 사전 정보, 선택적 ROI 보강, 계측값 결합 구조, palette PNG 기반 고속 시각화 전략을 통해 현업 적용 가능성을 높이고자 하였다.

본 연구의 기여는 다음과 같다.

- **도메인 지식 기반 등록 불량 분류**: 웨이퍼 불량의 공간적 위치 특성을 반영하여 Grad-CAM ROI 추출, 클래스별 평균 ROI 패턴 학습, YOLO 이차 검증을 결합한 2단계 분류 구조를 제안하였다.
- **미등록 불량 탐지용 자기지도 군집화**: ConvNeXtV2 백본 재사용, Global/Local InfoNCE, memory queue, HDBSCAN 기반 필터링을 결합하여 신규 불량 군집을 자동 발굴하는 파이프라인을 구현하였다.
- **운영형 데이터·시각화 인프라 구축**: palette-indexed PNG, positions JSON, 칩 단위 FTN/QTN 계측값, LT/TM/yield/sys 메타데이터, 그리고 BIN/FBT/QVL 오버레이와 수동 라벨링을 지원하는 웹 UI를 통해 향후 multimodal 분석 기반을 확보하였다.

---

## 2. 제안 시스템

본 시스템은 등록 불량의 고정 클래스 분류와 미등록 불량의 개방집합 탐지를 동시에 지원하는 복합 파이프라인으로 구성된다. 전체 구조는 (1) Failbit Map 생성 및 메타데이터 정합, (2) 2단계 지도학습 기반 등록 불량 분류, (3) 자기지도 대조 학습 기반 unknown 군집화, (4) 현업 분석 UI 기반 검토 및 라벨 확장으로 이루어진다.

### 2.1 2단계 지도학습 파이프라인 (등록 불량 분류)

등록 불량 분류를 위해 ConvNeXtV2-Base [3]를 백본으로 사용하는 1차 분류기를 구축하였다. 입력은 384×384 해상도의 웨이퍼 레벨 Failbit Map이며, 9개 클래스(center, donut, edge_loc, edge_ring, local, random, scratch, near_full, none)를 대상으로 분류한다. 1차 분류와 동시에 Grad-CAM [4]을 통해 예측 클래스에 대한 활성 영역을 추출한다.

이 과정에서 반도체 불량의 공간적 위치 패턴에 대한 도메인 지식을 적극 활용하였다. 예를 들어 center 패턴은 웨이퍼 중심부에, edge_ring은 외곽 링 형태에, scratch는 특정 방향성을 가진 선형 구조에 나타난다. 본 시스템은 이러한 특성을 반영하여 Grad-CAM heatmap을 형태학적으로 정제하고 ROI를 추출할 뿐 아니라, 클래스별 평균 ROI 좌표를 사전 학습하여 공간 사전 정보(spatial prior)로 활용한다. 또한 ROI 보강을 모든 샘플에 일괄 적용하지 않고, low-confidence 샘플 또는 difficult class에 한정하여 수행함으로써 불필요한 연산과 과보정을 줄였다. 이러한 선택적 보강 전략은 `CONFIDENCE_THRESHOLD`, `ROI_FOR_DIFFICULT_OR_LOWCONF_ONLY`, `ROI_PATTERN_BLEND_ALPHA`, `YOLO_CONF_THRESHOLD`와 같은 옵션으로 조정 가능하게 설계하였다.

2차 검증 단계에서는 추출된 ROI를 YOLO [5]에 입력하여 객체 기반 일관성을 확인한다. YOLO 결과가 1차 분류 결과와 상충하는 샘플은 재검토 후보로 간주되며, 이 절차는 단순한 재분류를 넘어 데이터 품질 개선에도 활용된다. 실제로 이러한 2단계 구조를 통해 weighted F1가 0.92에서 0.95로 향상되었으며, 성능 향상의 상당 부분이 라벨 오류 후보 탐지와 재정비 과정에서 비롯됨을 확인하였다.

### 2.2 Contrastive Learning + HDBSCAN (미등록 불량 탐지)

미등록 불량 탐지를 위해 별도의 자기지도 학습 기반 군집화 파이프라인을 구축하였다. 이 모듈은 기등록 불량 분류기에서 사용한 ConvNeXtV2 백본을 재사용하되, 백본은 동결하고 그 위에 2층 MLP projection head만 학습한다. 이를 통해 이미 학습된 웨이퍼 맵 공간 표현을 보존하면서 unknown 패턴 구분에 필요한 임베딩 공간을 형성할 수 있다.

손실 함수는 전역 Global InfoNCE [7]와 지역 Local InfoNCE의 조합으로 구성하였다. Global InfoNCE는 memory queue를 사용하여 대규모 음성 샘플을 효율적으로 활용하며, 유사도가 지나치게 높은 샘플은 음성 집합에서 제외하여 false negative 문제를 줄인다. Local InfoNCE는 feature map 상의 격자 앵커를 기준으로 국소 패턴 유사성을 학습하여, 전역 평균 표현만으로 놓치기 쉬운 영역별 결함 구조를 보완한다. Failbit Map 특성상 절대 위치와 방향성이 중요한 경우가 많으므로, 일반 영상에서 흔히 사용하는 좌우 반전은 배제하고, 소폭의 회전·이동·스케일 변화와 노이즈만 적용하였다. 학습 효율과 안정성을 위해 클래스별 비율 샘플링, warmup, queue size, local window, subbatch, worker/prefetch 옵션을 모두 노출하여 데이터 특성에 맞게 조정 가능하도록 하였다.

임베딩이 형성된 뒤에는 unknown 데이터 전체에 대해 HDBSCAN [6]을 적용하여 자동 군집화를 수행한다. HDBSCAN은 클러스터 수를 사전에 지정할 필요가 없고, 밀도 기반으로 잡음 샘플을 구분할 수 있어 unknown defect 환경에 적합하다. 본 구현에서는 minimum cluster size, minimum samples, cluster selection epsilon과 더불어, median membership probability, persistence, cluster size 조건을 함께 사용하여 keep/ignore 클러스터를 구분한다. 또한 각 군집에 대해 medoid 대표 이미지를 별도 저장하여 전문가가 cluster summary를 빠르게 검토할 수 있도록 하였다.

### 2.3 Failbit Map 생성, 계측값 정합, 분석 UI

알고리즘 성능뿐 아니라 데이터 생성과 분석 환경의 일관성 역시 현업 적용에 중요하다. 이를 위해 본 연구에서는 Failbit raw 파일로부터 palette-indexed PNG와 positions JSON을 동시에 생성하는 파이프라인을 구축하였다. Failbit Map 생성 시 Grade 인덱스, 배경, 텍스트, border, BIN border의 팔레트 인덱스 계약을 고정하고, 각 칩의 `rect`, `grid_edges`, 좌표계 정보가 포함된 positions JSON을 함께 저장하여 UI와 모델이 동일한 공간 기준을 공유하도록 하였다.

이와 같은 palette PNG 방식은 분석 UI에서 큰 장점을 제공한다. 웹 뷰어는 PLTE 청크만 패치하여 개인 색상, composite gradient, measure gradient를 빠르게 변경할 수 있으므로, IDAT 재압축이나 원본 재생성을 반복하지 않고도 색상 스킴 전환과 합성 맵 재표현이 가능하다. 또한 피라미드 렌더링, 썸네일 프리패치, chip overlay, chip selection/annotation, composite map, measure overlay가 하나의 인터페이스에서 제공되어, 모델 결과를 맵 단위와 칩 단위에서 동시에 검토할 수 있도록 하였다.

특히 데이터 확장성 측면에서, Bucket B 데이터 파싱을 통해 칩 단위 FTN/QTN 계측값을 positions JSON 내 `f`/`q` 필드로 저장하고, LT/TM, yield, sys, gd 등의 메타데이터도 함께 기록하였다. UI에서는 이 계측값을 FBT/QVL 항목으로 노출하고, BIN/FBT/QVL 기준의 gradient overlay 및 composite 생성을 지원한다. 이는 현재는 이미지 중심 분석에 사용되지만, 향후 이미지 임베딩과 계측값을 함께 활용하는 multimodal 불량 분석 모델로 확장할 수 있는 기반 데이터 구조를 제공한다.

### 2.4 Human-in-the-loop 라벨 확장

미등록 불량 군집화 결과는 자동 의사결정의 종착점이 아니라, 전문가 검토를 위한 후보 생성 단계로 사용된다. 현업 사용자는 군집 대표 이미지, cluster summary, 웨이퍼 맵 시각화, 칩 좌표 및 계측값 오버레이를 함께 확인하면서 신규 불량 여부를 판단할 수 있다. 이때 군집을 신규 클래스로 등록하거나 기존 클래스에 귀속시키는 절차를 지원함으로써, 지도학습 파이프라인의 학습 집합을 점진적으로 확장하는 human-in-the-loop 운영 구조를 마련하였다.

---

## 3. 실험 결과 및 구현 관찰

실험은 사내 Failbit Map 웨이퍼 레벨 이미지 데이터셋을 대상으로 수행하였다. 등록 불량 분류 성능을 Table 1에 정리한다.

**Table 1. 등록 불량 분류 성능 비교**

| 방법 | Weighted F1 | 비고 |
|------|-------------|------|
| ConvNeXtV2 단독 (Stage 1) | 0.92 | 기존 단일 CNN |
| ConvNeXtV2 + YOLO (2단계) | **0.95** | ROI 기반 이차 검증 포함 |

2단계 파이프라인은 Stage 1 단독 대비 3%p의 F1 향상을 달성하였다. 이 결과는 단순히 분류기 하나를 교체한 것이 아니라, 공간 사전 정보 기반 ROI 추출, difficult/low-confidence 샘플 선택적 보강, YOLO 이차 검증을 결합한 결과이다. 또한 2단계 검증은 라벨 오류 후보를 선별하는 데에도 유용하여, 데이터 재검토와 모델 성능 개선을 동시에 지원하였다.

미등록 불량 탐지의 경우, Contrastive Learning + HDBSCAN 파이프라인을 통해 unknown 데이터에서 의미 있는 군집 구조를 도출하고, 대표 이미지와 요약 통계를 자동 저장할 수 있음을 확인하였다. 다만 unknown defect는 정의상 사전 Ground Truth를 일관되게 구축하기 어려워, 현재 단계에서는 정성적 검토와 cluster summary 기반 운영 검증이 중심이며, 정량 지표 체계는 향후 과제로 남겨 두었다.

구현 측면에서는 데이터 인프라와 UI가 연구 재현성과 운영성에 중요한 역할을 하였다. palette-indexed PNG와 PLTE patch 기반 색상 전환은 대규모 웨이퍼 이미지 시각화의 응답성을 높였고, positions JSON과 chip annotation UI는 분류 결과와 칩 단위 정보를 정합성 있게 연결하였다. 또한 BIN뿐 아니라 FBT/QVL 계측값에 대한 gradient overlay 및 composite 생성 기능을 통해, 현재의 이미지 기반 분류를 넘어 데이터 융합 분석으로 확장할 수 있는 실무 기반을 확보하였다.

---

## 4. 결론

본 연구에서는 Failbit Map 기반 웨이퍼 불량 패턴 분석을 위해 등록 불량 분류와 미등록 불량 탐지를 결합한 지도-비지도 복합 파이프라인을 제안하였다. 등록 불량 경로에서는 ConvNeXtV2, Grad-CAM, ROI spatial prior, YOLO 이차 검증을 결합하여 weighted F1 0.95를 달성하였고, 미등록 불량 경로에서는 자기지도 대조 학습과 HDBSCAN을 통해 unknown defect 후보 군집을 자동 발굴할 수 있음을 보였다. 또한 palette PNG 기반 이미지 생성, positions JSON 기반 좌표 정합, BIN/FBT/QVL 분석 UI, 그리고 FTN/QTN 및 LT/TM/yield/sys 메타데이터 저장을 통해 현업 적용형 데이터·시각화 인프라를 함께 구축하였다.

향후 연구는 세 방향으로 확장될 수 있다. 첫째, 웨이퍼 레벨 분류를 칩 레벨 국소 분석으로 확장하여 다중 결함 공존 상황을 더 정밀하게 모델링하는 것이다. 둘째, 현재 확보된 이미지와 계측값을 결합하여 multimodal defect analysis 모델을 설계하는 것이다. 셋째, unknown defect 군집화에 대한 정량 평가 프로토콜을 수립하고, 더 다양한 제품군과 공정 라인으로 일반화 가능성을 검증하는 것이다.

---

## 참고문헌

[1] M. B. Alawieh et al., "Wafer Map Defect Patterns Classification Using Deep Neural Networks," DAC, 2019.

[2] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," IEEE Trans. Semiconductor Manufacturing, 2018.

[3] S. Woo et al., "ConvNeXt V2: Co-designing and Scaling ConvNets with Masked Autoencoders," CVPR, 2023.

[4] R. R. Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization," ICCV, 2017.

[5] G. Jocher et al., "Ultralytics YOLO," GitHub, 2023.

[6] R. J. G. B. Campello et al., "Density-Based Clustering Based on Hierarchical Density Estimates," PAKDD, 2013.

[7] T. Chen et al., "A Simple Framework for Contrastive Learning of Visual Representations," ICML, 2020.
