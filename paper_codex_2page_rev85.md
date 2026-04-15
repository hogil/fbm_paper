# DRAM Failbit Map 기반 Known·Unknown 불량 분석 AI 아키텍처

**An AI Architecture for Known/Unknown Defect Analysis Based on DRAM Failbit Maps**

홍길동¹, 김철수¹

¹ 반도체연구소, Samsung Electronics, 화성시, 대한민국

## 초록

Failbit Map은 반도체 EDS Test에서 생성되는 웨이퍼당 약 1,000만 point 규모의 초고밀도 데이터로, 수율 개선을 위한 공간적 불량 패턴 해석의 핵심 자료이다. 그러나 기존 시스템은 호출 기반으로 소수의 Map만 조회할 수 있어, 하루 수천 장 규모의 대량 분석을 위해서는 raw data를 별도로 수집해 Failbit Map과 메타데이터로 재구성하는 과정이 먼저 필요했다. 그 결과 실제 현업에서는 Failbit Map 대신 chip별 Measure 평균 기반 분석에 주로 의존해 왔으며, 등록 불량의 세밀한 분류와 미등록 Unknown 불량 후보 발굴을 동시에 수행하기 어려웠다. 본 논문은 이를 해결하기 위해 DRAM Failbit Map 기반 Known·Unknown 불량 분석 AI 아키텍처를 제안한다. Known 경로에서는 ConvNeXtV2-Base를 주 분류기로 사용하고, wafer 내 발생 영역이 유사하여 혼동이 집중되는 저신뢰 샘플에 한해 Grad-CAM ROI 기반 YOLO를 선택적으로 적용하는 2단계 구조를 설계하여 16-class weighted F1을 0.78에서 0.95까지 향상시켰다. Unknown 경로에서는 SimCLR 계열 contrastive learning, 6×6 structured local sampling, HDBSCAN 군집화를 결합하여 5일치 운영 이미지 약 10,000장으로 표현 공간을 학습하고 별도 1일치 2,000장을 13개 후보 그룹으로 압축하였다. 이는 직접 검토해야 할 대상을 약 154배 줄인 결과이며, 13개 그룹 모두 설명 가능한 패턴으로 정리되었다. 이 중 7개는 실제 의미 있는 불량 그룹으로 확인되었고, 나머지 후보 역시 1 lot 편중 패턴 또는 현업 불량으로 이어지지 않은 이상 이미지로 정리되어 후속 검토 리스트로 활용되었다. 또한 raw data 재구성, palette-indexed PNG 표현, 고속 UI, 후속 원인 분석용 Measure 연계를 결합함으로써, 제안 아키텍처가 실제 대량 불량 분석 환경에서 동작할 수 있음을 확인하였다.

Keywords: Failbit Map, Known Defect Classification, Unknown Defect Discovery, ConvNeXtV2, ROI-YOLO, Contrastive Learning, HDBSCAN

## 서론

Failbit Map은 EDS(Electrical Die Sorting) Test에서 각 Memory Cell Block의 불량 cell 개수를 Grade 0(정상)부터 7(최대 불량)까지로 표현한 데이터이다. Wafer 1장에는 평균적으로 약 1,000만 개의 block이 포함되므로, Failbit Map은 불량의 위치, 밀집도, 형상, 방향성을 직접 반영하는 초고밀도 공간 데이터이자 수율 저하 원인 분석의 핵심 근거가 된다. 그러나 현업 분석은 주로 Chip 단위 Measure(측정 항목별 집계값)의 발생 빈도를 기준으로 이상 여부를 판단하고 있어, Failbit Map 전체에서만 드러나는 불량 분포의 공간 패턴을 충분히 포착하지 못한다. 이로 인해 수율 저하 원인이 오분류되거나 미검출될 수 있으며, 정밀한 원인 분석을 위해서는 Measure 기반 접근을 넘어 Failbit Map 자체를 핵심 분석 단위로 활용할 필요가 있다.

Failbit Map 기반 분석을 실제 현업에 적용하기 위해서는 대량 Map 생성 체계와 자동 분석 체계가 동시에 확보되어야 한다. 대량 Map 생성 체계가 없으면 AI 학습과 운영에 필요한 입력 데이터를 충분히 확보할 수 없고, 반대로 자동 분석 체계가 없으면 생성된 Map 역시 엔지니어의 수작업 판정 병목을 해소할 수 없다. 설비 Log는 Wafer당 10~50MB 수준이며 특정 제품군에서는 하루 약 2,000장의 Wafer가 발생하지만, 기존 환경에서는 Log 다운로드, 데이터 변환, 이미지 생성 과정의 속도 및 메모리 제약으로 인해 한 번에 48매 이하만 처리할 수 있다. 또한 설령 Map 생성 체계가 확보되더라도 불량 여부와 유형 판단은 여전히 엔지니어의 직접 확인에 의존하고 있어, 대량 데이터를 일관되게 전수 분석하는 데 한계가 있다.

