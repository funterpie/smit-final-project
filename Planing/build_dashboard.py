#!/usr/bin/env python3
"""Parse the 9-model FYP markdown and fill the dashboard template.

Usage:
  python build_dashboard.py [ideas.md] [dashboard.html] [out.html] [--limit N]

Reads the template, replaces everything between <!--ARCHIVE_START--> and
<!--ARCHIVE_END--> with one card per non-claimed idea, and writes out.html.
The markers are preserved, so the output can itself be used as a template.
"""
import argparse, html, re, sys
from pathlib import Path

MODELS = ["ChatGPT", "Grok", "Claude", "Gemini", "Perplexity", "DeepSeek", "Kimi", "Qwen", "Copilot"]
TOP5 = {"chatgpt-8", "qwen-5", "qwen-4", "kimi-10", "qwen-14"}   # claimed: never rendered as cards
RANKED = ["qwen-19", "grok-14", "qwen-13", "kimi-20", "qwen-9", "chatgpt-15", "claude-2", "grok-7",
          "chatgpt-1", "qwen-7", "grok-20", "kimi-11", "qwen-3", "chatgpt-18", "kimi-19", "chatgpt-7",
          "grok-1", "chatgpt-14", "grok-17", "claude-6"]          # runner-up ranks #6..#25

