from langchain_core.runnables import Runnable, RunnableConfig
from agentic_system_design.build_agent_state import State
# from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field


class Assistant:
    """
    A class to manage interactions with a runnable agent and ensure valid responses.

    Attributes:
        runnable (Runnable): An instance of the Runnable class used to invoke actions and obtain results.

    Methods:
        __call__(state: State, config: RunnableConfig) -> dict:
            Executes the runnable with the provided state and configuration, and handles invalid responses by updating
            the state with appropriate messages until a valid response is obtained.

    Args:
        runnable (Runnable): The runnable instance that performs the actual work and provides the result.
    """

    def __init__(self, runnable: Runnable):
        """
        Initializes the Assistant with a runnable instance.

        Args:
            runnable (Runnable): An instance of the Runnable class to be used for invoking actions.
        """
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        """
        Executes the runnable with the given state and configuration, and ensures the response is valid.

        The method continuously invokes the runnable until a valid response is obtained. If the response is invalid (e.g., 
        no tool calls and empty or invalid content), it updates the state with a message prompting for a real output.

        Args:
            state (State): The current state of the agent, including messages and other relevant information.
            config (RunnableConfig): Configuration settings for the runnable.

        Returns:
            dict: A dictionary containing the updated messages and result from the runnable invocation.

        Example:
            result = self(state, config)
        """
        while True:
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + \
                    [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
                messages = state["messages"] + \
                    [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


# Primary Assistant
class ToFlightBookingAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle flight updates and cancellations."""

    request: str = Field(
        description="Any necessary followup questions the update flight assistant should clarify before proceeding."
    )


class ToBookCarRentalAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle car rental bookings."""

    location: str = Field(
        description="The location where the user wants to rent a car."
    )
    start_date: str = Field(description="The start date of the car rental.")
    end_date: str = Field(description="The end date of the car rental.")
    request: str = Field(
        description="Any additional information or requests from the user regarding the car rental."
    )

    class Config:
        schema_extra = {
            "example": {
                "location": "Basel",
                "start_date": "2023-07-01",
                "end_date": "2023-07-05",
                "request": "I need a compact car with automatic transmission.",
            }
        }


class ToHotelBookingAssistant(BaseModel):
    """Transfer work to a specialized assistant to handle hotel bookings."""

    location: str = Field(
        description="The location where the user wants to book a hotel."
    )
    checkin_date: str = Field(description="The check-in date for the hotel.")
    checkout_date: str = Field(description="The check-out date for the hotel.")
    request: str = Field(
        description="Any additional information or requests from the user regarding the hotel booking."
    )

    class Config:
        schema_extra = {
            "example": {
                "location": "Zurich",
                "checkin_date": "2023-08-15",
                "checkout_date": "2023-08-20",
                "request": "I prefer a hotel near the city center with a room that has a view.",
            }
        }


class ToBookExcursionAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle trip recommendation and other excursion bookings."""

    location: str = Field(
        description="The location where the user wants to book a recommended trip."
    )
    request: str = Field(
        description="Any additional information or requests from the user regarding the trip recommendation."
    )

    class Config:
        schema_extra = {
            "example": {
                "location": "Lucerne",
                "request": "The user is interested in outdoor activities and scenic views.",
            }
        }
