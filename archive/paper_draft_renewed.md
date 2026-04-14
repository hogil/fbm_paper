# 도메인 지식 기반 지도-비지도 복합 파이프라인을 이용한 반도체 웨이퍼 불량 패턴 분석

**A Domain-Knowledge-Driven Hybrid Pipeline for Semiconductor Wafer Defect Pattern Analysis**

---

## 초록

반도체 제조 공정에서 Failbit Map 기반 불량 패턴 분석은 수율 저하 원인 추적과 공정 이상 조기 탐지에 직결되는 핵심 과제이다. 초기에는 기등록 불량 클래스만을 대상으로 단일 CNN 분류기를 적용하는 접근을 우선 고려하였으나, 실제 현업에서는 라벨 등록 지연, 라벨 노이즈, 신규 불량의 돌발 발생, 그리고 이미지와 계측값을 함께 해석해야 하는 요구가 동시에 존재함을 확인하였다. 이에 본 연구에서는 등록 불량과 미등록 불량을 함께 다루는 지도-비지도 복합 파이프라인을 설계하고 파일럿 구현을 수행하였다. 등록 불량 분석 경로에서는 ConvNeXtV2 기반 1차 분류, Grad-CAM 기반 ROI 추출, 클래스별 평균 ROI spatial prior, YOLO 기반 2차 검증을 결합하여 weighted F1 0.95를 달성하였으며, 이는 단일 CNN 기반 0.92 대비 3%p 향상된 결과이다. 미등록 불량 경로에서는 자기지도 대조 학습과 HDBSCAN을 결합하여 unknown 패턴을 자동 군집화하고, 대표 이미지와 요약 정보를 생성하여 전문가 검토와 신규 라벨 등록을 지원하였다. 또한 palette-indexed PNG 기반 웨이퍼 맵 생성, positions JSON 기반 칩 좌표 정합, FTN/QTN 계측값과 LT/TM/yield/sys 메타데이터 저장, BIN/FBT/QVL 오버레이를 지원하는 분석 UI를 함께 구축함으로써 향후 이미지-계측 융합 기반 multimodal 불량 분석으로 확장 가능한 데이터 기반을 확보하였다.

---

## 1. 서론

웨이퍼 레벨 Failbit Map은 테스트 결과를 공간적으로 표현한 데이터로서, 불량의 위치, 형상, 분포 특성을 직접적으로 반영한다. center, edge ring, donut, scratch와 같은 대표 패턴은 단순한 시각적 특징을 넘어 공정 원인과 결부된 공간적 의미를 가지므로, 이를 자동 분류하는 기술은 반도체 제조 현장에서 높은 활용 가치를 가진다. 최근에는 CNN 기반 영상 분류 모델이 기등록된 패턴에 대해 우수한 성능을 보이면서, 웨이퍼 맵 자동 분류의 실용 가능성이 크게 향상되었다.

그러나 실제 현업 분석 환경은 전형적인 폐쇄집합 분류 문제와 다르다. 우선, 신규 제품 도입이나 공정 조건 변화에 따라 기존 라벨 체계에 없는 불량이 지속적으로 발생할 수 있으며, 이러한 샘플은 기존 CNN에서 알려진 클래스 중 하나로 강제 분류될 가능성이 높다. 또한 라벨 등록과 유지 자체가 전문가 의존적이기 때문에 라벨 누락이나 잘못된 라벨 기입이 축적되기 쉽다. 마지막으로 실제 분석 업무는 분류 정확도 자체뿐 아니라, 웨이퍼 맵 시각화, 칩 위치 확인, 계측값 비교, 전문가 검토 및 라벨 확장까지 포함하는 운영 workflow와 결합되어야 한다.

