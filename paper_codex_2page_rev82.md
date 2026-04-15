# DRAM Failbit Map 기반 Known·Unknown 불량 분류·검출 아키텍처

**A Known/Unknown Defect Classification and Detection Architecture Based on DRAM Failbit Maps**

홍길동¹, 김철수¹
¹ 반도체연구소, Samsung Electronics, 화성시, 대한민국

## 초록

Failbit Map은 반도체 EDS Test에서 생성되는 웨이퍼당 약 1,000만 point 규모의 초고밀도 데이터로, 수율 개선을 위한 공간적 불량 패턴 해석의 핵심 자료이다. 그러나 데이터 규모와 열람 한계로 인해 실제 현업에서는 Failbit Map 대신 chip별 Measure 평균 기반 분석에 주로 의존해 왔으며, 등록 불량의 세밀한 분류와 미등록 Unknown 불량 후보 발굴을 동시에 수행하기 어려웠다. 본 논문은 이를 해결하기 위해 DRAM Failbit Map 기반 Known·Unknown 불량 분류·검출 아키텍처를 제안한다. Known 경로에서는 ConvNeXtV2-Base를 주 분류기로 사용하고, wafer 내 발생 영역이 유사하여 혼동이 집중되는 저신뢰 샘플에 한해 Grad-CAM ROI 기반 YOLO를 선택적으로 적용하는 2단계 구조를 설계하여 16-class weighted F1을 0.78에서 0.95까지 향상시켰다. Unknown 경로에서는 SimCLR 계열 contrastive learning, 6×6 structured local sampling, HDBSCAN 군집화를 결합하여 5일치 운영 이미지 약 10,000장으로 표현 공간을 학습하고 별도 1일치 2,000장을 13개 후보 그룹으로 압축하였다. 이는 직접 검토해야 할 대상을 약 154배 줄인 결과이며, 13개 그룹 모두 설명 가능한 패턴으로 정리되었다. 이 중 7개는 실제 의미 있는 불량 그룹으로 확인되었고, 나머지 후보 역시 1 lot 편중 패턴 또는 현업 불량으로 이어지지 않은 이상 이미지로 정리되어 후속 검토 리스트로 활용되었다. 또한 palette-indexed PNG 기반 데이터 표현, 고속 UI, 후속 원인 분석용 Measure 연계를 통해 제안 아키텍처가 실제 불량 분석 workflow에 활용될 수 있음을 확인하였다.

Keywords: Failbit Map, FTN, QTN, Wafer Defect Analysis, ConvNeXtV2, ROI-YOLO, Contrastive Learning, HDBSCAN

## 서론

Failbit Map은 EDS Test에서 wafer 내 memory cell block의 fail 상태를 공간적으로 기록한 결과 데이터로, block별 fail cell 개수를 grade 0-7로 표현한다. Wafer 1장에는 약 1,000만 개 수준의 block이 존재하므로 Failbit Map은 불량의 위치, 밀집도, 형상, 방향성을 직접 보여주는 초고밀도 공간 데이터이며 수율 저하 원인 분석의 핵심 근거가 된다.

그러나 기존 현업 분석은 여전히 chip 단위 Measure 빈도 집계와 wafer 평균 비교에 크게 의존하고 있어, Map 수준에서만 드러나는 spatial defect와 중복 불량을 충분히 반영하지 못한다. 분석 관점에서 Failbit Map이 불량의 결과라면, FTN과 QTN은 원인을 좁히는 단서가 된다. 특정 FTN 또는 QTN test에서 이상값이 나타나면 bitline 또는 wordline 계열 이상을 추정할 수 있고, 특히 QTN은 cell block 내부의 cell 불량 패턴까지 제공하므로 관련 공정 분석으로 직접 연결될 수 있다.

실제 운영 환경에서는 원시 log가 wafer당 10-50MB 수준이며 기존 시스템도 1초당 1매, 최대 48매 수준으로만 조회가 가능해 특정 제품에서 하루 약 2,000장씩 발생하는 Failbit Map을 전수 확인하기 어렵다. Measure 데이터 역시 약 20조 row 규모 DB에 분산되어 있어 이미지와 계측값을 함께 overlay 또는 side-by-side로 해석하기가 사실상 불가능했다. 기존 연구가 주로 wafer map의 closed-set 분류 정확도 향상에 초점을 맞추었다면 [1-3], 사내 현업에서 필요한 것은 실제로 발생하는 등록 불량을 높은 정확도로 분류하고, 동시에 정의되지 않은 Unknown 불량 후보를 자동 발굴할 수 있는 AI 분석 아키텍처이다. 여기에 대량 Map 조회와 후속 원인 분석 연계가 더해져야 비로소 실제 활용성이 확보된다.

정리하면 본 연구의 기여는 다음과 같다. 첫째, ConvNeXtV2와 선택적 ROI-YOLO를 결합한 2단계 구조로 등록 불량의 취약 샘플을 정밀하게 분류하였다. 둘째, contrastive learning과 HDBSCAN을 결합하여 실제 운영 이미지에서 Unknown 후보를 그룹 단위로 압축하고 검토 리스트를 생성하였다. 셋째, Failbit Map과 FTN·QTN을 동일 chip 기준으로 정합하고 대량 조회 UI와 연결하여, 분류·검출 결과가 후속 원인 분석과 향후 multimodal 확장으로 이어질 수 있는 기반을 구축하였다.

