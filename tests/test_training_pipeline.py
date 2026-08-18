from brainchain.training_pipeline import temporal_split


def test_temporal_split_is_chronological():
    rows = [{"captured_at": f"2026-01-{day:02d}", "x": day} for day in range(1, 21)]
    train, validation, test = temporal_split(rows)
    assert train[-1]["x"] < validation[0]["x"]
    assert validation[-1]["x"] < test[0]["x"]
    assert len(train) == 14
    assert len(validation) == 3
    assert len(test) == 3
