# Final-Year AI & Data Science Project Ideas — 9-Model Comparison

This document compiles responses from nine different AI models (ChatGPT, Grok, Claude, Gemini, Perplexity, DeepSeek, Kimi, Qwen, and Copilot) to the same prompt: generate 20 final-year project ideas for a Bachelor's in AI & Data Science. It has been reformatted from the original 79-page PDF export for readability — line-wrapping artifacts from the PDF conversion were fixed, browser/UI chrome and tool-call logs were removed, and section headers were standardized. The substance of each model's own wording has been preserved.

> **Note on Perplexity:** unlike the other eight, Perplexity's response only produced one-line pitches (not the full pitch/problem/novelty/technique/dataset/risk breakdown the prompt asked for), followed by a dump of roughly 230 reference links with no clear mapping back to individual ideas. The 20 one-line pitches are kept below; the unmapped link dump was omitted for readability. Say the word if you want it included as an appendix.

> **Note on Gemini:** Gemini's response included small per-idea "dataset spec" tables (image counts, class breakdowns, etc.). The source PDF exports these table cells in a scrambled reading order that could not be reliably reconstructed, so a few rows below may have a label sitting next to the wrong fragment of its value. Cross-check against the original PDF if an exact figure matters.

## Table of Contents

- [Original Prompt](#original-prompt)
- [ChatGPT](#chatgpt)
- [Grok](#grok)
- [Claude](#claude)
- [Gemini](#gemini)
- [Perplexity](#perplexity)
- [DeepSeek](#deepseek)
- [Kimi](#kimi)
- [Qwen](#qwen)
- [Copilot](#copilot)

---

## Original Prompt

I need 20 final-year project ideas for a Bachelor's in AI & Data Science, due in 4 weeks (I have ~50-60 hours total to spend, alongside other commitments).

CONTEXT:
- Coder skill level: intermediate, will rely heavily on AI-assisted/"vibe" coding
- Must genuinely use AI/DS techniques (ML/DL/NLP/CV) — not just an API wrapper
- Should feel like a SaaS product, not just a script or notebook
- Available stack: Python, TensorFlow, scikit-learn, pandas, numpy, vector databases, LangChain/LangGraph, n8n, any frontend
- Deliverables needed: (1) a working demo app, (2) a report with real model evaluation (metrics, comparisons, not just "it works")

CONSTRAINTS — reject ideas that:
- Depend on data I can't realistically get in week 1 (scraping-heavy, proprietary, needs manual labeling of 1000s of samples)
- Are essentially solved/saturated in the market already (e.g. generic chatbot, generic chess engine, generic resume screener)
- Need real-time infra, telephony, or hardware I don't have access to
- Have legal/ethical landmines (medical diagnosis claims, unconsented call recording, financial advice without disclaimers)

FOR EACH OF THE 20 IDEAS, GIVE ME:
1. One-line pitch
2. The specific real-world problem it solves and for whom
3. What's genuinely novel/underserved about it vs existing tools
4. The core ML/DL technique involved (be specific: architecture, not just "AI")
5. A named public dataset it could realistically use (or state "needs synthetic/self-collected data" honestly if none exists)
6. Rough build risk: Low / Medium / High

Bias toward ideas that are unusual, regionally relevant, or solve a problem you don't see AI startups already doing to death. Avoid the most obvious/ overdone categories unless you have a genuinely fresh angle on them.

Output as a numbered list, ideas only — no intro or summary text.

---

## ChatGPT

1. **TenderTwin**
- **Pitch:** An AI procurement workspace that detects duplicate, near-duplicate, and suspiciously overlapping tender scopes before analysts waste time reviewing them.
- **Problem:** Government procurement teams, contractors, and compliance analysts deal with thousands of tender notices whose descriptions can overlap heavily; manually finding similar scopes is slow.
- **Novelty:** Instead of predicting whether a tender is “good” or “fraudulent,” it focuses on **semantic duplication and scope overlap**, including clusters of tenders that appear independently worded but describe almost the same work.
- **Technique:** Sentence-BERT embeddings + FAISS vector search + HDBSCAN clustering; compare against TF-IDF/cosine similarity baseline and report Precision@K / cluster purity.
- **Dataset:** **TED Open Data** — EU public procurement notices are published for analysis and reuse. ([TED Open Data Service][1])
- **Risk:** **Low**

2. **TenderFit**
- **Pitch:** A tender-to-supplier matching SaaS that converts a tender's technical scope into required skills/capabilities and ranks compatible supplier profiles.
- **Problem:** Small contractors often miss tenders because they do not know which of their capabilities actually match the specification.
- **Novelty:** The focus is **capability matching from technical scope**, not a generic job/recruitment recommender; you can demonstrate explainable matches such as “electrical installation + HVAC + civil works.”
- **Technique:** Sentence-BERT bi-encoder retrieval + cross-encoder reranking + skill/entity extraction with spaCy/transformer NER.
- **Dataset:** **TED Open Data** for tender text; supplier profiles can be **synthetically generated** from tender categories rather than requiring proprietary supplier data. ([TED Open Data Service][1])
- **Risk:** **Medium**

3. **ClauseConsistency**
- **Pitch:** Upload two contracts and get an AI map of clauses that are inconsistent, duplicated, missing, or materially different.
- **Problem:** SMEs and legal/admin teams manually compare contracts, amendments, and vendor agreements.
- **Novelty:** Avoids the saturated “legal chatbot”; the product is about **cross-document consistency analysis**, making the output measurable and auditable.
- **Technique:** DeBERTa-v3 / Legal-BERT sentence-pair classification + semantic similarity embeddings; evaluate F1, precision/recall and confusion matrix against TF-IDF + logistic regression.
- **Dataset:** **Contract Understanding Atticus Dataset (CUAD)** — 510 contracts, 13,000+ labels, 41 clause types. ([Atticus Project AI][2])
- **Risk:** **Low**

4. **InvoiceVision**
- **Pitch:** A document-intelligence SaaS that extracts invoice fields and automatically flags inconsistent totals, dates, quantities, or tax values.
- **Problem:** Small businesses still manually enter invoice data and can miss arithmetic or field-level inconsistencies.
- **Novelty:** The interesting part is not OCR alone; it is **OCR + structural understanding + numerical validation**, turning extraction into a quality-control system.
- **Technique:** Layout-aware transformer such as LayoutLMv3 for field classification + OCR + deterministic accounting validation rules; evaluate field-level precision/recall and exact-match accuracy.
- **Dataset:** **SROIE (Scanned Receipts OCR and Information Extraction)**; supplement with a small **synthetic invoice set** for invoice-specific fields.
- **Risk:** **Low**

5. **UrduFormLens**
- **Pitch:** An AI form-processing SaaS for extracting fields and detecting missing or malformed entries from Urdu-English administrative forms.
- **Problem:** Schools, small offices, NGOs, and local businesses still receive large quantities of scanned bilingual paperwork.
- **Novelty:** Most document AI examples concentrate on English-language documents; the project targets **Urdu-English mixed layouts and local administrative forms**.
- **Technique:** LayoutLMv3 or Donut + OCR + token classification for field labels; compare transformer extraction against OCR + regex.
- **Dataset:** **FUNSD** for document-layout pretraining/evaluation plus **self-collected/synthetic Urdu-English forms**. FUNSD contains annotated form images and is widely used for document understanding. ([GitHub][3])
- **Risk:** **Medium**

6. **ReceiptTamper**
- **Pitch:** Upload a receipt and receive an AI-generated integrity report highlighting regions whose visual and textual evidence do not agree.
- **Problem:** Small businesses and expense teams need to review submitted receipts without manually checking every field.
- **Novelty:** Focus on **cross-modal inconsistency**—for example, OCR says one total while the visual structure suggests alteration—rather than a generic receipt scanner.
- **Technique:** Vision Transformer/CNN image encoder + Siamese similarity model + OCR-derived numeric consistency features; evaluate tampered-vs-clean F1, ROC-AUC and localization IoU.
- **Dataset:** **SROIE** + **synthetically tampered copies** generated with controlled edits such as total/date/value replacement.
- **Risk:** **Medium**

7. **RoadFix Prioritizer**
- **Pitch:** A road-image SaaS that detects road defects and converts them into a ranked maintenance-priority map.
- **Problem:** Municipalities, contractors, and road-maintenance teams need to identify which road defects deserve attention first.
- **Novelty:** Pothole detection itself is common; the fresher angle is **defect detection → severity estimation → repair-priority score**, making it operational rather than merely visual.
- **Technique:** YOLOv8n/YOLO11n object detector + damage-area/severity regression; compare against classical image features or a smaller detector and report mAP, precision/recall and severity MAE.
- **Dataset:** **RDD2022**, containing annotated road-damage imagery from six countries. ([GitHub][4])
- **Risk:** **Low**

8. **TextileGuard**
- **Pitch:** An industrial visual-inspection SaaS that learns what a defect-free textile/material surface looks like and flags abnormal regions automatically.
- **Problem:** Small textile manufacturers need automated quality checks but may lack thousands of manually labeled defect images.
- **Novelty:** Use **unsupervised/few-shot anomaly detection** instead of requiring a massive labeled defect dataset—particularly relevant to manufacturing where new defect types constantly appear.
- **Technique:** PatchCore or PaDiM anomaly detection with ResNet/ViT features; report image-level ROC-AUC and pixel-level AUROC/PRO against a simpler autoencoder baseline.
- **Dataset:** **MVTec AD**, over 5,000 high-resolution images across 15 object/texture categories with pixel-level anomaly annotations. The dataset is non-commercial, so the SaaS should remain an academic prototype. ([MVTec Software][5])
- **Risk:** **Medium**

9. **FloodBuild Triage**
- **Pitch:** A disaster-response dashboard that compares pre- and post-event satellite imagery and estimates building-damage severity for rapid triage.
- **Problem:** NGOs, emergency planners, and disaster-response teams cannot manually inspect thousands of buildings immediately after a disaster.
- **Novelty:** The project is about **prioritizing inspection resources**, not claiming autonomous damage certification.
- **Technique:** Siamese/U-Net change-detection network + damage-severity classifier; compare image-difference baseline vs deep model using IoU, F1 and per-class recall.
- **Dataset:** **xBD**, containing pre/post-disaster satellite imagery and roughly 700,000 building annotations across 15 countries. ([CVF Open Access][6])
- **Risk:** **High**

10. **RecycleScore**
- **Pitch:** A computer-vision SaaS that estimates the composition and contamination level of mixed waste rather than simply saying “plastic/paper/metal.”
- **Problem:** Recycling operators and facilities need to know whether incoming material streams are reasonably sortable or heavily contaminated.
- **Novelty:** Most student projects stop at waste classification; this measures **mixture composition and contamination**, which is much closer to an operational recycling workflow.
- **Technique:** YOLO/RT-DETR object detection or segmentation + class-frequency aggregation; evaluate mAP, segmentation IoU and composition MAE.
- **Dataset:** **TACO — Trash Annotations in Context**, an open dataset of manually labeled litter images with segmentation annotations.
- **Risk:** **Low**

11. **EnergyDrift**
- **Pitch:** A lightweight energy-monitoring SaaS that learns normal electricity-consumption patterns and flags unusual usage periods.
- **Problem:** Offices, workshops, and households often notice energy waste only after receiving a large bill.
- **Novelty:** Instead of just forecasting consumption, it focuses on **behavioral baseline + anomaly explanation**, e.g. “this night's usage differs sharply from your normal weekday pattern.”
- **Technique:** LSTM/1D-CNN autoencoder for sequence reconstruction + Isolation Forest baseline + change-point detection.
- **Dataset:** **UCI Individual Household Electric Power Consumption**, with more than two million minute-level measurements over almost four years. ([UCI Machine Learning Repository] [7])
- **Risk:** **Low**

12. **AirCast**
- **Pitch:** A forecasting dashboard that predicts near-future particulate pollution and explains which meteorological variables are driving the forecast.
- **Problem:** Schools, outdoor-event planners, and environmental teams need short-horizon pollution forecasts rather than static historical charts.
- **Novelty:** The differentiator is **multisite forecasting + interpretable drivers**, rather than just plotting AQI.
- **Technique:** Temporal Fusion Transformer or LSTM with weather covariates; compare against XGBoost and seasonal-naive baselines using MAE, RMSE and MAPE.
- **Dataset:** **UCI Beijing Multi-Site Air Quality**, containing 420,768 hourly records from 12 monitoring stations. ([UCI Machine Learning Repository][8])
- **Risk:** **Medium**

13. **StockoutShield**
- **Pitch:** A retail SaaS that predicts which products are approaching a stockout and estimates how many sales are at risk over the next planning window.
- **Problem:** Small retailers often react to stockouts after they happen rather than prioritizing which products need replenishment first.
- **Novelty:** Optimize for **stockout-risk ranking**, not generic sales forecasting; the dashboard can show “top 10 SKUs needing action.”
- **Technique:** LightGBM/XGBoost using lag, rolling-window, calendar and price features; optionally compare with LSTM; evaluate RMSE/MAE plus Precision@K for actual stockout events.
- **Dataset:** **M5 Forecasting dataset**, using its Walmart sales-history data.
- **Risk:** **Low**

14. **GarmentPulse**
- **Pitch:** An AI production dashboard that predicts manufacturing productivity and identifies the operational factors associated with poor-performing production periods.
- **Problem:** Small garment factories lack sophisticated analytics for detecting inefficient production conditions.
- **Novelty:** This is specifically aimed at **small-scale garment production analytics**, a much less overdone student topic than generic sales/customer prediction.
- **Technique:** XGBoost/Random Forest regression + SHAP explanations; compare with linear regression and report R², MAE, RMSE and feature importance stability.
- **Dataset:** **UCI Productivity Prediction of Garment Employees**, an industry-collected garment-production dataset. ([UCI Machine Learning Repository][9])
- **Risk:** **Low**

15. **MathItemCalibrator**
- **Pitch:** A teacher-facing SaaS that estimates how difficult a mathematics question is and identifies which topic/skill combinations cause the most mistakes.
- **Problem:** Teachers often discover that an exam question was badly calibrated only after students have taken it.
- **Novelty:** It models **question difficulty independently from raw percentage scores**, giving teachers a data-driven way to construct balanced assessments.
- **Technique:** Item-response-theory features + gradient boosting or neural knowledge-tracing model; compare IRT/logistic regression vs neural network and report AUC, log-loss and calibration error.
- **Dataset:** **MathE — Assessing Mathematics Learning in Higher Education**, with 9,546 question-answer records and topic/difficulty metadata. ([UCI Machine Learning Repository][10])
- **Risk:** **Low**

16. **CrisisRoute**
- **Pitch:** An emergency-information dashboard that automatically classifies public crisis messages into actionable categories such as shelter, infrastructure damage, medical request, or resource need.
- **Problem:** NGOs and emergency coordinators face huge volumes of short, noisy messages during disasters.
- **Novelty:** The product is an **operational triage layer**, not a generic sentiment classifier or chatbot.
- **Technique:** RoBERTa/DeBERTa multi-class or multi-label classifier + confidence thresholding; evaluate macro-F1, per-class recall and calibration.
- **Dataset:** **CrisisNLP crisis-message datasets** / publicly available crisis-text corpora; no private call or message collection required.
- **Risk:** **Medium**

17. **SupportRoute Urdu**
- **Pitch:** A customer-support routing SaaS that understands English, Roman Urdu, and mixed Urdu-English messages and sends them to the correct support category.
- **Problem:** Pakistani businesses receive customer messages like “order abhi tak nahi aya,” which standard English-only intent models handle poorly.
- **Novelty:** The focus is **code-switching and Roman Urdu intent routing**, rather than building another generic customer chatbot.
- **Technique:** XLM-R fine-tuning with lightweight LoRA + confidence calibration; compare TF-IDF/SVM, multilingual BERT and XLM-R using macro-F1 and per-intent recall.
- **Dataset:** **CLINC150** for the initial intent taxonomy + **synthetic/self-collected Roman-Urdu paraphrases** for the regional adaptation.
- **Risk:** **Medium**

18. **AlertCompress**
- **Pitch:** A cybersecurity analyst dashboard that groups hundreds of similar network alerts into a few meaningful incident clusters.
- **Problem:** Small IT/security teams can be overwhelmed by repeated alerts generated by similar traffic patterns.
- **Novelty:** Don't compete as another intrusion detector; solve **alert deduplication and incident compression**, reducing analyst overload.
- **Technique:** Autoencoder or contrastive encoder for flow embeddings + HDBSCAN clustering; optionally classify cluster types with XGBoost; report clustering purity/silhouette and attack-class F1.
- **Dataset:** **CIC-IDS2017** or **UNSW-NB15**, both publicly available labeled network-flow datasets.
- **Risk:** **Medium**

19. **LogAnomaly Desk**
- **Pitch:** A SaaS that learns normal application/server log patterns and automatically flags anomalous sequences before engineers manually search thousands of log lines.
- **Problem:** Developers and DevOps teams waste time finding abnormal behavior inside huge volumes of repetitive logs.
- **Novelty:** Combine **sequence anomaly detection + event clustering + concise incident views**, rather than merely displaying raw logs.
- **Technique:** Log template parsing + sequence embeddings + LSTM/Transformer autoencoder; compare against frequency-based and Isolation Forest baselines using precision, recall, F1 and false-alert rate.
- **Dataset:** **HDFS log dataset** or another public system-log anomaly corpus.
- **Risk:** **Medium**

20. **SkillGraph**
- **Pitch:** A career-intelligence SaaS that converts a person's existing skills into a graph of adjacent skills and identifies the smallest realistic skill gaps for a target role.
- **Problem:** Students and early-career professionals usually know what they want to become but not which 2–5 skills are actually adjacent to what they already know.
- **Novelty:** It deliberately avoids resume scoring/recruitment ranking and focuses on **skill adjacency and explainable transition paths**.
- **Technique:** Sentence-transformer embeddings + graph construction over skills + Node2Vec/GraphSAGE + shortest-path or graph-ranking layer; evaluate target-skill retrieval Precision@K and compare graph ranking against cosine similarity alone.
- **Dataset:** **NYC Government Job Postings with ESCO Occupations & Skills**, containing 3,229 anonymized postings and 31,292 ESCO skill tags, plus the public **Job Skill Set** dataset. ([Kaggle][11])
- **Risk:** **Low**

[1]: https://data.ted.europa.eu/ "TED Open Data Service"
[2]: https://www.atticusprojectai.org/cuad/ "CUAD Dataset | The Atticus Project"
[3]: https://github.com/crcresearch/FUNSD "GitHub - crcresearch/FUNSD: FUNSD Datasets · GitHub"
[4]: https://github.com/sekilab/RoadDamageDetector "GitHub - sekilab/RoadDamageDetector · GitHub"
[5]: https://www.mvtec.com/research-teaching/datasets/mvtec-ad "MVTec AD | Industrial Anomaly Detection Dataset"
[6]: https://openaccess.thecvf.com/content_CVPRW_2019/html/cv4gc/Gupta_Creating_xBD_A_Dataset_for_Assessing_Building_Damage_from_Satellite_CVPRW_2019_paper.html "CVPR 2019 Open Access Repository"
[7]: https://dev.uci-ics-mlr-prod.aws.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption "Individual Household Electric Power Consumption - UCI Machine Learning Repository"
[8]: https://archive.ics.uci.edu/dataset/501/beijing "UCI Machine Learning Repository"
[9]: https://archive.ics.uci.edu/datasets?Task=Regression&Types=Time-Series&orderBy=NumHits&skip=0&take=10 "UCI Machine Learning Repository"
[10]: https://archive.ics.uci.edu/datasets?orderBy=NumHits&skip=80&take=10 "UCI Machine Learning Repository"
[11]: https://www.kaggle.com/datasets/benjaminkongshaug/nyc-job-postings-with-esco-occupations-and-skills "NYC Job Postings with ESCO Occupations & Skills"

---

## Grok

1. **Roman-Urdu financial scam SMS / WhatsApp classifier (JazzCash, EasyPaisa, fake NADRA, OTP-harvest)**
- **Pitch:** A moderation SaaS that flags code-mixed financial scams in Roman Urdu, not generic English spam.
- **Problem:** Pakistani users (and telco/fintech trust teams) drown in prize, KYC, and wallet-drain messages that English spam filters miss because of spelling variation (`account`, `acount`, `akaunt`).
- **Novelty:** Commercial filters are English/Unicode-Urdu; almost none are trained on Roman-Urdu scam *intents* (credential harvest vs promo vs ham).
- **Technique:** Character-aware CNN or CANINE + fine-tuned XLM-RoBERTa sequence classifier; compare against FastText, BiLSTM, and a keyword/regex baseline; report macro-F1, PR-AUC, and robustness to unseen spellings.
- **Dataset:** UCI Roman-Urdu Sentiment (20k) + Harvard Dataverse Roman Urdu Sentiment Corpus (134k) for language prior; SMS Spam Collection v.1; **needs a synthetic/self-collected scam set** (~800–1,500 templated + real screenshots you label in week 1 — not thousands).
- **Risk:** Low

2. **Punjab smog source attribution (crop-fire vs traffic vs industry vs dust), not AQI prediction**
- **Pitch:** A dashboard that answers “what is driving *today’s* smog in this tehsil?” rather than recycling 24h AQI forecasts.
- **Problem:** City managers and journalists in Lahore/Faisalabad get one AQI number; mitigation is different if the spike is stubble fire, brick kilns, or calm-wind dust.
- **Novelty:** Startups sell AQI apps; almost none do *source mixing* with explainability for South Asian winters.
- **Technique:** Gradient-boosted trees (XGBoost/LightGBM) on meteorology + emissions proxies, with SHAP source attribution; optional small ResNet on VIIRS/Sentinel-2 smoke plumes as a second head; compare vs multivariate linear regression and a persistence baseline (MAE, R², calibration).
- **Dataset:** OpenAQ (PM2.5/PM10/NO2), NASA FIRMS/VIIRS active fires, ERA5 wind/humidity/BLH, OpenStreetMap road density; brick-kiln coordinates from Zenodo “Brick Kiln Dataset for Pakistan’s IGP Region”.
- **Risk:** Medium

3. **Cloud-penetrating flood-extent mapper for union-council relief targeting**
- **Pitch:** Upload a Sentinel-1 scene (or pick a past event) and get a flood mask + population-exposed estimate, usable when optical satellites are blocked by monsoon cloud.
- **Problem:** District disaster cells and NGOs in Sindh/south Punjab need *where water actually is*, not rainfall totals.
- **Novelty:** Global flood APIs exist; a student-scale SaaS that fine-tunes on local 2010/2022-like events and reports IoU vs NDWI optical fallback is still rare in FYP demos.
- **Technique:** U-Net or SegFormer on Sentinel-1 VV/VH (+ DEM as extra channel); compare vs Otsu/thresholding on VH and a classical Random Forest on backscatter; metrics: IoU, Dice, flood vs permanent-water confusion.
- **Dataset:** Sen1Floods11 (4,831 chips, 11 events); Copernicus DEM; WorldPop for exposure overlay.
- **Risk:** Medium

4. **Smallholder field-boundary + kharif/rabi crop-type mapper**
- **Pitch:** A GIS SaaS that turns Sentinel-2 time series into plot polygons and wheat/cotton/rice/other labels for irregular &lt;2 ha fields.
- **Problem:** Extension officers and agri-insurers cannot use US-style field maps; Pakistani plots are tiny, mixed, and poorly cadastralized.
- **Novelty:** Commercial crop-ID is built for US/EU rectangles; small-plot delineation in the Indus basin is still an open applied problem.
- **Technique:** Temporal NDVI/EVI features → U-Net or Mask2Former for boundaries; crop type via 1D-CNN or LightGBM on seasonal signatures; compare vs single-date CNN and NDVI-threshold rules (mIoU, field-count error).
- **Dataset:** Sentinel-2 L2A (Planetary Computer, free); ESA WorldCereal / NASA Harvest labels where available; **needs a small self-traced set** of ~150–300 Punjab/Sindh plots from Google Earth (doable in week 1, not 1,000s).
- **Risk:** Medium

5. **Urdu paper-file digitizer for district offices (NER + key fields)**
- **Pitch:** Photo a Nastaliq/printed Urdu form or letter; get structured Name / Father / Address / CNIC-like ID / Organization / Dates.
- **Problem:** Tehsil and university admin still re-type stacks of Urdu applications; generic OCR dumps a text blob with no fields.
- **Novelty:** English KIE (FUNSD) is saturated; Urdu NER+KIE as a product workflow is not.
- **Technique:** TrOCR or a Urdu OCR frontend → XLM-RoBERTa token classification (BIO NER); compare vs BiLSTM-CRF and WikiAnn-transfer; entity-level F1, field exact-match.
- **Dataset:** MK-PUCIT NER, UNER/UNER-II; U-HAT (UHaT) for handwriting; **synthetic form overlays** on public Urdu text (generate in week 1).
- **Risk:** Medium

6. **University degree / transcript visual tamper detector**
- **Pitch:** Admissions SaaS: upload a scanned degree; get a forgery-risk score with a heatmap of spliced seals, fonts, and photocopied security patterns.
- **Problem:** Pakistani (and other) registrars still eyeball PDFs of degrees; Photoshopped seals are common.
- **Novelty:** ID-card KYC is a crowded market; *academic certificate forensics* for university back-offices is not a consumer app.
- **Technique:** Error Level Analysis + noise-residual CNN (SRNet-style) and/or Siamese EfficientNet-B0 on patch pairs; compare vs handcrafted ELA/copy-move (DCT) baselines; AUC, EER, localization IoU.
- **Dataset:** MIDV-2020 / MIDV-500 (document photos), DocTamper (ICDAR), Kaggle fake-vs-real document sets; **needs a small synthetic tamper set** (you splice seals/text on public certificate templates — ~200 images).
- **Risk:** Medium

7. **Mandi vegetable price-shock early warning for sabzi vendors**
- **Pitch:** A vendor/wholesaler dashboard: “onion in Lahore likely +25% within 7 days” with feature drivers (arrivals, season, lag prices, shocks).
- **Problem:** Small traders get wrecked by overnight mandi spikes; they have phones but no forecasting tool.
- **Novelty:** Agri “apps” show *yesterday’s* rates; few forecast *shocks* (classification of jump events) rather than smooth price regression.
- **Technique:** LightGBM + LSTM (or Temporal Fusion Transformer if time allows) on lags/seasonality; primary task = 7-day shock classification + quantile regression; compare vs ARIMA/Prophet (F1 on shocks, pinball loss, MASE).
- **Dataset:** Kaggle “Crop Prices Dataset of Pakistan” (AMIS, city-level); optional Agmarknet India as transfer test.
- **Risk:** Low

8. **Brick-kiln finder + school/hospital exposure map (FCBTK vs zigzag)**
- **Pitch:** NGO/EPA SaaS: detect kilns on Sentinel-2 chips, classify technology, overlay population and schools within 1 km.
- **Problem:** Kilns drive winter PM and sit next to settlements; enforcement still uses incomplete lists.
- **Novelty:** This is not another “object detection of cars.” Asset-level kiln *type* + exposure is a compliance tool, not a consumer CV demo.
- **Technique:** YOLOv8 or RT-DETR on 10 m Sentinel-2 RGB/false-color chips; second-stage kiln-type classifier; compare vs Random Forest on spectral indices (the original dataset paper’s baseline); precision/recall by region.
- **Dataset:** Zenodo/Scientific Data “Brick Kiln Dataset for Pakistan’s IGP Region” (~11k geolocated kilns, FCBTK vs zigzag) + Sentinel-2 chips you cut around those coordinates.
- **Risk:** Medium

9. **Municipal road-damage triage from citizen phone photos**
- **Pitch:** Citizen uploads a street photo; the city dashboard auto-labels pothole vs alligator crack vs longitudinal crack, scores severity, and clusters duplicates by GPS.
- **Problem:** 311/complaint portals in South Asian cities are untriaged photo dumps.
- **Novelty:** RDD-style papers exist; a *duplicate-aware municipal queue* (vision + geo clustering) is the product, not another Kaggle notebook.
- **Technique:** YOLOv8/YOLO11 detector fine-tuned on RDD classes; embedding (CLIP or EfficientNet) + HDBSCAN for near-duplicate complaints; compare vs SVM-on-HOG; mAP@0.5, complaint-merge purity.
- **Dataset:** RDD2022 (47k images, 6 countries including India — closest domain shift to Pakistan).
- **Risk:** Low

10. **Packaged-food label explainer: OCR → additive / allergen / halal-status flags**
- **Pitch:** Point-and-shoot SaaS for shoppers and small importers: parse a bilingual label and list E-numbers, allergen keywords, and likely halal/uncertain status *from ingredients*, with sources — not a health diagnosis.
- **Problem:** Imported/local packaged food in PK/IN/GCC mixes English, Urdu, Arabic; people cannot decode E-codes.
- **Novelty:** Open Food Facts is a database, not a camera workflow for messy South Asian labels; this is OCR+entity linking, not a calorie chatbot.
- **Technique:** DBNet/CRAFT text detection + TrOCR; then CRF or XLM-R span classifier for ingredient entities; rule+embedding match to an additive taxonomy; CER, field F1, linking accuracy.
- **Dataset:** ICDAR SROIE + CORD (receipt/label OCR); Open Food Facts (ingredients, allergens, additives); AMuRD/CORU for Arabic-English packaging-like text.
- **Risk:** Medium

11. **Code-mixed Pakistani academic AI-writing detector**
- **Pitch:** A university LMS plugin that scores *local* student-register essays (Pakistani English + Roman Urdu quotes), not generic GPTZero-for-NYT.
- **Problem:** Local campuses cannot trust US-trained detectors that fail on L2 English, transliteration, and Urdu quotations.
- **Novelty:** Detectors are benchmarked on Western news/Reddit; robustness on South Asian student writing + paraphrase attacks is an actual research gap you can measure.
- **Technique:** Fine-tuned RoBERTa/XLM-R classifier + stylometric features (burstiness, n-gram rank); compare vs DetectGPT/binoculars-style zero-shot and a TF-IDF SVM; TPR at 1% FPR, RAID adversarial transfer.
- **Dataset:** RAID (machine-text benchmark); **needs a small self-collected set** of 150–300 anonymized student paragraphs + matched LLM rewrites (week 1, ethics: consent, no grades attached).
- **Risk:** Medium

12. **Public-tender near-duplicate / collusion-pattern flagger**
- **Pitch:** Procurement-watch SaaS: ingest tender PDFs and bid texts, flag copy-paste specs, shared boilerplate across “competing” firms, and suspiciously similar prices.
- **Problem:** Journalists and PPRA-style watchdogs cannot read thousands of tenders for collusion cues.
- **Novelty:** Contract NLP (CUAD) extracts clauses; *cross-bid similarity as a collusion prior* for South Asian procurement is not a crowded SaaS.
- **Technique:** Layout-aware PDF parse → sentence-T5/E5 embeddings + MinHash/LSH; clustering + a supervised similarity classifier on planted duplicates; compare vs TF-IDF cosine; precision@k, duplicate-pair AUC.
- **Dataset:** EU TED (Tenders Electronic Daily, public) and/or World Bank e-procurement; **optional week-1 bulk of PPRA/provincial PDFs** (public, not scraping-heavy). Plant labelled near-duplicates yourself.
- **Risk:** Medium

13. **Katchi-abadi heat-exposure ranker (environmental, not medical)**
- **Pitch:** City-planning SaaS ranking neighborhoods by satellite land-surface temperature + built density + vegetation, so heat-action targeting isn’t only DHA vs “the rest.”
- **Problem:** Informal settlements are under-instrumented; official weather stations sit at airports.
- **Novelty:** UHI papers exist; a product that ranks *settlements* with Open Buildings footprints for Karachi/Lahore-like morphology is not on Product Hunt.
- **Technique:** Landsat LST derivation (single-channel or SWA) + Random Forest/spatial lag regression on NDBI, NDVI, albedo, building density; compare vs ordinary least squares; R², RMSE vs station LST where available.
- **Dataset:** Landsat 8/9 Collection 2 (free), Google Open Buildings, WorldPop, OSM land use; optional MODIS LST as coarse baseline.
- **Risk:** Medium

14. **Exam answer-pattern collusion detector (cheating rings, not plagiarism of essays)**
- **Pitch:** Exam-board SaaS: given anonymized MCQ/OMR matrices, surface *seating-adjacent identical-error clusters* that look like copied rings.
- **Problem:** Boards catch copied essays; they miss coordinated MCQ copying in large halls.
- **Novelty:** Turnitin is text; psychometric cheating detection (Harpp-Hogan, ω, IRT residual clustering) is unused as a simple web product in local universities.
- **Technique:** Item Response Theory (1–2PL) residuals + pairwise identical-wrong-answer scores; HDBSCAN on student vectors; compare vs raw Hamming-similarity threshold; recovery rate of planted rings, false-alarm rate.
- **Dataset:** **Needs synthetic/self-collected data** — generate 2,000–10,000 synthetic answer sheets with known planted clusters (standard in psychometrics; no private student data required). Optional: public ASSISTments item responses for realism.
- **Risk:** Low

15. **Textile fabric defect + shade-lot matcher (Faisalabad mill angle)**
- **Pitch:** Mill QA SaaS: phone photo of fabric → defect heatmap (hole, slub, oil, mispick) + ΔE shade match against the approved lot.
- **Problem:** Mid-size weaving/finishing units still do visual inspection; shade mismatch causes export rejections.
- **Novelty:** Generic “defect detection” demos use bottles/pills; fabric texture + colorimetry as one workflow is a real mill problem, not another MVTec bottle clone.
- **Technique:** Unsupervised anomaly segmentation (PatchCore or Student-Teacher / FastFlow) on frozen Wide-ResNet embeddings; shade via CIELab ΔE00; compare vs Autoencoder reconstruction error; AUROC, PRO, ΔE vs human lot labels.
- **Dataset:** MVTec AD (texture subset), AITEX, TILDA fabric defects.
- **Risk:** Low

16. **Classroom board / slide photo → bilingual study notes**
- **Pitch:** Student SaaS: snap a messy whiteboard or projected slide, get cleaned text + Urdu/English glossary and a 5-bullet recap — offline-ish, not a live lecture bot.
- **Problem:** Students in mixed-language classrooms lose notes when the board is erased; generic OCR fails on diagrams + handwriting mix.
- **Novelty:** Otter/Notta need audio and English; this is CV+layout+MT on *still images*, with real CER/BLEU vs a raw OCR baseline.
- **Technique:** LayoutLMv3 or Donut for layout+text; handwritten regions via CRNN/TrOCR; translation with fine-tuned NLLB-200 (en↔ur); compare vs Tesseract-only; CER, BLEU, named-term coverage.
- **Dataset:** U-HAT (Urdu handwriting), PubTabNet/SlideVQA-style slides, Roman-Urdu-Parl (6.37M pairs) for MT; **needs ~80–120 self-captured classroom photos** for a realistic test split.
- **Risk:** Medium

17. **Feeder / city load-shape forecaster for SME generator & solar sizing (including Ramadan effects)**
- **Pitch:** SME SaaS: forecast next-week load *shape* (not real-time dispatch) so shops can size UPS/solar and plan generator hours around predicted troughs.
- **Problem:** Load-shedding and Ramadan sehri/iftar peaks wreck small businesses; they only get rumor-based schedules.
- **Novelty:** Grid operators have internal tools; a *consumer-side* forecaster with Islamic-calendar features is not a generic energy Kaggle clone.
- **Technique:** LightGBM and a seq2seq LSTM/TFT on lags + weather + weekday + Ramadan/Eid dummies; compare vs seasonal naive and SARIMAX; nRMSE, pinball, peak-hour MAPE.
- **Dataset:** Kaggle PJM Hourly Energy Consumption or UCI Household Power as the trainable hourly series; ERA5 temperature; **honest transfer study** — apply the same feature recipe to any NTDC/NEPRA published series you can get in week 1 (monthly/hourly PDFs). Do not claim DISCO real-time control.
- **Risk:** Medium

18. **Kiryana GST / sales-tax receipt auditor**
- **Pitch:** Bookkeeping SaaS for small shops: snap receipts, extract fields, and flag arithmetic/GST-rate inconsistencies before the accountant sees them.
- **Problem:** SMEs leak money (and fail audits) on wrong tax rates and item-total mismatches; Excel is manual.
- **Novelty:** Expensify is English receipts + card feeds; multilingual receipt KIE + *tax-rule consistency head* is the FYP-sized novelty.
- **Technique:** LayoutLMv3 or Donut for KIE (store, date, line items, tax, total); a second classifier/regressor for consistency errors; compare vs regex+Tesseract; field F1, exact-total accuracy, fraud-flag F1 on injected errors.
- **Dataset:** SROIE, CORD, CORU/AMuRD (Arabic-English receipts — useful for bilingual packaging of numbers). Inject labeled GST mismatches yourself.
- **Risk:** Low

19. **Same-event Urdu news contradiction finder (casualty, price, and score conflicts)**
- **Pitch:** Newsroom/fact-check SaaS: cluster Urdu articles about one event and highlight disagreeing numbers (deaths, votes, gold rate, match score).
- **Problem:** Pakistani/Urdu readers see five headlines with five death tolls; no tool groups them and diffs the quantities.
- **Novelty:** “Fake news classifiers” are saturated and often unethical as products; *numeric claim differencing inside an event cluster* is a journalism tool, not a truth oracle.
- **Technique:** XLM-R embeddings + agglomerative/HDBSCAN event clustering; numeric NER (rules + token classifier); contradiction classifier on claim pairs; compare vs BERTopic + regex numbers; cluster V-measure, pair-level F1.
- **Dataset:** Public Urdu news corpora (iNLTK / Express-news headline sets, BBC Urdu dumps where licensed); UNER for person/location; **needs a small hand-labeled contradiction pair set** (~300 pairs from already-downloaded articles).
- **Risk:** Medium

20. **South-Asian code-switch language ID router (English / Urdu / Roman-Urdu / Sindhi / Pashto / Punjabi)**
- **Pitch:** A pre-moderation SaaS API: tag each message *and each span* so the right downstream filter (hate, scam, search index) is invoked — not a chatbot.
- **Problem:** Platforms and universities dump all “Pakistan traffic” into an English or Arabic model; Roman-Urdu and Sindhi/Pashto get misrouted.
- **Novelty:** langid.py/FastText LID is word-level and fails on intra-sentence switching; span-level LID for this language set is a research-shaped product.
- **Technique:** Token-level XLM-RoBERTa or DistilBERT classifier (BIO language tags) vs OpenLID/FastText baselines; mixed-script features; accuracy, span-F1, confusion between Roman-Urdu and English.
- **Dataset:** FLORES-200 / WikiAnn for Sindhi, Pashto, Urdu, Punjabi; Roman-Urdu-Parl; GlotLID-style public crawls; **synthetic code-switched sentences** generated by splicing parallel clauses (week 1, no scraping farm).
- **Risk:** Low

---

## Claude

1. Roman Urdu Fake-News Filter
- **Pitch:** A browser/webapp tool that flags likely-fake Urdu/Roman-Urdu news articles before you share them.
- **Problem:** Urdu-speaking users in Pakistan/India get most news via WhatsApp/Facebook forwards with no fact-check layer; existing fake-news tools are English-only.
- **Novelty:** Almost all commercial fake-news detectors ignore Urdu entirely; this targets an underserved language directly.
- **Technique:** Fine-tuned XLM-RoBERTa (or mBERT) sequence classifier, benchmarked against a TF-IDF + AdaBoost baseline (replicating the original paper's method) for a real accuracy/F1 comparison table.
- **Dataset:** "Bend the Truth" Urdu Fake News Corpus (Amjad et al., 900 articles, public) / UrduFake@FIRE shared-task data; larger "Ax-to-Grind Urdu" (10,083 articles, 2023) if you want more data.
- **Risk:** Low–Medium (small dataset, but well-documented and proven).

2. Roman Urdu Hate-Speech Moderation API
- **Pitch:** A content-moderation microservice that flags abusive/offensive Roman Urdu text for community platforms.
- **Problem:** Pakistani social platforms and comment sections have no reliable local-language moderation; English moderation APIs miss code-switched abuse entirely.
- **Novelty:** Roman Urdu (Latin-script, code-mixed) is a genuinely underserved NLP niche compared to saturated English toxicity-detection markets.
- **Technique:** Fine-tuned transformer (XLM-R) on coarse- and fine-grained labels, compared against BiLSTM+attention and classical SVM baselines.
- **Dataset:** RUHSOLD — Roman Urdu Hate-Speech and Offensive Language Detection dataset (~10k annotated tweets, MIT license, on HuggingFace/TFDS).
- **Risk:** Low.

3. Urdu AI-Generated Text Detector
- **Pitch:** A tool for Urdu-medium schools/universities to flag AI-written Urdu assignments.
- **Problem:** Academic-integrity tools (Turnitin, GPTZero) barely handle Urdu; instructors have no way to check Urdu submissions.
- **Novelty:** Essentially unaddressed market — every mainstream AI-text detector is English-centric.
- **Technique:** Fine-tuned XLM-R/Urdu-BERT classifier + stylometric/length features, compared against a zero-shot perplexity-threshold baseline (DetectGPT-style) to show supervised vs. zero-shot tradeoffs.
- **Dataset:** UHAT — Urdu Human and AI Text Dataset (3,600 balanced samples, human vs. GPT/Gemini/Kimi-generated, IEEE DataPort, DOI 10.21227/y77y-9917).
- **Risk:** Low–Medium.

4. Job-Scam Shield
- **Pitch:** A browser extension/webapp that scores job postings for fraud risk before you apply or pay any "processing fee."
- **Problem:** Fake job postings (fee scams, fake recruiters) are rampant on Facebook/WhatsApp job groups in Pakistan; job seekers have no screening tool.
- **Novelty:** Existing fraud-detection startups focus on payments/credit cards, not job-posting scams — an underbuilt niche with a real public dataset.
- **Technique:** Multimodal fusion model — fine-tuned DistilBERT on posting text fused with tabular meta-features (salary range present, logo present, etc.) via a gradient-boosted head; compare against text-only and tabular-only ablations.
- **Dataset:** EMSCAD / "Real or Fake Job Postings" (Kaggle, 17,880 postings, ~800 fraudulent, public).
- **Risk:** Low.

5. Crop Doctor: Diagnosis + Treatment Assistant
- **Pitch:** Farmer uploads a leaf photo, gets a disease diagnosis plus retrieved, grounded treatment guidance (not a prescription).
- **Problem:** Smallholder farmers in Pakistan/South Asia lack easy access to agronomists; existing leaf-classifier apps stop at "it's blight" with no next step.
- **Novelty:** Plain PlantVillage classifiers are a saturated student-project category — the RAG treatment-retrieval layer turning it into an actual advisory tool is what's underdone.
- **Technique:** CNN transfer learning (EfficientNet-B0 vs. MobileNetV3, compared on accuracy/latency) for 38-class disease classification + a RAG layer (sentence-transformer embeddings + vector DB) retrieving from a small curated agricultural-extension text corpus.
- **Dataset:** PlantVillage (~54k labeled leaf images, public, Kaggle); treatment corpus needs honest self-collection from public agri-extension PDFs (a few dozen documents, not scraping-heavy).
- **Risk:** Medium (add clear "informational, not prescriptive pesticide advice" disclaimer).

6. Karachi Air-Quality Forecast & Alert Dashboard
- **Pitch:** A dashboard forecasting next 24–48hr PM2.5 for Karachi with health-risk alerts.
- **Problem:** Karachi/Lahore residents have almost no forward-looking air-quality info, only live AQI snapshots.
- **Novelty:** Forecasting (not just reporting) local AQI is genuinely underbuilt regionally — most apps only show current readings.
- **Technique:** Compare classical (SARIMA/Prophet) vs. deep learning (LSTM or Temporal Fusion Transformer) forecasting, evaluated via MAE/RMSE, plus a threshold classifier for alert triggers.
- **Dataset:** OpenAQ API + Pakistan Air Quality Initiative historical sensor data for Karachi (confirmed public, actively maintained), supplemented by aqicn.org's historical CSV export for the Karachi US Consulate station.
- **Risk:** Medium (data has real gaps/missingness typical of developing-market sensors — treat that honestly in your report rather than hiding it).

7. SME Demand Forecasting & Reorder Assistant
- **Pitch:** A dashboard that forecasts SKU-level demand and tells small retailers when to reorder stock.
- **Problem:** Small retailers/kiryana-style shops over- or under-stock because they have no forecasting tools, unlike large chains.
- **Novelty:** Not saturated as a startup category for SMEs specifically (vs. enterprise inventory-management giants); explainability layer for non-technical shop owners is the differentiator.
- **Technique:** LightGBM/XGBoost gradient boosting vs. a Temporal Fusion Transformer, compared on MAPE; SHAP explainability driving plain-language reorder recommendations.
- **Dataset:** Corporación Favorita Grocery Sales Forecasting or "Store Item Demand Forecasting" (both Kaggle, large, public).
- **Risk:** Low.

8. Predictive Maintenance for Industrial Motors
- **Pitch:** A dashboard predicting remaining useful life of industrial equipment before failure.
- **Problem:** Pakistan's textile/manufacturing SMEs run equipment to failure with no predictive monitoring, causing costly downtime.
- **Novelty:** Predictive-maintenance SaaS is common in heavy industry globally but essentially absent as a tool for SME-scale manufacturers.
- **Technique:** LSTM/1D-CNN regression for Remaining Useful Life (RUL) prediction on sensor sequences, benchmarked against a Random Forest regressor using the standard NASA scoring metric.
- **Dataset:** NASA C-MAPSS Turbofan Engine Degradation Simulation dataset (public, NASA Prognostics Data Repository).
- **Risk:** Low–Medium.

9. SME Network Intrusion Dashboard
- **Pitch:** An explainable anomaly-detection dashboard for small businesses to monitor their network traffic.
- **Problem:** SMEs can't afford enterprise SOC tools (Splunk, CrowdStrike) and have zero visibility into network anomalies.
- **Novelty:** Explainable, SME-priced IDS is underserved — most cybersecurity AI targets enterprise buyers.
- **Technique:** Autoencoder-based unsupervised anomaly detection vs. supervised Random Forest/XGBoost, evaluated on Precision/Recall/F1 — including how each generalizes to attack types unseen during training, a genuine methodological point.
- **Dataset:** NSL-KDD (classic, lightweight, public); CICIDS2017 as an optional heavier stretch dataset.
- **Risk:** Low (NSL-KDD) / Medium-High if you add CICIDS2017.

10. Forward Checker: Manipulated-Image Detector
- **Pitch:** Upload a suspicious WhatsApp-forwarded photo, get a "likely manipulated" score with a visual explanation of which region looks fake.
- **Problem:** Doctored images spread fast via WhatsApp/Facebook in Pakistan with no easy verification tool for ordinary users.
- **Novelty:** Most deepfake detectors are trained/tested on pristine lab images; this one's angle is testing and improving robustness to social-media recompression (JPEG re-save, resizing), which is what forwarded images actually look like.
- **Technique:** EfficientNet-B4/XceptionNet CNN fine-tuned for real/fake classification + Grad-CAM overlay; report accuracy on original vs. recompressed test sets to quantify the robustness gap.
- **Dataset:** "140k Real and Fake Faces" (Kaggle, public, StyleGAN-generated vs. real Flickr faces).
- **Risk:** Medium (crowded research area — the recompression-robustness framing is what makes it defensible, don't skip that part).

11. Handwritten Urdu Digitizer
- **Pitch:** Teachers/madrassas scan handwritten Urdu pages and get searchable, editable digital text.
- **Problem:** Urdu-medium schools have no OCR tool for handwritten assignments/historical manuscripts, unlike English (which has mature OCR).
- **Novelty:** Urdu Nasta'liq cursive OCR is a genuinely hard, underserved research problem — very little consumer tooling exists.
- **Technique:** CRNN (CNN + BiLSTM + CTC loss) for line-level recognition, evaluated via Character/Word Error Rate against an out-of-the-box Tesseract-Urdu baseline.
- **Dataset:** UNHD — Urdu Nasta'liq Handwritten Dataset (500 writers, public) or UHLD — Urdu Handwritten Ligature Dataset (~6,000 lines, 200 writers, IEEE DataPort).
- **Risk:** High — be upfront in your report that cursive Urdu OCR accuracy will likely be modest; frame it as a research contribution, not a polished product.

12. Code Plagiarism Detector for CS Courses
- **Pitch:** Instructors upload a batch of student code submissions and get a similarity heatmap flagging likely-copied pairs.
- **Problem:** University CS instructors currently rely on MOSS or manual spot-checks; local universities often have no tool at all.
- **Novelty:** Not a startup-saturated category, and embedding-based (semantic) similarity catches copies that token-matching tools miss (renamed variables, reordered logic).
- **Technique:** CodeBERT embeddings + cosine similarity/Siamese network for pairwise clone detection, evaluated on Precision/Recall/F1 against a classical n-gram Jaccard-similarity baseline.
- **Dataset:** BigCloneBench via the CodeXGLUE clone-detection benchmark (public, GitHub/HuggingFace).
- **Risk:** Low–Medium.

13. Insurance Claim Fraud Explainability Dashboard
- **Pitch:** A dashboard that flags suspicious vehicle-insurance claims and explains exactly why each was flagged.
- **Problem:** Small insurers/claims teams lack affordable fraud-analytics tools; existing ones are black-box.
- **Novelty:** The explainability-for-non-technical-adjusters angle (not just a classifier) is what differentiates it from generic fraud-detection tutorials.
- **Technique:** XGBoost/Random Forest supervised classifier vs. Isolation Forest unsupervised anomaly detector (a genuine comparison, since fraud is heavily class-imbalanced), with per-claim SHAP explanations.
- **Dataset:** A public vehicle-insurance-fraud dataset on Kaggle (~15K claims, small fraud minority class).
- **Risk:** Low.

14. Loan Risk Explainability Tool for Microfinance Officers
- **Pitch:** An internal scoring tool that helps microfinance loan officers see default risk and the reasons behind it, for their own use — not a consumer-facing "get a loan" app.
- **Problem:** Small microfinance institutions in Pakistan often score credit manually with little consistency; larger banks have proprietary systems SMFIs can't afford.
- **Novelty:** The explainability-for-loan-officers framing (an internal decision-support tool, not automated financial advice) keeps this useful without the legal exposure of consumer-facing lending decisions.
- **Technique:** Gradient boosting classifier (XGBoost/LightGBM) + SHAP/LIME explanations per application, benchmarked against logistic regression.
- **Dataset:** "Give Me Some Credit" (Kaggle, ~150k borrowers, public) or the UCI German Credit dataset for a smaller/faster build.
- **Risk:** Low (include an explicit "not financial advice, decision-support only" disclaimer in the app).

15. Voice-Note Customer Feedback Analyzer
- **Pitch:** Businesses upload customer voice-note feedback (e.g., from WhatsApp Business) and get an emotion/sentiment breakdown.
- **Problem:** SMEs collect voice feedback informally but have no way to analyze it at scale, unlike text reviews.
- **Novelty:** Speech emotion recognition tools exist, but a "SaaS for SME customer-feedback voice notes" angle (not call-center telephony) is underbuilt and legally cleaner.
- **Technique:** 1D-CNN/BiLSTM on MFCC + prosodic features vs. a fine-tuned wav2vec2 model, compared on per-class F1 (emotion recognition is imbalanced, so report the full confusion matrix, not just accuracy).
- **Dataset:** RAVDESS and/or CREMA-D (public, established emotion-speech datasets); demo explicitly with user-uploaded, consented clips — no call recording or live telephony.
- **Risk:** Medium (audio pipelines have more moving parts; wav2vec2 fine-tuning is compute-heavier).

16. RAG Research-Repository Search Engine
- **Pitch:** A semantic search + Q&A tool over a body of academic papers, with real retrieval-quality benchmarking (not just "ask it a question and it seems to work").
- **Problem:** Students/researchers scanning large paper corpora rely on keyword search that misses semantically related work.
- **Novelty:** Most student RAG projects skip proper IR evaluation entirely — doing it rigorously (Recall@k, MRR, nDCG) is itself the differentiator and gives you real "model evaluation" content for your report.
- **Technique:** Dense retrieval (sentence-transformers bi-encoder) + vector DB (FAISS/Chroma) + LLM answer generation (LangChain), benchmarked against BM25 sparse retrieval and a hybrid retriever.
- **Dataset:** arXiv Dataset (Kaggle/Cornell, 1.7M+ paper abstracts and metadata, public) — scope to one subfield (e.g., cs.CL) to fit your time budget.
- **Risk:** Low–Medium.

17. Citation-Graph Research Explorer
- **Pitch:** An interactive tool that recommends related papers to cite using the citation graph, not just keyword similarity.
- **Problem:** Researchers/students miss relevant prior work that isn't keyword-similar but is structurally connected via citations.
- **Novelty:** Graph neural networks are rarely used in student capstones outside pure ML coursework — building it as an actual usable "research discovery" product is the fresh angle.
- **Technique:** GCN or GraphSAGE (via PyTorch Geometric) for node classification + link prediction, benchmarked against a non-graph baseline (logistic regression on node features alone) to prove the graph structure adds value; evaluated via Hits@K/MRR for link prediction.
- **Dataset:** OGB ogbn-arxiv (Open Graph Benchmark, public) or the smaller Cora/Citeseer citation datasets for faster iteration.
- **Risk:** Medium (new library/paradigm to learn, but well-tutorialized).

18. Electricity Load Forecast & Load-Shedding Predictor
- **Pitch:** A dashboard forecasting short-term electricity demand and flagging anomaly spikes that could trigger load-shedding.
- **Problem:** Pakistan's chronic load-shedding makes short-term demand forecasting genuinely useful for planning (homes, small businesses, microgrids/solar).
- **Novelty:** Regionally very meaningful problem, and not something you see generic AI startups building — most load-forecasting tools target large utilities, not this framing.
- **Technique:** Prophet/SARIMA vs. an LSTM/Temporal Fusion Transformer, evaluated via MAPE/RMSE, plus anomaly-flagging for unusual demand spikes.
- **Dataset:** Honestly, no clean public Pakistan-specific hourly grid-load dataset exists for week 1 — use the PJM Hourly Energy Consumption dataset (Kaggle, public, US grid) to build and validate the pipeline, and state clearly in your report that the same architecture would apply to local utility data if obtained later.
- **Risk:** Low.

19. Deceptive Review Detector for E-commerce
- **Pitch:** A tool that flags likely-fake/paid reviews on e-commerce listings.
- **Problem:** Online marketplaces (Daraz-style, Amazon-style) are full of incentivized fake reviews that mislead buyers.
- **Novelty:** Not saturated as an actual product category — most "review analysis" tools focus on sentiment, not deception detection specifically.
- **Technique:** Fine-tuned RoBERTa/DistilBERT + stylometric feature engineering (n-gram patterns, POS distributions), benchmarked against the classical SVM+TF-IDF method from the original research.
- **Dataset:** Deceptive Opinion Spam Corpus (Ott et al., Cornell, ~1,600 hotel reviews, public, the classic gold-standard benchmark for this task).
- **Risk:** Low.

20. Receipt/Invoice Extractor for SME Bookkeeping
- **Pitch:** SME owners photograph receipts and get structured bookkeeping entries (vendor, date, total, tax) auto-extracted.
- **Problem:** Small businesses in Pakistan mostly do bookkeeping manually or not at all; commercial invoice-AI tools are priced for enterprises.
- **Novelty:** Modern layout-aware document AI (not classic OCR+regex) applied to an SME-affordable price point is the differentiator.
- **Technique:** LayoutLMv3 fine-tuned for key-value entity extraction from scanned receipts, evaluated via field-level F1/exact-match against a Tesseract+regex rule-based baseline.
- **Dataset:** SROIE — Scanned Receipts OCR and Information Extraction dataset (ICDAR 2019, public).
- **Risk:** Medium–High (LayoutLM fine-tuning is more resource- and setup-intensive than the other ideas — budget extra hours here).

---

## Gemini

1. Automated Municipal Road Infrastructure Auditing API
- **Pitch:** A computer vision SaaS endpoint that processes dashcam footage from municipal fleet vehicles to automatically map, classify, and assess the severity of road surface damage for proactive maintenance triaging.
- **Problem:** Municipalities and local departments of transportation waste significant capital and labor hours conducting manual road infrastructure surveys. Potholes and severe alligator cracking cause vehicle damage and represent civic liability, but repair crews are traditionally deployed reactively based on citizen complaints rather than objective, data-driven severity mapping. This product serves city planners and civil engineering contractors by automating the audit process, allowing for predictive maintenance scheduling.
- **Novelty:** Existing road maintenance software relies on dedicated, expensive laser-scanning vehicles. This solution democratizes infrastructure auditing by functioning as a low-overhead SaaS that accepts standard 1080p RGB dashcam imagery from existing city fleets (e.g., garbage trucks, police cruisers), applying machine learning to geolocate and categorize damage without specialized hardware.
- **Technique:** The core architecture relies on an object detection framework, specifically a fine-tuned YOLOv8 or Faster R-CNN model designed for multi-class bounding box regression1. Model evaluation for the report must include Mean Average Precision (mAP) at various Intersection over Union (IoU) thresholds (e.g., mAP@0.5), inference speed metrics (FPS), and confusion matrices for class-specific performance across the defined damage categories. Ensemble methods combining YOLO and image tiling have proven highly effective in this domain2.
- **Dataset:** The RDD2022 (Road Damage Dataset 2022)2.

  - **Dataset Feature:** Specification
  - **Total Images:** 47,420 high-resolution images3
Japan, India, Czech Republic, Norway, US, Geographic Diversity China3
>55,000 labeled instances with bounding Annotations boxes3
Longitudinal cracks (D00), Transverse cracks
  - **Damage Classes:** (D10), Alligator cracks (D20), Potholes (D40)7

- **Risk:** Low. The dataset is meticulously structured, publicly available, and explicitly designed for computer vision benchmarking6. Utilizing modern frameworks like PyTorch and Ultralytics enables rapid prototyping within the 50-hour constraint, leaving ample time for frontend dashboard development and robust report writing.

2. Shift-Left DevSecOps Vulnerability Scanner
- **Pitch:** An AI-powered static application security testing (SAST) SaaS tool that integrates into CI/CD pipelines to predictively flag vulnerable C/C++ functions before they are merged into production codebases.
- **Problem:** Traditional static analysis tools generate overwhelming volumes of false positives, relying on brittle, rules-based regex engines. Software engineering teams and DevSecOps engineers spend excessive time triaging these alerts. A machine learning-based approach identifies semantic vulnerabilities based on historical exploit patterns rather than static rules, saving development time and preventing critical zero-day vulnerabilities in low-level systems.
- **Novelty:** While general-purpose LLMs can spot basic errors, they lack specialized, curated training on deep-seated common weakness enumerations (CWEs) and often struggle with context windows in legacy C/C++ code. This tool is a highly specialized, domain-specific classifier focused strictly on vulnerability detection, providing a targeted API for IDEs or GitHub Actions.
- **Technique:** The architecture requires fine-tuning a transformer-based model, such as CodeBERT, CodeT5, or XLM-RoBERTa, for binary sequence classification9. The model will process tokenized C/C++ functions to output a vulnerability probability score. The evaluation report must deeply analyze the False Positive Rate (FPR), True Positive Rate (TPR), and Macro F1-score, as high false positive rates are the primary failure mode of automated vulnerability detection9.
- **Dataset:** The DiverseVul Dataset11. This dataset represents the most comprehensive open-source corpus of vulnerable C/C++ source code, curated from security-fix commits.

  - **Dataset Metric:** Volume/Detail
  - **Vulnerable Functions:** 18,9459
  - **Non-Vulnerable Functions:** 330,4929
  - **Unique Fix Commits:** 7,514 across 150 distinct CWEs9
  - **Vulnerability Fraction:** 5.42% (severe class imbalance)11

- **Risk:** Medium. Handling source code tokenization (e.g., managing long sequences that exceed standard transformer limits) requires intermediate data wrangling skills. Furthermore, the significant class imbalance necessitates advanced sampling techniques or focal loss functions to train effectively, avoiding a model that simply predicts "safe" for every input11.

3. Web Application Firewall (WAF) Payload Anomaly Detector
- **Pitch:** A machine learning-driven WAF ruleset engine that analyzes incoming HTTP requests to classify and block zero-day application layer attacks, such as novel SQL injection and cross-site scripting (XSS) mutations.
- **Problem:** Signature-based WAFs rely on blacklists that are constantly evaded by attackers using obfuscation, encoding, and polymorphic payloads. Cybersecurity operations centers (SOCs) and cloud infrastructure providers require intelligent systems that can detect the underlying semantic intent of an attack rather than just matching known string signatures.
- **Novelty:** Most commercial WAFs charge premium enterprise rates for machine learning features that are essentially basic anomaly thresholds. By wrapping this capability into an easily deployable Python-based microservice or API, smaller SaaS startups can integrate deep learning-based payload inspection without expensive enterprise licensing.
- **Technique:** A hybrid Recurrent Neural Network architecture, specifically a Bidirectional Long Short-Term Memory (Bi-LSTM) network, or a lightweight transformer model (e.g., DistilBERT) adapted for character-level or byte-level tokenization14. The report must feature precision-recall curves, the Area Under the Receiver Operating Characteristic (AUC-ROC), and inference latency measurements, as a WAF must operate with millisecond latency.
- **Dataset:** The CSIC 2010 HTTP Dataset17.

  - **Attack Category:** Description within Dataset
Malicious database query payloads
  - **SQL Injection:** embedded in HTTP GET/POST parameters20
Client-side script injections targeting web Cross-Site Scripting (XSS) application vulnerabilities14
Abnormally large string payloads intended to Buffer Overflow corrupt memory20
Legitimate e-commerce web traffic used as Normal Traffic the baseline for non-anomalous behavior17

- **Risk:** Low. The dataset is tabular and readily available on platforms like Kaggle16. Preprocessing HTTP payloads using standard NLP techniques (TF-IDF or word/character embeddings) is straightforward, and deployment via FastAPI allows for an immediate demonstration of the SaaS endpoint functionality.

4. Emergency Department Operational Triage & Resource Engine
- **Pitch:** An operational forecasting dashboard for hospital administrators that leverages patient triage data to predict Emergency Department (ED) length of stay and hospital admission likelihood, optimizing resource allocation.
- **Problem:** Emergency department overcrowding leads to delayed care, inefficient bed allocation, and elevated patient risk23. Triage nurses and hospital bed managers struggle to accurately forecast which incoming patients will require extended observation or admission to inpatient wards. Predictive analytics streamline bed management and optimize resource rationing without interfering with clinical diagnoses.
- **Novelty:** By explicitly avoiding medical diagnosis (which poses severe ethical and legal liabilities), this tool focuses purely on operational logistics. It does not dictate pathology; rather, it informs administration regarding anticipated bed occupancy based on historical operational throughput.
- **Technique:** Gradient Boosting Decision Trees (GBDT), utilizing frameworks like XGBoost or LightGBM, configured for both regression (Length of Stay in hours) and binary classification (Admission: Yes/No)24. The evaluation must detail Root Mean Squared Error (RMSE) for the regression task, Brier scores for calibration, and feature importance analyses (e.g., SHAP values) to explain which variables most heavily influence resource consumption24.
- **Dataset:** The MIMIC-IV-ED database or the MIETIC (MIMIC-IV-Ext Triage Instruction Corpus)23.

  - **Data Component:** Description in MIMIC-IV-ED / MIETIC
~425,000 distinct patient visits from 2011- Total ED Stays 201927
Vital signs, pain scales, chief complaints, Triage Inputs patient demographics23
ESI levels (1-5), disposition
  - **Target Variables:** (admitted/discharged), outtime minus intime (LOS)23
18-30 (25.18%), 31-50 (23.38%), 51-70 Age Demographics (29.75%), 71+ (21.69%)23

- **Risk:** Medium. The MIMIC-IV-ED dataset requires robust data harmonization, handling missing values, and executing precise train/validation/test splits by patient ID to prevent data leakage across multiple visits by the same individual26.

5. Slang-Aware Brand Sentiment Monitor for Code-Mixed Markets
- **Pitch:** A social media analytics SaaS designed specifically to monitor brand health and product feedback in code-mixed Roman Urdu, catering to the vast, underserved digital demographics of South Asia.
- **Problem:** Global brand monitoring tools excel at English sentiment analysis but fail catastrophically when processing code-mixed languages (e.g., Urdu typed in Latin script, mixed with English slang). Marketing agencies, telecom companies, and FMCG brands operating in South Asia miss critical consumer insights and PR crises because standard NLP models classify Roman Urdu text as noise.
- **Novelty:** While English sentiment is arguably the most saturated project in data science, Roman Urdu remains a low-resource linguistic domain. A dedicated endpoint that understands slang, regional abbreviations, and phonetic variations of Roman Urdu provides a distinct competitive moat compared to generic wrappers around commercial APIs.
- **Technique:** Fine-tuning a multilingual transformer model, specifically XLM-RoBERTa or mBERT, utilizing sequence classification heads29. The evaluation report must highlight the model's Macro F1 score and provide a detailed confusion matrix to demonstrate balanced performance across Positive, Negative, and Neutral classes, testing robustness against slang-heavy adversarial inputs29.
- **Dataset:** The RomanUrdu-NLP-Sentiment-Corpus31.

  - **Dataset Feature:** Details
  - **Total Samples:** 134,052 labeled text sequences31
WhatsApp chat exports, YouTube comments, Data Sources Twitter30
Balanced across Positive, Negative, and Class Distribution Neutral sentiments30
Phonetic variability, code-switching with Linguistic Challenges English, extensive internet slang30

- **Risk:** Low. The dataset is meticulously cleaned and available on the HuggingFace Hub31. Utilizing the transformers library allows for highly efficient fine-tuning, leaving the bulk of the project hours for building an interactive Streamlit or Next.js dashboard to visualize sentiment trends over time.

6. Retail Shelf Planogram Compliance & Inventory API
- **Pitch:** A computer vision microservice that allows retail managers to upload photos of store aisles to automatically verify planogram compliance, detect out-of-stock items, and calculate brand share-of-shelf.
- **Problem:** Fast-moving consumer goods (FMCG) brands and supermarket managers lose substantial revenue due to out-of-stock items and improper product placement. Auditing store shelves manually is slow, error-prone, and labor-intensive. A visual API automates this process, providing immediate feedback on whether a physical display matches the contracted corporate planogram.
- **Novelty:** Standard object detection tutorials focus on sparse environments (e.g., detecting one dog or two cars in an image). Retail environments are exceptionally dense, sometimes featuring hundreds of tightly packed, visually similar objects in a single frame. Focusing on dense object detection demonstrates advanced capability and solves a highly specific enterprise logistics problem.
- **Technique:** Dense object detection architectures such as RetinaNet, Faster R-CNN, or YOLOv8, trained specifically to handle high-density bounding box regression34. The evaluation report must focus heavily on recall in dense clusters and the model's ability to handle scale variations (objects far down the aisle versus up close).
- **Dataset:** The SKU-110K dataset34.

  - **SKU-110K Dataset Metrics:** Specification
  - **Total Images:** 11,743 densely packed retail-shelf images34
  - **Data Splits:** 8,219 train / 588 validation / 2,936 test34
Over 1.7 million bounding boxes, focusing on Annotation Density dense packing34
Explicitly formatted for training YOLO and Model Compatibility RetinaNet models34

- **Risk:** Medium. Training on images with hundreds of annotations per frame is computationally expensive and requires careful anchor box tuning to prevent suppression of valid adjacent detections. The project can be scoped down by utilizing pre-trained weights and fine-tuning on a temporal subset of the data.

7. Automated Tactical Sports Action Spotting
- **Pitch:** A video analysis pipeline for amateur and semi-pro football clubs that processes match footage to automatically identify, timestamp, and clip key tactical events (goals, fouls, cards, substitutions).
- **Problem:** Elite sports teams employ armies of data analysts to tag match events, but amateur leagues, college teams, and lower-division clubs lack the budget for extensive manual video analysis. Coaches and sports journalists need affordable tools to automatically generate highlight reels and extract tactical events for post-match reviews.
- **Novelty:** While general video classification (e.g., predicting if a video contains sports) is common, action spotting—identifying the exact timestamp a specific micro-event occurs within a continuous, two-hour video stream—is a highly specialized and underserved computer vision domain with direct commercial application.
- **Technique:** Spatiotemporal feature extraction using 3D Convolutional Neural Networks (e.g., I3D or C3D architectures) or ActionVLAD, followed by a temporal localization module35. The report must critically evaluate temporal precision, utilizing Average-mAP within varying temporal tolerances (e.g., 1-second, 5-second, or 10-second localization windows).
- **Dataset:** The SoccerNet dataset35.

  - **SoccerNet Feature:** Details
  - **Scale:** Hundreds of full broadcast matches
Precise timestamps for crucial game events Annotations (goals, fouls, cards)35
Available via GitHub with baseline code Accessibility repositories35
Specifically built for scalable action spotting Task Focus in unclipped video35

- **Risk:** High. Video processing requires substantial compute power and memory. To fit the 50-hour constraint, the architecture should rely on pre-extracted feature embeddings (often provided alongside datasets like SoccerNet) rather than training 3D CNNs from scratch on raw pixel data, allowing the focus to remain on the temporal localization modeling.

8. Global Agricultural Yield Forecaster API
- **Pitch:** A predictive modeling API that aggregates historical crop yields, livestock production, and regional data to forecast future agricultural output, aiding supply chain planning for commodities traders and NGOs.
- **Problem:** Global food supply chains are highly volatile. Commodities traders, agricultural policy makers, and international NGOs require robust forecasts of crop yields to price futures, plan logistical routing, and anticipate food shortages. Manual economic modeling is often too slow to adapt to changing multilateral production data.
- **Novelty:** Instead of a standard sales forecasting project, this applies multivariate time-series forecasting to critical global infrastructure. By providing a SaaS-like API where a user inputs a country and a crop type, it bridges the gap between raw macroeconomic data and actionable supply chain intelligence.
- **Technique:** Advanced time-series forecasting utilizing Long Short-Term Memory (LSTM) networks or Temporal Fusion Transformers (TFT). The evaluation report must benchmark the deep learning models against traditional statistical baselines (like ARIMA or Prophet), utilizing Mean Absolute Percentage Error (MAPE) and symmetric MAPE to judge performance across varying scales of production volume.
- **Dataset:** The FAOSTAT Global Food and Agriculture Statistics dataset36.

  - **FAOSTAT Data Overview:** Scope and Granularity
Annual data spanning from 1961 to modern Temporal Coverage years37
Over 200 countries and regional Geographic Scope aggregates37
More than 200 primary agricultural products Variable Depth and inputs37
Over 3 million time-series and cross-sectional Data Structure records37

- **Risk:** Low. The data is highly structured, tabular, and well-documented. Time-series preprocessing (handling missing years, normalization, and windowing) is the primary technical hurdle, allowing fast deployment of a frontend visualization dashboard utilizing a framework like Plotly Dash or Streamlit.

9. B2B Legal Contract Clause Risk Extractor
- **Pitch:** An NLP-powered SaaS tool that allows legal teams to upload massive PDF contracts, automatically extracting, classifying, and highlighting high-risk clauses such as indemnification, termination, and non-compete agreements.
- **Problem:** During corporate mergers and acquisitions, paralegals and junior associates spend thousands of billable hours manually reading lengthy contracts during the due diligence phase. This manual review is exceptionally costly and prone to human error. A machine learning tool accelerates due diligence by instantly surfacing critical legal obligations.
- **Novelty:** Unlike generic document summarization using standard LLM wrappers, this solution treats contract review as a rigorous span-token classification and question-answering task. It focuses on the strict legal definitions of clauses rather than abstract summarization, providing a highly defensible, deterministic enterprise application.
- **Technique:** Token classification and extractive Question Answering (QA) using a domain-adapted transformer such as Legal-BERT or RoBERTa. The model is trained to identify the start and end tokens of specific clauses within lengthy documents. Evaluation requires strict metrics such as exact match (EM) and token-level F1-scores, documenting how well the model isolates precise legal boundaries.
- **Dataset:** The Contract Understanding Atticus Dataset (CUAD).

  - **CUAD Dataset Focus:** Description
Over 500 fully annotated commercial Volume contracts
  - **Clause Taxonomy:** 41 distinct types of essential legal clauses
  - **Annotation Quality:** Curated and validated by legal experts
Optimized for span extraction and token Task Suitability classification tasks

- **Risk:** Medium. Processing long legal documents requires intelligent chunking strategies to bypass standard transformer token limits (e.g., 512 tokens). Integrating a frontend that accurately overlays highlights onto the original PDF text (using OCR spatial alignment) adds engineering overhead but creates an exceptional portfolio piece.

10. Industrial Machinery Acoustic Anomaly Detection
- **Pitch:** An edge-deployable predictive maintenance system that analyzes the operational sound of factory machinery, automatically triggering alerts when acoustic signatures deviate from normal baseline operations.
- **Problem:** Unplanned downtime in manufacturing environments costs millions of dollars. Bearings, valves, and pumps often exhibit subtle changes in their acoustic profile (whining, grinding) long before catastrophic failure occurs. Factory operators need automated, non-invasive condition monitoring that does not require taking machines offline to install internal physical sensors.
- **Novelty:** Audio machine learning is highly underrepresented in academic portfolios compared to NLP and computer vision. Applying unsupervised acoustic learning to heavy industry demonstrates a sophisticated understanding of non-traditional data modalities and edge IoT deployment concepts.
- **Technique:** Unsupervised representation learning utilizing Convolutional Autoencoders or Variational Autoencoders (VAEs). Raw audio is transformed into Mel-spectrograms. The autoencoder is trained exclusively on "normal" machine sounds. During inference, sounds that result in a high reconstruction error are flagged as anomalous. Evaluation requires the Area Under the ROC Curve (AUC-ROC) utilizing the reconstruction loss as the primary anomaly score.
- **Dataset:** The MIMII (Malfunctioning Industrial Machine Investigation and Inspection) dataset.

  - **MIMII Dataset Components:** Details
  - **Machine Types:** Valves, pumps, fans, and slide rails
Audio recordings of normal and anomalous Acoustic Profiles operating conditions
Mixed with varying levels of background Environmental Realism factory noise (SNRs)
Designed specifically for unsupervised Learning Paradigm anomaly detection

- **Risk:** Medium. The transition from raw waveforms to optimal Mel-spectrograms requires an understanding of digital signal processing parameters (Fourier transforms, hop lengths, window sizing). However, the unsupervised nature of the architecture avoids the need for massive labeled anomaly datasets, streamlining the training process.

11. Agentic Customer Support Triaging & Semantic Routing
- **Pitch:** An intelligent ticket-routing workflow engine that analyzes incoming customer support emails, extracts the semantic intent, and autonomously routes the ticket to the correct departmental queue using vector similarity.
- **Problem:** Large enterprise SaaS companies receive thousands of support tickets daily. Tier 1 support agents spend excessive time merely reading and routing these tickets to the appropriate specialists (billing, technical, sales). Automated semantic routing drastically reduces time-to-resolution (TTR) and lowers Tier 1 operational costs.
- **Novelty:** Instead of a basic keyword-matching algorithm, this leverages modern orchestration frameworks (LangChain/LangGraph) integrated with vector databases. It goes beyond simple classification by building an "agentic" workflow that can autonomously query documentation to suggest a resolution context before routing the ticket.
- **Technique:** Retrieval-Augmented Generation (RAG) architecture combined with dense vector embeddings. Incoming text is embedded using models like all-MiniLM-L6-v2. The vector database (e.g., Pinecone, Chroma) performs a k-Nearest Neighbors (k-NN) search against historical, successfully resolved tickets to determine the optimal routing category. The report must evaluate retrieval accuracy (Recall@K) and routing classification precision.
- **Dataset:** The "Customer Support on Twitter" dataset available on Kaggle.

  - **Customer Support Dataset:** Utility for Routing
  - **Volume:** Over 3 million tweets and replies
Interactions covering major brands across Brand Diversity tech, retail, and travel
Can be synthesized into IT-specific Adaptability departmental routing queues
Short, informal text mimicking live chat and Text Characteristics email support queries

- **Risk:** Low. Integrating LangChain with a local or managed vector database is highly documented. The project focuses heavily on pipeline engineering and API integration rather than training neural networks from scratch, easily fitting the time constraint while showcasing modern architectural orchestration.

12. E-commerce Dynamic Pricing & Elasticity Engine
- **Pitch:** A dynamic pricing backend that analyzes historical sales velocity, freight costs, and review scores to recommend optimal product pricing in real-time, maximizing gross merchandise volume (GMV) and profit margins.
- **Problem:** Medium-sized e-commerce sellers typically rely on static pricing or rudimentary rules (e.g., "always be $0.01 cheaper than a competitor"). This leaves margin on the table during periods of high demand and results in stagnant inventory during low demand. Retailers need algorithmic pricing models akin to those used by Amazon and Uber to optimize revenue.
- **Novelty:** While many projects predict housing prices or stock markets, predicting price elasticity in a commercial retail setting is a highly sought-after industry skill. It frames machine learning as a direct revenue-generating tool rather than just a cost-saving automation, aligning data science with core business KPIs.
- **Technique:** A combination of Regression Trees (Random Forest, Gradient Boosting) for baseline demand forecasting, coupled with optimization algorithms to find the price point that maximizes expected revenue (Price × Predicted Sales Volume). The report must evaluate the model's regression metrics (Mean Absolute Error, R-squared) and mathematically simulate the projected revenue uplift compared to a static pricing baseline.
- **Dataset:** The Olist Brazilian E-commerce Public Dataset (Kaggle).

  - **Olist Dataset Features:** Relevance to Price Elasticity
  - **Order Volume:** >100,000 anonymized e-commerce orders
Precise product prices and dynamic freight Financial Data values
Delivery times, customer review scores, and Contextual Regressors product categories
Timestamps allowing for demand modeling Temporal Data over distinct seasons

- **Risk:** Low. The dataset is tabular and requires standard, albeit rigorous, data cleaning (joining multiple relational tables). The ML models are natively supported by scikit-learn and LightGBM, allowing for rapid iteration, mathematical optimization, and dashboard deployment.

13. Complex Document Information Extraction (Multimodal OCR)
- **Pitch:** A multimodal document processing API that processes unstructured business forms (invoices, receipts, shipping manifests) to extract key-value pairs by analyzing both the text and the spatial layout of the document.
- **Problem:** Logistics companies, accounting firms, and healthcare providers process millions of scanned PDF forms. Standard Optical Character Recognition (OCR) extracts text into a flat string, losing the critical context of where the text was located (e.g., a number might be a "Total Amount" or a "Phone Number" depending on its position). Multimodal extraction automates data entry with high fidelity.
- **Novelty:** Older tools rely on rigid, pixel-perfect templates. If a vendor moves a logo, the template breaks. Multimodal AI understands documents semantically and spatially, allowing the system to generalize to unseen form layouts. This mimics expensive enterprise solutions like AWS Textract or Google Document AI, bringing it into a localized, controllable SaaS environment.
- **Technique:** Multimodal Transformer architectures, specifically LayoutLMv2 or LayoutLMv3. These models combine visual features (from CNNs), spatial embeddings (bounding box coordinates), and text embeddings (from traditional OCR engines like Tesseract) to perform Token Classification (Named Entity Recognition) on a 2D plane.
- **Dataset:** The FUNSD (Form Understanding in Noisy Scanned Documents) dataset.

  - **FUNSD Dataset Attributes:** Implementation Detail
  - **Dataset Size:** 199 fully annotated, noisy scanned forms
  - **Spatial Annotations:** >31,000 word-level bounding boxes
Categorized into Header, Question, Answer, Semantic Entities and Other
Perfectly designed for benchmarking Task Alignment LayoutLM spatial architectures

- **Risk:** High. Coordinating an OCR engine (Tesseract) to generate bounding boxes, aligning those boxes with textual tokens, and feeding them into a multimodal transformer requires meticulous tensor manipulation and data handling. However, successful implementation yields a profoundly impressive portfolio asset.

14. Toxic Content Moderation API for Gaming Communities
- **Pitch:** A low-latency text moderation microservice designed to integrate with multiplayer gaming chats and Discord servers, detecting multiple overlapping vectors of toxicity (insults, threats, obscenity) to foster safer online communities.
- **Problem:** Online gaming environments and social platforms suffer from rampant toxicity, leading to user churn and PR liabilities. Human moderation is impossible at scale, and simple profanity filters are easily bypassed using character substitution. Community managers need a nuanced tool that distinguishes between friendly competitive banter, explicit threats, and identity-based hate speech.
- **Novelty:** Instead of a binary "toxic/not toxic" classifier, this tool treats moderation as a multi-label problem, recognizing that a single comment can simultaneously be obscene, a threat, and an insult. Structuring it as a Webhook/API that server administrators can plug directly into a Discord bot via n8n gives it a highly polished, SaaS-ready architecture.
- **Technique:** A lightweight transformer model (e.g., DistilBERT or ALBERT) configured with a multi-label classification head (Sigmoid activation on the output layer) optimized with Binary Cross-Entropy loss. The report must rigorously evaluate the model using macro and micro-averaged F1-scores, demonstrating the ability to handle highly imbalanced minority classes (like severe, actionable threats).
- **Dataset:** The Jigsaw Toxic Comment Classification Challenge dataset (Kaggle).

  - **Jigsaw Dataset Classes:** Description of Labels
  - **Data Volume:** ~150,000 Wikipedia talk page comments
toxic, severe_toxic, obscene, threat, insult, Toxicity Vectors identity_hate
Non-exclusive multi-label (a comment can Labeling Structure hold multiple tags)
Requires specialized loss functions to detect Imbalance Handling rare 'threat' classes

- **Risk:** Low. Multi-label text classification is well-supported by HuggingFace pipelines. The primary technical focus will be on optimizing inference speed to meet the low-latency requirements of a live chat environment and building the integration layer.

15. SaaS Churn Intervention Recommender
- **Pitch:** A predictive analytics dashboard for Customer Success teams that not only identifies which users are at risk of canceling their SaaS subscriptions but prescribes the specific intervention most likely to retain them.
- **Problem:** Customer acquisition costs (CAC) in B2B SaaS are exceptionally high, making retention critical to profitability. However, Customer Success Managers (CSMs) often only know a client is unhappy when the cancellation request is submitted. A proactive engine identifies behavioral degradation (e.g., declining logins, decreased feature usage) to flag at-risk accounts weeks in advance.
- **Novelty:** Standard churn prediction models simply output a probability score (e.g., "80% chance to churn"). This project incorporates Survival Analysis to answer when the user will churn, and combines it with uplift modeling to suggest what action (e.g., a discount, a technical training call) is statistically proven to alter that trajectory.
- **Technique:** Survival Analysis utilizing the Cox Proportional Hazards model or Random Survival Forests, combined with traditional classification (LightGBM/XGBoost). The evaluation report will highlight the Concordance Index (C-index) for survival metrics and standard classification metrics (AUC-ROC) for the binary churn flag.
- **Dataset:** The IBM Telco Customer Churn dataset.

  - **Telco Dataset Enhancements:** Modeling Application
IBM Telco Churn (thousands of customer Base Dataset profiles with churn flags)
Tenure (months active) applied to time-to-Survival Variables event modeling
Can be enriched with synthetic daily active Behavioral Synthesis user (DAU) logs
Mapping historical contract types to Intervention Mapping simulated retention actions

- **Risk:** Medium. While the standard churn classification is straightforward, implementing and evaluating Survival Analysis requires a deeper statistical understanding of censored data (users who have not churned yet but might in the future), pushing beyond standard supervised learning paradigms.

16. Semantic Podcast Chapter Generator & Summarizer
- **Pitch:** An automated content-repurposing engine that ingests long-form audio transcripts (podcasts, webinars), detects semantic shifts to automatically generate timestamped chapters, and provides concise summaries for each segment.
- **Problem:** Content creators and digital marketers spend hours manually listening to their own recordings to write show notes, YouTube chapters, and promotional summaries. Automating this workflow saves massive amounts of post-production time and drastically improves the SEO and accessibility of long-form audio content.
- **Novelty:** Utilizing deterministic sliding-window chunking destroys the context of a conversation by cutting off sentences arbitrarily. This project uses "agentic chunking"—utilizing NLP embeddings to identify natural semantic boundaries in a conversation, ensuring that chapters are cut exactly when the topic changes.
- **Technique:** Text Embeddings (e.g., all-MiniLM-L6-v2) for semantic similarity calculations to detect topic boundaries by measuring the cosine distance between sequential chunks. Once segmented, an abstractive summarization model (BART or Pegasus) generates the chapter titles. The evaluation relies on ROUGE scores for the summaries and a custom overlap metric against human-annotated boundaries.
- **Dataset:** The Spotify Podcast Dataset (TREC 2020) or YouTube Transcript APIs.

  - **Dataset Viability:** Source Mechanics
Thousands of English podcast transcripts Spotify TREC 2020 with creator descriptions
Extracting VTT files from tech podcasts using YouTube Scrape open-source scrapers
Utilizing creator-uploaded timestamp Ground Truth chapters as the target variable
Highly conversational text, requiring robust Format contextual analysis

- **Risk:** Medium. The integration of LangChain to handle the multi-step orchestration (embed -> segment -> summarize) requires careful prompt engineering and token management to process transcripts that easily extend beyond 10,000 words.

17. Edge-Deployed Precision Agriculture Disease Classifier
- **Pitch:** A lightweight, offline-capable mobile computer vision application that allows agronomists and farmers to photograph crop leaves and receive instant diagnoses of plant diseases.
- **Problem:** Plant diseases cause massive global crop yield losses, disproportionately affecting smallholder farmers in developing regions. These farmers lack access to agricultural extension officers and often rely on inaccurate guesswork to apply pesticides. Providing a fast, visual diagnosis tool helps minimize chemical overuse and saves crops.
- **Novelty:** Many CV models are hosted on massive cloud GPUs. This project deliberately constraints the architecture to lightweight models designed specifically for edge deployment. This ensures the tool can run natively on a smartphone in rural fields without cellular internet connectivity, solving a critical infrastructure barrier.
- **Technique:** Image classification using highly efficient Convolutional Neural Network architectures such as MobileNetV2 or EfficientNet-B0. The evaluation report must document the trade-off between model quantization (reducing precision from Float32 to Int8 to shrink file size) and the resulting impact on accuracy and inference speed on CPU hardware.
- **Dataset:** The PlantVillage Dataset.

  - **PlantVillage Architecture:** Specifications
  - **Total Images:** >50,000 controlled-environment leaf images
  - **Species Diversity:** 14 distinct crop species
26 specific plant diseases alongside healthy Disease Taxonomy baselines
Ideal for testing quantization degradation on Use Case Fit fine-grained classification

- **Risk:** Low to Medium. Training the base model is straightforward using transfer learning. The technical complexity—and the impressiveness of the deliverable—lies in exporting the model via TensorFlow Lite or ONNX and wrapping it in a basic frontend (like a Streamlit app simulating a mobile interface) to prove edge capability.

18. Smart Grid Load Forecaster for Renewable Integration
- **Pitch:** A temporal forecasting dashboard that predicts hourly energy demand across a power grid, allowing utility operators to efficiently balance baseline load with intermittent renewable energy sources.
- **Problem:** As electrical grids integrate more solar and wind power, they become vulnerable to instability because renewable generation is weather-dependent. Utility companies and grid operators must accurately predict user demand to know exactly when to spin up expensive, carbon-heavy peaker plants to prevent blackouts.
- **Novelty:** Energy demand exhibits highly complex, overlapping seasonality (daily routines, weekly work cycles, yearly weather patterns). This project challenges the developer to master advanced feature engineering—incorporating external regressors like temperature and holiday schedules—to solve a critical climate-tech infrastructure problem.
- **Technique:** Hybrid forecasting utilizing Facebook's Prophet algorithm (excellent at modeling human seasonality and holidays) combined with an LSTM or XGBoost model trained on the residuals (the error left over by Prophet) to capture non-linear, short-term shocks. Evaluation strictly relies on Mean Absolute Error (MAE) and forecasting horizon stability (e.g., 24-hour vs 7-day accuracy decay).
- **Dataset:** The PJM Hourly Energy Consumption Data (Kaggle).

  - **PJM Grid Dataset Features:** Time-Series Relevance
  - **Scale:** Multi-year, hourly power consumption data
Segmented across several regional utility Granularity companies
Exhibits strong diurnal, weekly, and annual Seasonality consumption cycles
Can be easily joined with historical weather Exogenous Variables APIs

- **Risk:** Low. Time-series data of this nature is generally clean and structured. Utilizing well-documented libraries (like prophet and statsmodels) ensures that the modeling phase is swift, leaving ample time to build a robust interactive graphing interface for the demo app.

19. Synthetic Review Graph Anomaly Detector
- **Pitch:** An auditing API for marketplace platforms that models users and reviews as a complex network, utilizing graph mathematics to identify coordinated bot rings and fake review campaigns.
- **Problem:** E-commerce sites, restaurant directories, and app stores are plagued by "astroturfing"—coordinated groups of fake accounts paid to artificially inflate or maliciously tank product ratings. Simple NLP sentiment analysis cannot detect this, because a fake review often reads exactly like a real one. Trust and Safety teams need tools that analyze the behavioral connections between accounts.
- **Novelty:** This project shifts the paradigm from analyzing text (NLP) to analyzing topology (Graph Theory). By viewing the dataset as a network (Users connected to Products via Reviews), the AI identifies unnatural clustering— such as a group of 50 users who all mysteriously reviewed the exact same 5 obscure products on the same day.
- **Technique:** Graph Neural Networks (GNNs), specifically Graph Convolutional Networks (GCN) or GraphSAGE. The model generates node embeddings based on the structural properties of the network and flags nodes (users) that exhibit highly anomalous structural patterns. Evaluation metrics must include Precision, Recall, and the F1-score specifically isolated on the minority class (fraudsters).
- **Dataset:** The YelpChi Dataset.

  - **YelpChi Dataset Overview:** Graph Characteristics
  - **Domain:** Restaurant reviews from the Chicago area
Labels derived from Yelp's proprietary fraud Filtering Ground Truth detection algorithm
Contains necessary relational mapping (User Network Structure -> Review -> Entity)
Includes text, timestamps, and rating Feature Richness metadata for node features

- **Risk:** High. Graph Neural Networks have a steep learning curve. Constructing adjacency matrices and working with graph-specific libraries like PyTorch Geometric (PyG) or NetworkX is substantially more complex than standard tabular Pandas workflows, requiring dedicated theoretical study.

20. Visual Reverse Search & Recommendation Engine
- **Pitch:** A computer vision SaaS endpoint for e-commerce retailers that allows shoppers to upload a photo of a clothing item they saw on the street and instantly returns visually similar products from the retailer's inventory.
- **Problem:** Keyword search is highly inefficient for fashion and furniture. A user cannot easily type a query for "a slightly oversized, floral print, bohemian midi dress with bell sleeves." Visual search eliminates the friction of textual translation, driving massive conversion rate improvements for online fashion retailers and marketplaces.
- **Novelty:** Standard recommendation engines rely on collaborative filtering (e.g., "users who bought X also bought Y"). This system relies purely on content-based visual similarity, utilizing state-of-the-art contrastive learning and modern vector databases to perform sub-second nearest-neighbor image retrieval.
- **Technique:** Feature extraction utilizing a pre-trained Contrastive Language-Image Pretraining (CLIP) model or a ResNet-50 architecture with the classification head removed. The images are converted into dense vector embeddings and stored in a vector database (like Pinecone, Milvus, or FAISS). Evaluation focuses on retrieval metrics, specifically Mean Reciprocal Rank (MRR) and Recall@K.
- **Dataset:** The DeepFashion dataset, or the Amazon Berkeley Objects (ABO) dataset.

  - **Visual Dataset Utility:** Application to Embeddings
Hundreds of thousands of rich fashion DeepFashion Scale images
Bounding boxes, clothing landmarks, and Annotations detailed semantic attributes
High variance in lighting and pose, ideal for Embedding Space robust retrieval
Specifically designed for visual search and Task Alignment cross-domain retrieval

- **Risk:** Medium. The actual extraction of embeddings is fast using HuggingFace. The complexity lies in managing the Vector DB infrastructure, indexing hundreds of thousands of images, and building a frontend that can seamlessly handle image uploads, API requests, and gallery rendering within the strict 4-week timeline.

Works cited

1. Real-Time Road Damage Detection Using YOLOv8 - ASCE Library, https://ascelibrary.org/doi/10.1061/9780784486191.036
2. A multi‐national image dataset for automatic road damage detection, https://www.semanticscholar.org/paper/RDD2022%3A-A-multi %E2%80%90national-image-dataset-for-road-Arya-Maeda/ 844f8d0d8f34c8dd22d1ed6c0518677249882783
3. A multi-national image dataset for automatic Road Damage Detection, https://www.researchgate.net/publication/363668453_RDD2022_A_multi-national_image_dataset_for_automatic_Road_Damage_Detection
4. A multi-national image dataset for automatic Road Damage Detection, https://arxiv.org/abs/2209.08538
5. RDD2022 - Dataset Ninja, https://datasetninja.com/road-damage-detector

6. RDD2022 - The multi-national Road Damage Dataset released, https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547
7. Road Damage Detection Documentation | PDF - Scribd, https://www.scribd.com/document/1032994352/Road-Damage-Detection-Documentation
8. 2022 IEEE International Conference on Big Data, https://crddc2022.sekilab.global/
9. DiverseVul: A New Vulnerable Source Code Dataset for Deep, https://arxiv.org/pdf/2304.00409 10.DiverseVul: A Comprehensive Vulnerable Code Dataset for Deep, https://www.studocu.vn/vn/document/truong-dai-hoc-cong-nghe-thong-tin-dai-hoc-quoc-gia-thanh-pho-ho-chi-minh/machine-learning/diversevul-a-comprehensive-vulnerable-code-dataset-for-deep-learning-raid/127443098 11.DiverseVul: C/C++ Vulnerability Dataset - Emergent Mind, https://www.emergentmind.com/topics/diversevul-dataset 12.starsofchance/My_DiverseVul · Datasets at Hugging Face, https://huggingface.co/datasets/starsofchance/My_DiverseVul 13.A New Vulnerable Source Code Dataset for Deep Learning Based, https://surrealyz.github.io/files/pubs/raid23-diversevul.pdf 14.XSS attack detection using a DistilBERT-based hybrid DSCNN-GRU, https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13993/139933X/ XSS-attack-detection-using-a-DistilBERT-based-hybrid-DSCNN-GRU/ 10.1117/12.3092242.full 15.Injections Attacks Efficient and Secure Techniques Based on, https://www.techscience.com/cmc/v76n3/54357/html 16.XSS-Net: An Intelligent Machine Learning Model for Detecting Cross, https://sciencepg.com/article/10.11648/j.mlr.20251001.12 17.Log-based Intrusion Detection System using Machine Learning, https://norma.ncirl.ie/7363/1/soniafrancisjavior.pdf 18.Threat-Detection-System/Dataset at main · YashNawale26/Threat, https://github.com/YashNawale26/Threat-Detection-System/blob/main/Dataset 19.An Adaptive Rule-Based Engine for Application-Layer Security - MDPI, https://www.mdpi.com/2076-3417/16/11/5220 20.Web Application Vulnerability Detection Using Hybrid Algorithm, https://www.ijraset.com/research-paper/web-application-vulnerability-detection-using-hybrid-algorithm 21.Web Attack Threat Hunting Deep Dive & Lab | by Or Ben Ari | Medium, https://medium.com/@OrBenAri/web-attack-threat-hunting-deep-dive-lab-452d0e16a822 22.Framework For The Detection And Mitigation Of Web Vulnerabilities, https://www.demo.internationaljournalssrg.org/IJECE/2025/Volume12-Issue12/ IJECE-V12I12P114.pdf 23.MIMIC-IV-Ext Triage Instruction Corpus v1.0.0 - PhysioNet, https://physionet.org/content/mietic/

24.Daily Papers - Hugging Face, https://huggingface.co/papers?q=MIMIC-IV %20dataset 25.A Machine Learning Approach Using MIMIC–IV-ED Database, https://aisel.aisnet.org/cgi/viewcontent.cgi?article=1357&context=hicss-58 26.MIMIC-IV Dataset Overview - Emergent Mind, https://www.emergentmind.com/topics/mimic-iv-dataset 27.MIMIC-IV-ED v2.2 - PhysioNet, https://physionet.org/content/mimic-iv-ed/ 28.A repository of code used to analyse the MIMIC-IV-ED dataset - GitHub, https://github.com/cavalab/mimic-iv-ed-epi 29.abdullaharoon/mbert-roman-urdu-sentiment - Hugging Face, https://huggingface.co/abdullaharoon/mbert-roman-urdu-sentiment 30.Khubaib01/roman-urdu-sentiment-xlm-r - Hugging Face, https://huggingface.co/Khubaib01/roman-urdu-sentiment-xlm-r 31.Khubaib01/RomanUrdu-NLP-Sentiment-Corpus · Datasets at, https://huggingface.co/datasets/Khubaib01/RomanUrdu-NLP-Sentiment-Corpus 32.Khubaib01/roman-urdu-sentiment-embeddings · Datasets at, https://huggingface.co/datasets/Khubaib01/roman-urdu-sentiment-embeddings 33.ERUPD -- English to Roman Urdu Parallel Dataset - Hugging Face, https://huggingface.co/papers/2412.17562 34.SKU-110K Detection Dataset - Ultralytics YOLO, https://docs.ultralytics.com/datasets/detect/sku-110k 35.SoccerNet: A Scalable Dataset for Action Spotting in Soccer Videos, https://github.com/SilvioGiancola/SoccerNet-code 36.FAOSTAT Agriculture Data - Kaggle, https://www.kaggle.com/datasets/vijayveersingh/faostat-crops-and-livestock-data 37.Global Food & Agriculture Statistics - Kaggle, https://www.kaggle.com/datasets/unitednations/global-food-agriculture-statistics

---

## Perplexity

1. Crop leaf disease triage app for smallholder farmers
2. Insect pest identification assistant for agriculture extension workers
3. Roman Urdu spelling normalizer for Pakistani SME customer feedback
4. Spelling-aware Roman Urdu review intelligence dashboard
5. Roman Urdu fake review detector for e-commerce platforms
6. Urdu fake news triage tool for newsroom editors
7. Claim veracity triage system for fact-checkers
8. Audio deepfake detector for media authenticity verification
9. Pakistan Sign Language gesture recognizer for accessibility
10. Urdu ASR correction dashboard for content creators
11. Flood building damage assessor for disaster response teams
12. Road damage reporter for municipal infrastructure monitoring
13. Smart parking occupancy monitor for facility managers
14. Dengue case-trend surveillance dashboard for public health researchers
15. Student dropout early-warning system for university administrators
16. Short-answer auto-grader with feedback for educators
17. Food calorie estimator for nutrition tracking
18. Smart-meter anomaly triage tool for utility operators
19. Bitcoin transaction fraud graph detector for compliance analysts
20. Multilingual waste sorter for recycling operations

---

## DeepSeek

1. **Urdu Emergency Call Triage Assistant** — An NLP system that transcribes and prioritizes incoming Urdu emergency calls by urgency and incident type, routing them to the right response unit.
- **Problem:** Emergency dispatch centers in Pakistan (Rescue 1122, police) manually listen to thousands of calls daily; no automated triage means critical calls wait. For call operators and emergency response coordinators.
- **Novelty:** Existing emergency triage AI is English-centric; Urdu emergency call processing is virtually nonexistent despite Pakistan’s population size.
- **Technique:** Whisper fine-tuned on Urdu audio + a BERT-based multilingual classifier (mDeBERTa) for urgency classification and named entity recognition for location extraction.
- **Dataset:** Urdu Emergency Call Conversations Dataset (5,000 curated samples) on Hugging Face.
- **Risk:** Medium.

2. **Sindhi Sentiment Dashboard for Regional News** — A SaaS dashboard that tracks public sentiment across Sindhi-language news and social media, giving NGOs and local businesses a real-time pulse on regional opinion.
- **Problem:** Sindhi media outlets and development organizations have no sentiment analysis tools for the Sindhi language. For regional media analysts and NGO program managers.
- **Novelty:** Most sentiment tools support Urdu or Hindi but ignore Sindhi, a language with 30M+ speakers and almost no commercial NLP tooling.
- **Technique:** Fine-tuned XLM-RoBERTa or mBERT on Sindhi text for multi-class sentiment classification, with an optional aspect-based sentiment module.
- **Dataset:** Sindhi Sentiment Analysis Dataset (100K) on Hugging Face.
- **Risk:** Low.

3. **Sindhi Question-Answering Study Companion** — A web app where students ask questions in Sindhi about textbooks and get sourced answers, built for low-resource language education.
- **Problem:** Sindhi-medium students lack digital study aids because QA models are trained on English/Hindi. For Sindhi-speaking school and college students.
- **Novelty:** SdQuAD is one of the few QA datasets for Sindhi; building a RAG-based study assistant on top of it is a genuine first.
- **Technique:** Retrieval-Augmented Generation using LangChain with a multilingual embedding model (LaBSE or multilingual-e5) and a small LLM (Llama-3.2-3B) fine-tuned for Sindhi QA.
- **Dataset:** Sindhi Question-Answering Dataset (SdQuAD) — 15,065 context-question-answer pairs.
- **Risk:** Medium.

4. **Pakistani Traffic Anomaly Detector for Fleet Operators** — A CV system that flags unusual driving events (wrong-way driving, sudden braking, rickshaw swerving) from dashcam footage, tailored to Pakistan’s chaotic traffic.
- **Problem:** Logistics and ride-hailing companies in Pakistan have no automated way to review driver footage; existing dashcam AI is trained on Western road patterns. For fleet safety managers.
- **Novelty:** CARL-ODD is the first Asian-traffic benchmark; building an anomaly detection layer on top of it addresses a gap no Western product covers.
- **Technique:** YOLOv8 for vehicle detection + a temporal autoencoder or LSTM on tracked object trajectories to flag deviations from normal traffic flow patterns.
- **Dataset:** CARL-ODD (20,000 labeled images from 80+ Pakistani cities).
- **Risk:** High.

5. **Multi-Crop Disease Scanner for Pakistani Farmers** — A mobile-first SaaS that identifies 41 different leaf diseases across 12 crops from a smartphone photo, with treatment recommendations in Urdu.
- **Problem:** Smallholder farmers in KP and Punjab lose yield to late disease detection; extension services are stretched thin. For farmers, agri-input dealers, and crop insurance assessors.
- **Novelty:** Most crop disease models are trained on PlantVillage’s lab-controlled images; PlantCity captures real-field conditions with high-temperature stress symptoms.
- **Technique:** EfficientNet-B3 or ConvNeXt-Tiny fine-tuned for 52-class classification, with Grad-CAM explainability to show farmers which leaf region triggered the diagnosis.
- **Dataset:** PlantCity (10,667 high-resolution images, 52 classes, collected in Charsadda & Chitral).
- **Risk:** Low.

6. **Tomato Disease Early-Warning System for Punjab Greenhouses** — A computer-vision SaaS that monitors tomato leaf images uploaded by greenhouse workers and predicts disease outbreaks 3–5 days before visible symptoms escalate.
- **Problem:** Greenhouse tomato growers in Punjab face recurring blight and leaf mold outbreaks; early intervention saves entire harvests. For commercial greenhouse operators and agri-tech cooperatives.
- **Novelty:** Existing tomato disease classifiers are single-image diagnosis tools; a temporal early-warning system that tracks disease progression across uploaded images is rare.
- **Technique:** Vision Transformer (ViT-B/16) with a temporal attention module over sequences of leaf images from the same plant, trained to predict severity escalation.
- **Dataset:** Tomato Leaf Disease Classification Dataset in Pakistan (7,200 field-condition images, 6 classes).
- **Risk:** Medium.

7. **Urdu Legal Document NER for Law Firms** — A SaaS that extracts names, dates, case numbers, and legal entities from Urdu legal documents, saving paralegals hours of manual indexing.
- **Problem:** Pakistani law firms and courts work with Urdu legal texts but have no NER tools; manual indexing is error-prone and slow. For paralegals and court clerks.
- **Novelty:** Urdu legal NER is an almost untouched research area; existing Urdu NER models are trained on news, not legal register.
- **Technique:** Fine-tuned XLM-RoBERTa with a CRF layer for token classification, using a legal-domain Urdu NER corpus.
- **Dataset:** Needs synthetic/self-collected data — no public Urdu legal NER dataset exists; can be bootstrapped by annotating 500–1,000 sentences from public court judgments with AI-assisted pre-labeling.
- **Risk:** High.

8. **Kashmiri News Snippet Classifier for Media Monitoring** — A dashboard that automatically categorizes Kashmiri news snippets into topics (politics, conflict, economy, culture) for regional media analysts.
- **Problem:** Kashmiri-language media monitoring is manual; no automated topic classification exists. For regional news aggregators and policy researchers.
- **Novelty:** Kashmiri is extremely low-resource; this would be one of the first deployed topic classifiers for the language.
- **Technique:** Fine-tuned mBERT or XLM-R with a classification head, compared against a TF-IDF + SVM baseline to show transformer benefit.
- **Dataset:** Kashmiri News Snippet Classification Dataset (available on GitHub from the referenced study).
- **Risk:** Medium.

9. **Urdu Instruction-Tuning Playground for EdTech** — A SaaS platform where teachers create Urdu-language educational content by prompting a fine-tuned Urdu LLM, with an evaluation dashboard comparing model outputs.
- **Problem:** Urdu-medium teachers lack AI tools that understand Urdu pedagogical language; most LLMs are English-first. For school teachers and curriculum developers in Pakistan.
- **Novelty:** Khudi AI Dataset is the largest open Urdu instruction-tuning dataset; building a teacher-facing tool around it is novel.
- **Technique:** LoRA fine-tuning of Llama-3.2-3B or Qwen2.5-3B on Urdu instruction data, with RAG over a curriculum knowledge base.
- **Dataset:** Khudi AI Dataset (Urdu instruction-tuning, merged from 8+ Pakistani datasets).
- **Risk:** Medium.

10. **Water Pump Failure Predictor for Pakistani Tube Wells** — A time-series SaaS that predicts tube well pump failure 48 hours in advance using sensor data, helping farmers avoid crop loss from irrigation failure.
- **Problem:** Tube well failures during critical irrigation windows cause crop stress and yield loss; farmers have no predictive maintenance tools. For large-farm operators and irrigation cooperatives.
- **Novelty:** Predictive maintenance is well-developed for industrial machinery but almost absent for agricultural water infrastructure in South Asia.
- **Technique:** LSTM-based anomaly detection on multivariate sensor time series (vibration, current, flow rate) with a reconstruction-error threshold for failure alerting.
- **Dataset:** Needs synthetic/self-collected data — can generate realistic pump failure sequences using physics-based simulation (e.g., Simulink model of a centrifugal pump) or use NASA’s IMS bearing dataset as a proxy for vibration patterns.
- **Risk:** High.

11. **Low-Resource Language Flashcard Generator** — A SaaS that generates vocabulary flashcards with images and example sentences for Mizo, Khasi, and other low-resource languages, using NLP to ensure pedagogical quality.
- **Problem:** Language learners of Mizo/Khasi have no digital learning tools; teachers create materials manually. For language teachers and heritage-language learners.
- **Novelty:** No commercial flashcard app supports these languages; this combines low-resource NLP with a consumer learning product.
- **Technique:** Multilingual sentence embeddings (LaBSE) for example-sentence retrieval + a small diffusion model (Stable Diffusion fine-tuned on culturally relevant prompts) for image generation.
- **Dataset:** Mizo and Khasi POS/NER datasets (from the referenced ACL work) + Wiktionary scrape for vocabulary.
- **Risk:** Medium.

12. **Federated Wearable Stress Detector for Students** — A privacy-preserving app that detects academic stress patterns from smartphone and wearable data, without raw data leaving the device.
- **Problem:** University students in high-pressure programs face burnout; existing mental-health apps are English-centric and cloud-based, raising privacy concerns. For university counseling centers and student wellness programs.
- **Novelty:** Federated learning for student stress is rare; most wellness apps use centralized data collection, which students distrust.
- **Technique:** Federated Averaging (FedAvg) with a lightweight 1D-CNN or GRU on time-series data (heart rate variability, screen time, sleep patterns).
- **Dataset:** WESAD (wearable stress and affect detection) or K-EmoCon — both public multimodal physiological datasets; can be adapted for federated simulation.
- **Risk:** High.

13. **Bioacoustic Bird Monitor for Urban Biodiversity** — A SaaS that identifies bird species from audio recordings in Pakistani cities, giving urban planners biodiversity data without manual surveys.
- **Problem:** Urban biodiversity monitoring in Pakistan is manual and sparse; planners lack data on how green spaces affect bird populations. For municipal planners and environmental NGOs.
- **Novelty:** Bioacoustic monitoring is growing in Europe but almost absent in South Asia; local bird species are underrepresented in existing acoustic models.
- **Technique:** CNN on mel-spectrograms (e.g., EfficientNet-B0) fine-tuned for multi-label bird species classification, with data augmentation for urban noise.
- **Dataset:** Xeno-canto (global bird audio) filtered for South Asian species + self-collected urban recordings for fine-tuning.
- **Risk:** Medium.

14. **Explainable Loan Rejection Reasoner for Microfinance** — A SaaS that gives microfinance borrowers clear, explainable reasons for loan rejection, using SHAP and counterfactual explanations in Urdu.
- **Problem:** Microfinance borrowers in Pakistan often get rejected without understanding why; this creates distrust and prevents improvement. For microfinance institutions and borrowers.
- **Novelty:** Explainable AI (XAI) is mostly applied to Western credit scoring; applying it with Urdu-language counterfactual explanations for microfinance is novel.
- **Technique:** Gradient boosting (XGBoost/LightGBM) for default prediction + SHAP for feature attribution + DiCE (Diverse Counterfactual Explanations) for actionable feedback.
- **Dataset:** Lending Club (public) for model training + synthetic Pakistani microfinance data for regional adaptation.
- **Risk:** Medium.

15. **Sign Language Fingerspelling Translator for Urdu** — A CV app that translates Urdu Sign Language fingerspelling from a webcam into Urdu text in real time, built for deaf students and teachers.
- **Problem:** Deaf students in Pakistan lack digital sign-language tools; teachers cannot always understand fingerspelling. For special-education teachers and deaf students.
- **Novelty:** Urdu Sign Language is severely under-resourced; most sign-language AI focuses on ASL or BSL.
- **Technique:** MediaPipe hand landmark extraction + a lightweight LSTM or Temporal Convolutional Network for sequence classification of fingerspelling gestures.
- **Dataset:** Needs synthetic/self-collected data — can collect 26 Urdu alphabet signs from 5– 10 volunteers in week 1, using MediaPipe to extract landmarks for training.
- **Risk:** Medium.

16. **Crop Yield Forecaster for Climate-Stressed Regions** — A dashboard that predicts wheat and rice yields at the district level in Pakistan using satellite imagery and weather data, helping agri-lenders and insurers.
- **Problem:** Agricultural lenders and crop insurers lack granular yield forecasts for climate-vulnerable districts in Punjab and Sindh. For agri-finance analysts and insurance underwriters.
- **Novelty:** Most yield prediction models focus on US/EU agriculture; South Asian smallholder systems with monsoon variability are underserved.
- **Technique:** 3D-CNN or ConvLSTM on Sentinel-2 NDVI time series + Random Forest on weather features, with spatial cross-validation to avoid leakage.
- **Dataset:** Sentinel-2 imagery (free via Copernicus) + Pakistan Bureau of Statistics district-level yield data (public) + NASA POWER weather data.
- **Risk:** High.

17. **Waste Sorting Assistant for Pakistani Municipalities** — A CV-powered app that classifies waste into recyclable, organic, and hazardous categories from a photo, designed for municipal waste workers.
- **Problem:** Pakistani municipalities lack automated waste sorting; workers manually separate waste with low accuracy. For municipal waste management departments.
- **Novelty:** Waste classification models are trained on Western waste streams (e.g., TrashNet); Pakistani waste composition (more organic, different packaging) is different.
- **Technique:** EfficientNet or MobileNetV3 fine-tuned on local waste images, with test-time augmentation for robustness to lighting variation.
- **Dataset:** TrashNet (public baseline) + self-collected local waste images (can collect 500– 1,000 images in week 1 from local waste facilities or campus).
- **Risk:** Low.

18. **Pakistani Bias Benchmark for QA Systems** — A SaaS evaluation tool that tests LLMs and QA systems for cultural and regional bias against Pakistani contexts, using PakBBQ.
- **Problem:** AI companies deploying models in Pakistan have no benchmark to test for cultural bias; they use Western benchmarks that miss local nuances. For AI product managers and ethics reviewers.
- **Novelty:** PakBBQ is culturally adapted bias benchmark; building a SaaS around it is a genuine first for the region.
- **Technique:** Evaluate LLM outputs against PakBBQ’s 17,180 QA pairs across 8 bias dimensions; use statistical bias metrics (e.g., stereotype score, unknown rate) to produce a bias report.
- **Dataset:** PakBBQ (214 templates, 17,180 QA pairs in English and Urdu).
- **Risk:** Low.

19. **Music Genre Classifier for South Asian Instruments** — A SaaS that identifies South Asian instruments (sitar, tabla, harmonium, etc.) from audio clips, built for music educators and ethnomusicology researchers.
- **Problem:** Music education platforms in South Asia lack instrument recognition tools; existing models recognize Western instruments only. For music teachers and streaming platforms.
- **Novelty:** South Asian instrument classification is a niche with almost no public datasets or models; this fills a gap for regional music education.
- **Technique:** CNN on MFCC or mel-spectrogram features (VGGish pre-trained embeddings + fine-tuned classifier).
- **Dataset:** Needs synthetic/self-collected data — can use YouTube audio from Creative Commons South Asian music (500–1,000 clips per instrument) + Freesound for augmenting.
- **Risk:** High.

20. **Urdu Readability Scorer for Educational Content** — A SaaS that scores Urdu text on readability for different grade levels, helping textbook publishers and edtech companies match content to student reading ability.
- **Problem:** Urdu textbook publishers and edtech platforms have no automated way to check if content is appropriate for a grade level. For curriculum designers and edtech content managers.
- **Novelty:** Readability formulas exist for English (Flesch-Kincaid) but not for Urdu; this would be the first Urdu readability tool.
- **Technique:** Fine-tuned XLM-RoBERTa regression model predicting grade-level readability from text features (vocabulary complexity, sentence length, semantic coherence).
- **Dataset:** Needs synthetic/self-collected data — can use Pakistan Textbook Board Urdu textbooks for grades 1–12 as labeled data (grade level = label), supplemented by AI-generated text at controlled difficulty levels.
- **Risk:** Medium.

---

## Kimi

1. **Dengue Early-Warning Dashboard**
- **Pitch:** 2–4 week ahead dengue outbreak risk forecaster for Pakistani cities, packaged as a public-health dashboard.
- **Problem:** Municipal health departments and hospitals get blindsided by seasonal dengue spikes; a lead time even in weeks helps prep fogging and beds.
- **Novelty:** Existing tools are global research demos; a city-level, explainable (SHAP) risk map for South Asian cities with a "what drives this spike" panel is underserved.
- **Technique:** Gradient-boosted trees (XGBoost/LightGBM) + lag-feature time-series engineering, with SHAP explainability; compare vs. seasonal-naive and ARIMA baselines.
- **Dataset:** DengAI (DrivenData/Iquitos+San Juan benchmark) for the pipeline + Pakistan dengue case series published on Kaggle/Punjab health dashboards.
- **Risk:** Medium.

2. **Lahore Air-Quality Nowcaster**
- **Pitch:** Predict next-24-hour AQI from a few monitors + weather, instead of just showing current readings.
- **Problem:** Residents and schools make outdoor decisions on stale readings; AQI nowcasting barely exists for Pakistani cities.
- **Novelty:** AirVisual-style apps show current/historical only; a hyperlocal, weather-conditioned forecast for smog season (Oct–Jan) is a real gap.
- **Technique:** Multivariate time-series forecasting — compare LSTM/Temporal CNN vs. XGBoost with rolling windows; report MAE by horizon.
- **Dataset:** OpenAQ (free API, historical Lahore PM2.5) + Open-Meteo historical weather (free API, no scraping).
- **Risk:** Low.

3. **Deepfake-Audio Detector for Newsrooms**
- **Pitch:** Upload an audio clip → get a "synthetic vs. genuine" verdict with confidence, aimed at journalists verifying voice notes.
- **Problem:** WhatsApp-era misinformation spreads via fabricated voice clips; newsrooms have no cheap tool for this.
- **Novelty:** Deepfake *video* detectors are common; a lightweight audio-only verification tool with a newsroom workflow is underserved.
- **Technique:** LFCC/MFCC feature extraction → deep classifier (small CNN or AASIST-style spoofing detector); report EER and AUC.
- **Dataset:** ASVspoof 2021 (large, public, purpose-built for synthetic speech detection).
- **Risk:** Medium.

4. **Roman Urdu Code-Mixed Toxicity Moderator**
- **Pitch:** API + dashboard that flags abusive/religious-hate/sexist content in Roman Urdu comments for local platforms and pages.
- **Problem:** Facebook groups, news-site comments, and local apps in Pakistan are flooded with Roman Urdu abuse that English-only moderation tools completely miss.
- **Novelty:** Low-resource language, sparse tooling; most moderation startups target English only.
- **Technique:** Fine-tuned multilingual transformer (XLM-R / mBERT) vs. character-CNN baseline, multi-class with macro-F1 comparison and error analysis on code-switching.
- **Dataset:** RUHSOLD — 10,012 annotated Roman Urdu tweets with coarse + fine-grained labels, publicly available via the EMNLP 2020 paper.
- **Risk:** Low.

5. **Urdu Lecture-to-Notes Engine**
- **Pitch:** Upload an Urdu lecture recording → get transcript, speaker segments, and auto-generated structured notes/quiz.
- **Problem:** Students in Urdu-medium institutions lack the Otter.ai-style tooling English students have.
- **Novelty:** Low-resource ASR + diarization combined into a study-productivity SaaS; nobody productizes this for Urdu.
- **Technique:** Fine-tune Whisper-small on Urdu (transfer learning), pyannote-style speaker diarization, then LLM-based note structuring; evaluate WER before/after fine-tuning.
- **Dataset:** Mozilla Common Voice (Urdu subset) for fine-tuning; short self-recorded lectures for the demo.
- **Risk:** Medium-High (compute time is the main gamble).

6. **Exam Question Difficulty Predictor + Practice-Exam Generator**
- **Pitch:** Feed in past board-exam papers → model predicts each question's difficulty/topic and assembles balanced mock papers.
- **Problem:** Teachers and academies hand-assemble practice exams; poorly calibrated papers waste student prep time.
- **Novelty:** Difficulty calibration from historical exam performance is a real edtech gap; generator + calibration loop is fresh.
- **Technique:** Feature-based + transformer text classifier for difficulty/topic; IRT (Item Response Theory) as the statistical backbone; measure with accuracy and a calibration curve.
- **Dataset:** Needs self-collected data — past 5–8 years of SSC/HSSC papers (freely available PDFs) with difficulty labels inferred from marking-scheme rubric, ~a few hundred questions, light manual tagging.
- **Risk:** Medium-High (data curation is the bottleneck, not the model).

7. **Freelancer Contract Risk Scanner**
- **Pitch:** Paste a client contract → highlights risky clauses (IP grab, non-compete, payment traps) in plain English for freelancers.
- **Problem:** Individual freelancers sign abusive contracts they can't afford a lawyer to review.
- **Novelty:** Legal-tech AI targets enterprises; a clause-level risk product for gig workers is underserved.
- **Technique:** Sequence labeling (BERT/BioBERT-style fine-tune) for clause extraction + clause-level risk classification; report span-level F1 on low-resource contract subsets.
- **Dataset:** CUAD (Contract Understanding Atticus Dataset — 510 contracts, ~13,000 clause annotations, public).
- **Risk:** Medium.

8. **Fake-Review Radar for Small Restaurants**
- **Pitch:** Dashboard where a restaurant owner pastes their review feed and gets suspicious-review flags with reasons.
- **Problem:** Small businesses get brigaded by fake reviews and have no way to evidence it to platforms.
- **Novelty:** Review fraud research exists, but almost no SMB-facing product with explanation ("burst of 5-star reviews from new accounts").
- **Technique:** Graph-based fraud detection (GNN or spatiotemporal features à la SpEagle) + text classifier ensemble; precision/recall on filtered vs. organic reviews.
- **Dataset:** YelpChi (Yelp filtered-review dataset with ground-truth fake labels).
- **Risk:** Low-Medium.

9. **Ramadan-Season Expiry & Waste Forecaster for Small Grocers**
- **Pitch:** Kirana-store SaaS that forecasts per-SKU demand around Ramadan/Eid and flags what will expire before it sells.
- **Problem:** Small shops overstock perishables before Ramadan and dump huge waste after Eid; margins are thin.
- **Novelty:** Demand forecasting is built for Walmart-scale data; a tiny-data, seasonality-aware version for informal retailers is underserved.
- **Technique:** Hierarchical/grouped time-series forecasting (LightGBM with calendar features vs. Prophet baseline); report WAPE/MAE per SKU group.
- **Dataset:** UCI "Online Retail" (transaction-level, ~500k rows) for the pipeline + honestly-labeled synthetic Ramadan demand overlay for the demo.
- **Risk:** Low.

10. **PR Risk Scorer (Risky-Commit Prediction)**
- **Pitch:** Analyzes a pull request's diff and metadata → flags "high-risk, needs senior review" before merge.
- **Problem:** Junior-heavy teams waste senior review time on safe PRs while risky ones slip through.
- **Novelty:** Commercial "AI code review" tools focus on style; defect-risk triage grounded in defect-prediction research is under-productized.
- **Technique:** Just-in-time defect prediction — code-change features (lines changed, entropy, history) + diff embeddings via CodeBERT; logistic regression baseline vs. deep model, report AUC/cost-effectiveness (top-20% recall).
- **Dataset:** ApacheJIT (public Apache project commit-level defect datasets from JIT-defect-prediction research).
- **Risk:** Medium.

11. **Bug-Severity Triage Bot**
- **Pitch:** Ingests incoming bug reports → routes severity and suggests assignee team, cutting triage meetings.
- **Problem:** Maintainers of mid-size OSS/commercial projects drown in untriaged issues.
- **Novelty:** Auto-labeling exists for spam; *severity + assignment* with calibration is a workflow tool, not a toy.
- **Technique:** Fine-tuned transformer multi-label classifier (severity) + a kNN/embedding retriever for duplicate detection; report macro-F1 and duplicate-retrieval hit@5.
- **Dataset:** Public Mozilla/Eclipse bug-report datasets (long-standing, downloadable from MSR/promise repositories).
- **Risk:** Medium.

12. **Meal Macro Estimator from One Photo**
- **Pitch:** Snap a photo of your plate → estimated calories and macros with portion sizing.
- **Problem:** Manual food logging is tedious and inaccurate; existing calorie apps are database-lookup based.
- **Novelty:** Direct multi-task regression from a single RGB image (no barcode/menu lookup) is still a genuine research problem with a clear product form.
- **Technique:** Multi-task CNN/ViT regression (EfficientNet/Inception backbone) predicting calories, mass, carbs, fat, protein simultaneously; report MAE per output, compare architectures. Nutrition5k provides ~5,000 meals with images + per-ingredient macro labels, and prior work shows a CNN trained on it can beat professional nutritionists at calorie estimation.
- **Dataset:** Nutrition5k (+ Food-101 for pretraining).
- **Risk:** Medium-High.

13. **Distribution-Loss / Electricity-Theft Anomaly Detector**
- **Pitch:** Flags feeders/meters with suspicious loss patterns to prioritize inspection for a distribution company.
- **Problem:** Non-technical losses (theft + metering failure) drain Pakistani DISCOs and drive load-shedding; inspection teams have no triage tool.
- **Novelty:** NTL detection papers exist, but there's no accessible regional product; inspection-prioritization framing is practical and defensible.
- **Technique:** Unsupervised anomaly detection (Isolation Forest / autoencoder) on feeder-level load time series; deliberately inject synthetic theft patterns into honest baseload to evaluate recall@inspection-budget.
- **Dataset:** Needs synthetic/self-collected data — honest baseline from UCI household/load datasets or public transmission data, with theft scenarios simulated per published literature distributions; say so openly in the report.
- **Risk:** Medium (data realism is the risk; mitigate with clearly documented simulation).

14. **Case-Law Plain-Language Summarizer**
- **Pitch:** Puts in a court judgment → returns a structured plain-English summary (who, what, ruling, reasoning) for journalists and students.
- **Problem:** Legal reporting and public understanding suffer because judgments are long and dense.
- **Novelty:** Legal AI is contract/enterprise focused; public-interest, plain-language judgment summarization with faithfulness evaluation is underserved.
- **Technique:** Long-document abstractive summarization (LongT5/LED fine-tune); evaluate with ROUGE + a human-style faithfulness checklist and comparison against extractive baseline.
- **Dataset:** CourtListener/Case Law Access Project bulk corpus (millions of public US judgments; open download).
- **Risk:** Medium.

15. **CS Skills-Gap Analyzer**
- **Pitch:** Compares a university's CS curriculum against current job-market demands and shows a per-course gap map for program heads.
- **Problem:** Universities update syllabi slowly; graduates learn outdated stacks and can't see the disconnect.
- **Novelty:** Skills taxonomies exist for recruiters; a curriculum-vs-market mapping product aimed at program administrators is unusual.
- **Technique:** NER/skill extraction (fine-tuned token classifier over job posts) + skill taxonomy embedding clustering + cosine similarity gap scoring; evaluate extraction F1 against a hand-labeled sample.
- **Dataset:** Large public tech job-postings datasets on Kaggle + 5–6 CS curricula copied by hand (light, not scraping-heavy).
- **Risk:** Medium.

16. **Typosquat & Phishing-Domain Monitor for Regional Fintech**
- **Pitch:** Watches for newly registered lookalike domains of banks/mobile-wallets (JazzCash/Easypaisa-style) and scores phishing risk.
- **Problem:** Phishing via SMS'd lookalike domains is rampant in emerging markets; brands learn about it from victims.
- **Novelty:** Brand-protection suites are enterprise-priced; a narrow, cheap monitor for regional banks/wallets is a real gap.
- **Technique:** URL lexical features + TF-IDF/fastText on HTML + WHOIS features → gradient-boosted classifier; report precision at high-recall operating point, plus edit-distance domain generation for the watchlist.
- **Dataset:** UCI "Phishing Websites" dataset + a PhishTank dump (freely downloadable).
- **Risk:** Low-Medium.

17. **Satellite Crop-Type Mapper for District Agriculture**
- **Pitch:** Classifies Sentinel-2 satellite tiles into crop types for a district, giving agriculture departments a cheap survey substitute.
- **Problem:** Crop surveys are manual, slow, and political; honest acreage data is a chronic problem.
- **Novelty:** Precision-ag platforms sell to industrial farms; district/state-level public monitoring with a simple web map is underserved.
- **Technique:** Multispectral (13-band Sentinel-2) CNN classification — 2D-CNN vs. temporal-ConvLSTM over the growing season; report per-class F1 and confusion between spectrally similar crops.
- **Dataset:** EuroSAT (Sentinel-2, 10 land-cover classes, public) for training, optionally CropHarvest for generalization tests.
- **Risk:** Medium-High.

18. **Flood-Extent Mapping from Satellite Radar**
- **Pitch:** Upload Sentinel-1 SAR images before/during a flood → outputs a water-extent map for NGOs and disaster cells.
- **Problem:** Flood response needs extent maps fast; cloud cover blocks optical satellites during monsoon — radar works at night and through clouds.
- **Novelty:** Disaster-mapping is done by big agencies; a lightweight tool for local NGOs/universities is underserved.
- **Technique:** Semantic segmentation (U-Net/DeepLabV3+) on SAR backscatter; report IoU/Dice on held-out flood events vs. thresholding baseline.
- **Dataset:** Sen1Floods11 (public global Sentinel-1 flood dataset with pixel-level water labels).
- **Risk:** Medium-High.

19. **Student-Dropout Early-Warning Advisor Dashboard**
- **Pitch:** Flags students at risk of dropping out in the first two semesters with interpretable reasons (attendance, grades, demographics) for advisors.
- **Problem:** Advisors with hundreds of students can't spot who needs intervention early.
- **Novelty:** Not novel academically — the fresh angle is an advisor-workflow product: what-to-do-next recommendations + fairness audit (does the model penalize low-income or rural students?). The fairness evaluation makes it report-worthy.
- **Technique:** Tabular classification (XGBoost vs. logistic baseline) with SHAP explanations + demographic parity / equalized-odds audit.
- **Dataset:** UCI "Predict Students' Dropout and Academic Success" (~4,400 students, real Portuguese higher-ed data, semester-level features).
- **Risk:** Low.

20. **Campus Lost-and-Found Visual Matcher**
- **Pitch:** Students upload a photo/description of a lost item or found item; CLIP embeddings + vector DB semantically match "black AirPods case with a scratch" to the found-object shelf.
- **Problem:** University lost-and-found is a shoebox of unmatched items; textual matching fails because people describe the same object differently.
- **Novelty:** Nobody builds for this micro-problem; it's a genuinely uncommon, demo-able SaaS with real users you can recruit on day one.
- **Technique:** OpenCLIP image+text dual embeddings, cosine similarity via a vector database (pgvector/Qdrant), optional zero-shot attribute extraction; evaluate retrieval Recall@K on a self-built test set of 50–100 items, zero-shot vs. fine-tuned.
- **Dataset:** Needs synthetic/self-collected data — demo items photographed on campus; evaluation set built the same way (100 items is a manageable afternoon, not thousands of labels).
- **Risk:** Low.

---

## Qwen

**1. DocAudit — Financial-Statement-to-XBRL Reconciliation Copilot**
- **Pitch:** An audit assistant that reads PDF financial statements and cross-checks every figure against the company's XBRL regulatory filing, flagging mismatches with evidence highlights.
- **Problem:** Audit juniors and financial analysts manually re-verify figures across hundreds of annual-report pages; transcription errors and filing inconsistencies surface late and cost dearly.
- **Novelty:** Table-extraction demos are everywhere; *cross-document numeric reconciliation* (PDF ↔ XBRL, tolerance rules, discrepancy explanations) is a workflow only big-4 internal tooling has.
- **Technique:** Layout-aware transformer (LayoutLMv3 or Donut) fine-tuned for table detection + structure recognition; numeric-cell alignment (edit distance over table grids); ablate vs Tesseract+regex. Eval: table F1, numeric-match precision/recall.
- **Dataset:** SEC EDGAR full-text filings + XBRL Financial Statement Data Sets (public); PubTabNet / FinTabNet for the table component.
- **Risk:** Medium

**2. RiskLens — Contract Clause Risk Triage for SMBs**
- **Pitch:** Upload a vendor contract; get risky clauses (auto-renewal, unlimited liability, broad indemnity) highlighted, explained in plain language, and scored against market norms.
- **Problem:** Small businesses, freelancers, and startup ops teams sign contracts without legal review; mid-size legal teams drown in low-stakes NDAs/MSAs.
- **Novelty:** "Chat with your PDF" is saturated; *trained clause-span detection* with per-clause-type metrics and a defensible risk taxonomy (not LLM vibes) is not.
- **Technique:** Long-document transformers (Longformer/BigBird) fine-tuned for span-level clause classification + RAG explanation grounded only in retrieved spans. Ablation: RAG-only vs fine-tuned vs hybrid; eval: clause-level P/R/F1, explanation-faithfulness audit.
- **Dataset:** CUAD (Atticus Project, 510 contracts) + LEDGAR (~80K labeled clauses from SEC filings), both public.
- **Risk:** Medium

**3. PIIShield — Personal Data Inventory for DPDP/GDPR Compliance**
- **Pitch:** Scans documents, exports, and DB dumps to detect and classify PII, then auto-generates a compliance-ready data map of "what personal data we hold, where."
- **Problem:** Compliance officers at small/Indian enterprises must answer DPDP Act and GDPR data-inventory questions that are today manual spreadsheet exercises.
- **Novelty:** Most PII demos run one English NER model; multi-format (text + tabular + semi-structured) inventory with entity-type metrics and schema inference is an underserved product surface.
- **Technique:** Fine-tuned RoBERTa/DeBERTa NER + rule/regex ensemble + embedding clustering for column-type inference. Eval: entity F1 per type vs Microsoft Presidio baseline; false-negative cost analysis.
- **Dataset:** AI4Privacy (HuggingFace), Enron Email Corpus, TabPrivacy — all public.
- **Risk:** Low

**4. LogSense — Log Parsing + Incident Narration for Small SRE Teams**
- **Pitch:** Ingests application logs, auto-discovers log templates, flags anomalous sequences, and drafts a "what likely happened" incident summary grounded in parsed events.
- **Problem:** Small SaaS ops teams drown in unstructured logs; commercial platforms assume you already know what to query.
- **Novelty:** Log parsing is well-studied but rarely packaged; differentiator is sequence-level anomaly detection + LLM narration with explicit *hallucination checking against parsed templates*.
- **Technique:** Drain3 streaming parser → template-token sequences → Transformer/LSTM anomaly scorer; LLM summary constrained to retrieved events. Eval: parsing accuracy vs ground-truth templates, F1 without point-adjustment gaming, precision@k on injected faults.
- **Dataset:** Loghub / Loghub-2.0 (HDFS, BGL, Thunderbird — labeled, public).
- **Risk:** Low

**5. GridGuard — Electricity Consumption Anomaly & Theft Screening**
- **Pitch:** Flags anomalous household consumption patterns consistent with meter tampering and ranks them for field inspection crews.
- **Problem:** Power distribution utilities (acute for Indian DISCOMs) lose revenue to theft; physical inspections are random and expensive.
- **Novelty:** Published work chases tabular AUC; a cost-aware *inspection-ranking* framing (precision@k under crew budget) plus honest treatment of label limitations is fresher and more report-worthy.
- **Technique:** Autoencoder/Transformer reconstruction on consumption series + gradient boosting on engineered features; conformal thresholds. Eval: ROC-AUC, PR-AUC, cost-weighted precision@k vs baselines.
- **Dataset:** Pecan Street Dataport (free academic license) or UCI Individual Household Electric Power Consumption; theft labels are **synthetic/self-injected** — no public labeled theft data exists; say so in the report.
- **Risk:** Medium

**6. MandiPulse — Mandi Price & Arrival Forecasting for Farmer Producer Orgs**
- **Pitch:** Forecasts weekly mandi prices and arrivals per district-commodity with uncertainty bands and sell-now/hold advisories for FPOs and small traders.
- **Problem:** Indian FPOs and small agri-traders decide when/where to sell with zero forecasting support; cross-mandi price gaps are exploitable but invisible without tooling.
- **Novelty:** Price-prediction papers are common but never productized with *quantile forecasts + spatial transfer* (predicting thin-data mandis from similar ones) plus a working advisory layer.
- **Technique:** Global deep time-series model (TFT/DeepAR/N-BEATS) with mandi-commodity embeddings vs per-series ETS/ARIMA and GBM baselines. Eval: MASE, sMAPE, pinball loss, slice analysis on low-volume mandis.
- **Dataset:** AgmarkNet daily mandi prices (public bulk CSVs via data.gov.in) + Open-Meteo historical weather API.
- **Risk:** Medium

**7. WardWatch — Civic Complaint Routing, Dedup & SLA Prediction**
- **Pitch:** A municipal complaint-intake layer that classifies, deduplicates, routes to the right department, and predicts resolution time per ticket.
- **Problem:** City corporations receive complaints via WhatsApp/social/portal; manual triage misroutes a large fraction and duplicates corrupt SLA statistics.
- **Novelty:** US 311 classification is a homework cliché; combining *semantic dedup + multi-label routing + survival-analysis SLA prediction* into one civic SaaS (n8n ingestion → queue dashboards) is not.
- **Technique:** SetFit/sentence-BERT embeddings + prototype/kNN routing; dedup via blocking + cross-encoder reranking; discrete-time survival model (Cox/GBM). Eval: routing macro-F1, dedup pairwise F1, survival C-index.
- **Dataset:** NYC 311 Service Requests or Chicago 311 (public, millions of labeled rows).
- **Risk:** Low

**8. ExamCoach — Question Bank Quality Auditor for Test-Prep**
- **Pitch:** Scans a coaching question bank for flaws — ambiguous MCQs, near-duplicate variants, suspect answer keys — and auto-tags topic/difficulty.
- **Problem:** Indian test-prep (JEE/NEET/UPSC/boards) publishers maintain huge banks with real error rates; teachers and students lose trust and time on broken questions.
- **Novelty:** Question *generation* is saturated; question *QA* (flaw detection) is unglamorous, real, and nearly untouched at student scale.
- **Technique:** Embedding similarity + MinHash blocking for near-dupes; cross-encoder validity classifier trained on controlled perturbations (shuffled keys, negated stems, removed constraints); zero-shot → fine-tuned topic tagging. Eval: dup-detection P/R, flaw-classification F1 per perturbation type.
- **Dataset:** AI2 Science Questions with Rich Context (public) + AR-Questions; flaw labels **synthetic (self-generated via controlled perturbations)** — honest and defensible.
- **Risk:** Medium

**9. OERadar — Early Struggle Detection in Online Courses (Privacy-First)**
- **Pitch:** A drop-in analytics layer for Moodle-style LMSs that predicts struggling/dropping students weeks in advance from clickstream, with per-student explanations for instructors.
- **Problem:** MOOCs and hybrid coaching programs see brutal dropout rates; interventions currently arrive after failure. Institutions want on-prem, non-invasive analytics.
- **Novelty:** Student-performance-prediction literature mostly uses toy grade tables; modeling *sessionized clickstream sequences* with SHAP explanations and lead-time metrics is underserved.
- **Technique:** Transformer/LSTM over event sequences → student-state embeddings → GBM hybrid; SHAP attributions. Eval: AUC, F1, early-warning lead time (weeks before dropout) vs static-feature baseline.
- **Dataset:** Open University Learning Analytics Dataset (OULAD, free) and/or ASSISTments 2012.
- **Risk:** Low

**10. PitchMirror — Pitch Deck Feedback Engine for First-Time Founders**
- **Pitch:** Upload a pitch deck; get rubric-based scoring on narrative, market-sizing logic, and slide clarity, benchmarked against funded decks, with concrete rewrite suggestions.
- **Problem:** First-time founders outside startup hubs get no structured feedback; accelerators can only deeply review a fraction of applications.
- **Novelty:** "Chat with your deck" exists; a *rubric-scored evaluator validated against human ratings* (inter-rater agreement + Spearman correlation in the report) is a defensible research-product hybrid, not a wrapper.
- **Technique:** Slide parsing (python-pptx + layout-aware vision model for charts), ordinal regression/fine-tuned classifier per rubric criterion, LLM rewrites grounded in low-scoring criteria. Eval: correlation with human rubric scores, per-criterion reliability.
- **Dataset:** **Self-collected:** public Y Combinator Demo Day decks (~1K) + your own ~200-deck human rubric annotations (no clean labeled public deck dataset exists — be honest).
- **Risk:** Medium

**11. MemeForensics — Out-of-Context Image Misinformation Detection**
- **Pitch:** Flags social images whose caption re-contextualizes a real photo to mislead, showing fact-checkers the evidence behind the verdict.
- **Problem:** Newsrooms and platform trust teams drown in out-of-context imagery during elections/disasters; manual reverse-image search doesn't scale.
- **Novelty:** Deepfake detection is saturated; *out-of-context* detection (real photo + false framing) is newer, genuinely multimodal, and has an established benchmark most students ignore.
- **Technique:** CLIP image/text encoders + cross-attention fusion head, fine-tuned with contrastive objectives. Ablations: unimodal vs naive concat vs cross-attention. Eval: accuracy/F1 vs published baselines.
- **Dataset:** NewsCLIPpings (public, ~78K images with generated out-of-context captions).
- **Risk:** Medium

**12. CodeMender — Vulnerability Triage + Verified Patch Suggestion**
- **Pitch:** Scans a repo, ranks security findings by "will a human actually fix this," and proposes a tested patch per finding — a Semgrep-sized tool for student/startup codebases.
- **Problem:** Small dev teams drown in scanner noise and lack security expertise to fix true positives; ignoring alerts is the default behavior.
- **Novelty:** SAST and AI-patching exist separately; the contribution is the *triage-ranking + verified-patch* loop evaluated on real CVEs, not just detection AUC.
- **Technique:** Fine-tuned CodeBERT/GraphCodeBERT on function+context features for detection ranking (optional GNN over code-property graphs if time permits); constrained LLM patch generation validated by tests. Eval: P/R on labeled vulns, ranking metrics, patch compile/pass rate.
- **Dataset:** BigVul / Devign / Project KB (SAP) — public; Juliet Test Suite for controlled baselines.
- **Risk:** High (GNN training can stall; CodeBERT-feature fallback keeps it feasible)

**13. BotNetBuster — Explainable Intrusion Detection for Campus/SME LANs**
- **Pitch:** A deployable NIDS that detects intrusion/botnet/IoT-malware traffic on a local network and explains *why* each alert fired in plain language.
- **Problem:** Colleges and small businesses have no SOC; commodity IDS produce unexplained alerts nobody acts on.
- **Novelty:** NIDS classification is crowded — the fresh part is *calibrated uncertainty (conformal prediction) + feature attributions + cross-year drift evaluation* (train on 2017 captures, test on 2023) that honestly exposes fragility. Excellent report material.
- **Technique:** 1D-CNN or Transformer over flow statistics vs GBM baselines; conformal prediction sets. Eval: PR-AUC on rare classes, calibration curves, cross-dataset generalization gap.
- **Dataset:** CIC-IDS2017, UNSW-NB15, CICIoT2023 (all public).
- **Risk:** Low

**14. VoiceGrade — Pronunciation Feedback for Non-Native English Speakers**
- **Pitch:** Speak a sentence; get phoneme-level accuracy, fluency, and stress scores with exact "fix this sound here" feedback — for Indian English speakers prepping for interviews/BPO work.
- **Problem:** Accent/soft-skills training is a huge South Asian BPO and edtech market; human trainers don't scale and consumer speech apps target US kids.
- **Novelty:** Pronunciation scoring is locked inside commercial apps; an open, *expert-score-correlated* phoneme-level system on non-native speech is publishable and productizable — and it's skills feedback, so no medical-claim landmine.
- **Technique:** Forced alignment (wav2vec2-based) → phone posteriorgrams → Goodness-of-Pronunciation scoring + regression heads to expert scores; optional fine-tuned self-supervised speech encoder. Eval: Pearson/Spearman vs expert scores, phoneme-level AUC.
- **Dataset:** speechocean762 (OpenSLR 101 — free, 5K non-native English sentences with expert pronunciation scores); optional L2-ARCTIC.
- **Risk:** Medium (alignment tooling is fiddly)

**15. HinglishDesk — Code-Mixed Support Triage for Bharat Customers**
- **Pitch:** Understands Hinglish/code-mixed customer messages (roman-script Hindi+English), classifies intent/sentiment, routes tickets, and drafts replies in the customer's own register.
- **Problem:** Brands serving tier-2/3 Indian customers receive support chats in romanized code-mixed Hindi that English-trained NLP misclassifies badly.
- **Novelty:** Most Indic NLP targets Devanagari; a single pipeline doing *language-ID → script normalization (transliteration) → intent/sentiment* on romanized code-mixed text is genuinely underserved, with clean modular-vs-end-to-end ablations.
- **Technique:** Char-n-gram/fastText language ID; seq2seq transliteration fine-tuned on Aksharantar; intent+sentiment via fine-tuned MuRIL/IndicBERT. Eval: per-stage and end-to-end F1 vs English-only and LLM-prompting baselines.
- **Dataset:** Dravidian-CodeMix / HASOC Hinglish shared-task data (public), MASSIVE (includes hi-IN, ta-IN, te-IN, kn-IN, ml-IN), Aksharantar (AI4Bharat, 26M pairs).
- **Risk:** Medium

**16. LedgerLens — Spreadsheet Risk Auditor for Financial Models**
- **Pitch:** Parses an Excel financial model and flags error-prone patterns — hardcodes inside formula regions, inconsistent row formulas, broken references — with a ranked risk report.
- **Problem:** Finance/FP&A teams run businesses on spreadsheets with documented error rates near 90%; there is no "linter for Excel," so mistakes surface only after they cost money.
- **Novelty:** Code linters are everywhere; *spreadsheet* defect detection trained on real fault corpora, with ML ranking of which smells matter, is nearly untouched as a product.
- **Technique:** AST extraction (openpyxl + `formulas` lib) → dependency graph → smell detectors + GNN/GBM risk ranker. Eval: P/R against documented defects, MAP on ranking, score calibration.
- **Dataset:** SpreadsheetDB and the EUSES corpus (public collections of real spreadsheets with documented faults).
- **Risk:** Medium

**17. FloodScout — Post-Disaster Damage Triage from Aerial Imagery**
- **Pitch:** Runs flood segmentation over drone/satellite imagery and outputs a prioritized damage map plus an auto-drafted situation report for relief coordinators.
- **Problem:** District disaster-management teams in the first 72 hours post-flood can't manually interpret aerial coverage; existing tools are research demos, not field workflows.
- **Novelty:** Segmentation alone is a solved benchmark — the product layer is the value: multi-class severity ranking, flood-mask ∩ building-footprint damage estimation, and generated sitreps piped through n8n alerts.
- **Technique:** SegFormer or DeepLabV3+/U-Net fine-tuned with class-weighted/Lovász losses; geospatial join with building footprints; damage-priority scoring. Eval: per-class mIoU vs published FloodNet baselines.
- **Dataset:** FloodNet (public, 2,343 high-res labeled UAV images) + Google Open Buildings footprints (public, South Asia coverage).
- **Risk:** Medium

**18. ShelfCast — Demand Forecasting with Cold-Start SKUs for Small Retail**
- **Pitch:** Weekly demand forecasts for kirana/D2C retailers that handle brand-new products and promo spikes, with reorder suggestions and honest uncertainty bands.
- **Problem:** Small retailers alternately stock out and overstock; enterprise planners are out of reach and per-series classical stats break on new SKUs and intermittent demand.
- **Novelty:** Forecasting is old hat, but *cold-start transfer via product/store embeddings* evaluated with proper intermittent-demand metrics (not just MAPE), plus a SaaS reorder layer, is not the usual student treatment.
- **Technique:** Global deep models (DeepAR/N-BEATS/TFT) vs per-series ETS/Croston and GBM baselines; embeddings for cold-start SKUs. Eval: MASE, sMAPE, pinball loss, cold-start and sparse-series slices.
- **Dataset:** M5 Forecasting (Walmart, public on Kaggle) or Corporación Favorita.
- **Risk:** Low

**19. TurboTrend — Uncertainty-Calibrated RUL + Maintenance Scheduling**
- **Pitch:** Predicts machinery remaining useful life from sensor streams and turns it into a cost-optimized maintenance calendar, not just a number.
- **Problem:** Mid-size manufacturers maintain on fixed schedules; existing PdM tools emit black-box RUL numbers planners neither trust nor act on.
- **Novelty:** RUL regression is a benchmark staple; the fresh contribution is *uncertainty-calibrated* RUL feeding an explicit cost model (early-replacement vs late-failure cost) — a decision layer almost no student project builds.
- **Technique:** LSTM/1D-CNN/Transformer on multivariate sensor windows; deep ensembles or MC-dropout for intervals. Eval: RMSE, NASA scoring function, interval coverage, cost curves vs run-to-failure and scheduled baselines.
- **Dataset:** NASA C-MAPSS turbofan degradation dataset (public).
- **Risk:** Low

**20. FactFrame — Claim Detection + Evidence Retrieval Assist for Newsrooms**
- **Pitch:** Monitors a topic feed, extracts check-worthy claims, retrieves evidence from a trusted corpus, and drafts a verdict *suggestion* card — a human fact-checker always decides.
- **Problem:** Small regional fact-checking orgs (booming around elections) can't monitor the firehose; platform trust tooling is closed to them.
- **Novelty:** Most "AI fact-checker" demos are naive LLM verdicts; a staged pipeline (claim-worthiness → hybrid retrieval → stance) with *per-stage metrics* and an explicitly human-in-the-loop, no-auto-truth ethic is rare.
- **Technique:** Fine-tuned transformer claim detector; BM25 + dense hybrid retrieval with cross-encoder reranking; 3-way NLI stance classifier. Eval: claim-detection F1, retrieval recall@k, stance macro-F1 vs published FEVER baselines.
- **Dataset:** FEVER (public) for evidence/stance, ClaimBuster (public) for worthiness; optional light self-collection of public fact-check articles for a regional demo slice.
- **Risk:** Medium

---

## Copilot

1. Semantic Search for Urdu & Roman Urdu Community Q&A
- **Pitch:** A SaaS-style semantic search engine for Urdu and Roman Urdu Q&A forums, enabling users to find relevant answers across mixed scripts and dialects.
- **Problem:** Pakistan’s online forums and help groups (e.g., Stack Exchange clones, Facebook groups) are filled with questions and answers in a blend of Urdu, Roman Urdu, and English. Existing search tools fail to retrieve relevant answers due to script and dialect mismatches, making it hard for users to find help in their preferred language.
- **Novelty:** Unlike generic search or translation tools, this project targets the unique challenge of cross-script and cross-dialect retrieval in Pakistani online communities. It leverages sentence embeddings and vector search to bridge Urdu, Roman Urdu, and English, a gap underserved by mainstream search engines.
- **Technique:** 
• Architecture: Sentence-BERT (e.g., paraphrase-multilingual-mpnet-base-v2) for multilingual embeddings; FAISS or ChromaDB for vector search; custom script normalization and transliteration pipeline.
• Pipeline: Preprocess forum data, normalize scripts, embed questions/answers, index in vector DB, retrieve semantically similar answers.
- **Dataset:** 
• Public: mirfan899/Urdu for Urdu/Roman Urdu datasets (sentiment, QA, news, NER); Smat26/Roman-Urdu-Dataset; scrape or use small samples from open Q&A sites (with proper consent).
• Synthetic/self-collected: For Roman Urdu, may need to augment with synthetic transliterations.
- **Risk:** Medium. Requires careful preprocessing and script handling, but feasible with transfer learning and small-scale data. No large-scale scraping or labeling needed.

2. Crop Yield Predictor for Sindh Smallholder Farmers
- **Pitch:** A web app that predicts wheat, rice, or cotton yields for small farms in Sindh using minimal user inputs and public weather/crop data.
- **Problem:** Smallholder farmers in Sindh lack access to personalized yield forecasts, which hinders planning and resource allocation. Most existing tools are designed for large-scale, Western farms and require unavailable data.
- **Novelty:** Focuses on regionally relevant crops and minimal input requirements (e.g., farm size, location, sowing date), using transfer learning and public datasets tailored to Pakistan’s context.
- **Technique:** 
• Architecture: Gradient Boosting (e.g., XGBoost) or Random Forest for tabular regression; optional LSTM for time-series weather data.
• Pipeline: Feature engineering with weather, soil, and crop data; model training and evaluation; simple web frontend.
- **Dataset:** 
• Public: FAOSTAT Pakistan Crop Dataset (Kaggle) — wheat, rice, maize, sugarcane, potatoes, cotton, 2000–2024.
• Supplement: Open weather APIs for recent data.
- **Risk:** Low. Dataset is small and clean; model complexity is manageable; no scraping or manual labeling required.

3. Explainable Fake News Detector for Pakistani News
- **Pitch:** A web app that flags potentially fake news articles in English, Urdu, or Roman Urdu, providing explainable model outputs for each prediction.
- **Problem:** Misinformation is rampant in Pakistani media, especially in local languages. Users lack tools to verify news credibility, and existing detectors are English-centric and opaque.
- **Novelty:** Adds explainability (LIME/SHAP) and multilingual support, focusing on local news and social media content. Unlike generic detectors, it highlights which phrases or features led to the fake/real classification.
- **Technique:** 
• Architecture: Multilingual BERT (e.g., bert-base-multilingual-cased), fine-tuned for fake news detection; LIME or SHAP for explainability.
• Pipeline: Preprocess news articles, train classifier, integrate explainability, deploy with Streamlit.
- **Dataset:** 
• Public: LIAR or FakeNewsNet (for English); mirfan899/Urdu for Urdu fake news; small self-collected samples for Roman Urdu.
• Synthetic: For Roman Urdu, augment via transliteration.
- **Risk:** Medium. Multilingual fine-tuning and explainability add complexity, but transfer learning and small datasets make it feasible.

4. Low-Resource Urdu/Roman Urdu Sentiment Analyzer
- **Pitch:** A SaaS tool for sentiment analysis of Urdu and Roman Urdu social media posts, optimized for low-data settings and regional slang.
- **Problem:** Brands, NGOs, and researchers in Pakistan need sentiment analysis for local languages, but existing tools are English-only or require large labeled datasets.
- **Novelty:** Focuses on low-resource strategies (transfer learning, few-shot learning) and regional slang, supporting both Urdu script and Roman Urdu.
- **Technique:** 
• Architecture: Fine-tuned multilingual BERT or DistilBERT; optionally, few-shot learning with prompt-based methods.
• Pipeline: Preprocess and normalize text, train classifier, evaluate on small test set.
- **Dataset:** 
• Public: mirfan899/Urdu (sentiment, Roman Urdu); Smat26/Roman-Urdu-Dataset.
• Synthetic: Augment with small self-collected samples if needed.
- **Risk:** Low. Transfer learning and small datasets suffice; no heavy annotation or scraping.

5. Medical Report Summarizer for Pakistani Doctors
- **Pitch:** A web app that summarizes long medical reports (in English) into concise, patient-friendly summaries, with evaluation against human-written summaries.
- **Problem:** Doctors and patients in Pakistan often struggle with lengthy, jargon-heavy medical reports. Existing summarizers are generic and not tailored to medical language.
- **Novelty:** Targets medical domain, uses public medical datasets, and includes real evaluation (ROUGE, BERTScore, human comparison). Focuses on accessibility for non-expert users.
- **Technique:** 
• Architecture: Fine-tuned BioBERT or T5 for abstractive summarization.
• Pipeline: Preprocess reports, train/fine-tune model, evaluate with standard metrics.
- **Dataset:** 
• Public: MT-Samples (medical transcription samples); harishnair04/mtsamples on Hugging Face.
• No scraping/manual labeling required.
- **Risk:** Medium. Summarization is challenging, but dataset is available and evaluation is straightforward.

6. Small-Scale Crop Disease Detector (Leaf Images)
- **Pitch:** A web app that classifies crop leaf images (e.g., wheat, rice, cotton) as healthy or diseased, using transfer learning and explainable AI.
- **Problem:** Farmers in Pakistan lack accessible tools for early crop disease detection. Most existing apps are for Western crops or require large, labeled datasets.
- **Novelty:** Focuses on regionally relevant crops, uses transfer learning for small datasets, and provides visual explanations (e.g., Grad-CAM) for predictions.
- **Technique:** 
• Architecture: MobileNetV2 or EfficientNet (transfer learning); Grad-CAM for explainability.
• Pipeline: Preprocess images, fine-tune model, deploy with FastAPI or Streamlit.
- **Dataset:** 
• Public: PlantVillage Dataset — 54,000+ images, 14 crops, 26 diseases.
• Subset: Use only relevant crops for Pakistan.
- **Risk:** Low. Transfer learning and small data splits make it feasible; no manual labeling needed.

7. Multimodal Hate Speech & Meme Detector for Social Media
- **Pitch:** A SaaS tool that detects hate speech in both text and memes (images with text), targeting Pakistani social media content.
- **Problem:** Hate speech is often spread via memes and mixed-language posts. Existing detectors focus on text only and miss multimodal content.
- **Novelty:** Combines computer vision (CLIP) and NLP for multimodal detection, supports Urdu, Roman Urdu, and English, and provides explainable outputs.
- **Technique:** 
• Architecture: CLIP for image-text embeddings; classifier head for hate speech detection.
• Pipeline: Preprocess images and text, train classifier, evaluate multimodal accuracy.
- **Dataset:** 
• Public: Hateful Memes Dataset (Facebook AI).
• Synthetic: For Urdu memes, create a small set or use text overlays.
- **Risk:** Medium. Multimodal models are complex, but dataset is available and transfer learning helps.

8. RAG-Based Document QA for Pakistani Legal Documents
- **Pitch:** A SaaS app that answers user questions about Pakistani legal documents (e.g., tenancy laws, labor rights) using Retrieval-Augmented Generation (RAG).
- **Problem:** Citizens and lawyers struggle to find relevant information in lengthy legal documents. Existing chatbots are generic and not grounded in local law.
- **Novelty:** Uses RAG pipelines with vector DBs (Chroma/FAISS), supports Urdu/English, and evaluates retrieval quality (RAGAS). Focuses on local legal content.
- **Technique:** 
• Architecture: LangChain or LangGraph for RAG; Sentence Transformers for embeddings; ChromaDB or FAISS for vector search.
• Pipeline: Chunk legal docs, embed, store in vector DB, retrieve and generate answers.
- **Dataset:** 
• Public: Downloadable Pakistani legal documents (e.g., tenancy acts, labor laws) from government sites.
• Self-collected: Small set of PDFs or text files.
- **Risk:** Medium. Requires document chunking and embedding, but no scraping or manual labeling.

9. Bias Auditing Dashboard for AI Models (Pakistani Context)
- **Pitch:** A dashboard that audits AI model predictions for bias across gender, region, or language, using explainability tools and fairness metrics.
- **Problem:** AI models deployed in Pakistan may exhibit bias (e.g., urban/rural, gender, language), but few tools exist to audit and visualize these biases.
- **Novelty:** Focuses on local demographic attributes, integrates SHAP/LIME for explainability, and provides actionable bias metrics.
- **Technique:** 
• Architecture: SHAP or LIME for explainability; fairness metrics (e.g., demographic parity, equal opportunity).
• Pipeline: Analyze model predictions, visualize bias, generate model cards.
- **Dataset:** 
• Public: Any open dataset with demographic labels (e.g., Pakistan Economic Indicators).
• Synthetic: Simulate bias in predictions for demonstration.
- **Risk:** Low. No heavy data requirements; focus is on analysis and visualization.

10. Smart Attendance System with Face Recognition & Anti-Spoofing
- **Pitch:** A web-based attendance system using face recognition and liveness detection to prevent spoofing (e.g., photo attacks).
- **Problem:** Manual attendance is error-prone and easy to spoof. Existing face recognition systems are vulnerable to photo/video attacks.
- **Novelty:** Combines face recognition (dlib/face_recognition) with lightweight liveness detection, deployable on standard laptops.
- **Technique:** 
• Architecture: dlib or face_recognition for face ID; simple liveness detection (e.g., blink detection, texture analysis).
• Pipeline: Register faces, verify liveness, mark attendance.
- **Dataset:** 
• Self-collected: Register faces of a small group (classmates, friends).
• Public: Use open liveness datasets for testing.
- **Risk:** Low. No large dataset needed; self-registration suffices.

11. AI-Powered Urdu Handwriting Recognition (Prescription Reader)
- **Pitch:** A demo app that reads handwritten Urdu prescriptions, extracting drug names and dosages, with fuzzy matching to a drug database.
- **Problem:** Pharmacists and patients struggle to read handwritten Urdu prescriptions, leading to errors. Existing OCR tools are English-centric.
- **Novelty:** Focuses on Urdu handwriting, integrates OCR (TrOCR/PaddleOCR) with fuzzy matching, and supports small-scale, real-world testing.
- **Technique:** 
• Architecture: TrOCR or PaddleOCR for handwriting recognition; fuzzy string matching for drug names.
• Pipeline: Preprocess images, run OCR, match to drug database.
- **Dataset:** 
• Public: [IAM Handwriting Dataset] for base OCR; small self-collected set of Urdu prescription images (50–100 samples).
• Synthetic: Generate handwritten samples if needed.
- **Risk:** High. Handwriting OCR is challenging, especially for Urdu; requires small self-collected dataset.

12. Mental Health Support Chatbot for Urdu/Roman Urdu
- **Pitch:** A chatbot that detects emotional tone in Urdu/Roman Urdu messages and provides supportive responses, with emotion classification and safety disclaimers.
- **Problem:** Mental health support in Pakistan is stigmatized and under-resourced. Existing chatbots are English-only and lack local language support.
- **Novelty:** Focuses on emotion detection in local languages, integrates safety disclaimers, and avoids medical diagnosis claims.
- **Technique:** 
• Architecture: GoEmotions-based emotion classifier (fine-tuned for Urdu/Roman Urdu); rule-based response generator.
• Pipeline: Classify emotion, generate supportive response, display disclaimer.
- **Dataset:** 
• Public: GoEmotions for base model; small self-collected Urdu/Roman Urdu samples.
• Synthetic: Translate GoEmotions samples.
- **Risk:** Medium. Requires translation/adaptation for Urdu; emotion classification is feasible with transfer learning.

13. AI Interview Coach (Multimodal Feedback)
- **Pitch:** A web app that analyzes video/audio of mock interviews, providing feedback on speech clarity, filler words, and facial expressions.
- **Problem:** Job seekers in Pakistan lack access to affordable interview coaching. Existing tools are expensive or English-centric.
- **Novelty:** Combines speech-to-text (Whisper), emotion detection (OpenCV), and feedback on both verbal and nonverbal cues.
- **Technique:** 
• Architecture: Whisper for speech-to-text; pre-trained emotion detection model for facial analysis; librosa for audio features.
• Pipeline: Record/upload video, analyze speech and expressions, generate feedback.
- **Dataset:** 
• Self-collected: Record a small set of mock interviews for testing.
• Public: Use open emotion datasets for model evaluation.
- **Risk:** High. Multimodal analysis is complex; requires collecting test clips.

14. Credit Card Fraud Detection with Explainable AI
- **Pitch:** A SaaS demo that detects fraudulent transactions using tabular data, with explainable outputs for each prediction.
- **Problem:** Banks and fintechs in Pakistan face rising fraud, but lack transparent, explainable AI tools for transaction screening.
- **Novelty:** Focuses on explainability (LIME/SHAP) and real evaluation metrics (precision, recall, threshold tuning).
- **Technique:** 
• Architecture: XGBoost, Isolation Forest, or Autoencoder for anomaly detection; LIME/SHAP for explainability.
• Pipeline: Train model, evaluate with precision-recall, display explanations.
- **Dataset:** 
• Public: Kaggle Credit Card Fraud Detection — 284,807 transactions, 0.17% fraud.
- **Risk:** Low. Dataset is public and manageable; focus is on modeling and explainability.

15. Urdu/Roman Urdu News Headline Summarizer
- **Pitch:** A web app that generates concise summaries of Urdu and Roman Urdu news headlines, supporting both scripts and regional topics.
- **Problem:** News consumers in Pakistan are overwhelmed by information, especially in local languages. Existing summarizers are English-only.
- **Novelty:** Targets local scripts and topics, uses transfer learning for low-resource summarization, and supports both Urdu and Roman Urdu.
- **Technique:** 
• Architecture: Fine-tuned T5 or mT5 for summarization; script normalization pipeline.
• Pipeline: Preprocess headlines, train/fine-tune model, evaluate summaries.
- **Dataset:** 
• Public: mirfan899/Urdu (news headlines); [Urdu News Dataset 1M].
• Synthetic: Augment with small self-collected samples.
- **Risk:** Medium. Summarization is challenging, but dataset is available and project is scoped for small-scale demo.

16. Semantic Search for Pakistani Government Data
- **Pitch:** A SaaS tool that enables semantic search over open government datasets (e.g., economic indicators, census data) in English and Urdu.
- **Problem:** Researchers and journalists struggle to find relevant data in sprawling government datasets, often available only as CSVs or PDFs.
- **Novelty:** Applies semantic search (vector DBs, embeddings) to structured and unstructured government data, supporting both English and Urdu queries.
- **Technique:** 
• Architecture: Sentence Transformers for embeddings; ChromaDB or FAISS for vector search.
• Pipeline: Ingest datasets, chunk and embed documents, build search interface.
- **Dataset:** 
• Public: Open Data Pakistan; Kaggle Pakistan Economic Indicators.
- **Risk:** Low. Data is public and manageable; focus is on embedding and search.

17. Personalized Study Plan Generator for Pakistani Students
- **Pitch:** A web app that generates personalized study plans for students based on their academic history, goals, and available time.
- **Problem:** Students in Pakistan lack access to tailored study planning tools that consider local curricula and constraints.
- **Novelty:** Focuses on local context, uses simple ML (collaborative filtering, time series) to recommend study schedules, and supports Urdu/English.
- **Technique:** 
• Architecture: Collaborative filtering or rule-based recommendation; optional time series forecasting for workload.
• Pipeline: Collect user inputs, generate plan, allow feedback.
- **Dataset:** 
• Synthetic/self-collected: Simulate student profiles and study patterns for demo.
- **Risk:** Low. No external data required; can use synthetic data for demonstration.

18. Small-Scale Urdu/Roman Urdu Named Entity Recognition (NER)
- **Pitch:** A demo app that tags named entities (person, location, organization) in Urdu and Roman Urdu text, with evaluation against labeled data.
- **Problem:** NER tools for Urdu and Roman Urdu are scarce, limiting NLP applications in Pakistan.
- **Novelty:** Focuses on low-resource NER, supports both scripts, and evaluates with real metrics (precision, recall, F1).
- **Technique:** 
• Architecture: Fine-tuned multilingual BERT or spaCy model for NER.
• Pipeline: Preprocess text, train/fine-tune model, evaluate on test set.
- **Dataset:** 
• Public: mirfan899/Urdu (NER datasets); [MK-PUCIT NER Dataset].
- **Risk:** Medium. NER is challenging in low-resource settings, but dataset is available and project is scoped for small-scale demo.

19. AI-Powered Resume Ranker for Pakistani Job Market
- **Pitch:** A SaaS demo that ranks resumes for local job postings using contextual AI, with explainable scoring and bias mitigation.
- **Problem:** Recruiters in Pakistan face high volumes of resumes, often in mixed formats and languages. Existing rankers are generic and may reinforce bias.
- **Novelty:** Focuses on local job market, supports Urdu/English resumes, integrates explainable AI (e.g., SHAP), and includes bias auditing.
- **Technique:** 
• Architecture: Fine-tuned BERT or Sentence Transformers for embedding; XGBoost or neural net for ranking; SHAP for explainability.
• Pipeline: Parse resumes, extract features, rank candidates, display explanations.
- **Dataset:** 
• Public: Kaggle resume datasets (English); small self-collected Urdu/English resumes for demo.
• Synthetic: Generate sample resumes if needed.
- **Risk:** Medium. Resume parsing and ranking are feasible with small datasets; focus is on explainability and bias control.

20. Pakistani Regional Language Speech-to-Text Demo
- **Pitch:** A web app that transcribes short audio clips in Sindhi, Punjabi, or Pashto using transfer learning and open-source models.
- **Problem:** Speech-to-text tools for Pakistani regional languages are scarce, limiting accessibility for millions of speakers.
- **Novelty:** Focuses on regional languages, uses transfer learning (e.g., Whisper, wav2vec 2.0), and supports small-scale demo with short clips.
- **Technique:** 
• Architecture: Fine-tuned Whisper or wav2vec 2.0 for target language.
• Pipeline: Collect short audio samples, train/fine-tune model, evaluate WER (Word Error Rate).
- **Dataset:** 
• Public: Open speech datasets for regional languages (if available); small self-collected audio clips.
• Synthetic: Record short phrases for demo.
- **Risk:** High. Regional speech data is limited; requires small self-collected dataset and careful evaluation.

Note: All ideas are designed for a 4-week, 50–60 hour capstone, with a focus on real AI/DS techniques, public or easily collectible datasets, and SaaS-style demo apps. Each project includes a working demo and a report with real model evaluation (metrics, comparisons). Legal and ethical constraints (especially for health, finance, and personal data) must be respected, with disclaimers and privacy-by-design principles applied where appropriate.