본 연구는 이러한 실무 요구에서 출발하였다. 처음에는 등록된 불량 클래스만을 대상으로 CNN 기반 자동 분류기를 구축하는 것이 목표였으나, 개발 과정에서 현업의 핵심 요구는 단순 분류기보다 "등록되지 않은 불량을 어떻게 발견하고, 검토하고, 체계적으로 등록할 것인가"에 더 가깝다는 점을 확인하였다. 이에 따라 본 연구는 등록 불량에 대한 고정 클래스 분류 성능 향상과 더불어, 미등록 불량에 대한 군집 기반 후보 발굴, 시각화 기반 검토, 후속 라벨 확장까지 연결되는 지도-비지도 복합 구조로 시스템을 재설계하였다.

특히 본 연구는 순수한 모델 교체보다 도메인 지식의 구조적 반영에 중점을 두었다. 웨이퍼 불량은 일반 자연영상과 달리 절대 위치와 형태가 중요한 경우가 많으므로, Grad-CAM으로 추출한 활성 영역을 클래스별 평균 ROI 패턴과 결합하여 spatial prior로 활용하였다. 또한 모든 샘플에 동일한 후처리를 적용하지 않고, 저신뢰 샘플 또는 난분류 클래스에만 선택적으로 ROI 보강과 2차 검증을 수행하도록 옵션화하였다. 더 나아가 웨이퍼 맵 생성 단계에서 palette PNG와 positions JSON을 함께 생성하고, 칩 단위 계측값을 동일 좌표계에 정합시킴으로써 모델, 시각화, 사용자 검토가 하나의 데이터 구조를 공유하도록 구성하였다.

본 논문의 기여는 다음과 같다.

1. 웨이퍼 불량의 공간적 특성을 반영한 2단계 등록 불량 분류 파이프라인을 제안하고, weighted F1 0.95를 달성하였다.
2. 자기지도 대조 학습과 HDBSCAN을 활용하여 미등록 불량 후보를 자동 군집화하고, 전문가 검토 중심의 human-in-the-loop 확장 경로를 구현하였다.
3. palette-indexed PNG, positions JSON, 칩 단위 FTN/QTN 계측값, BIN/FBT/QVL 오버레이 UI를 결합하여 향후 multimodal 분석으로 확장 가능한 운영형 데이터 인프라를 구축하였다.

---

## 2. 제안 방법

### 2.1 전체 구조

제안 시스템은 크게 네 단계로 구성된다. 첫째, raw failbit 데이터로부터 palette-indexed PNG 형태의 웨이퍼 맵과 positions JSON을 생성한다. 둘째, 기등록 불량에 대해서는 ConvNeXtV2 기반 1차 분류와 ROI 기반 2차 검증을 통해 고정 클래스 분류를 수행한다. 셋째, 미등록 불량에 대해서는 자기지도 대조 학습으로 임베딩을 형성한 뒤 HDBSCAN으로 자동 군집화한다. 넷째, 시각화 UI에서 웨이퍼 맵, 칩 오버레이, 계측값, 군집 결과를 함께 검토하면서 신규 라벨 등록 또는 수동 분석을 수행한다. 본 연구는 전 제품 라인에 대한 완전 배포가 아니라, 상기 workflow를 검증하기 위한 파일럿 수준의 통합 파이프라인 구현을 목표로 한다.

전체 시스템 아키텍처는 Figure 1과 같다.

```text
Raw Failbit / Bucket B Data
          |
          v
Failbit Map Generation
(palette PNG + positions JSON)
          |
          +-------------------------------+
          |                               |
          v                               v
Registered Defect Path             Unknown Defect Path
ConvNeXtV2 Classification          Contrastive Embedding
-> Grad-CAM ROI                    -> HDBSCAN Clustering
-> ROI Spatial Prior               -> Cluster Summary / Medoid
-> YOLO Verification               -> Expert Review Candidate
          |                               |
          +---------------+---------------+
                          |
                          v
        Analysis UI / Human-in-the-loop Review
      (BIN, FBT, QVL Overlay / Annotation / Labeling)
                          |
                          v
              Label Expansion / Future Multimodal
```

**Figure 1.** 제안한 웨이퍼 불량 분석 시스템 아키텍처. Failbit Map 생성, 등록 불량 분류, 미등록 불량 군집화, 그리고 분석 UI 기반 검토 및 라벨 확장 workflow를 통합적으로 나타낸다.

