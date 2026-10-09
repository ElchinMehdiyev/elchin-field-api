from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select


# ---- 1. Table definition: one class = one database table ----
class Outlet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # created by the database
    name: str
    address: str


# What a client sends to CREATE an outlet (no id — the database gives it one)
class OutletCreate(SQLModel):
    name: str
    address: str


# ---- 2. Database connection: everything is stored in the file elchin.db ----
engine = create_engine("sqlite:///elchin.db", connect_args={"check_same_thread": False})


def get_session():
    # Opens a connection for each request, closes it afterwards
    with Session(engine) as session:
        yield session


def seed_data():
    # Fills in the 4 starting outlets — only if the table is empty
    with Session(engine) as session:
        if session.exec(select(Outlet)).first() is None:
            session.add_all([
                Outlet(name="Pub Pod Zegarem", address="ul. Floriańska 12, Kraków"),
                Outlet(name="Sklep Mała Żabka", address="ul. Długa 45, Kraków"),
                Outlet(name="Restauracja Wawel View", address="ul. Grodzka 8, Kraków"),
                Outlet(name="Bar Kazimierz", address="ul. Szeroka 3, Kraków"),
            ])
            session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: create tables, add starting data
    SQLModel.metadata.create_all(engine)
    seed_data()
    yield


app = FastAPI(title="Elchin CO LTD – Field Sales API", lifespan=lifespan)


# ---- 3. Endpoints ----
@app.get("/")
def home():
    return {"message": "Elchin CO LTD API is running"}


# GET /outlets → all outlets from the database
@app.get("/outlets", response_model=list[Outlet])
def get_outlets(session: Session = Depends(get_session)):
    return session.exec(select(Outlet)).all()


# GET /outlets/2 → one outlet
@app.get("/outlets/{outlet_id}", response_model=Outlet)
def get_outlet(outlet_id: int, session: Session = Depends(get_session)):
    outlet = session.get(Outlet, outlet_id)
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return outlet


# NEW: POST /outlets → create a new outlet and save it
@app.post("/outlets", response_model=Outlet, status_code=201)
def create_outlet(data: OutletCreate, session: Session = Depends(get_session)):
    outlet = Outlet.model_validate(data)
    session.add(outlet)
    session.commit()
    session.refresh(outlet)  # get the id the database assigned
    return outlet