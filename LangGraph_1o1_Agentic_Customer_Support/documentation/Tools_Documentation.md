
# Lookup Company Policies (for RAG) Tools Description:

The assistant retrieve policy information to answer user questions. Note that enforcement of these policies still must be done within the tools/APIs themselves, since the LLM can always ignore this.

## `lookup_policy`

Consults company policies to check whether certain options are permitted.

Uses the retriever to find and return the most relevant sections of the FAQ document that pertain to the given query. This is useful for checking policy details before making changes or performing write events.

### Args:

- `query` (str): The query string to look up in the company policies.

### Returns:

- `str`: A string containing the contents of the most relevant sections of the FAQ document.

# Flight Tools Descriptions

## `fetch_user_flight_information`

Fetches all tickets for the user along with corresponding flight information and seat assignments.

This function retrieves ticket details, associated flight details, and seat assignments for all tickets belonging to the currently configured user. It connects to a SQLite database, queries the relevant tables, and returns the data as a list of dictionaries.

### Returns

- `list[dict]`: A list of dictionaries where each dictionary contains:
  - `ticket_no`: The ticket number.
  - `book_ref`: The booking reference.
  - `flight_id`: The flight identifier.
  - `flight_no`: The flight number.
  - `departure_airport`: The departure airport code.
  - `arrival_airport`: The arrival airport code.
  - `scheduled_departure`: The scheduled departure time of the flight.
  - `scheduled_arrival`: The scheduled arrival time of the flight.
  - `seat_no`: The seat number assigned to the ticket.
  - `fare_conditions`: The fare conditions for the ticket.

### Raises

- `ValueError`: If no passenger ID is configured in the context.

---

## `search_flights`

Searches for flights based on departure airport, arrival airport, and departure time range.

This function queries the SQLite database for flights that match the specified criteria and returns a list of flights sorted according to the provided filters.

### Args

- `departure_airport` (Optional[str]): The airport code from which the flight is departing.
- `arrival_airport` (Optional[str]): The airport code where the flight is arriving.
- `start_time` (Optional[date | datetime]): The earliest departure time to filter flights.
- `end_time` (Optional[date | datetime]): The latest departure time to filter flights.
- `limit` (int): The maximum number of flights to return. Defaults to 20.

### Returns

- `list[dict]`: A list of dictionaries where each dictionary contains the details of a flight including all columns from the `flights` table.

### Raises

- `sqlite3.DatabaseError`: If there is an issue with reading from the SQLite database.

---

## `update_ticket_to_new_flight`

Updates the user's ticket to a new valid flight.

This function updates the flight associated with a specific ticket number to a new flight ID. It ensures that the new flight ID is valid and that the current user owns the ticket. It also checks that the new flight's departure time is at least 3 hours from the current time.

### Args

- `ticket_no` (str): The ticket number to be updated.
- `new_flight_id` (int): The ID of the new flight to which the ticket should be updated.

### Returns

- `str`: A message indicating whether the ticket was successfully updated or if there were errors such as an invalid flight ID, the flight being too soon, or the user not owning the ticket.

### Raises

- `ValueError`: If no passenger ID is configured in the context.
- `sqlite3.DatabaseError`: If there is an issue with reading or updating the SQLite database.

---

## `Cancel_ticket`

Cancels the user's ticket and removes it from the database.

This function removes a specified ticket from the database, including its associations with flights and other related tables. It ensures that the current user owns the ticket before performing the cancellation.

### Args

- `ticket_no` (str): The ticket number to be cancelled.

### Returns

- `str`: A message indicating whether the ticket was successfully cancelled or if there were errors such as no existing ticket being found or the user not owning the ticket.

### Raises

- `ValueError`: If no passenger ID is configured in the context.
- `sqlite3.DatabaseError`: If there is an issue with reading or deleting from the SQLite database.


# Car Rentals Tools Descriptions

## `search_car_rentals`

Search for car rentals based on location, name, price tier, start date, and end date.

### Args

