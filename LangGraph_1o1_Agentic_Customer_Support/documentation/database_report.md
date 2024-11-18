### Database Report

This report provides an overview of the database, including its structure, key metrics, and insights derived from the data.

#### Table: aircrafts_data

Columns:

- **aircraft_code** (TEXT)
- **model** (TEXT)
- **range** (INTEGER)

Row Count: 9

Estimated Table Size: 111760.00 KB

Sample Data:

|    | aircraft_code   | model               |   range |
|---:|:----------------|:--------------------|--------:|
|  0 | 773             | Boeing 777-300      |   11100 |
|  1 | 763             | Boeing 767-300      |    7900 |
|  2 | SU9             | Sukhoi Superjet-100 |    3000 |
|  3 | 320             | Airbus A320-200     |    5700 |
|  4 | 321             | Airbus A321-200     |    5600 |

Summary Statistics:

|       |    range |
|:------|---------:|
| count |     9    |
| mean  |  5344.44 |
| std   |  3013.76 |
| min   |  1200    |
| 25%   |  3000    |
| 50%   |  5600    |
| 75%   |  6700    |
| max   | 11100    |


#### Table: airports_data

Columns:

- **airport_code** (TEXT)
- **airport_name** (TEXT)
- **city** (TEXT)
- **coordinates** (TEXT)
- **timezone** (TEXT)

Row Count: 115

Estimated Table Size: 111760.00 KB

Sample Data:

|    | airport_code   | airport_name                                     | city        | coordinates          | timezone            |
|---:|:---------------|:-------------------------------------------------|:------------|:---------------------|:--------------------|
|  0 | ATL            | Hartsfield-Jackson Atlanta International Airport | Atlanta     | [33.6407, -84.4277]  | America/New_York    |
|  1 | PEK            | Beijing Capital International Airport            | Beijing     | [40.0799, 116.6031]  | Asia/Shanghai       |
|  2 | DXB            | Dubai International Airport                      | Dubai       | [25.2532, 55.3657]   | Asia/Dubai          |
|  3 | LAX            | Los Angeles International Airport                | Los Angeles | [33.9416, -118.4085] | America/Los_Angeles |
|  4 | HND            | Tokyo Haneda Airport                             | Tokyo       | [35.5494, 139.7798]  | Asia/Tokyo          |


#### Table: boarding_passes

Columns:

- **ticket_no** (TEXT)
- **flight_id** (INTEGER)
- **boarding_no** (INTEGER)
- **seat_no** (TEXT)

Row Count: 579686

Estimated Table Size: 111760.00 KB

Sample Data:

|    |        ticket_no |   flight_id |   boarding_no | seat_no   |
|---:|-----------------:|------------:|--------------:|:----------|
|  0 | 0060005435212351 |       30625 |             1 | 2D        |
|  1 | 0060005435212386 |       30625 |             2 | 3G        |
|  2 | 0060005435212381 |       30625 |             3 | 4H        |
|  3 | 0060005432211370 |       30625 |             4 | 5D        |
|  4 | 0060005435212357 |       30625 |             5 | 11A       |

Summary Statistics:

|       |   flight_id |   boarding_no |
|:------|------------:|--------------:|
| count |   579686    |   579686      |
| mean  |    13720.8  |       54.9715 |
| std   |     9713.92 |       58.819  |
| min   |        1    |        1      |
| 25%   |     5351    |       15      |
| 50%   |    11217    |       36      |
| 75%   |    22481    |       72      |
| max   |    33120    |      374      |


#### Table: bookings

Columns:

- **book_ref** (TEXT)
- **book_date** (TIMESTAMP)
- **total_amount** (INTEGER)

Row Count: 262788

Estimated Table Size: 111760.00 KB

Sample Data:

|    | book_ref   | book_date                        |   total_amount |
|---:|:-----------|:---------------------------------|---------------:|
|  0 | 00000F     | 2024-03-20 01:21:03.561731+00:00 |         265700 |
|  1 | 000012     | 2024-03-29 07:11:03.561731+00:00 |          37900 |
|  2 | 000068     | 2024-04-30 12:36:03.561731+00:00 |          18100 |
|  3 | 000181     | 2024-04-25 11:37:03.561731+00:00 |         131800 |
|  4 | 0002D8     | 2024-04-22 19:49:03.561731+00:00 |          23600 |

Summary Statistics:

|       |    total_amount |
|:------|----------------:|
| count | 262788          |
| mean  |  79025.6        |
| std   |  77621.9        |
| min   |   3400          |
| 25%   |  29000          |
| 50%   |  55900          |
| 75%   |  99200          |
| max   |      1.2045e+06 |


#### Table: flights

Columns:

