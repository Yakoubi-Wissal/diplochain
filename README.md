# DiploChain Microservices Architecture

This repository has been refactored into a true microservices ecosystem following Domain-Driven Design and the `Database per Service` pattern.

## Services
Each microservice lives in its own folder and owns its own database schema:

1. **user-service** – user accounts, roles, authentication
2. **institution-service** – institutions and their admins/settings
3. **student-service** – student profiles and identifiers
4. **diploma-service** – diploma lifecycle operations
5. **document-service** – PDF storage metadata
6. **blockchain-service** – Hyperledger Fabric interactions
7. **storage-service** – IPFS integration, CID management
8. **verification-service** – diploma verification, logs
9. **analytics-service** – dashboard metrics and statistics
10. **api-gateway** – single entry point forwarding `/api/*` to appropriate service

Additional components include the legacy `backend` monolith (for compatibility), `enterprise-service` and frontends.

## Databases
`database/init.sql` now creates separate databases for each service (e.g. `user_service_db`, `diploma_service_db`, etc.) during initialization.

Each service uses `asyncpg`/SQLAlchemy configured via its own `.env`.

## Docker Compose
`docker-compose.yml` orchestrates all services plus supporting infrastructure:

- Postgres + PgAdmin
- IPFS node
- Fabric gateway (stubbed)
- API gateway on port 8001
- Frontends on ports 3000/3001

### Running the stack
```bash
docker-compose build
docker-compose up
```

The React applications proxy `/api` requests to the gateway which routes to microservices.

## Development
Each service has its own FastAPI app, Dockerfile, requirements, and database initialization.  To work on a specific service, enter its directory and run:

```bash
uvicorn app.main:app --reload --port 8000
``` 

Use the Vite servers in the frontend folders; they forward API calls to the gateway.

## Extensibility
This architecture allows independent deployment, scaling, and versioning of each business capability. Communication between services occurs over well-defined REST endpoints – no direct database access.

## Next Steps
- Implement business logic inside each service (validation, authorization) and add comprehensive tests.
- Remove legacy monolith or keep as aggregator during migration.
- Add authentication / Azure AD integration in user-service.
- Add rate limiting, logging, tracing across services.

---
The repository structure now mirrors a production-grade microservices platform.
