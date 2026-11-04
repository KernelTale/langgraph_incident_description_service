# Langgraph Incident Description Service
## Intended use
For surface level incident research, it helps gathering info using raw data and applying tools.
## Description
The service utilizes simple Flask to accept and process requests made with web-interface. It passes preprocessed data into Langgraph pipeline which has tools support. This demo features the asset data retriever.
<p>One node gathers the hosts, and another uses the tool with that input to gather additional info on asset related to the incident.</p>
