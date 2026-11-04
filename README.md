# Langgraph Incident Description Service
## Intended use
For surface level incident research, it helps gathering info using raw data and applying tools.
## Description
The service utilizes simple Flask to accept and process requests made by client with web-interface. It passes SOAR preprocessed incident data into Langgraph pipeline which has tools support. This demo features the asset data retriever.
<p>The first node gathers the hosts. The second node evaluates results. The third node then passes this data as input to a tool that retrieves additional information about assets related to the incident.</p>
<p>Then the fourth node utilizes lightweight LLM to mix retrieval results with initial description from SOAR into enriched description. Fifth node estimates the alignment of enriched description to the original incident topic afterwards.</p>
<p>If new description considered insufficient then following small router node passes initial description from SOAR and retrieval results to the sixth node. Sixth node utilizes heavy LLM to mix same data into enriched description, rewriting previous one attempt.</p>
<p>The seventh node is a translator that receives enriched description either from fourth node if its results passed evaluation node or from sixth node. The translated text is being passed as response to the client with web-interface.</p>
<br>
<p>In most cases, the fourth node (running a small LLM) provides sufficient results, making the sixth node unnecessary.</p>
<p>This is my first work on LangGraph that comes alongside with the idea of leveraging LLMs to assist a SOC with enterprise incident handling.</p>
