def compute_bottom_right_position(
    screen_width: int,
    screen_height: int,
    window_width: int,
    window_height: int,
    margin: int,
) -> tuple[int, int]:
    x = max(0, screen_width - window_width - margin)
    y = max(0, screen_height - window_height - margin)
    return x, y
