import contextlib
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from auth import AuthMiddleware
from config import settings
from finance import mcp as finance_news_server

# Create a combined lifespan to manage the MCP session manager
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with finance_news_server.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# MCP well-known endpoint
@app.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_metadata():
    """
    OAuth 2.0 Protected Resource Metadata endpoint for MCP client discovery.
    Required by the MCP specification for authorization server discovery.
    """

    return {
        "authorization_servers": [settings.SCALEKIT_AUTHORIZATION_SERVERS],
        "bearer_methods_supported": ["header"],
        "resource": settings.SCALEKIT_RESOURCE_NAME,
        "resource_documentation": settings.SCALEKIT_RESOURCE_DOCS_URL,
        "scopes_supported": [
          "mcp:tools:news:read"
        ],
    }

# Create and mount the MCP server with authentication
mcp_server = finance_news_server.streamable_http_app()
app.add_middleware(AuthMiddleware)
app.mount("/", mcp_server)

def main():
    """Main entry point for the MCP server."""
    uvicorn.run(app, host="localhost", port=settings.PORT, log_level="debug")

if __name__ == "__main__":
    main()