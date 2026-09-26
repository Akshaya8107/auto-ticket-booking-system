# ServiceNow configuration mapping

The supplied project documentation calls for a Local Update Set named `Project Update Set`, in progress, Global application, then made current. It then creates a custom table labeled `Incident Workflow`, disables module creation, and enables Auto Number.

## Table

Label: `Incident Workflow`

Suggested generated name: `u_incident_workflow`

Fields from the source document:

| Field | Type | Values/reference |
|---|---|---|
| Number | Auto Number | — |
| Caller | Reference | `sys_user` |
| Category | Choice | Network, Hardware, Access, Performance |
| Subcategory | Choice | Wi-Fi, Projector, Forgot Password, Slow Computer |
| Short Description | String | — |
| Description | String | — |
| State | Choice | New, In progress, On hold, Resolved, Closed |
| Assigned Group | Reference | `sys_user_group` |
| Assigned To | Reference | `sys_user` |

## Dependent choice

Configure Subcategory as dependent on Category. Use these mappings:

- Wi-Fi -> Network
- Projector -> Hardware
- Forgot Password -> Access
- Slow Computer -> Performance

The local application exposes the same mapping at `/api/metadata` and `/api/dependencies/{category}`.
