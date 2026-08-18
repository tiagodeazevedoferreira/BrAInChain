from datetime import datetime, timedelta, timezone


def classify(values, threshold):
    counts = {"up": 0, "down": 0, "neutral": 0}
    for value in values:
        if value >= threshold:
            counts["up"] += 1
        elif value <= -threshold:
            counts["down"] += 1
        else:
            counts["neutral"] += 1
    return counts


def test_threshold_boundaries_are_symmetric():
    counts = classify([-0.01, -0.0025, -0.001, 0.0, 0.001, 0.0025, 0.01], 0.0025)
    assert counts == {"up": 2, "down": 2, "neutral": 3}


def test_fine_thresholds_are_ordered():
    values = [-0.004, -0.002, -0.0008, 0.0007, 0.0018, 0.0032]
    previous = None
    for threshold in (0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004):
        counts = classify(values, threshold)
        minority = min(counts.values())
        if previous is not None:
            assert minority >= 0
        previous = minority