- `location` (Optional[str]): The location of the car rental. Defaults to `None`.
- `name` (Optional[str]): The name of the car rental company. Defaults to `None`.
- `price_tier` (Optional[str]): The price tier of the car rental. Defaults to `None`.
- `start_date` (Optional[Union[datetime, date]]): The start date of the car rental. Defaults to `None`.
- `end_date` (Optional[Union[datetime, date]]): The end date of the car rental. Defaults to `None`.

### Returns

- `list[dict]`: A list of car rental dictionaries matching the search criteria.

---

## `book_car_rental`

Book a car rental by its ID.

### Args

- `rental_id` (int): The ID of the car rental to book.

### Returns

- `str`: A message indicating whether the car rental was successfully booked or not.

---

## `update_car_rental`

Update a car rental's start and end dates by its ID.

### Args

- `rental_id` (int): The ID of the car rental to update.
- `start_date` (Optional[Union[datetime, date]]): The new start date of the car rental. Defaults to `None`.
- `end_date` (Optional[Union[datetime, date]]): The new end date of the car rental. Defaults to `None`.

### Returns

- `str`: A message indicating whether the car rental was successfully updated or not.

---

## `cancel_car_rental`

Cancel a car rental by its ID.

### Args

- `rental_id` (int): The ID of the car rental to cancel.

### Returns

- `str`: A message indicating whether the car rental was successfully cancelled or not.


# Hotels Tools Description

## `search_hotels`

Search for hotels based on location, name, price tier, check-in date, and check-out date.

### Args

- `location` (Optional[str]): The location of the hotel. Defaults to `None`.
- `name` (Optional[str]): The name of the hotel. Defaults to `None`.
- `price_tier` (Optional[str]): The price tier of the hotel. Defaults to `None`. Examples: Midscale, Upper Midscale, Upscale, Luxury.
- `checkin_date` (Optional[Union[datetime, date]]): The check-in date of the hotel. Defaults to `None`.
- `checkout_date` (Optional[Union[datetime, date]]): The check-out date of the hotel. Defaults to `None`.

### Returns

- `list[dict]`: A list of hotel dictionaries matching the search criteria.

---

## `book_hotel`

Book a hotel by its ID.

### Args

- `hotel_id` (int): The ID of the hotel to book.

### Returns

- `str`: A message indicating whether the hotel was successfully booked or not.

---

## `update_hotel`

Update a hotel's check-in and check-out dates by its ID.

### Args

- `hotel_id` (int): The ID of the hotel to update.
- `checkin_date` (Optional[Union[datetime, date]]): The new check-in date of the hotel. Defaults to `None`.
- `checkout_date` (Optional[Union[datetime, date]]): The new check-out date of the hotel. Defaults to `None`.

### Returns

- `str`: A message indicating whether the hotel was successfully updated or not.

---

## `cancel_hotel`

Cancel a hotel by its ID.

### Args

- `hotel_id` (int): The ID of the hotel to cancel.

### Returns

- `str`: A message indicating whether the hotel was successfully cancelled or not.

# Exersion Tools Descriptions

## `search_trip_recommendations`

Search for trip recommendations based on location, name, and keywords.

### Args

- `location` (Optional[str]): The location of the trip recommendation. Defaults to `None`.
- `name` (Optional[str]): The name of the trip recommendation. Defaults to `None`.
- `keywords` (Optional[str]): The keywords associated with the trip recommendation. Defaults to `None`.

### Returns

- `list[dict]`: A list of trip recommendation dictionaries matching the search criteria.

---

## `book_excursion`

Book an excursion by its recommendation ID.

### Args

- `recommendation_id` (int): The ID of the trip recommendation to book.

### Returns

- `str`: A message indicating whether the trip recommendation was successfully booked or not.

---

## `update_excursion`

Update a trip recommendation's details by its ID.

### Args

- `recommendation_id` (int): The ID of the trip recommendation to update.
- `details` (str): The new details of the trip recommendation.

### Returns

- `str`: A message indicating whether the trip recommendation was successfully updated or not.

---

## `cancel_excursion`

Cancel a trip recommendation by its ID.

### Args

- `recommendation_id` (int): The ID of the trip recommendation to cancel.

### Returns

- `str`: A message indicating whether the trip recommendation was successfully cancelled or not.
