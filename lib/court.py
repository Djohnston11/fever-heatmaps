"""
Court drawing and shot-chart rendering for my Indiana Fever heat-map project

Giving these functions a table of shots returns a chart. The scraper and
the Streamlit dashboard both import from here, so the visuals look identical
everywhere.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

import numpy as np
import pandas as pd

# naming colors that will show up on the map, just using hex codes
BG     = "#0f0f1a"   # dark background
COURT  = "#e6e6e6"   # court lines (light grey)
MADE   = "#2ecc71"   # green — makes
MISSED = "#e74c3c"   # red — misses
GOLD   = "#ffcf00"   # titles
MUTED  = "#9aa"      # small subtitle text

# My WNBA stats data reports that I am using reports every shot as an (x,y)
# location measured in tenths of a foot, with the hoop at (0,0)
# The court is 50 feet wide so x is -250 to +250

def draw_court(ax, color=COURT, lw=1.6):
    """Draws a half court onto an existing axes which is ax
    Coordinates are in tenths of a foot with hoop at (0,0)"""

    elements = [
        Circle((0,0), 7.5, lw=lw, color=color, fill=False),                 # the rim
        Rectangle((-30, -7.5), 60, -1, lw=lw, color=color),                 # backboard
        Rectangle((-80, -47.5), 160, 190, lw=lw, color=color, fill=False),  # outer paint
        Rectangle((-60, -47.5), 120, 190, lw=lw, color=color, fill=False),  # inner paint
        Arc((0, 142.5), 120, 120, theta1=0, theta2=180, lw=lw, color=color), # ft circle top
        Arc((0, 142.5), 120, 120, theta1=180, theta2=0, lw=lw, ls="dashed", color=color), # ft circle bottom
        Arc((0,0), 80, 80, theta1=0, theta2=180, lw=lw, color=color),        # restricted area
        Rectangle((-220, -47.5), 0, 140, lw=lw, color=color),                # left corner 3 point line
        Rectangle((220, -47.5), 0, 140, lw=lw, color=color),                 # right corner 3 point line
        Arc((0,0), 475, 475, theta1=22, theta2=158, lw=lw, color=color),     # 3-point arc
        Rectangle((-250, -47.5), 500, 470, lw=lw, color=color, fill=False),  # court boundary
    ]
    for element in elements:
        ax.add_patch(element)
    return ax

def sample_shots(n=280, seed=7):
    """Fake shot data so I can build the chart and make sure it works
    before the scraper exists. Returns a DataFrame shaped like the real data. Delete later"""
    rng = np.random.default_rng(seed)
    xs, ys, made, shot_type = [], [], [], []

    def cluster(cx, cy, spread, count, make_prob, is_three):
        xs.extend(rng.normal(cx, spread, count))
        ys.extend(rng.normal(cy, spread, count))
        made.extend((rng.random(count) < make_prob).astype(int))
        shot_type.extend(["3PT Field Goal" if is_three else "2PT Field Goal"] * count)

    cluster(0,   10,  25, int(n*.35), .63, False)  # at the rim
    cluster(-210, 40, 30, int(n*.12), .41, True)   # left corner three
    cluster(210,  40, 30, int(n*.12), .38, True)   # right corner three
    cluster(-120, 210,35, int(n*.13), .44, True)   # left wing three
    cluster(150,  230,35, int(n*.13), .34, True)   # right wing three
    cluster(0,   150, 40, int(n*.15), .47, False)  # mid-range

    return pd.DataFrame({
        "LOC_X": xs,
        "LOC_Y": ys,
        "SHOT_MADE_FLAG": made,
        "SHOT_TYPE": shot_type,
    })

def shot_chart(shots, player_name, subtitle=None):
    """ Green makes and red misses on a half court. This will return a matplotlib figure """
    fig, ax = plt.subplots(figsize=(7.2, 6.8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Pull the columns out as arrays
    x = shots["LOC_X"].to_numpy()
    y = shots["LOC_Y"].to_numpy()
    made = shots["SHOT_MADE_FLAG"].to_numpy().astype(bool)

    # Keep front-court shots only (I am not going to include half court heaves haha)
    keep = y <= 300
    x, y, made = x[keep], y[keep], made[keep]

    # Green hollow circles for makes
    ax.scatter(x[made], y[made], marker="o", s=48, facecolors="none",
               edgecolors=MADE, linewidths=1.6, alpha=0.9,
               label=f"Missed ({int(made.sum())})")
    
    # Red x's for misses
    ax.scatter(x[~made], y[~made], marker="x", s=44, c=MISSED,
               linewidths=1.8, alpha=0.85,
               label=f"Missed ({int((~made).sum())})")
    
    draw_court(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 300)
    ax.set_aspect("equal")
    ax.axis("off")

    fg_pct = 100 * made.mean() if len(made) else 0.0
    ax.set_title(f"{player_name} - {len(made)} FGA · {fg_pct:.1f}% FG",
                 color=GOLD, fontsize=14, pad=10)
    
    if subtitle:
        fig.text(0.5, 0.02, subtitle, ha="center", color=MUTED, fontsize=8)
    ax.legend(loc="upper right", frameon=False, labelcolor=COURT, fontsize=10)
    return fig


if __name__ == "__main__":
    fig = shot_chart(sample_shots(), "Caitlin Clark (sample data)",
                     subtitle="Indiana Fever · sample render")
    plt.show()