from tbo.geometry import Point, Rect, handle_at, normalized_points, resize_rect


def test_resize_from_se_grows_and_keeps_origin() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "se", Point(20, 10))
    assert (result.x, result.y) == (0, 0)
    assert (result.width, result.height) == (120, 60)


def test_resize_from_nw_keeps_bottom_right_fixed() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "nw", Point(-20, -10))
    assert (result.x, result.y) == (-20, -10)
    assert (result.width, result.height) == (120, 60)


def test_resize_from_w_only_changes_width() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "w", Point(30, 0))
    assert result.height == 50
    assert result.y == 0
    assert (result.x, result.width) == (30, 70)


def test_resize_from_n_only_changes_height() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "n", Point(0, -30))
    assert result.width == 100
    assert (result.y, result.height) == (-30, 80)


def test_resize_keeps_aspect_ratio_when_asked() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "se", Point(100, 0), keep_aspect=True)
    assert result.width == 200
    assert result.height == 100


def test_resize_from_centre_keeps_centre_fixed() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "se", Point(20, 20), from_center=True)
    assert (result.x, result.y) == (-20, -20)
    assert (result.width, result.height) == (140, 90)


def test_resize_enforces_minimum_size() -> None:
    result = resize_rect(Rect(0, 0, 100, 50), "se", Point(-500, -500), min_size=8)
    assert (result.width, result.height) == (8, 8)


def test_unknown_handle_is_rejected() -> None:
    try:
        resize_rect(Rect(0, 0, 10, 10), "middle", Point(1, 1))
    except ValueError as error:
        assert "handle" in str(error)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_handle_at_finds_closest_handle() -> None:
    rect = Rect(0, 0, 100, 50)
    assert handle_at(rect, Point(100, 50), 2.0) == "se"
    assert handle_at(rect, Point(50, 0), 2.0) == "n"
    assert handle_at(rect, Point(50, 25), 2.0) is None


def test_normalized_points_are_relative_to_bounds() -> None:
    points = normalized_points([(10, 20), (30, 40)], Rect(10, 20, 20, 20))
    assert points == [(0.0, 0.0), (1.0, 1.0)]
