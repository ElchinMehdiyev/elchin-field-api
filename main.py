from fastapi import FastAPI, HTTPException

app = FastAPI(title="Elchin CO LTD – Field Sales API")

# Fake data for now — next step this moves into a real database
OUTLETS = [
    {"id": 1, "name": "Pub Pod Zegarem", "address": "ul. Floriańska 12, Kraków"},
    {"id": 2, "name": "Sklep Mała Żabka", "address": "ul. Długa 45, Kraków"},
    {"id": 3, "name": "Restauracja Wawel View", "address": "ul. Grodzka 8, Kraków"},
    {"id": 4, "name": "Bar Kazimierz", "address": "ul. Szeroka 3, Kraków"},
]


@app.get("/")
def home():
    return {"message": "Elchin CO LTD API is running"}


# GET /outlets → the full list
@app.get("/outlets")
def get_outlets():
    return OUTLETS


# GET /outlets/2 → one outlet by its id
@app.get("/outlets/{outlet_id}")
def get_outlet(outlet_id: int):
    for outlet in OUTLETS:
        if outlet["id"] == outlet_id:
            return outlet
    raise HTTPException(status_code=404, detail="Outlet not found")