따라서 실제 현업 적용을 위해서는 대량 Raw Data를 Failbit Map으로 안정적으로 변환, 생성, 저장, 조회할 수 있는 데이터 파이프라인과, 그 위에서 Known 불량은 정밀하게 분류하고 기존 분류 체계에 등록되지 않은 상태에서 새롭게 발생하는 Unknown 불량은 검출할 수 있는 AI 구조가 함께 필요하다. Known 불량 분석에서는 Wafer 전역 형상과 국소 위치 정보를 함께 고려해야 하며, Unknown 불량 분석에서는 레이블이 없는 데이터로부터 새로운 패턴을 식별할 수 있어야 한다. 본 논문은 이러한 요구를 충족하기 위해 Failbit Map 기반 Known 불량 분류와 Unknown 불량 검출을 통합한 AI 아키텍처와, 이를 현업에 적용하기 위한 End-to-End 분석 구조를 구현하여 실데이터에 적용·검증하였다. 본 논문의 주요 기여는 다음과 같다.

첫째, Test 부서와의 협의를 통해 대량 Raw Data 적재 체계를 구축하고, 이를 기반으로 전수 Failbit Map 생성 파이프라인을 구현하였다. 또한 palette-indexed PNG를 적용하여 기존 포맷 대비 이미지 용량을 약 75% 절감하였다. 아울러 실시간 설비 Log 수집과 1시간 주기의 Failbit Map 생성 체계를 구축함으로써, 대량 Failbit Map의 생성, 저장, 조회 및 AI 분석이 가능한 운영 기반을 마련하였다.

둘째, Known 불량의 정밀 분류를 위해 ConvNeXt V2와 ROI(Region of Interest) 기반 YOLO를 결합한 2단계 분석 구조를 제안하였다. 1단계에서는 ConvNeXt V2를 이용해 Wafer 전역 패턴을 우선 분류하고, 전역 형상만으로 구분이 어려워 신뢰도가 낮은 샘플에 한해 2단계에서 ROI 기반 YOLO를 선택적으로 적용하여 불량 영역의 위치 정보를 추가 반영하였다. 이를 통해 전역 패턴과 국소 위치 정보를 함께 활용하는 정밀 분류를 구현하였다.

셋째, 기존 분류 체계에 등록되지 않은 상태에서 새롭게 발생하는 Unknown 불량을 검출하기 위해 SimCLR 계열 contrastive learning 기반의 Unknown 불량 분석 구조를 구현하였다. 또한 grid structured local sampling을 적용하여 Wafer를 격자 단위의 국소 영역으로 나누어 특징을 학습함으로써, 동일한 형태의 불량이라도 발생 위치가 다를 경우 구분될 수 있도록 하였다. 이를 통해 Unknown 불량을 개별 샘플이 아닌 유사 패턴 그룹 수준에서 검출하고 해석할 수 있도록 하였다.

## 제안 방법

### 데이터 생성 및 표현 계층

제안 아키텍처의 기반 계층은 기존 시스템의 호출형 조회만으로는 Known·Unknown AI 분석을 대량 운영 데이터에 적용할 수 없다는 한계를 해결하기 위해, 설비 log 기반 raw data를 서버에서 1시간 주기로 자동 수집하고 이를 Failbit Map 이미지와 메타데이터로 재구성하여 분석과 UI에 동시에 활용할 수 있도록 적재하는 구조이다. Failbit Map은 grade 0-7과 chip boundary 등 제한된 색상 집합만 사용하므로 palette-indexed PNG로 저장해 RGB 대비 약 75%의 용량 절감을 달성하였다. 또한 chip index 기준으로 FTN, QTN, BIN 정보를 정합하여 Failbit Map과 Measure를 동일 화면에서 overlay, composite, side-by-side 형태로 함께 해석할 수 있도록 하였다. 현재 FTN·QTN은 모델 입력이 아니라 원인 해석과 공정 추적을 위한 분석 정보로 활용되며, 20조 row DB를 직접 반복 조회하던 구조 대신 사전 정합된 annotation으로 제공하여 ms급으로 즉시 확인할 수 있도록 하였다. 이러한 정합 구조는 향후 multimodal 분석의 기반으로도 활용될 수 있다.

