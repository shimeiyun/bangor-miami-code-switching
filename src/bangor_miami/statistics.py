from __future__ import annotations

import math
import statistics
from collections import defaultdict


_EPS = 3.0e-14
_FPMIN = 1.0e-300
_MAX_ITER = 200
_RATE_FIELD = "switch_rate_per_1000_eligible_pairs"


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = _FPMIN if abs(d) < _FPMIN else d
    d = 1.0 / d
    h = d
    for m in range(1, _MAX_ITER + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = _FPMIN if abs(d) < _FPMIN else d
        c = 1.0 + aa / c
        c = _FPMIN if abs(c) < _FPMIN else c
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = _FPMIN if abs(d) < _FPMIN else d
        c = 1.0 + aa / c
        c = _FPMIN if abs(c) < _FPMIN else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return h


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1.0 - front * _beta_continued_fraction(b, a, 1.0 - x) / b


def gamma_q(a: float, x: float) -> float:
    if x <= 0.0:
        return 1.0
    if x < a + 1.0:
        total = term = 1.0 / a
        ap = a
        for _ in range(_MAX_ITER):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * _EPS:
                break
        p = total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return max(0.0, min(1.0, 1.0 - p))
    b = x + 1.0 - a
    c = 1.0 / _FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, _MAX_ITER + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = _FPMIN if abs(d) < _FPMIN else d
        c = b + an / c
        c = _FPMIN if abs(c) < _FPMIN else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return max(
        0.0,
        min(1.0, math.exp(-x + a * math.log(x) - math.lgamma(a)) * h),
    )


def f_survival(value: float, df1: float, df2: float) -> float:
    x = df2 / (df2 + df1 * value)
    return regularized_beta(x, df2 / 2.0, df1 / 2.0)


def t_two_sided_p(value: float, df: float) -> float:
    x = df / (df + value * value)
    return regularized_beta(x, df / 2.0, 0.5)


def _group_values(participants: list[dict]) -> dict[str, list[float]]:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in participants:
        groups[row["education_group"]].append(
            float(row[_RATE_FIELD])
        )
    return dict(groups)


def ordinary_anova(groups: dict[str, list[float]]) -> dict:
    values = [value for group in groups.values() for value in group]
    k = len(groups)
    n = len(values)
    grand = statistics.mean(values)
    ss_between = sum(
        len(group) * (statistics.mean(group) - grand) ** 2
        for group in groups.values()
    )
    ss_within = sum(
        sum((value - statistics.mean(group)) ** 2 for value in group)
        for group in groups.values()
    )
    df1 = k - 1
    df2 = n - k
    f_value = (ss_between / df1) / (ss_within / df2)
    return {
        "statistic": f_value,
        "df1": df1,
        "df2": df2,
        "p_value": f_survival(f_value, df1, df2),
        "eta_squared": ss_between / (ss_between + ss_within),
    }


def welch_anova(groups: dict[str, list[float]]) -> dict:
    summaries = []
    for values in groups.values():
        summaries.append(
            (len(values), statistics.mean(values), statistics.variance(values))
        )
    k = len(summaries)
    weights = [n / variance for n, _, variance in summaries]
    weight_total = sum(weights)
    weighted_mean = sum(
        weight * mean for weight, (_, mean, _) in zip(weights, summaries)
    ) / weight_total
    numerator = sum(
        weight * (mean - weighted_mean) ** 2
        for weight, (_, mean, _) in zip(weights, summaries)
    ) / (k - 1)
    adjustment = sum(
        (1.0 - weight / weight_total) ** 2 / (n - 1)
        for weight, (n, _, _) in zip(weights, summaries)
    )
    denominator = 1.0 + 2.0 * (k - 2) * adjustment / (k * k - 1)
    f_value = numerator / denominator
    df1 = k - 1
    df2 = (k * k - 1) / (3.0 * adjustment)
    return {
        "statistic": f_value,
        "df1": df1,
        "df2": df2,
        "p_value": f_survival(f_value, df1, df2),
    }


def kruskal_wallis(groups: dict[str, list[float]]) -> dict:
    pooled = [
        (value, group_name)
        for group_name, values in groups.items()
        for value in values
    ]
    pooled.sort(key=lambda item: item[0])
    rank_sums = defaultdict(float)
    tie_sum = 0.0
    index = 0
    while index < len(pooled):
        end = index + 1
        while end < len(pooled) and pooled[end][0] == pooled[index][0]:
            end += 1
        average_rank = ((index + 1) + end) / 2.0
        tie_count = end - index
        tie_sum += tie_count ** 3 - tie_count
        for _, group_name in pooled[index:end]:
            rank_sums[group_name] += average_rank
        index = end
    n = len(pooled)
    h_value = 12.0 / (n * (n + 1)) * sum(
        rank_sums[name] ** 2 / len(values)
        for name, values in groups.items()
    ) - 3.0 * (n + 1)
    correction = 1.0 - tie_sum / (n ** 3 - n)
    h_value /= correction
    df = len(groups) - 1
    return {
        "statistic": h_value,
        "df1": df,
        "df2": "",
        "p_value": gamma_q(df / 2.0, h_value / 2.0),
    }


def brown_forsythe(groups: dict[str, list[float]]) -> dict:
    deviations = {
        name: [abs(value - statistics.median(values)) for value in values]
        for name, values in groups.items()
    }
    result = ordinary_anova(deviations)
    return {key: result[key] for key in ("statistic", "df1", "df2", "p_value")}


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def iqr_outlier_ids(participants: list[dict]) -> list[str]:
    rows_by_group: dict[str, list[dict]] = defaultdict(list)
    for row in participants:
        rows_by_group[row["education_group"]].append(row)
    outliers = []
    for rows in rows_by_group.values():
        rates = [float(row[_RATE_FIELD]) for row in rows]
        q1 = _quantile(rates, 0.25)
        q3 = _quantile(rates, 0.75)
        lower = q1 - 1.5 * (q3 - q1)
        upper = q3 + 1.5 * (q3 - q1)
        outliers.extend(
            row["questionnaire_id"]
            for row in rows
            if not lower <= float(row[_RATE_FIELD]) <= upper
        )
    return sorted(outliers)


def hc3_regression(participants: list[dict]) -> dict:
    x = [float(row["education_level"]) for row in participants]
    y = [float(row[_RATE_FIELD]) for row in participants]
    n = len(x)
    sx = sum(x)
    sxx = sum(value * value for value in x)
    determinant = n * sxx - sx * sx
    inverse = ((sxx / determinant, -sx / determinant),
               (-sx / determinant, n / determinant))
    sy = sum(y)
    sxy = sum(xv * yv for xv, yv in zip(x, y))
    intercept = inverse[0][0] * sy + inverse[0][1] * sxy
    slope = inverse[1][0] * sy + inverse[1][1] * sxy
    meat00 = meat01 = meat11 = 0.0
    residuals = []
    for xv, yv in zip(x, y):
        residual = yv - intercept - slope * xv
        residuals.append(residual)
        leverage = (
            inverse[0][0] + 2.0 * inverse[0][1] * xv
            + inverse[1][1] * xv * xv
        )
        adjusted = residual / (1.0 - leverage)
        squared = adjusted * adjusted
        meat00 += squared
        meat01 += squared * xv
        meat11 += squared * xv * xv
    covariance00 = (
        inverse[0][0] ** 2 * meat00
        + 2.0 * inverse[0][0] * inverse[0][1] * meat01
        + inverse[0][1] ** 2 * meat11
    )
    covariance11 = (
        inverse[1][0] ** 2 * meat00
        + 2.0 * inverse[1][0] * inverse[1][1] * meat01
        + inverse[1][1] ** 2 * meat11
    )
    intercept_se = math.sqrt(covariance00)
    slope_se = math.sqrt(covariance11)
    t_value = slope / slope_se
    df = n - 2
    y_mean = statistics.mean(y)
    ss_total = sum((value - y_mean) ** 2 for value in y)
    ss_residual = sum(value * value for value in residuals)
    return {
        "intercept": intercept,
        "intercept_hc3_se": intercept_se,
        "slope_per_education_level": slope,
        "slope_hc3_se": slope_se,
        "slope_t": t_value,
        "slope_df": df,
        "slope_p_value": t_two_sided_p(t_value, df),
        "slope_95ci_lower_normal": slope - 1.96 * slope_se,
        "slope_95ci_upper_normal": slope + 1.96 * slope_se,
        "r_squared": 1.0 - ss_residual / ss_total,
        "n": n,
    }


def inferential_analysis(participants: list[dict]) -> dict:
    groups = _group_values(participants)
    ordinary = ordinary_anova(groups)
    outlier_ids = iqr_outlier_ids(participants)
    reduced = [
        row for row in participants if row["questionnaire_id"] not in outlier_ids
    ]
    reduced_groups = _group_values(reduced)
    tests = [
        {"test": "Brown-Forsythe variance test", **brown_forsythe(groups),
         "role": "variance diagnostic"},
        {"test": "Welch one-way ANOVA", **welch_anova(groups),
         "role": "preferred exploratory group comparison"},
        {"test": "Kruskal-Wallis", **kruskal_wallis(groups),
         "role": "nonparametric sensitivity analysis"},
        {"test": "Ordinary one-way ANOVA",
         **{key: ordinary[key] for key in ("statistic", "df1", "df2", "p_value")},
         "role": "proposal-aligned supplementary analysis"},
        {"test": "Welch ANOVA excluding IQR outliers",
         **welch_anova(reduced_groups), "role": "outlier sensitivity analysis"},
        {"test": "Kruskal-Wallis excluding IQR outliers",
         **kruskal_wallis(reduced_groups), "role": "outlier sensitivity analysis"},
    ]
    return {
        "tests": tests,
        "ordinary_anova_eta_squared": ordinary["eta_squared"],
        "hc3_regression": hc3_regression(participants),
        "outlier_questionnaire_ids": outlier_ids,
        "n_after_outlier_exclusion": len(reduced),
    }
