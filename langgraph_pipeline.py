from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langchain.messages import SystemMessage, ToolMessage
from dependencies.langgraph_tools import get_tools
from dependencies.io_handler import IncidentDataSchema, EventDataSchema
from langchain_openai import ChatOpenAI
from functools import partial
import logging
#comment not but prod
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

# Get tools
user_tools = get_tools()
tools_by_name = {tool.name: tool for tool in user_tools}


# Add LLMs
mistral_small = ChatOpenAI(
model="langraph/mistral-small:24b-instruct-2501-q8_0",
base_url="http://msk01-llms02:81/v1",
api_key="sk-bf-12345678-663a-4fdc-b0e7-1ee1208cca49",
temperature=0.4
)
qwen_medium = ChatOpenAI(
model="langraph/qwen3:32b-q8_0",
base_url="http://msk01-llms02:81/v1",
temperature=0.8,
api_key="sk-bf-12345678-663a-4fdc-b0e7-1ee1208cca49"
)

deepseek_large = ChatOpenAI(
model="langraph/deepseek-r1:671b",
base_url="http://msk01-llms02:81/v1",
api_key="sk-bf-12345678-663a-4fdc-b0e7-1ee1208cca49",
temperature=0.8
)

qwen3_large = ChatOpenAI(
model="langraph/qwen3:235b-a22b-q8_0",
base_url="http://msk01-llms02:81/v1",
temperature=0.8,
api_key="sk-bf-12345678-663a-4fdc-b0e7-1ee1208cca49"
)

qwen2_instruct= ChatOpenAI(
model="langraph/qwen2.5:14b-instruct-q8_0",
base_url="http://msk01-llms02:81/v1",
temperature=0.3,
api_key="sk-bf-12345678-663a-4fdc-b0e7-1ee1208cca49"
)


# Nodes

def retrieve_hosts(state: IncidentDataSchema, llm: ChatOpenAI):
"""LLM call to retrieve additional data on source and destination of attack"""
msg = llm.invoke(f"Retrieve hostnames and IP addresses found in following text:\n{state.description}\nMake it one line and separate hosts and IP addresses with commas. If there is none then reply None.")
logger.info("LLM {}: {}".format(retrieve_hosts.name, msg.content))
return {"hosts": (msg.content).split(",")}

def evaluate_if_tool_call_is_needed(state: IncidentDataSchema, llm: ChatOpenAI):
"""Whether to use a tool or not"""
llm_with_tools = llm.bind_tools(user_tools)
return {
"notes": [
llm_with_tools.invoke(
[
SystemMessage(
content="You are network administrator who retrieves data using list of hosts."
)
]
+ state.hosts
)
]
}

def tool_usage(state: IncidentDataSchema, llm: ChatOpenAI):
"""Performs the tool call"""
result = []
for tool_call in state.notes[-1].tool_calls:
tool = tools_by_name[tool_call["name"]]
observation = tool.invoke(tool_call["args"])
result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]).content)
return {"notes": result}


def enrich_the_description_silly(state: IncidentDataSchema, llm: ChatOpenAI):
"""LLM call to form new description of the incident based on notes"""
if state.base_events:
description = str()
for event in state.base_events:
description += "-" * 90 + "\nEvent {}\n{}\n".format(event.ID, event.Name)
for field in event:
if field[1]:
description += "{}. {} : {}\n".format(field[0], (EventDataSchema.model_fields.get(field[0])).description, field[1])
else:
description = state.description
logger.info(description)
msg = llm.invoke(f"Form new description of the incident based on original description: {description} AND notes: {state.notes}. Make it comprehensive Make it comprehensive with cybersecurity expert tone. But don't make the facts up. And don't give recommendations.")
logger.info("LLM {}: {}".format(enrich_the_description_silly.name, msg.content))
return {"description_enriched": msg.content}

def enrich_the_description_smart(state: IncidentDataSchema, llm: ChatOpenAI):
"""LLM call to form new description of the incident based on notes"""
if state.base_events:
description = str()
for event in state.base_events:
description += "-" * 90 + "\nEvent {}\n{}\n".format(event.ID, event.Name)
for field in event:
if field[1]:
description += "{}. {} : {}\n".format(field[0], (EventDataSchema.model_fields.get(field[0])).description, field[1])
else:
description = state.description
logger.info(description)
msg = llm.invoke(f"Form new description of the incident compiling original one description into human readable format: {description}\nMake it comprehensive with cybersecurity expert tone. But don't make the facts up. And don't give recommendations.")
logger.info("LLM {}: {}".format(enrich_the_description_smart.name, msg.content))
return {"description_enriched": msg.content}

def check_input_data_for_alert_name_allignment(state: IncidentDataSchema, llm: ChatOpenAI):
"""Gate function to check if LLM reply alligns with main alert_name"""
msg = llm.invoke(f"Check if description alligns with its topic.\nDescription:\n{state.description_enriched}\nAND Topic: {state.alert_name}.\nAnswer only yes or no.")
logger.info("LLM {}: {}".format(check_input_data_for_alert_name_allignment.name, msg.content))
return (msg.content).lower()

def russian_translator(state: IncidentDataSchema, llm: ChatOpenAI):
"""LLM call to form Russian description of the incident based on enriched description"""
msg = llm.invoke(f"Translate to Russian language: {state.description_enriched}. Make it comprehensive, stick to cybersecurity expert tone.")
logger.info("LLM {}: {}".format(russian_translator.name, msg.content))
return {"conclusion": msg.content}


# Build workflow
workflow = StateGraph(IncidentDataSchema)

# Add nodes
workflow.add_node("retrieve_hosts", partial(retrieve_hosts, llm=qwen2_instruct))
workflow.add_node("evaluate_if_tool_call_is_needed", partial(evaluate_if_tool_call_is_needed, llm=qwen_medium))
workflow.add_node("tool_usage", partial(tool_usage, llm=qwen2_instruct))
workflow.add_node("enrich_the_description_silly", partial(enrich_the_description_silly, llm=qwen2_instruct))
workflow.add_node("enrich_the_description_smart", partial(enrich_the_description_smart, llm=qwen3_large))
workflow.add_node("russian_translator", partial(russian_translator, llm=qwen_medium))

# Add edges to connect nodes
workflow.add_edge(START, "retrieve_hosts")
workflow.add_edge("retrieve_hosts", "evaluate_if_tool_call_is_needed")
workflow.add_edge("evaluate_if_tool_call_is_needed", "tool_usage")
workflow.add_edge("tool_usage", "enrich_the_description_silly")
workflow.add_conditional_edges("enrich_the_description_silly", partial(check_input_data_for_alert_name_allignment, llm=mistral_small), {"yes": "russian_translator", "no": "enrich_the_description_smart"})
workflow.add_edge("enrich_the_description_smart", "russian_translator")
workflow.add_edge("russian_translator", END)


def run_langgraph_pipeline(preprocessed_state: dict):
# Invoke the chain with initial state
chain = workflow.compile()
state = chain.invoke(preprocessed_state)
print("\n{}".format(state.get('conclusion')))
logger.info(chain.get_graph().draw_mermaid())
return state.get('conclusion')
