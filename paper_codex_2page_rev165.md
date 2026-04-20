# Failbit Map Known & Unknown 불량 분석 아키텍처

**Hybrid Failbit Map Analysis Architecture for Known Classification and Unknown Discovery**

홍길동¹, 김철수¹

¹ 반도체연구소, Samsung Electronics, 화성시, 대한민국

(Abstract)

Failbit Map은 반도체 EDS Test에서 생성되는 웨이퍼당 약 1,000만 pixel 수준의 초고해상도 데이터로, 불량 패턴 분석의 핵심 자료이다. 그러나 실제 현업에서는 대량의 Failbit Map 조회가 불가능하고, 조회 가능한 일부 Map의 분석조차 엔지니어의 수작업에 의존하고 있다. 본 논문은 이를 해결하기 위해 대량 Failbit Map 데이터 파이프라인을 구축하고, Known 불량은 2-stage supervised classification으로, Unknown 불량은 self-supervised로 검출하는 아키텍처를 구현하였다. 변환 속도는 Cython 적용으로 약 100배 향상되었고, 이미지 용량은 32-color palette-indexed PNG 적용으로 약 75% 절감되었다. Known 불량 분류는 ConvNeXtV2 기반 1차 분류와 저신뢰 샘플에 대한 ROI(Region of Interest) 기반 YOLO 2차 분류를 결합한 구조로 설계하였으며, weighted F1 0.95를 달성하였다. Unknown 불량 검출에서는 SimCLR 계열 모델에 대조학습을 적용하였으며, wafer의 zone 기반 불량 해석 특성을 반영하기 위해 grid-structured local sampling을 함께 적용하였다. 양산 5일치 Failbit Map 10,000장을 학습에 사용하고 별도 1일치 2,000장에 적용한 결과 13개 불량 그룹이 검출되었으며, 이 중 7개가 현업 엔지니어 검증에서 실제 불량 그룹으로 판정되어 현업 적용 가능성을 입증하였다.

Keywords: Failbit Map, Wafer Failure Analysis, ConvNeXtV2, YOLO, Contrastive Learning, HDBSCAN

## 1. INTRODUCTION

Failbit Map은 EDS Test에서 Memory Cell Block 단위의 불량 정도를 Grade 0부터 7까지로 표현한 데이터이다. Wafer 1장에는 약 1,000만 개의 block이 존재하므로, 이는 불량의 위치와 형태를 반영하는 초고해상도 데이터이다. 현업의 Measure 기반 분석만으로는 이러한 정보를 확인할 수 없어 Failbit Map의 전수 분석이 필요하다.

실제 현업 적용에는 두 가지 제약이 있다. 첫째, 기존 시스템은 설비 Log를 대량 Failbit Map으로 변환하고 저장·조회하는 처리 성능이 부족하였다. 설비 Log는 Wafer당 10~50MB 수준이며 전 제품 기준 하루 약 2만 장의 Wafer가 생산되지만, 기존 환경에서는 속도와 메모리 제약으로 대량 처리가 어려웠고 엔지니어가 한 번에 조회·확인할 수 있는 수량도 48매 수준에 머물렀다. 둘째, 생성된 Map에 대한 불량 여부 및 유형 판정이 엔지니어의 수동 판독에 의존하여 전수 분석이 어려웠다. 본 논문은 이러한 한계를 해결하는 통합 분석 아키텍처를 제안하며, 주요 기여는 다음과 같다.

첫째, 대량 설비 Log의 실시간 적재와 1시간 주기 Failbit Map 생성 체계를 구현하여 대량 Map 운영이 가능한 데이터 처리 기반을 구축하였다. 둘째, Known 불량은 ConvNeXt V2 기반 1차 wafer-level 분류와 ROI 기반 YOLO 2차 분류를 결합한 2-stage 구조로 성능을 향상시켰다. 셋째, Unknown 불량은 SimCLR 계열 self-supervised 분석과 grid-structured local sampling을 통해 보다 정밀하게 검출하도록 하였다.

## 2. PROPOSED METHOD

본 아키텍처는 데이터 파이프라인, Known 2-stage 분류기, Unknown self-supervised 검출기로 구성되며, 전용 분석 Web App[5]으로 배포되었다.

### 2.1 DATA PIPELINE

데이터 파이프라인은 설비 Raw Log를 실시간 적재해 1시간 주기로 Failbit Map을 생성하도록 설계하였다. 핵심 병목은 wafer당 약 1,000만 개 test result의 hex-to-grade 변환 속도와 이미지 저장 용량이며, 전자는 Cython으로 약 100배 향상시켰고(Fig. 1), 후자는 32-color palette-indexed PNG로 약 75% 절감하였다(Fig. 2). 생성된 Map은 중앙 저장소에 적재되며 분석 Web App[5]으로 대량 조회·분석이 가능하다.

<table>
<tr><td>
<div align="center"><b>Hex-to-grade conversion</b></div>

```text
    Raw:
        090B0C0D0E0F090A0B0C

    Decoding:
        "0C" -> "C" -> 12 (hex to decimal) -> 3


    Python:
        interpreter-based loop execution

    Cython:
        compiled integer loop execution

    Grade:
        0 2 3 4 5 6 0 1 2 3
```
</td></tr>
</table>

