from fastapi import Header


def get_device_id(
    x_device_id: str = Header(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9-]+$"),
) -> str:
    # the browser makes a random id once and sends it with every request.
    # only letters, digits and dashes are allowed, so a real id can never
    # equal the "__global__" row used for the overall usage cap
    return x_device_id