### 2.2 등록 불량 분류: ConvNeXtV2 + Grad-CAM + YOLO

등록 불량 분류 경로의 1차 모델은 ConvNeXtV2를 백본으로 하는 이미지 분류기이다. 입력은 384×384 해상도의 웨이퍼 레벨 Failbit Map이며, center, donut, edge_loc, edge_ring, local, random, scratch, near_full, none 등 기등록된 클래스를 대상으로 분류한다. 1차 분류 결과와 함께 Grad-CAM을 이용해 예측 클래스의 주요 활성 영역을 heatmap으로 계산하고, 이를 형태학적 처리 후 ROI로 변환한다.

이 단계에서 가장 중요한 설계 요소는 웨이퍼 불량의 공간 사전 정보이다. 예를 들어 center 계열은 중심부 집중, edge_ring은 외곽부 띠 형태, scratch는 방향성 있는 선형 구조라는 특성을 가지며, 이러한 특성은 일반적인 자연영상 분류에서 사용하는 위치 불변 가정보다 훨씬 강한 의미를 가진다. 본 연구는 이러한 도메인 지식을 반영하여 클래스별 평균 ROI 좌표 패턴을 사전 학습하고, 개별 샘플의 동적 ROI와 혼합하여 2차 검증 입력을 생성하였다. 즉, 단일 샘플의 noisy한 heatmap만을 쓰지 않고, 클래스 평균 위치 패턴을 함께 반영함으로써 보다 안정적인 spatial prior를 구현하였다.

또한 성능 향상을 위해 보강 전략을 옵션화하였다. ROI 보강은 모든 샘플에 일괄 적용하지 않고, confidence threshold 이하의 저신뢰 샘플이나 난분류 클래스에 한해 선택적으로 적용한다. 아울러 ROI pattern blend 비율, YOLO confidence threshold, difficult-only 적용 여부 등 여러 옵션을 독립적으로 조정할 수 있도록 구현하여 데이터셋 특성과 클래스 난이도에 맞는 실험이 가능하게 하였다. 이와 같은 세부 옵션은 단순한 하이퍼파라미터 조정이 아니라, "어떤 샘플에 추가 검증이 필요한가"라는 현업 분석자의 판단 로직을 시스템화한 것으로 볼 수 있다.

2차 검증기에는 YOLO를 사용하였다. YOLO는 추출된 ROI 내 객체적 일관성을 다시 확인하는 역할을 수행하며, 1차 분류 결과와 불일치하는 샘플은 재검토 후보로 활용된다. 이 구조는 분류 정확도 향상뿐 아니라 라벨 노이즈 탐지에도 기여하였으며, 단일 CNN 대비 weighted F1 0.92에서 0.95로 향상된 결과를 얻었다.

추가적으로 코드 구현 관점에서 보면, 등록 불량 성능 향상은 단일 기법이 아니라 여러 보정 요소의 조합으로 이루어져 있다. 우선 클래스별 precision/F1 분석을 통해 difficult class를 선별하고, 이러한 클래스 또는 low-confidence 샘플에 대해서만 ROI enhancement를 수행하도록 하여 보정 연산을 필요한 경우에 집중시켰다. 또한 ROI가 과도하게 작거나 비정상적으로 추출되는 경우를 방지하기 위해 최소 ROI 크기와 좌표 정규화 규칙을 적용하였다. 마지막으로 분류 클래스와 YOLO 객체 클래스 간의 수동/자동 매핑 구조를 도입하여, 단순 검출 결과가 아니라 도메인 의미에 맞는 이차 검증이 수행되도록 설계하였다.

### 2.3 미등록 불량 탐지: Contrastive Learning + HDBSCAN