**Fig. 1.** Hex-to-grade conversion accelerated by Cython

<table>
<tr><td>
<div align="center"><b>RGB PNG vs Palette-indexed PNG</b></div>

```text
    RGB PNG:
        [(123,54,24), (123,54,24), ..., (123,54,24)],
        [(123,54,24), (123,54,24), ..., (123,54,24)]

    Palette-indexed PNG:
        P[3] = (123,54,24)
        [(3), (3), ..., (3)],
        [(3), (3), ..., (3)]

    RGB_to_Palette:
        (123,54,24) -> (3)
```
</td></tr>
</table>

**Fig. 2.** Palette-indexed PNG for failbit map compression.

### 2.2 Known 불량 분류

Known 불량 분석은 16개 등록 클래스를 대상으로 하였으며, 1,500개의 Failbit Map을 사용하여 ConvNeXtV2[1] 기반 1단계 wafer-level 분류기와 저신뢰 샘플 대상 2단계 ROI(Region of Interest) 기반 YOLO를 결합한 2-stage 구조를 설계하였다.
ConvNeXtV2 기반 wafer-level 분류는 전반적으로 높은 정확도와 처리 속도를 보였으나, wafer 내 불량 chip의 분포가 유사한 클래스에서는 분류 성능이 저하되었다. 이를 보완하기 위해 2단계에서는 1차 분류의 저신뢰 샘플에 ROI 기반 YOLO를 적용하여 ROI 영역 내 불량 chip의 형태와 출현 패턴을 추가로 판별하도록 구성하였다(Fig. 3).

![Fig. 3. Two-stage known-defect classification with ROI-YOLO.](_fig_yolo_roi.png)

**Fig. 3.** Representative patterns of Class A(a) and Class B(b), and a true Class A sample(c) misclassified as Class B by the first-stage CNN but corrected to Class A by the second-stage ROI-YOLO. The blue circle indicates the ROI, and the red boxes denote YOLO detections of chip-level defect patterns within the ROI.


**Table 1.** Backbone comparison and staged improvements for known-fail classification (16-class, test weighted F1)

| Configuration | Pre Train | Test F1 | Note |
|---|---|---:|---|
| ViT | IN-21k | 0.81 | fine-tune |
| Swin | IN-1k | 0.84 | fine-tune |
| EffNetV2 | IN-1k | 0.85 | fine-tune |
| MaxViT | IN-21k | 0.87 | fine-tune |
| ConvNeXtV2 (Ref) | IN-22k | 0.87 | selected |
| Ref + Optuna | IN-22k | 0.92 | HPO |
| Ref + Optuna + ROI | IN-22k | 0.95 | 2-stage |

MaxViT[2]와 ConvNeXtV2 (Ref)는 동일한 weighted F1 0.87을 보였으나, ConvNeXtV2는 파라미터 수 약 26% 감소(119.5M → 88.6M)와 FLOPs 약 39% 감소(74.2G → 45.1G)로 더 효율적이라 최종 backbone으로 선정하였다. 이후 Optuna를 통해 lr, weight decay, focal loss, class weight 등을 최적화하여 weighted F1을 0.92까지 향상시켰고, ROI-YOLO 보정으로 최종 0.95를 달성하였다.

### 2.3 Unknown 불량 검출

5일치 운영 데이터 10,000장을 사용하여 SimCLR[3] 계열 모델을 대조학습하였으며, wafer의 zone 기반 불량 해석 특성을 반영하기 위해 grid-structured local sampling을 함께 적용하였다. 이후 별도 1일치 2,000장에 HDBSCAN[4]을 적용하여 유사 패턴을 그룹화하였다.

![Fig. 4. Unknown-defect grouping on production images.](_fig_cluster.png)

**Fig. 4.** Unknown-fail grouping on production images.


Unknown 불량 검출에서는 운영 이미지 2,000장에 대한 grouping 결과 13개 후보 그룹이 검출되었으며, 현업 분석 엔지니어 검증 결과 이 중 7개가 실제 불량 그룹으로 판정되었다. 나머지 6개는 일부 lot에 국한된 warning이거나 실제 불량으로 이어지지 않는 패턴이었다.

## 3. CONCLUSION

본 연구는 Failbit Map 전수 생성과 자동 불량 분석을 위한 통합 아키텍처를 구현하였다. Cython 최적화와 32-color palette-indexed PNG로 Failbit Map의 대량 생성과 저장·운영을 가능하게 하였고, Known 2-stage 분류와 Unknown self-supervised 검출을 결합하여 자동 분석 흐름을 구축하였다.

## REFERENCES

[1] S. Woo et al., "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 16133-16142, 2023.

[2] Z. Tu et al., "MaxViT: Multi-Axis Vision Transformer," in Proceedings of the European Conference on Computer Vision (ECCV), pp. 459-479, 2022.

[3] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in Proceedings of the 37th International Conference on Machine Learning (ICML), PMLR 119, pp. 1597-1607, 2020.

[4] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in Advances in Knowledge Discovery and Data Mining, PAKDD 2013, pp. 160-172, 2013.

[5] FBM, https://www.failbitmap.com