- **flight_id** (INTEGER)
- **flight_no** (TEXT)
- **scheduled_departure** (TIMESTAMP)
- **scheduled_arrival** (TIMESTAMP)
- **departure_airport** (TEXT)
- **arrival_airport** (TEXT)
- **status** (TEXT)
- **aircraft_code** (TEXT)
- **actual_departure** (TIMESTAMP)
- **actual_arrival** (TIMESTAMP)

Row Count: 33121

Estimated Table Size: 111760.00 KB

Sample Data:

|    |   flight_id | flight_no   | scheduled_departure              | scheduled_arrival                | departure_airport   | arrival_airport   | status    | aircraft_code   | actual_departure   | actual_arrival   |
|---:|------------:|:------------|:---------------------------------|:---------------------------------|:--------------------|:------------------|:----------|:----------------|:-------------------|:-----------------|
|  0 |        1185 | QR0051      | 2024-05-26 03:59:03.561731-04:00 | 2024-05-26 09:04:03.561731-04:00 | BSL                 | BKK               | Scheduled | 319             |                    |                  |
|  1 |        3979 | MU0066      | 2024-05-10 08:59:03.561731-04:00 | 2024-05-10 11:44:03.561731-04:00 | SHA                 | CUN               | Scheduled | CR2             |                    |                  |
|  2 |        4739 | QF0126      | 2024-05-21 06:39:03.561731-04:00 | 2024-05-21 08:24:03.561731-04:00 | SHA                 | AMS               | Scheduled | 763             |                    |                  |
|  3 |        5502 | LX0136      | 2024-05-28 03:59:03.561731-04:00 | 2024-05-28 05:29:03.561731-04:00 | OSL                 | PRG               | Scheduled | 763             |                    |                  |
|  4 |        6938 | IB0075      | 2024-05-20 06:34:03.561731-04:00 | 2024-05-20 07:29:03.561731-04:00 | OSL                 | RGN               | Scheduled | SU9             |                    |                  |

Summary Statistics:

|       |   flight_id |
|:------|------------:|
| count |    33121    |
| mean  |    16561    |
| std   |     9561.35 |
| min   |        1    |
| 25%   |     8281    |
| 50%   |    16561    |
| 75%   |    24841    |
| max   |    33121    |


#### Table: seats

Columns:

- **aircraft_code** (TEXT)
- **seat_no** (TEXT)
- **fare_conditions** (TEXT)

Row Count: 1339

Estimated Table Size: 111760.00 KB

Sample Data:

|    |   aircraft_code | seat_no   | fare_conditions   |
|---:|----------------:|:----------|:------------------|
|  0 |             319 | 2A        | Business          |
|  1 |             319 | 2C        | Business          |
|  2 |             319 | 2D        | Business          |
|  3 |             319 | 2F        | Business          |
|  4 |             319 | 3A        | Business          |


#### Table: ticket_flights

Columns:

- **ticket_no** (TEXT)
- **flight_id** (INTEGER)
- **fare_conditions** (TEXT)
- **amount** (INTEGER)

Row Count: 1045726

Estimated Table Size: 111760.00 KB

Sample Data:

|    |        ticket_no |   flight_id | fare_conditions   |   amount |
|---:|-----------------:|------------:|:------------------|---------:|
|  0 | 0060005432159776 |       30625 | Business          |    42100 |
|  1 | 0060005435212351 |       30625 | Business          |    42100 |
|  2 | 0060005435212386 |       30625 | Business          |    42100 |
|  3 | 0060005435212381 |       30625 | Business          |    42100 |
|  4 | 0060005432211370 |       30625 | Business          |    42100 |

Summary Statistics:

|       |       flight_id |           amount |
|:------|----------------:|-----------------:|
| count |     1.04573e+06 |      1.04573e+06 |
| mean  | 14110.1         |  19858.9         |
| std   |  9732.94        |  22612.4         |
| min   |     1           |   3000           |
| 25%   |  5501           |   7200           |
| 50%   | 11926           |  13400           |
| 75%   | 23039           |  23100           |
| max   | 33121           | 203300           |


#### Table: tickets

Columns:

- **ticket_no** (TEXT)
- **book_ref** (TEXT)
- **passenger_id** (TEXT)

Row Count: 366733

Estimated Table Size: 111760.00 KB

Sample Data:

|    |        ticket_no | book_ref   | passenger_id   |
|---:|-----------------:|:-----------|:---------------|
|  0 | 9880005432000987 | 06B046     | 8149 604011    |
|  1 | 9880005432000988 | 06B046     | 8499 420203    |
|  2 | 9880005432000989 | E170C3     | 1011 752484    |
|  3 | 9880005432000990 | E170C3     | 4849 400049    |
|  4 | 9880005432000991 | F313DD     | 6615 976589    |


#### Table: car_rentals

Columns:

