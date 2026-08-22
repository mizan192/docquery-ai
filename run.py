import uvicorn
import os

if __name__ == "__main__":
    # read port from environment variable
    # default to 8010 if not set
    port = int(os.getenv("PORT", 8010))

    # read debug mode from environment
    debug = os.getenv("DEBUG", "False").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",    # required for Docker
        port=port,
        reload=debug        # only reload in debug mode
    )