# id -> (primary rejection tag, one-line Stress Test Verdict)
V = {
 # ---- ChatGPT
 "chatgpt-1": ("Data risk", "TED notices are messy multilingual XML with no duplicate labels, so evaluation rests on planted duplicates and heavy parsing."),
 "chatgpt-2": ("Weak eval", "Supplier profiles would be synthetic, so ranking quality is scored against ground truth you invented."),
 "chatgpt-3": ("Weak eval", "CUAD has no inconsistent-clause-pair labels; you would fabricate them, and contract NLP appears in four lists."),
 "chatgpt-4": ("Saturated", "SROIE holds receipts, not invoices; receipt extraction appears in four lists and LayoutLMv3 setup eats hours."),
 "chatgpt-5": ("Data risk", "Needs self-collected or synthetic Urdu forms (FUNSD is English-only); Urdu OCR is a research problem."),
 "chatgpt-6": ("Weak eval", "Only synthetic tampering to train and test on, so results say little about real forgeries."),
 "chatgpt-7": ("Saturated", "RDD2022 road damage appears in four lists, and severity has no ground-truth labels, so severity MAE is unmeasurable."),
 "chatgpt-9": ("Compute", "xBD is a huge, registration-gated satellite corpus and the Siamese U-Net needs real GPU time; the author rates it High."),
 "chatgpt-10": ("Saturated", "Waste classification is a student staple; TACO is long-tailed with Flickr-hosted images and no composition labels."),
 "chatgpt-11": ("Weak eval", "UCI household power has no anomaly labels, so detection cannot be scored without injecting synthetic faults."),
 "chatgpt-12": ("Saturated", "Air-quality forecasting appears in four lists and the Beijing data has no local relevance."),
 "chatgpt-13": ("Complexity", "M5 records sales, not stockouts; true stockout labels do not exist, so the core target must be guessed."),
 "chatgpt-14": ("Weak eval", "Regionally sharp but only about 1,200 rows, too little for rigorous model comparison."),
 "chatgpt-15": ("Backup", "Sound teacher-facing idea, but the MathE table is small and mostly tabular, which caps model depth and comparisons."),
 "chatgpt-16": ("Data risk", "Crisis corpora often ship tweet IDs only and hydration is impractical now; confirm text availability first."),
 "chatgpt-17": ("Saturated", "Roman-Urdu NLP fills many entries here; the regional data would be synthetic paraphrase over English CLINC150."),
 "chatgpt-18": ("Weak eval", "NIDS is crowded, and cluster purity against attack labels does not prove alert compression helps analysts."),
 "chatgpt-19": ("Overlap", "Same concept as the claimed LogSense pick (template parsing plus sequence anomaly detection)."),
 "chatgpt-20": ("Saturated", "Career/skills matching sits beside the resume-screener trap, and GraphSAGE adds learning curve for little gain."),
 # ---- Grok
 "grok-1": ("Data risk", "Needs 800-1,500 self-labelled scam messages, and Roman-Urdu classification is the most duplicated theme here."),
 "grok-2": ("Complexity", "No ground-truth pollution-source labels plus a four-source geospatial merge; attribution claims cannot be validated."),
 "grok-3": ("Compute", "Sentinel-1 GeoTIFF handling, multi-GB tiles and U-Net training need GPU hours and a geospatial stack to learn."),
 "grok-4": ("Data risk", "Requires hand-tracing 150-300 field polygons and a two-stage segmentation-plus-classification pipeline."),
 "grok-5": ("Complexity", "Nastaliq OCR plus Urdu NER is two research-grade problems stacked; synthetic form overlays weaken evaluation."),
 "grok-6": ("Data risk", "Forgery ground truth is the bottleneck (DocTamper access, your own splices), and the output accuses people of forgery."),
 "grok-7": ("Data risk", "Plausible forecasting project, but it rests on one Kaggle price table of unverified coverage; check it in week 1."),
 "grok-8": ("Complexity", "Kilns are only a few pixels at 10 m resolution and you must cut Sentinel-2 chips around 11k coordinates."),
 "grok-9": ("Saturated", "Road damage (RDD2022) again; the duplicate-aware queue is a nice twist on the most common CV pick here."),
 "grok-10": ("Ethics", "Halal-status inference carries religious and consumer-claim liability, on top of bilingual label OCR."),
 "grok-11": ("Ethics", "Needs consented student writing and yields accusatory scores; AI-text detectors have known false-positive harms."),
 "grok-12": ("Weak eval", "Collusion is accusatory and cannot be validated with planted near-duplicates; overlaps the TED tender idea."),
 "grok-13": ("Complexity", "No ground truth for neighbourhood heat ranking, and a Landsat land-surface-temperature pipeline to build first."),
 "grok-14": ("Weak eval", "Genuinely unusual and CPU-light, but evaluation is a simulation on synthetic answer sheets and outputs accuse students."),
 "grok-15": ("Overlap", "Same concept as the claimed TextileGuard pick; shade-lot matching is an optional extension of it."),
 "grok-16": ("Complexity", "Four-model stack (layout, handwriting, OCR, translation) plus self-captured photos: scope creep for 50 hours."),
 "grok-17": ("Saturated", "No Pakistani load data, so it runs on a PJM proxy; load forecasting appears in three lists."),
 "grok-18": ("Saturated", "Receipt extraction appears in four lists, and the tax-consistency head has no real labels."),
 "grok-19": ("Complexity", "Clustering, numeric NER and contradiction detection with 300 hand-labelled pairs and unclear news licensing."),
 "grok-20": ("Weak eval", "Test data is synthetic code-switched text spliced from parallel clauses, so scores are circular."),
 # ---- Claude
 "claude-1": ("Saturated", "Title promises Roman Urdu but the cited corpus is Urdu-script with about 900 articles; fake-news classifiers are saturated."),
 "claude-2": ("Saturated", "RUHSOLD is clean, real data, but Roman-Urdu abuse moderation is duplicated across lists: low risk, low distinctiveness."),
 "claude-3": ("Ethics", "False positives from AI-text detectors penalise students, and UHAT is only 3,600 samples."),
 "claude-4": ("Saturated", "EMSCAD is an old Kaggle staple with very few fraudulent postings."),
 "claude-5": ("Saturated", "PlantVillage is the textbook saturated CV project; the RAG layer needs a self-collected corpus and raises advice liability."),
 "claude-6": ("Saturated", "Regional AQ forecasting is duplicated four times, and sensor gaps make clean baselines harder than they look."),
 "claude-7": ("Saturated", "Retail demand forecasting on Favorita is generic; big data and no distinctive angle beyond SHAP text."),
 "claude-8": ("Saturated", "C-MAPSS models jet engines, not motors (title mismatch), and RUL on it is a classic; see Qwen TurboTrend for the twist."),
 "claude-9": ("Saturated", "NSL-KDD dates from the 1990s and is widely considered obsolete for evaluation."),
 "claude-10": ("Data risk", "Dataset mismatch: 140k real/fake faces are GAN faces, not manipulated photos, so the forensic claim is untestable."),
 "claude-11": ("Complexity", "Nasta'liq handwriting recognition; the source itself rates it High and expects modest accuracy."),
 "claude-12": ("Saturated", "MOSS and JPlag already serve this need, and BigCloneBench labels are noisy."),
 "claude-13": ("Saturated", "Generic tabular fraud classification on a Kaggle claims set; SHAP dashboards are the default tutorial."),
 "claude-14": ("Ethics", "Credit scoring draws fairness and financial-advice scrutiny, and Give Me Some Credit is a generic tabular task."),
 "claude-15": ("Weak eval", "RAVDESS is acted speech and will not transfer to real voice notes; wav2vec2 fine-tuning is compute-heavy."),
 "claude-16": ("Saturated", "RAG search is the most-built student project, and arXiv has no relevance labels (you would need BEIR-style qrels)."),
 "claude-17": ("Complexity", "PyTorch Geometric plus ogbn-arxiv scale is a steep learning curve for a 50-hour budget."),
 "claude-18": ("Saturated", "No public Pakistani grid data, so it runs on a PJM proxy; load forecasting appears in three lists."),
 "claude-19": ("Saturated", "The Ott corpus is 1,600 hotel reviews, heavily used, and results do not generalise to marketplaces."),
 "claude-20": ("Saturated", "SROIE receipt extraction appears in four lists, and the author flags LayoutLM fine-tuning as Medium-High risk."),
 # ---- Gemini
 "gemini-1": ("Saturated", "RDD2022 road damage again (four lists); the dashcam-fleet framing changes neither dataset nor model."),
 "gemini-2": ("Complexity", "DiverseVul is heavily imbalanced (about 5%) with label noise, and vulnerability detectors generalise poorly."),
 "gemini-3": ("Saturated", "CSIC 2010 is dated and heavily reused; payload classifiers are a standard course project."),
 "gemini-4": ("Data risk", "MIMIC-IV-ED needs credentialed PhysioNet access, and hospital data is a medical-adjacent landmine."),
 "gemini-5": ("Saturated", "Roman-Urdu sentiment is duplicated across lists, and the cited Hugging Face corpus is unverified."),
 "gemini-6": ("Compute", "SKU-110K dense detection has hundreds of boxes per image; training is expensive and anchor tuning is fiddly."),
 "gemini-7": ("Compute", "Video action spotting; the author rates it High even with pre-extracted features."),
 "gemini-8": ("Weak eval", "FAOSTAT gives about 60 annual points per series, too short to justify LSTM/TFT over ARIMA."),
 "gemini-9": ("Saturated", "CUAD clause extraction appears in four lists; PDF highlight alignment adds engineering, not ML."),
 "gemini-10": ("Compute", "MIMII downloads run to tens of GB across machine types and SNRs, and DSP tuning is a hidden time sink."),
 "gemini-11": ("Saturated", "Ticket routing is a chatbot-adjacent RAG build, and the Twitter support data has no department labels."),
 "gemini-12": ("Complexity", "Price elasticity cannot be identified from observational Olist data without price experiments."),
 "gemini-13": ("Saturated", "FUNSD is only 199 forms, document extraction is heavily duplicated, and the author rates it High."),
 "gemini-14": ("Saturated", "Jigsaw toxicity is among the most-built NLP projects, and it is Wikipedia text, not gaming chat."),
 "gemini-15": ("Weak eval", "Telco churn is saturated and the intervention/uplift part needs treatment data that would be simulated."),
 "gemini-16": ("Data risk", "Spotify TREC transcripts need an access agreement; the YouTube route is scraping."),
 "gemini-17": ("Saturated", "PlantVillage classification again; TFLite quantisation is the only differentiator."),
 "gemini-18": ("Saturated", "PJM hourly load is the standard forecasting toy and appears in three lists."),
 "gemini-19": ("Complexity", "GNN tooling plus Yelp labels derived from a filter rather than ground truth; the author rates it High."),
 "gemini-20": ("Saturated", "Visual search is a commercial commodity and DeepFashion needs an access request (ABO is the open route)."),
 # ---- Perplexity (source gives one-line pitches only)
 "perplexity-1": ("Saturated", "Leaf-disease triage duplicates PlantVillage-style projects; the source names no dataset or method."),
 "perplexity-2": ("Saturated", "Pest identification is a long-tailed variant of crop-disease classification; no dataset named."),
 "perplexity-3": ("Data risk", "No parallel Roman-Urdu normalisation corpus is named, so you would build the labels yourself."),
 "perplexity-4": ("Saturated", "Roman-Urdu review sentiment, duplicated across lists."),
 "perplexity-5": ("Data risk", "No labelled Roman-Urdu fake-review data exists in the cited material."),
 "perplexity-6": ("Saturated", "Urdu fake-news triage repeats a theme found in the Claude and Copilot lists."),
 "perplexity-7": ("Complexity", "Claim-veracity pipelines are multi-stage (detect, retrieve, verify) and the source names no data."),
 "perplexity-8": ("Complexity", "Audio-deepfake detectors generalise poorly across attack types, so evaluation is harder than it looks."),
 "perplexity-9": ("Infra", "Needs a live webcam pipeline and self-collected gesture data; no public sign-language dataset is named."),
 "perplexity-10": ("Compute", "Urdu ASR correction needs fine-tuning compute and the source specifies no dataset."),
 "perplexity-11": ("Compute", "Satellite building-damage assessment means multi-GB data and heavy segmentation training."),
 "perplexity-12": ("Saturated", "RDD2022 road damage again."),
 "perplexity-13": ("Infra", "Occupancy monitoring implies live camera feeds; an offline demo would drop the SaaS story."),
 "perplexity-14": ("Data risk", "Public-health case data is scarce and health-adjacent, which adds access and claim risk."),
 "perplexity-15": ("Saturated", "Tabular dropout prediction is a student staple."),
 "perplexity-16": ("Ethics", "Automated grading is high-stakes with fairness scrutiny, and the source names no dataset."),
 "perplexity-17": ("Ethics", "Calorie estimation edges into health advice, and image datasets like Nutrition5k are very large."),
 "perplexity-18": ("Overlap", "Same concept as the claimed GridGuard pick (anomaly ranking on smart-meter data)."),
 "perplexity-19": ("Saturated", "Crypto-fraud graph classification is a common GNN tutorial."),
 "perplexity-20": ("Saturated", "Waste sorting again."),
 # ---- DeepSeek
 "deepseek-1": ("Infra", "Telephony and recorded emergency calls hit two dealbreakers, and the cited dataset's provenance is unverified."),
 "deepseek-2": ("Data risk", "The 100K Sindhi sentiment set is unverified, so outputs cannot be sanity-checked."),
 "deepseek-3": ("Compute", "Fine-tuning a 3B LLM for Sindhi QA plus RAG is heavy, and generative evaluation in a low-resource language is hard."),
 "deepseek-4": ("Compute", "Dashcam video plus trajectory modelling; the source rates it High and the dataset claim is unverified."),
 "deepseek-5": ("Data risk", "The PlantCity dataset is unverified; confirm it exists and downloads before building anything."),
 "deepseek-6": ("Weak eval", "Early warning needs longitudinal plant photos; a static image-classification set cannot support the claim."),
 "deepseek-7": ("Data risk", "No public Urdu legal NER data; you would annotate 500-1,000 sentences yourself. Rated High."),
 "deepseek-8": ("Data risk", "Tiny, obscure corpus in a language most reviewers cannot check."),
 "deepseek-9": ("Compute", "LoRA-tuning an LLM and evaluating generated Urdu is costly, and the Khudi dataset is unverified."),
 "deepseek-10": ("Data risk", "No data: needs physics-simulated pump failures, so evaluation happens on your own simulation. Rated High."),
 "deepseek-11": ("Complexity", "Wiktionary scraping plus diffusion image generation for Mizo/Khasi: irrelevant region and scope creep."),
 "deepseek-12": ("Ethics", "Wearable stress data is mental-health-adjacent, and federated learning adds simulation overhead."),
 "deepseek-13": ("Data risk", "Filtering Xeno-canto and self-recording birds is collection-heavy; multi-label audio adds tuning time."),
 "deepseek-14": ("Ethics", "Loan-rejection reasoning touches credit decisions; Lending Club is US data and synthetic Pakistani data is circular."),
 "deepseek-15": ("Infra", "Real-time webcam inference and self-collected sign data; live hardware is a dealbreaker."),
 "deepseek-16": ("Data risk", "Needs district yield statistics from PDFs plus Sentinel-2 processing; the source rates it High."),
 "deepseek-17": ("Saturated", "Waste classification on a self-collected set of 500-1,000 photos."),
 "deepseek-18": ("Thin ML", "An evaluation harness around PakBBQ rather than a trained model, so the ML contribution is thin."),
 "deepseek-19": ("Data risk", "No dataset exists and YouTube audio collection is scraping. Rated High."),
 "deepseek-20": ("Data risk", "Textbook scans need OCR and copyright care, and grade labels leak vocabulary by textbook."),
 # ---- Kimi
 "kimi-1": ("Data risk", "DengAI is Latin American data, the Pakistani case series is unverified, and disease forecasting is health-adjacent."),
 "kimi-2": ("Saturated", "Air-quality forecasting is duplicated four times."),
 "kimi-3": ("Compute", "ASVspoof downloads are large, and audio-spoof detectors generalise poorly across attacks."),
 "kimi-4": ("Saturated", "Roman-Urdu toxicity moderation duplicates the Claude RUHSOLD entry: solid data, not distinctive."),
 "kimi-5": ("Compute", "Whisper fine-tuning plus diarization is compute-hungry; the source itself flags Medium-High."),
 "kimi-6": ("Data risk", "Data curation is the bottleneck by the source's own admission, and inferred difficulty labels are noisy."),
 "kimi-7": ("Saturated", "CUAD-based contract review appears in four lists, and legal-advice adjacency adds risk."),
 "kimi-8": ("Complexity", "YelpChi plus GNN tooling, with labels from Yelp's own filter rather than ground truth."),
 "kimi-9": ("Weak eval", "UCI Online Retail is a UK wholesaler and the Ramadan overlay is synthetic, so the headline result is circular."),
 "kimi-11": ("Weak eval", "Bug-severity labels are subjective and noisy, which caps what any model can show."),
 "kimi-12": ("Compute", "Nutrition5k is huge, multi-task image regression is GPU-heavy, and calorie claims edge toward health advice."),
 "kimi-13": ("Overlap", "Same concept as the claimed GridGuard pick, which uses real labelled SGCC data instead of simulated theft."),
 "kimi-14": ("Compute", "Long-document summarisation (LongT5/LED) is GPU-heavy and faithfulness is hard to score; US case law only."),
 "kimi-15": ("Data risk", "Relies on hand-copied curricula plus job-posting data with noisy skill taxonomies; drifts into scraping."),
 "kimi-16": ("Complexity", "UCI Phishing Websites is pre-featurised, so new URLs cannot be scored; WHOIS/HTML features add hidden work."),
 "kimi-17": ("Data risk", "Dataset mismatch: EuroSAT is European land cover, not crop types, so the crop claim cannot be tested."),
 "kimi-18": ("Compute", "Same Sen1Floods11 geospatial pipeline as Grok's flood mapper: multi-GB SAR tiles and GPU training."),
 "kimi-19": ("Saturated", "Dropout prediction is a student staple; the fairness audit is nice but the base task is common."),
 "kimi-20": ("Thin ML", "Best demo-per-hour, but zero-shot CLIP with a 50-100 item test set means thin ML and wide confidence intervals."),
 # ---- Qwen
 "qwen-1": ("Complexity", "Table-structure recognition plus PDF-to-XBRL alignment; FinTabNet access and financial-document parsing are heavy."),
 "qwen-2": ("Saturated", "CUAD/LEDGAR clause classifiers are duplicated across lists, and a market-norms risk taxonomy is subjective."),
 "qwen-3": ("Saturated", "PII detection is well trodden (public Kaggle competition) and AI4Privacy is synthetic, so scores hit a ceiling."),
 "qwen-6": ("Data risk", "AgmarkNet has no clean bulk export; the realistic access route is scraping."),
 "qwen-7": ("Complexity", "Three subsystems (routing, dedup, survival) in one project, and NYC 311 has no duplicate labels."),
 "qwen-8": ("Weak eval", "Flaws are synthetic perturbations, so models learn perturbation artefacts rather than real question defects."),
 "qwen-9": ("Saturated", "OULAD is excellent data, but student-performance prediction is heavily done and clickstream prep takes time."),
 "qwen-10": ("Data risk", "Needs about 200 self-annotated decks and a scraped deck collection, with subjective rubric scoring."),
 "qwen-11": ("Data risk", "NewsCLIPpings needs the separately gated VisualNews images; a caption-swap benchmark with large downloads."),
 "qwen-12": ("Complexity", "Detection, ranking and verified patch generation in one project; the source rates it High and GNNs can stall."),
 "qwen-13": ("Saturated", "NIDS is crowded and CIC datasets are multi-GB with documented labelling problems; the conformal/drift angle makes it a real cyber fallback."),
 "qwen-15": ("Compute", "Transliteration seq2seq on 26M pairs plus an intent model is heavy for 50 hours."),
 "qwen-16": ("Data risk", "Fault-labelled spreadsheet corpora are old and hard to obtain, and Excel parsing adds hidden complexity."),
 "qwen-17": ("Complexity", "Segmentation, footprint join and report generation across several datasets: scope creep."),
 "qwen-18": ("Saturated", "Demand forecasting on M5/Favorita with DeepAR/N-BEATS: big data and a very common topic."),
 "qwen-19": ("Backup", "C-MAPSS is a benchmark cliché, but calibrated uncertainty plus a cost-optimal maintenance schedule is a genuine twist. First fallback."),
 "qwen-20": ("Complexity", "Three-stage pipeline (claim detection, retrieval, NLI) on Wikipedia-based FEVER, with a fact-checking ethics burden."),
 # ---- Copilot
 "copilot-1": ("Data risk", "No relevance labels, and the plan leans on scraping forums; cross-script retrieval cannot be scored properly."),
 "copilot-2": ("Weak eval", "National annual FAOSTAT rows cannot support farm-level yield predictions, and the dataset is unverified."),
 "copilot-3": ("Saturated", "Fake-news classifiers are duplicated across lists; explainability is a tutorial add-on."),
 "copilot-4": ("Saturated", "Roman-Urdu sentiment, duplicated across lists."),
 "copilot-5": ("Ethics", "Medical report summarisation is a medical-content landmine, and MTSamples is a small US transcription set."),
 "copilot-6": ("Saturated", "PlantVillage has no wheat, rice or cotton, so the regional crop claim does not match the data."),
 "copilot-7": ("Data risk", "Hateful Memes sits behind an access agreement, and Urdu memes would need self-made data."),
 "copilot-8": ("Saturated", "A RAG chatbot over legal PDFs is the generic-chatbot case, plus legal-advice liability."),
 "copilot-9": ("Weak eval", "Audits a bias you inject yourself, so results are circular and no model is trained."),
 "copilot-10": ("Ethics", "Face recognition raises consent and privacy issues; off-the-shelf dlib plus a live camera adds no ML depth."),
 "copilot-11": ("Ethics", "Medical prescriptions plus Urdu handwriting: a medical landmine on an unsolved OCR problem. Rated High."),
 "copilot-12": ("Ethics", "Mental-health chatbot: an explicit ethical landmine and a chatbot in disguise."),
 "copilot-13": ("Complexity", "Multimodal video/audio analysis, and facial-expression scoring has weak scientific validity. Rated High."),
 "copilot-14": ("Saturated", "The ULB credit-card fraud set is one of the most-used datasets on Kaggle."),
 "copilot-15": ("Compute", "mT5 fine-tuning for Urdu; Roman-Urdu summaries have no dataset in the cited material."),
 "copilot-16": ("Saturated", "Chat-with-datasets search over government data has no relevance labels to evaluate against."),
 "copilot-17": ("Weak eval", "Entirely synthetic student profiles, so nothing real to validate; simple rules would do."),
 "copilot-18": ("Data risk", "Roman-Urdu NER data is not in the cited sources, and NER alone is a model, not a product."),
 "copilot-19": ("Saturated", "The resume ranker is the explicit saturated example in your own dealbreaker list."),
 "copilot-20": ("Data risk", "No labelled Sindhi/Punjabi/Pashto speech in hand; self-collection needed. Rated High."),
}

