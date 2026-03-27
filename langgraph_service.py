import json
import requests
from flask import Flask, request, jsonify, Response
import logging
from pipelines_langgraph.pulse_langgraph_pipeline import run_langgraph_pipeline
import re
from dependencies.io_handler import get_base_events, EventDataSchema

app = Flask(name)

TARGET_URL = "http://some01-llms01:11434/api/chat"
LISTEN_PORT = 8000
DEBUG_INPUT = True

#///////////////////////
#leave some space for logging, WiLl mAke iT "laTeR"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

#//////////////////////




@app.route('/v1/chat/completions', methods=['POST'])
def forward_request_sync():
"""Synchronous forwarding endpoint"""
# one piece
req_json = request.get_json()
if 'ai_assistant' in req_json[0]:
req_json[0]['ai_assistant'] = {}
if DEBUG_INPUT:
logger.info("USER_INPUT:\n{}\n\n\n".format(req_json))
if "correlation_event_json" in req_json[0]:
base_events = get_base_events((req_json[0].get("correlation_event_json")).get("BaseEvents"), EventDataSchema)
else:
base_events = get_base_events(req_json[0].get("BaseEvents"), EventDataSchema)
preprocessed_state = dict({
"uid": req_json[0].get("alert_uuid"),
"alert_name": req_json[0].get("alert_name"),
"base_events": base_events,
"alert_irp_data": req_json[0].get("alert_irp_data"),
"description": str(req_json[0]),
"description_enriched": str(),
"hosts": [],
"notes": [],
"conclusion": str()
})

response = run_langgraph_pipeline(preprocessed_state)
response = re.sub(r'<think>.*?</think>\n?', '', response, flags=re.DOTALL).strip()
return str(response), requests.codes.ok

if name == 'main':
# Start the Flask server
app.run(host='0.0.0.0', port=LISTEN_PORT, debug=True)
