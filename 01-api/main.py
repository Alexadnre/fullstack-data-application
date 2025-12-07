from fastapi import FastAPI

from routes import auth, health, users, events, stats

app = FastAPI(title="Calendar API")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(stats.router)
