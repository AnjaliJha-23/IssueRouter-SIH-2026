# SIC Portal Frontend

This React/Vite application provides the shared role-scoped experience for the SIC Portal workflow:

`Citizen intake -> IssueRouter AI Engine -> Master Challenge -> Government verification -> Smart Router -> Collaboration -> Project Workspace -> Impact Analytics`

## Run

```bash
npm install
npm run dev
```

The frontend consumes the FastAPI backend and includes government, citizen, organization, analytics, maps, progress, and project workspace views. University and Industry experiences are shared portals whose data is scoped by organization and role; they are not separate institution-specific applications.

See [the repository README](../README.md) and [the blueprint](../IssueRouter_SIH_Final_Implementation_Blueprint.md) for the complete product contract.
