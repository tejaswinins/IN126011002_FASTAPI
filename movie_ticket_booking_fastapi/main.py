# IMPORTS
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Q1 - Home Route
@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

# Q2 - Movies Data + GET /movies
movies = [
    {"id": 1, "title": "Avengers", "genre": "Action", "language": "English", "duration_mins": 180, "ticket_price": 300, "seats_available": 50},
    {"id": 2, "title": "Inception", "genre": "Drama", "language": "English", "duration_mins": 150, "ticket_price": 250, "seats_available": 40},
    {"id": 3, "title": "KGF", "genre": "Action", "language": "Kannada", "duration_mins": 170, "ticket_price": 200, "seats_available": 60},
    {"id": 4, "title": "Drishyam", "genre": "Drama", "language": "Hindi", "duration_mins": 140, "ticket_price": 180, "seats_available": 30},
    {"id": 5, "title": "Hangover", "genre": "Comedy", "language": "English", "duration_mins": 120, "ticket_price": 150, "seats_available": 25},
    {"id": 6, "title": "Conjuring", "genre": "Horror", "language": "English", "duration_mins": 110, "ticket_price": 220, "seats_available": 20}
]

@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {
        "movies": movies,
        "total": len(movies),
        "total_seats_available": total_seats
    }

# Q4 - Bookings
bookings = []
booking_counter = 1

@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b["total_cost"] for b in bookings)
    return {
        "bookings": bookings,
        "total": len(bookings),
        "total_revenue": total_revenue
    }

# Q6 - BookingRequest Model
class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

# Q7 - Helper Functions

def find_movie(movie_id):
    for m in movies:
        if m["id"] == movie_id:
            return m
    return None

def calculate_ticket_cost(base_price, seats, seat_type, promo_code):
    multiplier = 1   # default = standard

    if seat_type == "premium":
        multiplier = 1.5
    elif seat_type == "recliner":
        multiplier = 2   

    original_cost = base_price * seats * multiplier

    discount = 0
    if promo_code == "SAVE10":
        discount = 0.10
    elif promo_code == "SAVE20":
        discount = 0.20

    discounted_cost = original_cost * (1 - discount)

    return original_cost, discounted_cost

# Q8 + Q9 - POST Booking
@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie["seats_available"] < request.seats:
        raise HTTPException(status_code=400, detail="Not enough seats")

    original, final = calculate_ticket_cost(
        movie["ticket_price"],
        request.seats,
        request.seat_type,
        request.promo_code
    )

    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "movie_title": movie["title"],
        "seats": request.seats,
        "seat_type": request.seat_type,
        "original_cost": original,
        "total_cost": final
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# Q5 - Movies Summary
@app.get("/movies/summary")
def movies_summary():
    prices = [m["ticket_price"] for m in movies]

    genre_count = {}
    for m in movies:
        genre_count[m["genre"]] = genre_count.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(prices),
        "cheapest": min(prices),
        "total_seats": sum(m["seats_available"] for m in movies),
        "genre_count": genre_count
    }


# Q10 - Filter Movies
@app.get("/movies/filter")
def filter_movies(
    genre: Optional[str] = None,
    language: Optional[str] = None,
    max_price: Optional[int] = None,
    min_seats: Optional[int] = None
):
    result = movies

    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]

    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]

    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]

    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return {"filtered_movies": result}


# Q16 - Search Movies
@app.get("/movies/search")
def search_movies(keyword: str):
    result = [
        m for m in movies
        if keyword.lower() in m["title"].lower()
        or keyword.lower() in m["genre"].lower()
        or keyword.lower() in m["language"].lower()
    ]

    if not result:
        return {"message": "No movies found"}

    return {"results": result, "total_found": len(result)}

# Q17 - Sort Movies
@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price"):
    if sort_by not in ["ticket_price", "title", "duration_mins", "seats_available"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    return sorted(movies, key=lambda x: x[sort_by])


# Q18 - Pagination
@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    total = len(movies)
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "total_pages": total_pages,
        "data": movies[start:end]
    }


# Q20 - Combined Browse
@app.get("/movies/browse")
def browse_movies(
    keyword: Optional[str] = None,
    genre: Optional[str] = None,
    language: Optional[str] = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = movies

    # search
    if keyword:
        result = [
            m for m in result
            if keyword.lower() in m["title"].lower()
            or keyword.lower() in m["genre"].lower()
            or keyword.lower() in m["language"].lower()
    ]
    # filter
    if genre:
        result = [m for m in result if m["genre"].lower() == genre.lower()]

    if language:
        result = [m for m in result if m["language"].lower() == language.lower()]

    # sort
    reverse = order == "desc"
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # pagination
    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "data": result[start:end]
    }

# Q3 - GET movie by ID

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    for m in movies:
        if m["id"] == movie_id:
            return m
    raise HTTPException(status_code=404, detail="Movie not found")

# Q11 - Add Movie
class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)


@app.post("/movies", status_code=201)
def add_movie(new_movie: NewMovie):
    for m in movies:
        if m["title"].lower() == new_movie.title.lower():
            raise HTTPException(status_code=400, detail="Movie already exists")

    movie = new_movie.dict()
    movie["id"] = len(movies) + 1
    movies.append(movie)

    return movie

# Q12 - Update Movie

@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    ticket_price: Optional[int] = None,
    seats_available: Optional[int] = None
):
    movie = find_movie(movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price

    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie

# Q13 - Delete Movie
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    for b in bookings:
        if b["movie_title"] == movie["title"]:
            raise HTTPException(status_code=400, detail="Movie has bookings")

    movies.remove(movie)
    return {"message": "Movie deleted"}

# Q14 - Seat Hold
holds = []
hold_counter = 1


class HoldRequest(BaseModel):
    customer_name: str
    movie_id: int
    seats: int


@app.post("/seat-hold")
def create_hold(request: HoldRequest):
    global hold_counter

    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie["seats_available"] < request.seats:
        raise HTTPException(status_code=400, detail="Not enough seats")

    movie["seats_available"] -= request.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": request.customer_name,
        "movie_id": request.movie_id,
        "seats": request.seats
    }

    holds.append(hold)
    hold_counter += 1

    return hold


@app.get("/seat-hold")
def get_holds():
    return holds

# Q15 - Confirm / Release Hold
@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    for h in holds:
        if h["hold_id"] == hold_id:
            movie = find_movie(h["movie_id"])

            booking = {
                "booking_id": len(bookings) + 1,
                "customer_name": h["customer_name"],
                "movie_title": movie["title"],
                "seats": h["seats"],
                "seat_type": "standard",
                "total_cost": movie["ticket_price"] * h["seats"]
            }

            bookings.append(booking)
            holds.remove(h)

            return booking

    raise HTTPException(status_code=404, detail="Hold not found")


@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    for h in holds:
        if h["hold_id"] == hold_id:
            movie = find_movie(h["movie_id"])
            movie["seats_available"] += h["seats"]

            holds.remove(h)
            return {"message": "Hold released"}

    raise HTTPException(status_code=404, detail="Hold not found")

# Q19 - Booking Search/Sort/Page
@app.get("/bookings/search")
def search_bookings(name: str):
    return [b for b in bookings if name.lower() in b["customer_name"].lower()]


@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost"):
    return sorted(bookings, key=lambda x: x[sort_by])


@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return bookings[start:end]
