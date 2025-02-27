import streamlit as st
import openai
from authenticate import return_api_key
# exercise 11
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from kb_module import display_vectorstores
from users_module import vectorstore_selection_interface
# exercis 12
from langchain.memory import ConversationBufferWindowMemory

# exercise 13

import lancedb
import os
import tempfile

from gradio_tools.tools import (
	StableDiffusionTool,
	ImageCaptioningTool,
	StableDiffusionPromptGeneratorTool,
	TextToVideoTool,
)


# exercise 16
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.agents import load_tools
from langchain.utilities.dalle_image_generator import DallEAPIWrapper


from langchain.agents import tool
import json


# smart agents accessing the internet for free
# https://github.com/langchain-ai/streamlit-agent/blob/main/streamlit_agent/search_and_chat.py
@tool("Document search")
def document_search(query: str) -> str:
	# this is the prompt to the tool itself
	"Use this function first to search for documents pertaining to the query before going into the internet"
	docs = st.session_state.vs.similarity_search(query)
	docs = docs[0].page_content
	json_string = json.dumps(docs, ensure_ascii=False, indent=4)
	return json_string

@tool("Wiki search")
def wiki_search(query: str) -> str:
	"Use this function to search for documents in Wikipedia"
	wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
	results = wikipedia.run(query)
	return results

@tool("Image Generator")
def dalle_image_generator(query: str) -> str:
	"Use this function to generate images from text"
	llm = ChatOpenAI(temperature=0.9)
	prompt = PromptTemplate(
	input_variables=["image_desc"],
	template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
	)
	chain = LLMChain(llm=llm, prompt=prompt)
	image_url = DallEAPIWrapper().run(chain.run(query))
	return image_url

def agent_bot():
	st.subheader("🦜 LangChain Agent Smart Bot with Tools")
	openai.api_key = return_api_key()
	os.environ["OPENAI_API_KEY"] = return_api_key()

	msgs = StreamlitChatMessageHistory()
	memory = ConversationBufferMemory(
		chat_memory=msgs,
		return_messages=True,
		memory_key="chat_history",
		output_key="output",
	)
	if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
		msgs.clear()
		msgs.add_ai_message("How can I help you?")
		st.session_state.steps = {}

	avatars = {"human": "user", "ai": "assistant"}
	for idx, msg in enumerate(msgs.messages):
		with st.chat_message(avatars[msg.type]):
			# Render intermediate steps if any were saved
			for step in st.session_state.steps.get(str(idx), []):
				if step[0].tool == "_Exception":
					continue
				with st.status(
					f"**{step[0].tool}**: {step[0].tool_input}", state="complete"
				):
					st.write(step[0].log)
					st.write(step[1])
			st.write(msg.content)

	if prompt := st.chat_input(placeholder="Enter a query on the Internet"):
		st.chat_message("user").write(prompt)

		llm = ChatOpenAI(
			model_name="gpt-3.5-turbo", openai_api_key=return_api_key(), streaming=True
		)
		tools = st.session_state.tools
		chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
		executor = AgentExecutor.from_agent_and_tools(
			agent=chat_agent,
			tools=tools,
			memory=memory,
			return_intermediate_steps=True,
			handle_parsing_errors=True,
		)
		with st.chat_message("assistant"):
			st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
			response = executor(prompt, callbacks=[st_cb])
			st.write(response["output"])
			st.session_state.steps[str(len(msgs.messages) - 1)] = response[
				"intermediate_steps"
			]

def agent_bot_no_memory():
	st.subheader("🦜 LangChain Agent Smart Bot with Tools (No Memory)")
	openai.api_key = return_api_key()
	os.environ["OPENAI_API_KEY"] = return_api_key()

	msgs = StreamlitChatMessageHistory()
	
	if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
		msgs.clear()
		msgs.add_ai_message("How can I help you?")
		st.session_state.steps = {}

	avatars = {"human": "user", "ai": "assistant"}
	for idx, msg in enumerate(msgs.messages):
		with st.chat_message(avatars[msg.type]):
			# Render intermediate steps if any were saved
			for step in st.session_state.steps.get(str(idx), []):
				if step[0].tool == "_Exception":
					continue
				with st.status(
					f"**{step[0].tool}**: {step[0].tool_input}", state="complete"
				):
					st.write(step[0].log)
					st.write(step[1])
			st.write(msg.content)

	if prompt := st.chat_input(placeholder="Enter a query on the Internet"):
		st.chat_message("user").write(prompt)

		llm = ChatOpenAI(
			model_name="gpt-3.5-turbo", openai_api_key=return_api_key(), streaming=True
		)
		tools = st.session_state.tools
		chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
		executor = AgentExecutor.from_agent_and_tools(
			agent=chat_agent,
			tools=tools,
			return_intermediate_steps=True,
			handle_parsing_errors=True,
		)
		with st.chat_message("assistant"):
			st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
			inputs = {
						'input': prompt,
						'chat_history': [] }
			response = executor(inputs, callbacks=[st_cb])
			st.write(response["output"])
			st.session_state.steps[str(len(msgs.messages) - 1)] = response[
				"intermediate_steps"
			]

@st.cache_resource
def load_gradio_kb():
	all_tools = {
				"Document Search": document_search,
				"Wiki Search": wiki_search,
				"Langchain": StableDiffusionTool().langchain,
				"Image Captioning": ImageCaptioningTool().langchain,
				"Diffusion Prompt Generator": StableDiffusionPromptGeneratorTool().langchain,
				"Text To Video": TextToVideoTool().langchain,
				"Internet Search": DuckDuckGoSearchRun(name="Internet Search")
			}
	return all_tools

@st.cache_resource
def load_gradio():
	all_tools = {
				"Wiki Search": wiki_search,
				"Langchain": StableDiffusionTool().langchain,
				"Image Captioning": ImageCaptioningTool().langchain,
				"Diffusion Prompt Generator": StableDiffusionPromptGeneratorTool().langchain,
				"Text To Video": TextToVideoTool().langchain,
				"Internet Search": DuckDuckGoSearchRun(name="Internet Search")
			}
	return all_tools
			

def agent_management():
	display_vectorstores()
	vectorstore_selection_interface(st.session_state.user['id'])
	
	if st.checkbox("Load Gradio Tools (Slow loading time)"):
		if st.session_state.vs:
			all_tools = load_gradio_kb()
		else:
			all_tools = load_gradio()
			
	elif st.session_state.vs:
		all_tools = {
			"Document Search": document_search,
			"Wiki Search": wiki_search,
			"Internet Search": DuckDuckGoSearchRun(name="Internet Search"),
		
			}
	else:
		all_tools = {
			"Wiki Search": wiki_search,
			"Internet Search": DuckDuckGoSearchRun(name="Internet Search"),
		
		}
	
	# Create a Streamlit multiselect widget
	st.write("Select Tools (Note: Image Generator tool will set to a memoryless agent)")
	selected_tool_names = st.multiselect(
		"Select up to 3 tools:", list(all_tools.keys()), default=list(all_tools.keys())[:3]
	)
	if len(selected_tool_names) == 0:
		st.stop()
	else:
		# Map selected tool names to their respective functions
		tools = [all_tools[name] for name in selected_tool_names]
		st.session_state.tools = tools
		