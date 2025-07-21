def get_significance_code(p):
    if p <= 0.001:
        return '(***)'
    elif p <= 0.01:
        return '(**)'
    elif p <= 0.05:
        return '(*)'
    elif p <= 0.1:
        return '(.)'
    else:
        return '(ns)'