미등록 불량은 정의상 사전에 라벨이 존재하지 않으므로, supervised classifier만으로는 적절히 다루기 어렵다. 본 연구에서는 이를 위해 자기지도 대조 학습 기반 임베딩 모델과 HDBSCAN 군집화를 결합한 파이프라인을 구성하였다. 백본은 ConvNeXtV2를 재사용하되 projection head를 추가하여 임베딩 공간을 학습하였다.

대조 학습 손실은 Global InfoNCE와 Local InfoNCE를 함께 사용하였다. Global loss는 전체 표현 공간에서 샘플 간 구분력을 높이고, memory queue를 통해 풍부한 negative pair를 효율적으로 활용한다. 반면 Local loss는 feature map 상의 국소 영역 유사성을 학습하여, 전역 평균 표현만으로는 포착하기 어려운 결함 패턴의 세부 구조를 보완한다. 이때 웨이퍼 맵은 좌우 반전이 물리적 의미를 훼손할 수 있으므로, 일반 영상 증강과 달리 flip은 배제하고 소규모 회전, 이동, 스케일 변화, 노이즈만을 적용하였다. 이는 반도체 맵 데이터에 대한 도메인 제약을 학습 증강 전략에 직접 반영한 사례이다.

학습된 임베딩에 대해서는 HDBSCAN을 적용하여 unknown 샘플을 자동 군집화하였다. HDBSCAN은 클러스터 수를 사전에 정하지 않아도 되며, 밀도 기반으로 잡음 샘플을 분리할 수 있어 신규 불량 후보 발굴에 적합하다. 본 구현에서는 minimum cluster size, minimum samples, cluster selection epsilon뿐 아니라, median membership probability, persistence, cluster size 기준을 함께 사용하여 keep/ignore 클러스터를 구분하였다. 또한 각 군집에 대해 medoid 대표 이미지와 summary를 저장하여, 전문가가 군집 품질을 빠르게 검토할 수 있도록 하였다.

### 2.4 Failbit Map 생성 및 분석 환경

본 연구의 또 다른 특징은 모델 학습과 운영 도구가 동일한 데이터 표현을 공유하도록 설계했다는 점이다. 웨이퍼 맵 생성 단계에서는 색상 자체보다 인덱스 의미가 중요한 palette-indexed PNG 방식을 채택하였다. Grade, 배경, 텍스트, border, BIN border의 팔레트 인덱스 계약을 고정함으로써, 후속 UI에서는 이미지 재생성 없이 PLTE patch만으로 색상 스킴이나 overlay 표현을 빠르게 전환할 수 있도록 하였다. 이는 대용량 웨이퍼 맵 시각화에서 응답성을 높이는 실용적 장점이 있다.

동시에 positions JSON에는 칩별 rect, grid_edges, 좌표계 정보와 함께 칩 단위 메타데이터를 저장하였다. 특히 Bucket B 데이터로부터 FTN/QTN 값을 파싱하여 각 칩에 연계하고, LT/TM, yield, sys, gd 등의 정보도 함께 보존하였다. UI에서는 이를 BIN/FBT/QVL overlay와 composite map 형태로 노출하여, 단순 이미지 패턴뿐 아니라 칩 단위 계측 경향까지 함께 검토할 수 있게 하였다. 여기서 FBT/QVL은 운영 화면에서 사용되는 계측값 관점의 표현이며, 내부 저장 구조는 FTN/QTN 및 관련 메타데이터를 기반으로 한다.

결과적으로 본 시스템의 UI는 단순 viewer가 아니라, chip overlay, chip annotation, personal color scheme, measure overlay, composite generation, cluster review를 통합한 분석 환경으로 동작한다. 이는 모델 출력의 해석 가능성과 라벨 확장 workflow를 지원하는 운영 계층으로서 중요한 의미를 가진다.

---

## 3. 실험 및 구현 결과

등록 불량 경로에 대한 정량 결과를 Table 1에 정리하였다.

| 방법 | Weighted F1 | 설명 |
|------|-------------|------|
| ConvNeXtV2 단일 분류기 | 0.92 | 기등록 클래스 분류 baseline |
| ConvNeXtV2 + ROI prior + YOLO 2차 검증 | 0.95 | 제안한 2단계 구조 |