# ----------------------------------------------------------------------------- parsing
ITEM_RE = re.compile(r"^\*{0,2}(\d{1,2})\.\s+(.*\S)\s*$")
FIELD_RE = re.compile(r"^\s*[-•]\s*\*\*(Pitch|Problem|Novelty|Technique|Dataset|Risk):\*\*\s*(.*)$")


def clean(s):
    s = html.unescape(s)
    s = re.sub(r"\s*\(\[[^\]]+\]\s*\[\d+\]\)", "", s)      # ([Source][3])
    s = re.sub(r"\[\d+\]", "", s)
    s = re.sub(r"\*\*|`", "", s)
    return re.sub(r"\s+", " ", s).strip()


def clip(s, n):
    s = clean(s)
    if len(s) <= n:
        return s
    return s[:n].rsplit(" ", 1)[0].rstrip(",;:-—") + "…"


def parse(md):
    out, sections = [], re.split(r"^## (.+?)\s*$", md, flags=re.M)
    for i in range(1, len(sections), 2):
        model, body = sections[i].strip(), sections[i + 1]
        if model not in MODELS:
            continue
        body = body.split("Works cited")[0]                  # Gemini footnote list
        items, cur, field = [], None, None
        for line in body.splitlines():
            m = ITEM_RE.match(line)
            if m and int(m.group(1)) == len(items) + 1:
                head = m.group(2).rstrip("*").strip()
                cur = {"model": model, "n": len(items) + 1, "head": head, "f": {}}
                items.append(cur); field = None
                continue
            if cur is None:
                continue
            fm = FIELD_RE.match(line)
            if fm:
                field = fm.group(1); cur["f"][field] = fm.group(2)
            elif field and line.strip().startswith("•"):     # Copilot bullet continuations
                prev = cur["f"][field].strip()
                cur["f"][field] = (prev + "; " if prev else "") + line.strip().lstrip("• ")
        for it in items:
            head, pitch = it["head"], it["f"].get("Pitch", "")
            if model == "DeepSeek":
                m = re.match(r"^\*\*(.+?)\*\*\s*[—-]\s*(.*)$", head)
                if m:
                    head, pitch = m.group(1), m.group(2)
            if model == "Perplexity":
                pitch = head
            title = clean(head)
            if model == "Gemini":                             # strip footnote digits like 'regression1.'
                strip = lambda t: re.sub(r"(?<=[A-Za-z\)])\d{1,2}(?=\.(?:\s|$))", "", t)
                pitch, it["f"] = strip(pitch), {k: strip(v) for k, v in it["f"].items()}
            spec = "Not specified in source (one-line pitch only)"
            out.append({
                "id": f"{model.lower()}-{it['n']}", "model": model, "n": it["n"],
                "title": clip(title, 110), "pitch": clip(pitch or "—", 200),
                "tech": clip(it["f"].get("Technique", spec if model == "Perplexity" else "—"), 160),
                "data": clip(it["f"].get("Dataset", spec if model == "Perplexity" else "—"), 130),
            })
    return out


