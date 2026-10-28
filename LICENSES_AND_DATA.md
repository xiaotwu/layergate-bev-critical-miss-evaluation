# Rights, data attribution, and third-party scope

No single repository-wide open-source or publication license has been assigned to the project's own code and manuscript in this release. Public access and a repository citation do not, by themselves, grant additional reuse rights. Existing upstream rights and file-specific notices remain applicable. Contact the repository maintainer for permissions not already granted by an applicable upstream license. This release does not invent authorship, transfer copyright, or relicense third-party materials.

## nuScenes-derived research records

This case uses nuScenes mini by Holger Caesar and colleagues / the nuScenes team. The nuScenes paper states that the dataset was released under CC BY-NC-SA 4.0 for non-commercial research. Consult the current [nuScenes terms of use](https://www.nuscenes.org/terms-of-use), [official dataset page](https://www.nuscenes.org/), and applicable [CC BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/) for reuse conditions. No commercial rights or exemption from those terms is granted here.

The compact files contain dataset sample/log identifiers and derived per-frame features, failure labels, counts, probabilities and aggregated results. They are not raw sensor data or a newly owned unrestricted dataset. Analysis grouping/roles and derived counts were added for this exploratory study; they are not the official nuScenes challenge split or official driving-safety labels. The same upstream terms continue to apply where applicable; no blanket MIT/CC-BY relicensing is asserted for these records.

Dataset reference: H. Caesar et al., “nuScenes: A Multimodal Dataset for Autonomous Driving,” CVPR2020. [Primary paper](https://openaccess.thecvf.com/content_CVPR_2020/html/Caesar_nuScenes_A_Multimodal_Dataset_for_Autonomous_Driving_CVPR_2020_paper.html). Complete BibTeX appears in `paper/latex/references.bib`.

## LaTeX and prior methods

The manuscript uses IEEEtran. Third-party IEEEtran class/style files are not vendored; install them through a normal TeX distribution and follow their [LPPL notices](https://www.latex-project.org/lppl/). Bibliographic references credit nuScenes, BEVFormer, PointPillars, CenterPoint, CenterNet, focal loss, calibration/scoring-rule and selective-classification background. Literature performance and guarantees do not transfer to this implementation.

The original detector implementation includes limitations described in the manuscript. This companion does not redistribute the full detector/SDK/dependency trees, pretrained weights, checkpoints, full prediction payloads, original dataset annotation tables or vendor toolchains. It does not represent a complete implementation of all components of CenterPoint, temporal BEVFormer or camera fusion.

## Document review

Academic Writing Toolkit is used only for offline paragraph-logic and BibTeX-record structure checks. Tool receipts are recorded as document-assistance provenance, not authorship, peer review, external scientific replication, certification or endorsement by the tool provider or cited researchers.

## New identity-preserving follow-up

The new compact package also contains derived annotation/instance identities, endpoint match statuses, scores/distances, gates and burden counts. Illustrative paper figures may show limited derived GT coordinates. These are nuScenes-derived research records subject to applicable upstream terms; they are not a newly unrestricted dataset. Full annotation tables and detector predictions are not redistributed. The new authored LaTeX does not vendor IEEEtran class/style files. FiLM and ReZero are credited design precedents, not evidence of BEV efficacy.
