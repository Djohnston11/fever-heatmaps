"""Renders a sample shot chart to prove the library works before I create the scraper.
Run from the repo root: python examples/demo.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
from lib import shot_chart, sample_shots

fig = shot_chart(sample_shots(), "Caitlin Clark (sample data)",
                 subtitle="Indiana Fever · sample render")

os.makedirs("output", exist_ok=True)
fig.savefig("output/sample_shot_chart.png", dpi=130,
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("Wrote output/sample_shot_chart.png")