- **id** (INTEGER)
- **name** (TEXT)
- **location** (TEXT)
- **price_tier** (TEXT)
- **start_date** (DATE)
- **end_date** (DATE)
- **booked** (INTEGER)

Row Count: 10

Estimated Table Size: 111760.00 KB

Sample Data:

|    |   id | name     | location   | price_tier   | start_date   | end_date   |   booked |
|---:|-----:|:---------|:-----------|:-------------|:-------------|:-----------|---------:|
|  0 |    1 | Europcar | Basel      | Economy      | 2024-04-14   | 2024-04-11 |        0 |
|  1 |    2 | Avis     | Basel      | Luxury       | 2024-04-10   | 2024-04-20 |        0 |
|  2 |    3 | Hertz    | Zurich     | Midsize      | 2024-04-10   | 2024-04-07 |        0 |
|  3 |    4 | Sixt     | Bern       | SUV          | 2024-04-20   | 2024-04-26 |        0 |
|  4 |    5 | Budget   | Lucerne    | Compact      | 2024-04-01   | 2024-04-19 |        0 |

Summary Statistics:

|       |       id |   booked |
|:------|---------:|---------:|
| count | 10       |       10 |
| mean  |  5.5     |        0 |
| std   |  3.02765 |        0 |
| min   |  1       |        0 |
| 25%   |  3.25    |        0 |
| 50%   |  5.5     |        0 |
| 75%   |  7.75    |        0 |
| max   | 10       |        0 |


#### Table: hotels

Columns:

- **id** (INTEGER)
- **name** (TEXT)
- **location** (TEXT)
- **price_tier** (TEXT)
- **checkin_date** (DATE)
- **checkout_date** (DATE)
- **booked** (INTEGER)

Row Count: 10

Estimated Table Size: 111760.00 KB

Sample Data:

|    |   id | name                 | location   | price_tier     | checkin_date   | checkout_date   |   booked |
|---:|-----:|:---------------------|:-----------|:---------------|:---------------|:----------------|---------:|
|  0 |    1 | Hilton Basel         | Basel      | Luxury         | 2024-04-22     | 2024-04-20      |        0 |
|  1 |    2 | Marriott Zurich      | Zurich     | Upscale        | 2024-04-14     | 2024-04-21      |        0 |
|  2 |    3 | Hyatt Regency Basel  | Basel      | Upper Upscale  | 2024-04-02     | 2024-04-20      |        0 |
|  3 |    4 | Radisson Blu Lucerne | Lucerne    | Midscale       | 2024-04-24     | 2024-04-05      |        0 |
|  4 |    5 | Best Western Bern    | Bern       | Upper Midscale | 2024-04-23     | 2024-04-01      |        0 |

Summary Statistics:

|       |       id |   booked |
|:------|---------:|---------:|
| count | 10       |       10 |
| mean  |  5.5     |        0 |
| std   |  3.02765 |        0 |
| min   |  1       |        0 |
| 25%   |  3.25    |        0 |
| 50%   |  5.5     |        0 |
| 75%   |  7.75    |        0 |
| max   | 10       |        0 |


#### Table: trip_recommendations

Columns:

- **id** (INTEGER)
- **name** (TEXT)
- **location** (TEXT)
- **keywords** (TEXT)
- **details** (TEXT)
- **booked** (INTEGER)

Row Count: 10

Estimated Table Size: 111760.00 KB

Sample Data:

|    |   id | name                  | location   | keywords              | details                                                          |   booked |
|---:|-----:|:----------------------|:-----------|:----------------------|:-----------------------------------------------------------------|---------:|
|  0 |    1 | Basel Minster         | Basel      | landmark, history     | Visit the historic Basel Minster, a beautiful Gothic cathedral.  |        0 |
|  1 |    2 | Kunstmuseum Basel     | Basel      | art, museum           | Explore the extensive art collection at the Kunstmuseum Basel.   |        0 |
|  2 |    3 | Zurich Old Town       | Zurich     | history, architecture | Take a stroll through the charming streets of Zurich's Old Town. |        0 |
|  3 |    4 | Lucerne Chapel Bridge | Lucerne    | landmark, history     | Walk across the iconic Chapel Bridge in Lucerne.                 |        0 |
|  4 |    5 | Bern Bear Park        | Bern       | wildlife, park        | Visit the Bern Bear Park and see the city's famous bears.        |        0 |

Summary Statistics:

|       |       id |   booked |
|:------|---------:|---------:|
| count | 10       |       10 |
| mean  |  5.5     |        0 |
| std   |  3.02765 |        0 |
| min   |  1       |        0 |
| 25%   |  3.25    |        0 |
| 50%   |  5.5     |        0 |
| 75%   |  7.75    |        0 |
| max   | 10       |        0 |


