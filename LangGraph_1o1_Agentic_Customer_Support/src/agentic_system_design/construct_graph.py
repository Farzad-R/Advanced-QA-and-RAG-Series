from langgraph.prebuilt import tools_condition
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal
from tools.tools_flights import fetch_user_flight_information
from utils.utilities import create_entry_node, create_tool_node_with_fallback
from agentic_system_design.build_agent_assistants import Assistant, ToFlightBookingAssistant, ToBookCarRentalAssistant, ToHotelBookingAssistant, ToBookExcursionAssistant
from agentic_system_design.build_agent_runnables import AIAgentRunnables
from agentic_system_design.complete_or_escalate import CompleteOrEscalate
from agentic_system_design.build_agent_state import State
from langchain_core.messages import ToolMessage
AGENT_RUNNABLES = AIAgentRunnables()


class AgenticGraph:
    def __init__(self) -> None:
        self.builder = StateGraph(State)
        self.builder.add_node("fetch_user_info", self.user_info)
        self.builder.add_edge(START, "fetch_user_info")

    def user_info(self, state: State):
        return {"user_info": fetch_user_flight_information.invoke({})}

    # ============================
    # Flight booking assistant
    # ============================

    def add_flight_nodes_to_graph(self):
        self.builder.add_node(
            "enter_update_flight",
            create_entry_node(
                "Flight Updates & Booking Assistant", "update_flight"),
        )
        self.builder.add_node("update_flight", Assistant(
            AGENT_RUNNABLES.update_flight_runnable))
        self.builder.add_edge("enter_update_flight", "update_flight")
        self.builder.add_node(
            "update_flight_sensitive_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.update_flight_sensitive_tools),
        )
        self.builder.add_node(
            "update_flight_safe_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.update_flight_safe_tools),
        )

        def route_update_flight(
            state: State,
        ) -> Literal[
            "update_flight_sensitive_tools",
            "update_flight_safe_tools",
            "leave_skill",
            "__end__",
        ]:
            route = tools_condition(state)
            if route == END:
                return END
            tool_calls = state["messages"][-1].tool_calls
            did_cancel = any(
                tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
            if did_cancel:
                return "leave_skill"
            safe_toolnames = [
                t.name for t in AGENT_RUNNABLES.update_flight_safe_tools]
            if all(tc["name"] in safe_toolnames for tc in tool_calls):
                return "update_flight_safe_tools"
            return "update_flight_sensitive_tools"

        self.builder.add_edge("update_flight_sensitive_tools", "update_flight")
        self.builder.add_edge("update_flight_safe_tools", "update_flight")
        self.builder.add_conditional_edges(
            "update_flight", route_update_flight)

        # This node will be shared for exiting all specialized assistants

        def pop_dialog_state(state: State) -> dict:
            """Pop the dialog stack and return to the main assistant.

            This lets the full graph explicitly track the dialog flow and delegate control
            to specific sub-graphs.
            """
            messages = []
            if state["messages"][-1].tool_calls:
                # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
                messages.append(
                    ToolMessage(
                        content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                        tool_call_id=state["messages"][-1].tool_calls[0]["id"],
                    )
                )
            return {
                "dialog_state": "pop",
                "messages": messages,
            }

        self.builder.add_node("leave_skill", pop_dialog_state)
        self.builder.add_edge("leave_skill", "primary_assistant")

    # ====================
    # Car rental assistant
    # ====================
    def add_car_rental_nodes_to_graph(self):
        self.builder.add_node(
            "enter_book_car_rental",
            create_entry_node("Car Rental Assistant", "book_car_rental"),
        )
        self.builder.add_node("book_car_rental", Assistant(
            AGENT_RUNNABLES.book_car_rental_runnable))
        self.builder.add_edge("enter_book_car_rental", "book_car_rental")
        self.builder.add_node(
            "book_car_rental_safe_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.book_car_rental_safe_tools),
        )
        self.builder.add_node(
            "book_car_rental_sensitive_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.book_car_rental_sensitive_tools),
        )

        def route_book_car_rental(
            state: State,
        ) -> Literal[
            "book_car_rental_safe_tools",
            "book_car_rental_sensitive_tools",
            "leave_skill",
            "__end__",
        ]:
            route = tools_condition(state)
            if route == END:
                return END
            tool_calls = state["messages"][-1].tool_calls
            did_cancel = any(
                tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
            if did_cancel:
                return "leave_skill"
            safe_toolnames = [
                t.name for t in AGENT_RUNNABLES.book_car_rental_safe_tools]
            if all(tc["name"] in safe_toolnames for tc in tool_calls):
                return "book_car_rental_safe_tools"
            return "book_car_rental_sensitive_tools"

        self.builder.add_edge(
            "book_car_rental_sensitive_tools", "book_car_rental")
        self.builder.add_edge("book_car_rental_safe_tools", "book_car_rental")
        self.builder.add_conditional_edges(
            "book_car_rental", route_book_car_rental)

    # ========================
    # Hotel booking assistant
    # ========================
    def add_hotel_booking_nodes_to_graph(self):
        self.builder.add_node(
            "enter_book_hotel", create_entry_node(
                "Hotel Booking Assistant", "book_hotel")
        )
        self.builder.add_node("book_hotel", Assistant(
            AGENT_RUNNABLES.book_hotel_runnable))
        self.builder.add_edge("enter_book_hotel", "book_hotel")
        self.builder.add_node(
            "book_hotel_safe_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.book_hotel_safe_tools),
        )
        self.builder.add_node(
            "book_hotel_sensitive_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.book_hotel_sensitive_tools),
        )

        def route_book_hotel(
            state: State,
        ) -> Literal[
            "leave_skill", "book_hotel_safe_tools", "book_hotel_sensitive_tools", "__end__"
        ]:
            route = tools_condition(state)
            if route == END:
                return END
            tool_calls = state["messages"][-1].tool_calls
            did_cancel = any(
                tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
            if did_cancel:
                return "leave_skill"
            tool_names = [
                t.name for t in AGENT_RUNNABLES.book_hotel_safe_tools]
            if all(tc["name"] in tool_names for tc in tool_calls):
                return "book_hotel_safe_tools"
            return "book_hotel_sensitive_tools"

        self.builder.add_edge("book_hotel_sensitive_tools", "book_hotel")
        self.builder.add_edge("book_hotel_safe_tools", "book_hotel")
        self.builder.add_conditional_edges("book_hotel", route_book_hotel)

    # ========================
    # Excursion assistant
    # ========================
    def add_excursion_nodes_to_graph(self):
        self.builder.add_node(
            "enter_book_excursion",
            create_entry_node(
                "Trip Recommendation Assistant", "book_excursion"),
        )
        self.builder.add_node("book_excursion", Assistant(
            AGENT_RUNNABLES.book_excursion_runnable))
        self.builder.add_edge("enter_book_excursion", "book_excursion")
        self.builder.add_node(
            "book_excursion_safe_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.book_excursion_safe_tools),
        )
        self.builder.add_node(
            "book_excursion_sensitive_tools",
            create_tool_node_with_fallback(
                AGENT_RUNNABLES.book_excursion_sensitive_tools),
        )

        def route_book_excursion(
            state: State,
        ) -> Literal[
            "book_excursion_safe_tools",
            "book_excursion_sensitive_tools",
            "leave_skill",
            "__end__",
        ]:
            route = tools_condition(state)
            if route == END:
                return END
            tool_calls = state["messages"][-1].tool_calls
            did_cancel = any(
                tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
            if did_cancel:
                return "leave_skill"
            tool_names = [
                t.name for t in AGENT_RUNNABLES.book_excursion_safe_tools]
            if all(tc["name"] in tool_names for tc in tool_calls):
                return "book_excursion_safe_tools"
            return "book_excursion_sensitive_tools"

        self.builder.add_edge(
            "book_excursion_sensitive_tools", "book_excursion")
        self.builder.add_edge("book_excursion_safe_tools", "book_excursion")
        self.builder.add_conditional_edges(
            "book_excursion", route_book_excursion)

    # ========================
    # Primary assistant
    # ========================
    def add_primary_assistant_nodes_to_graph(self):
        self.builder.add_node("primary_assistant", Assistant(
            AGENT_RUNNABLES.primary_assistant_runnable))
        self.builder.add_node(
            "primary_assistant_tools", create_tool_node_with_fallback(
                AGENT_RUNNABLES.primary_assistant_tools)
        )

        def route_primary_assistant(
            state: State,
        ) -> Literal[
            "primary_assistant_tools",
            "enter_update_flight",
            "enter_book_hotel",
            "enter_book_excursion",
            "__end__",
        ]:
            route = tools_condition(state)
            if route == END:
                return END
            tool_calls = state["messages"][-1].tool_calls
            if tool_calls:
                if tool_calls[0]["name"] == ToFlightBookingAssistant.__name__:
                    return "enter_update_flight"
                elif tool_calls[0]["name"] == ToBookCarRentalAssistant.__name__:
                    return "enter_book_car_rental"
                elif tool_calls[0]["name"] == ToHotelBookingAssistant.__name__:
                    return "enter_book_hotel"
                elif tool_calls[0]["name"] == ToBookExcursionAssistant.__name__:
                    return "enter_book_excursion"
                return "primary_assistant_tools"
            raise ValueError("Invalid route")

        # The assistant can route to one of the delegated assistants,
        # directly use a tool, or directly respond to the user
        self.builder.add_conditional_edges(
            "primary_assistant",
            route_primary_assistant,
            {
                "enter_update_flight": "enter_update_flight",
                "enter_book_car_rental": "enter_book_car_rental",
                "enter_book_hotel": "enter_book_hotel",
                "enter_book_excursion": "enter_book_excursion",
                "primary_assistant_tools": "primary_assistant_tools",
                END: END,
            },
        )
        self.builder.add_edge("primary_assistant_tools", "primary_assistant")

        # Each delegated workflow can directly respond to the user
        # When the user responds, we want to return to the currently active workflow

        def route_to_workflow(
            state: State,
        ) -> Literal[
            "primary_assistant",
            "update_flight",
            "book_car_rental",
            "book_hotel",
            "book_excursion",
        ]:
            """If we are in a delegated state, route directly to the appropriate assistant."""
            dialog_state = state.get("dialog_state")
            if not dialog_state:
                return "primary_assistant"
            return dialog_state[-1]

        self.builder.add_conditional_edges(
            "fetch_user_info", route_to_workflow)

    def Compile_graph(self):
        self.add_flight_nodes_to_graph()
        self.add_car_rental_nodes_to_graph()
        self.add_hotel_booking_nodes_to_graph()
        self.add_excursion_nodes_to_graph()
        self.add_primary_assistant_nodes_to_graph()

        # Compile graph
        memory = MemorySaver()
        graph = self.builder.compile(
            checkpointer=memory,
            # Let the user approve or deny the use of sensitive tools
            interrupt_before=[
                "update_flight_sensitive_tools",
                "book_car_rental_sensitive_tools",
                "book_hotel_sensitive_tools",
                "book_excursion_sensitive_tools",
            ],
        )
        return graph
