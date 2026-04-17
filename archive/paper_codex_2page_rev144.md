# Failbit Map Known & Unknown 불량 분석 아키텍처

**Hybrid Failbit Map Analysis Architecture for Known Classification and Unknown Discovery**

홍길동¹, 김철수¹

¹ 반도체연구소, Samsung Electronics, 화성시, 대한민국

(Abstract)

Failbit Map은 반도체 EDS Test에서 생성되는 웨이퍼당 약 1,000만 pixel 수준의 초고해상도 데이터로, 불량 패턴 분석의 핵심 자료이다. 그러나 실제 현업에서는 대량의 Failbit Map 조회가 불가능하고, 일부 Map 분석도 엔지니어의 수작업에 의존하고 있다. 본 논문은 이를 해결하기 위해 대량 Failbit Map 운영용 데이터 파이프라인을 구축하고, 그 위에서 Known 불량은 2-stage supervised classification으로, Unknown 불량은 self-supervised 기반 검출 구조로 처리하는 통합 아키텍처를 구현하였다. Cython 적용으로 데이터 변환 속도를 약 100배 향상시켰고, Palette PNG 적용으로 이미지 용량을 약 75% 절감하였다. Known 불량 분류는 ConvNeXtV2 기반 1차 분류와 저신뢰 샘플에 대한 ROI 기반 YOLO 2차 분류를 결합한 구조로 설계하였으며, F1-score 0.95를 달성하였다. Unknown 불량 검출은 레이블 없이 SimCLR 계열 contrastive learning 기반으로 수행하였고, wafer의 zone 기반 불량 해석 특성을 반영하기 위해 grid structured local sampling을 적용하였다. 실제 양산 5일치 Failbit Map 10,000장을 학습한 뒤 1일치 2,000장에 적용한 결과 13개 불량 그룹이 검출되었고, 이 중 7개가 현업 엔지니어 검증에서 실제 불량 그룹으로 판정되어 실전 운영 가능성을 입증하였다.

Keywords: Failbit Map, Wafer Failure Analysis, ConvNeXtV2, YOLO, Contrastive Learning, HDBSCAN

## 1. INTRODUCTION

Failbit Map은 EDS Test에서 Memory Cell Block 단위의 불량 정도를 Grade 0부터 7까지로 표현한 데이터이다. Wafer 1장에는 약 1,000만 개의 block이 존재하므로, 현업의 Measure 기반 분석만으로는 Failbit Map에서만 발현되는 불량을 검출하기 어렵다. 따라서 불량 분석을 위해서는 Failbit Map을 전수 분석해야 한다.

실제 현업 적용에는 두 가지 제약이 있다. 첫째, 기존 시스템은 설비 Log를 대량 Failbit Map으로 변환하고 저장·조회하는 처리 성능이 부족하였다. 설비 Log는 Wafer당 10~50MB 수준이며 특정 제품에서는 하루 약 2,000장의 Wafer가 발생하지만, 기존 환경에서는 속도와 메모리 제약으로 대량 처리가 어려웠고 실제 확인 가능 수량도 한 번에 48매 수준으로 제한되었다. 둘째, 생성된 Map에 대한 불량 여부 및 유형 판정이 엔지니어의 수동 판독에 의존하여 전수 분석이 어려웠다. 본 논문은 이러한 한계를 해결하기 위해, 대량 Raw Data를 지속적으로 Failbit Map으로 생성 및 운영하는 데이터 파이프라인과, Known 불량을 2-stage supervised classification으로 분석하고 Unknown 불량을 self-supervised 기반으로 검출하는 통합 분석 아키텍처를 제안한다. 주요 기여는 다음과 같다.

본 논문의 주요 기여는 대량 Log 적재 및 1시간 주기 Failbit Map 생성 파이프라인 구축, ConvNeXtV2와 ROI-YOLO를 결합한 Known 불량 2-stage 분류, 그리고 SimCLR 기반 Unknown 불량 그룹 검출의 세 가지이다.

## 2. PROPOSED METHOD

### 2.1 DATA PIPELINE

주요 병목은 wafer당 약 1,000만 개의 암호화된 test 결과를 grade 값으로 변환하는 속도와 초고해상도 이미지의 저장 용량 부담이었다. 이에 Cython 최적화로 변환 속도를 약 100배 향상시키고(Fig. 1), palette-indexed PNG로 이미지 용량을 약 75% 절감하였다(Fig. 2).

<table>
<tr><td>
<div align="center"><b>Hex-to-grade conversion</b></div>

```text
    Raw:
        090B0C0D0E0F090A0B0C

    Decoding:
        "0C" -> "C" -> 12 (hex to decimal) -> 3


    Python:
        interpreter-based loop

    Cython:
        compiled integer loop

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
        [(123,54,24), (123,54,24), ...]

    Palette-indexed PNG:
        P[3]=(123,54,24), [(3), (3), ...]

    RGB_to_Palette:
        (123,54,24) -> (3)
```
</td></tr>
</table>

**Fig. 2.** Palette-indexed PNG for failbit map compression.

