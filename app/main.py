from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .schema import schema

app = FastAPI(title="MICROSERVICIO-BI-KPIS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://frontend-historial-clinico.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema, path="/graphql")
app.include_router(graphql_app, prefix="")

@app.get("/health")
def health():
    return {"status": "ok"}
