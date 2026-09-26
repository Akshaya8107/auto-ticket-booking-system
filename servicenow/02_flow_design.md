# ServiceNow Flow Designer mapping

Flow name: `Auto Classify School IT Tickets`

Application: Global

Trigger:
- Record Created
- Table: Incident Workflow
- Condition: Category is empty

Actions:

1. If Short Description contains Wi-Fi OR Network:
   - Category = Network
   - Subcategory = Wi-Fi

2. Else If Short Description contains Projector:
   - Category = Hardware
   - Subcategory = Projector

3. Else If Short Description contains Forgot Password / Password / Login:
   - Category = Access
   - Subcategory = Forgot Password

4. Else If Short Description contains Slow / Hanging:
   - Category = Performance
   - Subcategory = Slow Computer

5. Send Email:
   - To: Caller email
   - Subject: `Your Request for the issue has been submitted.`
   - Body: ticket confirmation

Activate the flow after testing.

The local project implements these actions in Python so the same behavior can be tested without a ServiceNow instance.