# ----------------------------------------------------------------------------- rendering
def card(idea, rank=None):
    tag, verdict = V.get(idea["id"], ("Review", "No verdict written for this idea."))
    slug = re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")
    e = html.escape
    r = f'<span class="rank">#{rank}</span>' if rank else ""
    return (
        f'<details class="card" data-model="{idea["model"]}" data-tag="{e(tag)}">'
        f'<summary><div class="top"><span class="title">{r}{e(idea["title"])}</span>'
        f'<span class="src">{idea["model"]} #{idea["n"]}</span></div>'
        f'<span class="chip t-{slug}">{e(tag)}</span>'
        f'<div class="verdict"><b>Stress Test Verdict</b>{e(verdict)}</div></summary>'
        f'<div class="body"><dl><dt>Pitch</dt><dd>{e(idea["pitch"])}</dd>'
        f'<dt>Core tech</dt><dd>{e(idea["tech"])}</dd><dt>Dataset</dt><dd>{e(idea["data"])}</dd></dl></div>'
        f'</details>'
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md", nargs="?", default="final_year_project_ideas_9_model_comparison.md")
    ap.add_argument("template", nargs="?", default="dashboard.html")
    ap.add_argument("out", nargs="?", default="dashboard_full.html")
    ap.add_argument("--limit", type=int, default=0, help="only render the first N runner-ups (0 = all)")
    a = ap.parse_args()

    ideas = parse(Path(a.md).read_text(encoding="utf-8"))
    by_id = {i["id"]: i for i in ideas}
    print(f"parsed {len(ideas)} ideas from {len({i['model'] for i in ideas})} models", file=sys.stderr)
    missing = [i for i in by_id if i not in TOP5 and i not in V]
    if missing:
        print("no verdict for:", ", ".join(missing), file=sys.stderr)

    rest = [i for i in ideas if i["id"] not in TOP5 and i["id"] not in RANKED]
    ordered = [(by_id[k], n + 6) for n, k in enumerate(RANKED) if k in by_id] + [(i, None) for i in rest]
    if a.limit:
        ordered = ordered[: a.limit]
    cards = "\n".join(card(i, r) for i, r in ordered)

    tpl = Path(a.template).read_text(encoding="utf-8")
    new = re.sub(r"(<!--ARCHIVE_START-->).*?(<!--ARCHIVE_END-->)",
                 lambda m: f"{m.group(1)}\n{cards}\n{m.group(2)}", tpl, flags=re.S)
    Path(a.out).write_text(new, encoding="utf-8")
    print(f"wrote {a.out} with {len(ordered)} cards", file=sys.stderr)


if __name__ == "__main__":
    main()
