"""Render submission charts from the checked-in evaluation artifacts."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "eval/results.json").read_text())
NAMES = {
    "heuristic": "Heuristic",
    "baseline_lr": "Logistic Regression",
    "baseline_rf": "Random Forest",
    "codebert": "CodeBERT",
}


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def chart_metrics():
    keys = list(DATA)
    names = [NAMES.get(k, k) for k in keys]
    metrics = [
        ("AUC-ROC", "auc_roc", None),
        ("AUC-PR", "auc_pr", "auc_pr_ci"),
        ("Recall@20%", "recall_at_20pct", "recall_at_20pct_ci"),
        ("FPR@0.5", "fpr_at_0.5", None),
    ]
    width, height = 1500, 1040
    im = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(im)
    d.text((75, 35), "Model evaluation on the 1,200-commit test split", fill="#152238", font=font(32, True))
    colors = ["#64748b", "#0ea5e9", "#16a34a", "#7c3aed"]
    left, right, top, bottom = 100, 1430, 150, 860
    panel_w = (right-left) // 2
    panel_h = (bottom-top) // 2
    for idx, (title, key, ci_key) in enumerate(metrics):
        row, col = divmod(idx, 2)
        x0, y0 = left + col*panel_w, top + row*panel_h
        d.text((x0, y0), title, fill="#152238", font=font(25, True))
        gx0, gx1, gy0, gy1 = x0+65, x0+panel_w-25, y0+50, y0+panel_h-50
        d.line((gx0, gy1, gx1, gy1), fill="#94a3b8", width=2)
        d.line((gx0, gy0, gx0, gy1), fill="#94a3b8", width=2)
        values = [float(DATA[k][key]) for k in keys]
        vmax = max(1.0, max(values)*1.18)
        bar_w = max(30, (gx1-gx0)//(len(keys)*2))
        slot = (gx1-gx0)//len(keys)
        for j, val in enumerate(values):
            bx = gx0 + j*slot + (slot-bar_w)//2
            by = gy1 - int((gy1-gy0)*val/vmax)
            d.rectangle((bx, by, bx+bar_w, gy1), fill=colors[j])
            d.text((bx-6, by-27), f"{val:.3f}", fill="#1e293b", font=font(15))
            d.text((gx0+j*slot, gy1+8), names[j][:13], fill="#334155", font=font(14))
            if ci_key and f"{ci_key}_lower" in DATA[keys[j]]:
                low = DATA[keys[j]][f"{ci_key}_lower"]
                high = DATA[keys[j]][f"{ci_key}_upper"]
                yhi = gy1-int((gy1-gy0)*float(high)/vmax)
                ylo = gy1-int((gy1-gy0)*float(low)/vmax)
                cx = bx+bar_w//2
                d.line((cx, yhi, cx, ylo), fill="#111827", width=3)
                d.line((cx-7, yhi, cx+7, yhi), fill="#111827", width=2)
                d.line((cx-7, ylo, cx+7, ylo), fill="#111827", width=2)
    d.text((75, 970), "Whiskers show stored 95% bootstrap CIs for AUC-PR and Recall@20% only.", fill="#475569", font=font(18))
    d.text((75, 1000), "No confidence intervals are available in the artifact for AUC-ROC or FPR@0.5.", fill="#475569", font=font(18))
    im.save(OUT / "model_metrics.png")


def chart_architecture():
    im = Image.new("RGB", (1500, 500), "#f8fafc")
    d = ImageDraw.Draw(im)
    d.text((65, 35), "PR Risk Scorer — system flow", fill="#152238", font=font(32, True))
    labels = [
        ("Git commit", "PyDriller\nstructured features"),
        ("Risk engine", "Heuristic + optional\nLR / RF / CodeBERT"),
        ("Evidence", "FAISS retrieval\nthresholded match"),
        ("Explanation", "Groq from derived data\nor local fallback"),
        ("Human review", "FastAPI + dashboard\nSQLite audit"),
    ]
    x, y, w, h, gap = 45, 170, 245, 190, 48
    fills = ["#dbeafe", "#dcfce7", "#fef3c7", "#ede9fe", "#ffe4e6"]
    for i, (title, subtitle) in enumerate(labels):
        xx = x+i*(w+gap)
        d.rounded_rectangle((xx, y, xx+w, y+h), radius=18, fill=fills[i], outline="#64748b", width=2)
        d.text((xx+18, y+22), title, fill="#152238", font=font(23, True))
        d.multiline_text((xx+18, y+72), subtitle, fill="#334155", font=font(17), spacing=8)
        if i < len(labels)-1:
            ax = xx+w+7
            d.line((ax, y+h//2, ax+gap-14, y+h//2), fill="#475569", width=4)
            d.polygon([(ax+gap-14, y+h//2), (ax+gap-26, y+h//2-9), (ax+gap-26, y+h//2+9)], fill="#475569")
    d.text((65, 405), "Raw diff stays local; the explanation component receives derived risk metadata and retrieved evidence.", fill="#475569", font=font(18))
    im.save(OUT / "system_architecture.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    chart_metrics()
    chart_architecture()