*Note [5]. FBM(Failbit Map Browser): https://www.failbitmap.com*


### 2.2 Known 불량 분류

Known 불량 분석은 16개 등록 클래스를 대상으로 하였으며, 1,500개의 Failbit Map을 사용하여 ConvNeXtV2[1] 기반 1단계 wafer-level 분류기와 저신뢰 샘플 대상 2단계 ROI(Region of Interest) 기반 YOLO를 결합한 2-stage 구조를 설계하였다.
ConvNeXtV2 기반 wafer-level 분류는 전반적으로 높은 정확도와 처리 속도를 보였으나, wafer 내 불량 chip의 분포가 유사한 클래스에서는 분류 성능이 저하되었다. 이를 보완하기 위해 1차 분류의 저신뢰 샘플에 대해 ROI 기반 YOLO를 적용하여 ROI 영역 내 불량 chip의 형태와 출현 패턴을 추가 판별하는 2-stage 구조를 설계하였다(Fig. 3).

![Fig. 3. Two-stage known-defect classification with ROI-YOLO.](_fig_yolo_roi.png)

**Fig. 3.** Representative patterns of Class A(a) and Class B(b), and a true Class A sample(c) misclassified as Class B by the first-stage CNN but corrected to Class A by the second-stage ROI-YOLO.


**Table 1.** Backbone comparison and staged improvements for known-fail classification (16-class, test Weighted F1)

| Configuration | Pre Train | Test F1 | Note |
|---|---|---:|---|
| ViT | IN-21k | 0.81 | fine-tune |
| Swin | IN-1k | 0.84 | fine-tune |
| EffNetV2 | IN-1k | 0.85 | fine-tune |
| MaxViT | IN-21k | 0.87 | fine-tune |
| ConvNeXtV2 (Ref) | IN-22k | 0.87 | selected |
| Ref + Optuna | IN-22k | 0.92 | HPO |
| Ref + Optuna + ROI | IN-22k | 0.95 | 2-stage |

하루 약 2만 장 이상의 Wafer Failbit Map이 발생하므로 backbone 선택에서는 정확도와 추론 처리량을 함께 고려하였다. MaxViT[4]와 ConvNeXtV2 (Ref)는 동일한 test Weighted F1 0.87을 보였으나, ConvNeXtV2는 파라미터 수 약 26% 감소(119.5M → 88.6M)와 FLOPs 약 39% 감소(74.2G → 45.1G)로 추론 처리량이 우수하여 최종 backbone으로 선정하였다. 이후 Optuna 기반 hyperparameter 최적화로 test Weighted F1을 0.92까지 높였고, ROI-YOLO 보정으로 최종 0.95를 달성하였다.

### 2.3 Unknown 불량 검출

Unknown 불량 검출은 유사한 형태를 그룹화하여 불량 후보 그룹을 찾는 문제로 정의하였다. 5일치 운영 데이터 10,000장으로 SimCLR 계열 contrastive learning[2] 기반 임베딩을 학습하고, 별도 1일치 2,000장에 HDBSCAN[3]을 적용하여 유사 패턴을 그룹화하였다. 또한 Wafer 이미지를 N×N grid로 균등 분할하고 동일 grid cell 내 샘플을 positive pair로 구성하는 grid structured local sampling으로 발생 위치 정보를 반영하였다.

![Fig. 4. Unknown-defect grouping on production images.](_fig_cluster.png)

**Fig. 4.** Unknown-fail grouping on production images.


Unknown 불량 검출에서는 운영 이미지 2,000장에 대한 grouping 결과 13개 후보 그룹이 검출되었으며, 현업 분석 엔지니어 검증 결과 이 중 7개가 실제 불량 그룹으로 판정되었다. 나머지 6개 그룹은 lot성 warning 수준의 noise이거나 실제 chip 불량으로 이어지지 않는 패턴으로 해석되었다.

## 3. CONCLUSION

본 연구는 1시간 주기의 Failbit Map 전수 생성과 자동 불량 분석을 위한 통합 아키텍처를 구현하였다. Cython 최적화와 palette-indexed PNG로 대량 Map의 생성 및 저장을 가능하게 하였고, Known 2-stage 분류와 Unknown self-supervised 검출을 결합하여 Failbit Map 분석을 수작업 중심 업무에서 자동화 체계로 고도화하였다. 또한 Failbit Map 조회 및 분석용 시스템을 개발하여 운영 중이며, 현업 피드백을 반영해 지속적으로 개선하고 있다.

## REFERENCES

[1] S. Woo et al., "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 16133-16142, 2023.

[2] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in Proceedings of the 37th International Conference on Machine Learning (ICML), PMLR 119, pp. 1597-1607, 2020.

[3] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in Advances in Knowledge Discovery and Data Mining, PAKDD 2013, pp. 160-172, 2013.

[4] Z. Tu et al., "MaxViT: Multi-Axis Vision Transformer," in Proceedings of the European Conference on Computer Vision (ECCV), pp. 459-479, 2022.

[5] FBM, https://www.failbitmap.com
