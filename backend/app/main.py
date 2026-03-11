from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine, SessionLocal
from .models import User
from .auth import router as auth_router
from .routers.cars import router as cars_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def create_admin():
    db = SessionLocal()

    user = db.query(User).filter(User.email == "admin@example.com").first()

    if not user:
        admin = User(
            email="admin@example.com",
            password="admin"
        )

        db.add(admin)
        db.commit()

    db.close()


create_admin()

app.include_router(auth_router)
app.include_router(cars_router)