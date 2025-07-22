from scipy.stats import mannwhitneyu
import numpy as np


def get_significance_code(p):
    if p <= 0.001:
        return r'(\*\*\*)'
    elif p <= 0.01:
        return r'(\*\*)'
    elif p <= 0.05:
        return r'(\*)'
    elif p <= 0.1:
        return '(.)'
    else:
        return '(ns)'


def get_mannwhitneyu_string(x, y):
    if len(x) > 0 and len(y) > 0:
        u_stat, p_val = mannwhitneyu(x, y, alternative='two-sided')
        n1 = len(x)
        n2 = len(y)
        n = n1 + n2
        mean_u = n1 * n2 / 2
        std_u = np.sqrt(n1 * n2 * (n + 1) / 12)
        z = (u_stat - mean_u) / std_u
        r = z / np.sqrt(n)

        stat_text = "\n".join(["Mann-Whitney U Test",
                               f"U={int(u_stat)}, p={p_val:.3e} {get_significance_code(p_val)}",
                               f"n1={n1}, n2={n2}",
                               f"Effect Size (r)={r:.4f}"])

        if p_val <= 0.05:
            stat_text = f"**{stat_text}**"
    else:
        stat_text = "Insufficient data"

    return stat_text
