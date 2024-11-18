from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """
    Push or pop the state: Updates the dialog stack by either adding a new state or removing the last state.

    Args:
        left (list[str]): The current state of the dialog stack, represented as a list of strings.
        right (Optional[str]): The operation to perform. If `right` is None, the function returns the current state.
                               If `right` is "pop", the last element of the stack is removed. Otherwise, `right` is 
                               appended to the stack.

    Returns:
        list[str]: The updated dialog stack.
    """
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class State(TypedDict):
    """
    Represents the state of a dialog system.

    Attributes:
        messages (list[AnyMessage]): A list of messages, annotated with the `add_messages` function for additional 
                                     processing or validation.
        user_info (str): Information about the user.
        dialog_state (list[str]): A list representing the dialog stack, annotated with the `update_dialog_stack` 
                                  function to manage state transitions. Possible states include "assistant", 
                                  "update_flight", "book_car_rental", "book_hotel", and "book_excursion".
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                "assistant",
                "update_flight",
                "book_car_rental",
                "book_hotel",
                "book_excursion",
            ]
        ],
        update_dialog_stack,
    ]
