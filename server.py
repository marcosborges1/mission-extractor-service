# server.py
import os
from dotenv import load_dotenv
import uvicorn
from ariadne import QueryType, make_executable_schema
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from my_graphql.schemas.index import type_defs
from my_graphql.resolvers.index import resolve_extract_mission
from ariadne.contrib.federation import make_federated_schema

# Load dotenv
load_dotenv()

# Ariadne setup
query = QueryType()
query.set_field("extract_mission", resolve_extract_mission)
schema = make_federated_schema(type_defs, query)
graphql_app = GraphQL(schema, debug=True)

# Define the routes for the app
routes = [
    Route("/", graphql_app),
    Mount("/data", StaticFiles(directory="data"), name="static"),
]

# Create the Starlette app with the defined routes
app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(
        "server:app", host="localhost", port=int(os.getenv("PORT")), reload=True
    )
