from tenacity import RetryCallState, Retrying, stop_after_attempt

from ..utils._utils.print_formatters import italics


def create_retry_logic(max_retries: int) -> Retrying:
    """Create the retry controller."""

    return Retrying(
        stop=stop_after_attempt(max_retries),
        before=display_before_contents,
    )


def display_before_contents(retry_state: RetryCallState) -> None:
    """Print the contents of the `retry_state`"""

    if retry_state.attempt_number > 1:
        print("\r" + italics(f"Attempts | {retry_state.attempt_number}  "), end="")
    else:
        print(italics(f"Attempts | {retry_state.attempt_number}  "), end="")