### Known 불량 분류

Known 불량 분석은 16개 기등록 클래스를 대상으로 하며, 총 1,500개의 라벨된 Failbit Map을 사용하였다. Backbone 후보로는 Hugging Face에서 제공되는 `facebook/convnextv2-base-22k-384` [8]와 `timm/maxvit_base_tf_384.in21k_ft_in1k` [9,10]를 포함한 사전학습 모델을 비교하였다. MaxViT와 ConvNeXtV2는 분류 성능이 유사했으나, MaxViT의 추론 속도가 더 느려 본 연구에서는 성능-속도 균형이 더 우수한 ConvNeXtV2-Base [4,8]를 최종 backbone으로 채택하였다. baseline 대비 backbone 교체와 하이퍼파라미터 최적화 후 weighted F1은 0.78에서 0.92까지 향상되었다.

다만 center, edge, local 계열처럼 wafer 내 발생 영역이 유사한 클래스에서는 전역 문맥만으로는 취약 샘플이 남았고, 이러한 샘플은 공통적으로 confidence가 낮게 나타났다. 이에 모든 샘플에 detector를 적용하지 않고, 저신뢰 샘플에 한해 Grad-CAM 기반 ROI [5]와 ROI-YOLO를 선택적으로 적용하여 chip 수준의 국부 형상을 다시 확인하도록 설계하였다. 그 결과 ConvNeXtV2 단독 분류기의 weighted F1 0.92를 0.95까지 향상시켰으며, 전체 속도 저하를 최소화하면서 유사 클래스 간 오분류를 보정할 수 있음을 확인하였다.

### Unknown 후보 발굴

Unknown 불량은 사전에 정답 클래스를 정의하기 어려운 실제 운영 이미지를 대상으로 하므로, 본 연구에서는 이를 정답 분류 문제가 아니라 후보 grouping 문제로 정의하였다. 특정 제품의 하루 전체 Map이 약 2,000장 수준으로 발생하는 환경에서, 5일치 운영 데이터 약 10,000장으로 SimCLR 계열 contrastive learning [6] 기반 임베딩을 학습하고, 별도 1일치 2,000장에 HDBSCAN [7]을 적용하여 유사 패턴을 후보 그룹 단위로 압축하였다.

이때 6×6 grid 기반 structured local sampling을 적용하여 wafer 내 위치와 형상 정보를 함께 반영하였고, 실제 운영 이미지 2,000장은 13개 후보 그룹으로 정리되었다. Unknown 경로는 closed-set 분류처럼 정답 label 기반 F1으로 평가하는 대신, 실제 현업에서 필요한 후보 발굴 성과로 평가하였다. 구체적으로는 (1) 하루 2,000장의 검토 대상을 13개 그룹으로 압축한 검토 단위 축소 효과, (2) 각 그룹이 실제 불량, 1 lot 편중 패턴, 이상 이미지 중 하나로 설명 가능한 해석 가능성, (3) 이 중 실제 의미 있는 불량 그룹을 얼마나 발굴했는가의 세 축으로 해석하였다. 분석 담당자 검토 결과 13개 그룹 모두 설명 가능한 패턴으로 정리되었고, 이 중 7개는 실제 의미 있는 불량 그룹으로 확인되었다. 나머지 후보 역시 1 lot 편중 패턴 또는 현업 불량으로 이어지지 않은 이상 이미지로 분류되어, 무의미한 랜덤 군집이 아니라 실제 검토 가치가 있는 후보 묶음을 자동 생성했음을 보여준다.

### 분석 UI와 후속 연계

사전 변환 구조를 통해 UI에서는 Failbit Map을 초당 약 50매 수준으로 로드하고, 최대 5,000매를 단일 grid에서 끊김 없이 탐색할 수 있도록 하였다. 사용자는 Failbit Map과 FTN·QTN을 함께 비교하며 불량 유형과 샘플을 즉시 등록할 수 있고, 등록 결과는 이후 Known 분류 학습 데이터와 Unknown 검토 이력으로 연결된다. 즉, 본 시스템은 대량 이미지 탐색, 후보 선별, 원인 추론, 데이터 등록을 하나의 흐름으로 연결한 분석 체계이다.

## 결과 및 논의

