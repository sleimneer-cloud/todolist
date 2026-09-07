from todolist.geometry import compute_bottom_right_position


def test_bottom_right_with_margin():
    x, y = compute_bottom_right_position(
        screen_width=1920, screen_height=1080, window_width=300, window_height=420, margin=16
    )
    assert (x, y) == (1920 - 300 - 16, 1080 - 420 - 16)


def test_bottom_right_zero_margin():
    x, y = compute_bottom_right_position(
        screen_width=800, screen_height=600, window_width=200, window_height=200, margin=0
    )
    assert (x, y) == (600, 400)


def test_window_larger_than_screen_clamps_to_zero():
    x, y = compute_bottom_right_position(
        screen_width=400, screen_height=300, window_width=500, window_height=500, margin=16
    )
    assert (x, y) == (0, 0)