## 제안 방법

### 데이터 생성 및 표현 계층

제안 아키텍처의 기반 계층은 설비 log를 서버에서 1시간 주기로 자동 수집하고, Failbit Map 이미지를 사전 변환하여 Known·Unknown 분석과 UI에 동시에 활용할 수 있도록 적재하는 구조이다. Failbit Map은 grade 0-7과 chip boundary 등 제한된 색상 집합만 사용하므로 palette-indexed PNG로 저장해 RGB 대비 약 75%의 용량 절감을 달성하였다. 또한 chip index 기준으로 FTN, QTN, BIN 정보를 정합하여 Failbit Map과 Measure를 동일 화면에서 overlay, composite, side-by-side 형태로 함께 해석할 수 있도록 하였다. 현재 FTN·QTN은 모델 입력이 아니라 원인 해석과 공정 추적을 위한 분석 정보로 활용되며, 20조 row DB를 직접 반복 조회하던 구조 대신 사전 정합된 annotation으로 제공하여 ms급으로 즉시 확인할 수 있도록 하였다. 이러한 정합 구조는 향후 multimodal 분석의 기반으로도 활용될 수 있다.

### Known 불량 분류

Known 불량 분석은 16개 기등록 클래스를 대상으로 하며, 총 1,500개의 라벨된 Failbit Map을 사용하였다. Backbone 후보로는 Hugging Face에서 제공되는 `facebook/convnextv2-base-22k-384` [8]와 `timm/maxvit_base_tf_384.in21k_ft_in1k` [9,10]를 포함한 사전학습 모델을 비교하였다. MaxViT와 ConvNeXtV2는 분류 성능이 유사했으나, MaxViT의 추론 속도가 더 느려 본 연구에서는 성능-속도 균형이 더 우수한 ConvNeXtV2-Base [4,8]를 최종 backbone으로 채택하였다. baseline 대비 backbone 교체와 하이퍼파라미터 최적화 후 weighted F1은 0.78에서 0.92까지 향상되었다.

다만 center, edge, local 계열처럼 wafer 내 발생 영역이 유사한 클래스에서는 전역 문맥만으로는 취약 샘플이 남았고, 이러한 샘플은 공통적으로 confidence가 낮게 나타났다. 이에 모든 샘플에 detector를 적용하지 않고, 저신뢰 샘플에 한해 Grad-CAM 기반 ROI [5]와 ROI-YOLO를 선택적으로 적용하여 chip 수준의 국부 형상을 다시 확인하도록 설계하였다. 그 결과 ConvNeXtV2 단독 분류기의 weighted F1 0.92를 0.95까지 향상시켰으며, 전체 속도 저하를 최소화하면서 유사 클래스 간 오분류를 보정할 수 있음을 확인하였다.

### Unknown 후보 발굴

Unknown 불량은 사전에 정답 클래스를 정의하기 어려운 실제 운영 이미지를 대상으로 하므로, 본 연구에서는 이를 정답 분류 문제가 아니라 후보 grouping 문제로 정의하였다. 특정 제품의 하루 전체 Map이 약 2,000장 수준으로 발생하는 환경에서, 5일치 운영 데이터 약 10,000장으로 SimCLR 계열 contrastive learning [6] 기반 임베딩을 학습하고, 별도 1일치 2,000장에 HDBSCAN [7]을 적용하여 유사 패턴을 후보 그룹 단위로 압축하였다.

이때 6×6 grid 기반 structured local sampling을 적용하여 wafer 내 위치와 형상 정보를 함께 반영하였고, 실제 운영 이미지 2,000장은 13개 후보 그룹으로 정리되었다. Unknown 경로는 closed-set 분류처럼 정답 label 기반 F1으로 평가하는 대신, 실제 현업에서 필요한 후보 발굴 성과로 평가하였다. 구체적으로는 (1) 하루 2,000장의 검토 대상을 13개 그룹으로 압축한 검토 단위 축소 효과, (2) 각 그룹이 실제 불량, 1 lot 편중 패턴, 이상 이미지 중 하나로 설명 가능한 해석 가능성, (3) 이 중 실제 의미 있는 불량 그룹을 얼마나 발굴했는가의 세 축으로 해석하였다. 분석 담당자 검토 결과 13개 그룹 모두 설명 가능한 패턴으로 정리되었고, 이 중 7개는 실제 의미 있는 불량 그룹으로 확인되었다. 나머지 후보 역시 1 lot 편중 패턴 또는 현업 불량으로 이어지지 않은 이상 이미지로 분류되어, 무의미한 랜덤 군집이 아니라 실제 검토 가치가 있는 후보 묶음을 자동 생성했음을 보여준다.

### 분석 UI와 후속 연계