제안 방법은 baseline 대비 3%p의 성능 향상을 보였다. 이 향상은 단순 백본 변경의 결과가 아니라, Grad-CAM 기반 ROI 추출, 클래스별 평균 ROI spatial prior, 저신뢰 샘플 중심의 선택적 보강, YOLO 기반 이차 검증이 결합된 결과이다. 특히 2차 검증은 성능 향상뿐 아니라 라벨 이상 샘플을 재검토 후보로 좁히는 데에도 유용하게 작동하였다.

미등록 불량 경로는 현재 정량 ground truth 체계가 충분히 정리되지 않아, 군집 purity나 NMI와 같은 정량 지표보다는 운영 검토 중심으로 평가하였다. 그럼에도 불구하고 contrastive embedding과 HDBSCAN을 통해 unknown 샘플을 의미 있는 cluster candidate로 정리하고, 대표 이미지 및 cluster summary를 자동 생성할 수 있음을 확인하였다. 이는 향후 신규 라벨 등록 workflow를 체계화하는 출발점으로 활용 가능하다.

현재 코드 기준으로 unknown 경로의 품질을 높인 핵심 요소는 다음과 같이 정리할 수 있다. 첫째, 웨이퍼 맵의 위치 의미를 보존하기 위해 좌우 반전을 제거하고, 소규모 회전·이동·스케일 변화와 노이즈만 적용하여 도메인 친화적 증강을 사용하였다. 둘째, backbone은 고정하고 projection head만 학습하여 기존 웨이퍼 표현을 안정적으로 유지하였다. 셋째, Global InfoNCE에 queue-based negative bank를 결합하여 더 풍부한 negative pair를 확보하되, 지나치게 유사한 negative는 제외하여 false negative를 줄였다. 넷째, Local InfoNCE를 추가하여 전역 평균 임베딩만으로 놓치기 쉬운 국소 결함 패턴을 보완하였다. 다섯째, HDBSCAN 후처리에서 cluster size, median membership probability, persistence를 기준으로 keep/ignore 클러스터를 나누어, 노이즈나 약한 군집이 곧바로 신규 불량 후보로 해석되지 않도록 하였다.

unknown defect의 성능 평가는 본질적으로 supervised classification과 다른 기준이 필요하다. 본 연구에서는 다음과 같은 세 단계 평가 프로토콜을 제안한다. 첫째, 오프라인 평가에서는 일부 클래스를 의도적으로 train set에서 제외한 뒤 unknown set으로 보내는 pseudo-open-set 실험을 수행하고, cluster purity, NMI, ARI, noise ratio, kept cluster coverage를 측정한다. 둘째, 현재 구현처럼 cluster summary가 생성되는 운영 환경에서는 median probability, persistence, cohesion, margin과 같은 내부 cluster quality 지표를 사용하여 군집의 안정성을 평가한다. 셋째, 실제 현업 기준에서는 전문가가 의미 있는 신규 불량으로 승인한 cluster 비율, 군집당 검토 이미지 수, 신규 라벨 등록까지의 시간 단축량을 측정하는 것이 중요하다. 즉 unknown 경로의 평가는 "정확히 몇 퍼센트 맞췄는가"보다 "신규 불량 후보를 얼마나 잘 압축해서 검토 가능한 형태로 제시했는가"에 더 가깝다.

구현 측면에서는 모델 외 요소들도 중요한 결과로 볼 수 있다. palette PNG 기반 표현은 색상 교체와 composite 재표현을 빠르게 수행하게 하였고, positions JSON은 이미지, 칩 좌표, 계측값을 정합된 단위로 연결하였다. 또한 BIN/FBT/QVL overlay와 annotation UI는 분류 결과 해석, 수동 검토, 후속 라벨링을 지원함으로써, 연구용 모델을 현업 분석 workflow에 연결하는 기반을 제공하였다. 마지막으로 칩 단위 FTN/QTN 및 기타 메타데이터를 함께 축적함으로써, 향후 이미지와 수치 계측값을 함께 사용하는 multimodal defect analysis 연구로 자연스럽게 확장할 수 있는 데이터 토대를 마련하였다.

