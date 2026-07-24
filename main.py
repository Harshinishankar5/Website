from fastapi import FastAPI
from app.database import Base, engine

from app.routers.careers_routers import router as careers_router
from app.routers.book_appointment import router as appointment_router
from app.routers.auth import router as auth
from app.routers.blogs_routers import router as blogs
from app.routers.jobs_routers import router as jobs
from app.routers.contact_router import router as contact
from app.routers.product_routers import router as products
from app.routers.blogs_demo import router as blogs_demo
from app.routers.analytics_routers import router as dashboard


from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React
        "http://localhost:5173",  # Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)
app.include_router(careers_router)
app.include_router(appointment_router)
app.include_router(blogs)
app.include_router(jobs)
app.include_router(contact)
app.include_router(products)
app.include_router(blogs_demo)
app.include_router(dashboard)