사전 변환 구조를 통해 UI에서는 Failbit Map을 초당 약 50매 수준으로 로드하고, 최대 5,000매를 단일 grid에서 끊김 없이 탐색할 수 있도록 하였다. 사용자는 Failbit Map과 FTN·QTN을 함께 비교하며 불량 유형과 샘플을 즉시 등록할 수 있고, 등록 결과는 이후 Known 분류 학습 데이터와 Unknown 검토 이력으로 연결된다. 즉, 본 시스템은 대량 이미지 탐색, 후보 선별, 원인 추론, 데이터 등록을 하나의 흐름으로 연결한 분석 체계이다.

## 결과 및 논의

**Table 1. 등록 불량 Backbone 비교 및 ConvNeXtV2 개선 단계 (16-class, test Weighted F1)**

표 1과 같이 backbone fine-tuning 비교에서는 MaxViT와 ConvNeXtV2가 가장 높은 수준의 성능을 보였으나, MaxViT의 추론 속도가 더 느려 본 연구에서는 ConvNeXtV2를 최종 backbone으로 선택하였다. 이후 Optuna 기반 하이퍼파라미터 최적화로 weighted F1을 0.92까지 향상시켰고, 저신뢰 샘플에 대한 선택적 ROI-YOLO 보정을 추가하여 최종 0.95를 달성하였다. 이는 wafer 전역 문맥을 빠르게 판별하는 CNN과 취약 샘플을 국부적으로 재확인하는 ROI-YOLO의 역할 분리가 유효함을 보여준다.

Unknown 경로에서는 특정 제품의 하루 2,000장 이미지를 13개 후보 그룹으로 압축하여 검토 단위를 약 154배 축소하였다. 13개 그룹은 모두 실제 의미를 해석할 수 있는 패턴으로 정리되었고, 이 중 7개는 실제 의미 있는 불량 그룹으로 판정되었다. 나머지 후보도 1 lot 편중 패턴 또는 현업 불량으로 이어지지 않은 이상 이미지로 정리되어, 후보 리스트 전체가 검토 가능한 작업 단위로 기능하였다. 즉 Unknown 결과의 핵심은 단순 군집 정확도가 아니라, 대량 운영 이미지에서 실제 검토 가치가 있는 후보 리스트를 안정적으로 생성했다는 점이다.

시스템 측면에서도 FTN·QTN 연계와 대량 Map 탐색 UI를 통해 후속 분석 효율을 함께 개선하였다.

## 결론

본 연구는 DRAM Failbit Map을 대상으로 등록 불량을 정밀 분류하고 미등록 불량 후보를 자동 발굴하는 Known·Unknown 불량 분석 아키텍처를 제안하였다. Known 경로에서는 ConvNeXtV2와 선택적 ROI-YOLO의 역할 분리를 통해 높은 분류 성능을 확보하였고, Unknown 경로에서는 contrastive learning 기반 표현 학습과 군집화를 통해 실제 검토 가능한 후보 리스트를 생성할 수 있음을 확인하였다. 또한 Failbit Map의 결과 정보와 FTN·QTN의 원인 단서를 같은 분석 환경에서 해석할 수 있도록 함으로써, defect pattern 확인에서 공정 원인 추론까지 이어지는 분석 흐름을 마련하였다. 향후에는 현재 구축한 정합 구조를 바탕으로 Failbit Map 이미지와 FTN·QTN test 정보를 함께 활용하는 multimodal 분석으로 확장할 계획이다.

## 참고문헌
- [1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," IEEE Transactions on Semiconductor Manufacturing, vol. 31, no. 2, pp. 309-314, 2018.
- [2] M. B. Alawieh, D. Boning, and D. Z. Pan, "Wafer Map Defect Patterns Classification Using Deep Selective Learning," in Proceedings of the 57th ACM/IEEE Design Automation Conference (DAC), pp. 1-6, 2020.
- [3] J. Jang and G. T. Lee, "Decision fusion approach for detecting unknown wafer bin map patterns based on a deep multitask learning model," Expert Systems with Applications, vol. 215, art. 119363, 2023.
- [4] S. Woo et al., "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 16133-16142, 2023.
- [5] R. R. Selvaraju et al., "Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based Localization," in Proceedings of the IEEE International Conference on Computer Vision (ICCV), pp. 618-626, 2017.
- [6] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in Proceedings of the 37th International Conference on Machine Learning (ICML), PMLR 119, pp. 1597-1607, 2020.
- [7] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in Advances in Knowledge Discovery and Data Mining, PAKDD 2013, pp. 160-172, 2013.
- [8] Hugging Face, "facebook/convnextv2-base-22k-384," model card, accessed Apr. 15, 2026. Available: https://huggingface.co/facebook/convnextv2-base-22k-384
- [9] Hugging Face timm, "maxvit_base_tf_384.in21k_ft_in1k," model card, accessed Apr. 15, 2026. Available: https://huggingface.co/timm/maxvit_base_tf_384.in21k_ft_in1k
- [10] Z. Tu et al., "MaxViT: Multi-Axis Vision Transformer," in Proceedings of the European Conference on Computer Vision (ECCV), pp. 459-479, 2022.
