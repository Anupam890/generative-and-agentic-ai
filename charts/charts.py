"""
Chart generation module for ResearchMind AI.
Parses structured JSON chart data from the LLM and renders matplotlib figures.
"""

import json
import re
import io
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for Streamlit / headless use
import matplotlib.pyplot as plt


def parse_chart_data(raw_text: str) -> list[dict]:
    """Parse the LLM's JSON response into a list of chart spec dicts.
    
    Returns an empty list if parsing fails or the data is invalid.
    """
    text = raw_text.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    if not text or text == "[]":
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to find a JSON array inside the text
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return []
        else:
            return []

    if not isinstance(data, list):
        return []

    valid_charts = []
    for item in data:
        if not isinstance(item, dict):
            continue
        required = {"title", "type", "labels", "values"}
        if not required.issubset(item.keys()):
            continue
        if item["type"] not in ("bar", "pie", "line"):
            continue
        if not isinstance(item["labels"], list) or not isinstance(item["values"], list):
            continue
        if len(item["labels"]) != len(item["values"]):
            continue
        if len(item["values"]) == 0:
            continue
        # Ensure values are numeric
        try:
            item["values"] = [float(v) for v in item["values"]]
        except (ValueError, TypeError):
            continue
        valid_charts.append(item)

    return valid_charts[:4]  # Max 4 charts


def generate_charts(chart_specs: list[dict]) -> list[tuple[str, bytes]]:
    """Generate matplotlib chart images from chart specs.
    
    Returns a list of (title, png_bytes) tuples.
    """
    if not chart_specs:
        return []

    results = []
    # Color palette
    colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
              "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac"]

    for spec in chart_specs:
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")

        chart_type = spec["type"]
        labels = spec["labels"]
        values = spec["values"]
        title = spec.get("title", "Chart")
        xlabel = spec.get("xlabel", "")
        ylabel = spec.get("ylabel", "")

        try:
            if chart_type == "bar":
                bar_colors = [colors[i % len(colors)] for i in range(len(labels))]
                ax.bar(labels, values, color=bar_colors, edgecolor="white", linewidth=0.5)
                ax.set_xlabel(xlabel, color="white", fontsize=10)
                ax.set_ylabel(ylabel, color="white", fontsize=10)
                if len(labels) > 4:
                    plt.xticks(rotation=45, ha="right")

            elif chart_type == "pie":
                pie_colors = [colors[i % len(colors)] for i in range(len(labels))]
                wedges, texts, autotexts = ax.pie(
                    values, labels=labels, colors=pie_colors, autopct="%1.1f%%",
                    startangle=140, textprops={"color": "white", "fontsize": 9}
                )
                for t in autotexts:
                    t.set_color("white")
                    t.set_fontsize(8)

            elif chart_type == "line":
                ax.plot(labels, values, color=colors[0], marker="o",
                        linewidth=2, markersize=6, markerfacecolor=colors[1])
                ax.fill_between(range(len(labels)), values, alpha=0.15, color=colors[0])
                ax.set_xlabel(xlabel, color="white", fontsize=10)
                ax.set_ylabel(ylabel, color="white", fontsize=10)
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels)
                if len(labels) > 4:
                    plt.xticks(rotation=45, ha="right")

            ax.set_title(title, color="white", fontsize=13, fontweight="bold", pad=12)
            ax.tick_params(colors="white", labelsize=9)
            for spine in ax.spines.values():
                spine.set_color("#333333")

            plt.tight_layout()

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                        facecolor=fig.get_facecolor(), edgecolor="none")
            buf.seek(0)
            results.append((title, buf.getvalue()))

        except Exception:
            pass  # Skip charts that fail to render
        finally:
            plt.close(fig)

    return results