Table 2는 등록 불량 및 미등록 불량 경로에서 성능 향상에 기여한 주요 요소를 정리한 것이다.

| 경로 | 성능 향상 요소 | 역할 |
|------|----------------|------|
| 등록 불량 | difficult class 식별 | 재검증이 필요한 클래스에 후단 보정 집중 |
| 등록 불량 | low-confidence 샘플 선택적 ROI 보강 | 불필요한 과보정 방지 및 계산 효율 확보 |
| 등록 불량 | 클래스별 평균 ROI spatial prior | noisy Grad-CAM을 공간 사전 정보로 안정화 |
| 등록 불량 | ROI blend alpha / min ROI / confidence 옵션화 | 데이터셋 특성에 맞는 보정 강도 조절 |
| 등록 불량 | YOLO 기반 이차 검증 및 class-object mapping | 라벨 노이즈 후보 탐지와 객체 일관성 검증 |
| 미등록 불량 | no-flip 도메인 증강 | 위치/방향 의미 보존 |
| 미등록 불량 | Global InfoNCE + queue | 임베딩 분리도 향상 및 negative 다양성 확보 |
| 미등록 불량 | Local InfoNCE | 국소 결함 패턴 보존 |
| 미등록 불량 | HDBSCAN keep/ignore filtering | 약한 군집과 노이즈 제거, 검토 품질 향상 |

---

## 4. 결론

본 연구는 Failbit Map 기반 반도체 웨이퍼 불량 분석을 위해 등록 불량 분류와 미등록 불량 탐지를 결합한 도메인 지식 기반 지도-비지도 복합 파이프라인을 제안하였다. 등록 불량 경로에서는 ConvNeXtV2, Grad-CAM, ROI spatial prior, YOLO 2차 검증을 결합하여 weighted F1 0.95를 달성하였고, 미등록 불량 경로에서는 contrastive learning과 HDBSCAN을 통해 신규 불량 후보 군집을 생성하는 구조를 구현하였다. 또한 palette PNG, positions JSON, 칩 단위 계측값 정합, BIN/FBT/QVL 분석 UI를 함께 구축하여 단순 분류 모델을 넘어서는 운영형 분석 기반을 제시하였다.

본 연구는 아직 모든 제품군과 공정 라인에 대해 완전한 운영 배포를 목표로 한 단계는 아니며, 파일럿 수준의 통합 구조와 그 가능성을 보이는 데 초점을 두었다. 그럼에도 불구하고 본 시스템은 등록된 불량의 정밀 분류, 미등록 불량의 탐색적 발굴, 전문가 검토 기반 라벨 확장, 그리고 향후 multimodal 분석으로의 진화를 하나의 아키텍처 안에서 연결했다는 점에서 의의를 가진다. 향후에는 unknown defect 평가 지표 정립, 칩 레벨 국소 분석 고도화, 이미지와 계측값을 함께 활용하는 융합 모델 설계, 제품군 확장 검증을 통해 실사용 범위를 더욱 넓힐 계획이다.

---

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," IEEE Transactions on Semiconductor Manufacturing, 2018.

[2] M. B. Alawieh et al., "Wafer Map Defect Patterns Classification Using Deep Neural Networks," DAC, 2019.

[3] S. Woo et al., "ConvNeXt V2: Co-designing and Scaling ConvNets with Masked Autoencoders," CVPR, 2023.

[4] R. R. Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization," ICCV, 2017.

[5] G. Jocher et al., "Ultralytics YOLO," GitHub, 2023.

[6] R. J. G. B. Campello et al., "Density-Based Clustering Based on Hierarchical Density Estimates," PAKDD, 2013.

[7] T. Chen et al., "A Simple Framework for Contrastive Learning of Visual Representations," ICML, 2020.