Table 1. 등록 불량 Backbone 비교 및 ConvNeXtV2 개선 단계 (16-class, test Weighted F1)

표 1과 같이 backbone fine-tuning 비교에서는 MaxViT와 ConvNeXtV2가 가장 높은 수준의 성능을 보였으나, MaxViT의 추론 속도가 더 느려 본 연구에서는 ConvNeXtV2를 최종 backbone으로 선택하였다. 이후 Optuna 기반 하이퍼파라미터 최적화로 weighted F1을 0.92까지 향상시켰고, 저신뢰 샘플에 대한 선택적 ROI-YOLO 보정을 추가하여 최종 0.95를 달성하였다. 이는 wafer 전역 문맥을 빠르게 판별하는 CNN과 취약 샘플을 국부적으로 재확인하는 ROI-YOLO의 역할 분리가 유효함을 보여준다.

Unknown 경로에서는 특정 제품의 하루 2,000장 이미지를 13개 후보 그룹으로 압축하여 검토 단위를 약 154배 축소하였다. 13개 그룹은 모두 실제 의미를 해석할 수 있는 패턴으로 정리되었고, 이 중 7개는 실제 의미 있는 불량 그룹으로 판정되었다. 나머지 후보도 1 lot 편중 패턴 또는 현업 불량으로 이어지지 않은 이상 이미지로 정리되어, 후보 리스트 전체가 검토 가능한 작업 단위로 기능하였다. 즉 Unknown 결과의 핵심은 단순 군집 정확도가 아니라, 대량 운영 이미지에서 실제 검토 가치가 있는 후보 리스트를 안정적으로 생성했다는 점이다.

또한 raw data 재구성, FTN·QTN 정합, 대량 Map 탐색 UI를 결합함으로써 AI 결과를 후속 원인 분석과 데이터 등록으로 바로 연결할 수 있었다.

## 결론

본 연구의 핵심은 그동안 평균 Measure 분석에 가려졌던 Failbit Map을 대량 AI 분석 대상으로 전환하고, Known·Unknown 불량을 하나의 아키텍처 안에서 동시에 다룰 수 있도록 설계했다는 점에 있다. Known 경로에서는 ConvNeXtV2와 선택적 ROI-YOLO의 역할 분리를 통해 높은 분류 성능을 확보하였고, Unknown 경로에서는 contrastive learning 기반 표현 학습과 군집화를 통해 실제 검토 가능한 후보 리스트를 생성할 수 있음을 확인하였다. 또한 raw data 재구성, FTN·QTN 정합, 대량 탐색 UI를 결합하여 AI 결과를 후속 원인 분석까지 연결하였으며, 향후에는 현재 구축한 정합 구조를 바탕으로 Failbit Map 이미지와 FTN·QTN test 정보를 함께 활용하는 multimodal 분석으로 확장할 계획이다.

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," IEEE Transactions on Semiconductor Manufacturing, vol. 31, no. 2, pp. 309-314, 2018.

[2] M. B. Alawieh, D. Boning, and D. Z. Pan, "Wafer Map Defect Patterns Classification Using Deep Selective Learning," in Proceedings of the 57th ACM/IEEE Design Automation Conference (DAC), pp. 1-6, 2020.

[3] J. Jang and G. T. Lee, "Decision fusion approach for detecting unknown wafer bin map patterns based on a deep multitask learning model," Expert Systems with Applications, vol. 215, art. 119363, 2023.

[4] S. Woo et al., "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 16133-16142, 2023.

[5] R. R. Selvaraju et al., "Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based Localization," in Proceedings of the IEEE International Conference on Computer Vision (ICCV), pp. 618-626, 2017.

[6] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in Proceedings of the 37th International Conference on Machine Learning (ICML), PMLR 119, pp. 1597-1607, 2020.

[7] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in Advances in Knowledge Discovery and Data Mining, PAKDD 2013, pp. 160-172, 2013.

[8] Hugging Face, "facebook/convnextv2-base-22k-384," model card, accessed Apr. 15, 2026. Available: https://huggingface.co/facebook/convnextv2-base-22k-384

[9] Hugging Face timm, "maxvit_base_tf_384.in21k_ft_in1k," model card, accessed Apr. 15, 2026. Available: https://huggingface.co/timm/maxvit_base_tf_384.in21k_ft_in1k

[10] Z. Tu et al., "MaxViT: Multi-Axis Vision Transformer," in Proceedings of the European Conference on Computer Vision (ECCV), pp. 459-479, 2022.
