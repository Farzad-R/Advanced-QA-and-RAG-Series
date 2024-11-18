import shutil
import pandas as pd
import sqlite3
from typing import Callable
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from build_agent_state import State


def handle_tool_error(state) -> dict:
    """
    Handles errors by formatting them into a message and adding them to the chat history.

    This function retrieves the error from the given state and formats it into a `ToolMessage`, which is then
    added to the chat history. It uses the latest tool calls from the state to attach the error message.

    Args:
        state (dict): The current state of the tool, which includes error information and tool calls.

    Returns:
        dict: A dictionary containing a list of `ToolMessage` objects with error information.
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    """
    Creates a `ToolNode` with fallback error handling.

    This function creates a `ToolNode` object and configures it to use a fallback function for error handling. 
    The fallback function handles errors by calling `handle_tool_error`.

    Args:
        tools (list): A list of tools to be included in the `ToolNode`.

    Returns:
        dict: A `ToolNode` configured with fallback error handling.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    """
    Prints the current state and messages of an event, with optional truncation for long messages.

    This function prints information about the current dialog state and the latest message in the event. If the message 
    is too long, it is truncated to a specified maximum length.

    Args:
        event (dict): The event containing dialog state and messages.
        _printed (set): A set of message IDs that have already been printed, to avoid duplicate output.
        max_length (int, optional): The maximum length of the message to print before truncating. Defaults to 1500.
    """
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    """
    Creates an entry node function for transitioning the dialog state within a conversation.

    Args:
        assistant_name (str): The name of the assistant to be referenced in the tool message.
        new_dialog_state (str): The new state of the dialog after the transition.

    Returns:
        Callable: A function that, when called with a `State` object, returns a dictionary containing a tool message 
                  and the updated dialog state.

    The returned `entry_node` function performs the following:
        - Extracts the `tool_call_id` from the last message's first tool call in the `State`.
        - Constructs a tool message informing the user that the assistant is now acting as the specified `assistant_name`.
        - Updates the dialog state to the provided `new_dialog_state`.
        - The tool message instructs the assistant on how to proceed with the user's intent, emphasizing that the task 
          is incomplete until the appropriate tool is successfully invoked.
        - If the user changes their mind or needs additional help, the message advises calling the `CompleteOrEscalate` 
          function to allow the primary assistant to regain control.
    """
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the booking, update, other other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node


def update_dates(file, backup_file):
    shutil.copy(backup_file, file)
    conn = sqlite3.connect(file)

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    tdf["bookings"]["book_date"] = (
        pd.to_datetime(tdf["bookings"]["book_date"].replace(
            "\\N", pd.NaT), utc=True)
        + time_diff
    )

    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    for column in datetime_columns:
        tdf["flights"][column] = (
            pd.to_datetime(tdf["flights"][column].replace(
                "\\N", pd.NaT)) + time_diff
        )

    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

    return file
