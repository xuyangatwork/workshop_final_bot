#No need SQLite
import streamlit as st
from analytics_dashboard import pandas_ai, download_data
from streamlit_antd_components import menu, MenuItem
import streamlit_antd_components as sac
from main_bot import basebot_memory, basebot_qa_memory, clear_session_states, search_bot, basebot, basebot_qa
from files_module import display_files,docs_uploader, delete_files
from kb_module import display_vectorstores, create_vectorstore, delete_vectorstores
from authenticate import login_function,check_password
from class_dash import download_data_table_csv
#New schema move function fom settings
from database_schema import create_dbs
from database_module import (
    manage_tables, 
	delete_tables, 
	download_database, 
	upload_database, 
	upload_s3_database, 
	download_from_s3_and_unzip, 
	check_aws_secrets_exist,
	backup_s3_database,
	db_was_modified
	)
from org_module import (
	has_at_least_two_rows,
	initialise_admin_account,
	load_user_profile,
	display_accounts,
	create_org_structure,
	check_multiple_schools,
	process_user_profile,
	remove_or_reassign_teacher_ui,
	reassign_student_ui,
	change_teacher_profile_ui
)
from pwd_module import reset_passwords, password_settings
from users_module import (
	link_users_to_app_function_ui,
	set_function_access_for_user,
	create_prompt_template,
	update_prompt_template,
	vectorstore_selection_interface,
	pre_load_variables,
	load_and_fetch_vectorstore_for_user,
	link_profiles_to_vectorstore_interface
)
from k_map import (
	map_prompter, 
	generate_mindmap,
	map_creation_form, 
	map_prompter_with_plantuml_form, 
	generate_plantuml_mindmap, 
	render_diagram,
	output_mermaid_diagram
)
#from audio import record_myself,assessment_prompt
from bot_settings import bot_settings_interface, load_bot_settings
from PIL import Image
import configparser
import ast
from machine import upload_csv, plot_prices, prepare_data_and_train, plot_predictions, load_teachable_machines
from chatbot import call_api
from agent import agent_bot, agent_management
from prototype_application import my_first_app, prototype_settings

class ConfigHandler:
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')

	def get_value(self, section, key):
		value = self.config.get(section, key)
		try:
			# Convert string value to a Python data structure
			return ast.literal_eval(value)
		except (SyntaxError, ValueError):
			# If not a data structure, return the plain string
			return value

# Initialization
config_handler = ConfigHandler()

# Setting Streamlit configurations
st.set_page_config(layout="wide")

# Fetching secrets from Streamlit
DEFAULT_TITLE = st.secrets["default_title"]
SUPER_PWD = st.secrets["super_admin_password"]
SUPER = st.secrets["super_admin"]
DEFAULT_DB = st.secrets["default_db"]

# Fetching values from config.ini
DEFAULT_TEXT = config_handler.get_value('constants', 'DEFAULT_TEXT')
TCH = config_handler.get_value('constants', 'TCH')
STU = config_handler.get_value('constants', 'STU')
SA = config_handler.get_value('constants', 'SA')
AD = config_handler.get_value('constants', 'AD')
COTF = config_handler.get_value('constants', 'COTF')
META = config_handler.get_value('constants', 'META')
PANDAI = config_handler.get_value('constants', 'PANDAI')
MENU_FUNCS = config_handler.get_value('menu_lists', 'MENU_FUNCS')
META_BOT = config_handler.get_value('constants', 'META_BOT')
QA_BOT = config_handler.get_value('constants', 'QA_BOT')
LESSON_BOT = config_handler.get_value('constants', 'LESSON_BOT')
LESSON_COLLAB = config_handler.get_value('constants', 'LESSON_COLLAB')
LESSON_COMMENT = config_handler.get_value('constants', 'LESSON_COMMENT')
LESSON_MAP = config_handler.get_value('constants', 'LESSON_MAP')
REFLECTIVE = config_handler.get_value('constants', 'REFLECTIVE')
CONVERSATION = config_handler.get_value('constants', 'CONVERSATION')
MINDMAP = config_handler.get_value('constants', 'MINDMAP')
METACOG = config_handler.get_value('constants', 'METACOG')
PROTOTYPE = config_handler.get_value('constants', 'PROTOTYPE')


def is_function_disabled(function_name):
	return st.session_state.func_options.get(function_name, True)


def initialize_session_state( menu_funcs, default_value):
	st.session_state.func_options = {key: default_value for key in menu_funcs.keys()}
	

def main():
	try:
		if "title_page"	not in st.session_state:
			st.session_state.title_page = DEFAULT_TITLE 

		st.title(st.session_state.title_page)
		sac.divider(label='ITD Workshop Framework', icon='house', align='center', direction='horizontal', dashed=False, bold=False)
		
		if "api_key" not in st.session_state:
			st.session_state.api_key = ""

		if "option" not in st.session_state:
			st.session_state.option = False
		
		if "login" not in st.session_state:
			st.session_state.login = False
		
		if "user" not in st.session_state:
			st.session_state.user = None
		
		if "openai_model" not in st.session_state:
			st.session_state.openai_model = st.secrets["default_model"]

		if "msg" not in st.session_state:
			st.session_state.msg = []

		if "rating" not in st.session_state:
			st.session_state.rating = False

		if "temp" not in st.session_state:
			st.session_state.temp = st.secrets["default_temp"]
		
		if "frequency_penalty" not in st.session_state:
			st.session_state.frequency_penalty = st.secrets["default_frequency_penalty"]

		if "presence_penalty" not in st.session_state:
			st.session_state.presence_penalty = st.secrets["default_presence_penalty"]
		
		if "memoryless" not in st.session_state:
			st.session_state.memoryless = False
		
		if "k_memory" not in st.session_state:
			st.session_state.k_memory = 4

		if "vs" not in st.session_state:
			st.session_state.vs = False
		
		if "visuals" not in st.session_state:
			st.session_state.visuals = False
		
		if "svg_height" not in st.session_state:
			st.session_state["svg_height"] = 1000

		if "previous_mermaid" not in st.session_state:
			st.session_state["previous_mermaid"] = ""
			
		if "current_model" not in st.session_state:
			st.session_state.current_model = "No KB loaded"

		if "func_options" not in st.session_state:
			st.session_state.func_options = {}
			initialize_session_state(MENU_FUNCS, True)

		if "tools" not in st.session_state:
			st.session_state.tools = []
		
		
		create_dbs()
		initialise_admin_account()
		with st.sidebar: #options for sidebar

			if st.session_state.login == False:
				image = Image.open('AI logo.png')
				st.image(image)
				st.session_state.option = menu([MenuItem('Users login', icon='people'), MenuItem('Application Info', icon='info-circle')])
			else:
				#can do a test if user is school is something show a different logo and set a different API key
				
				if st.session_state.user['profile_id'] == SA: #super admin login feature
					# Initialize the session state for function options
					initialize_session_state(MENU_FUNCS, False)
		
				else:
					
					set_function_access_for_user(st.session_state.user['id'])
					
				
					# Using the is_function_disabled function for setting the `disabled` attribute
				
				st.session_state.option = sac.menu([
					sac.MenuItem('Home', icon='house', children=[
						sac.MenuItem('Personal Dashboard', icon='person-circle', disabled=is_function_disabled('Personal Dashboard')),
						sac.MenuItem('Prototype Application', icon='star-fill', disabled=is_function_disabled('Prototype Application')),
						sac.MenuItem('Prototype Settings', icon='wrench', disabled=is_function_disabled('Prototype Settings')),
					]),
		
					sac.MenuItem('Basics of Machine Learning', icon='robot', children=[
						sac.MenuItem('Machine Learning', icon='clipboard-data', disabled=is_function_disabled('Machine Learning')),
						sac.MenuItem('Deep Learning', icon='clipboard-data', disabled=is_function_disabled('Deep Learning')),
					]),
					sac.MenuItem('Types of Chatbot', icon='book', children=[
						sac.MenuItem('Rule Based Chatbot', icon='chat-square-dots', disabled=is_function_disabled('Rule Based Chatbot')),
						sac.MenuItem('Open AI API Call', icon='chat-square-dots', disabled=is_function_disabled('Open AI API Call')),
						sac.MenuItem('AI Chatbot', icon='chat-square-dots', disabled=is_function_disabled('AI Chatbot')),
						sac.MenuItem('Chatbot Management', icon='wrench', disabled=is_function_disabled('AI Chatbot')),
						sac.MenuItem('Agent Chatbot', icon='chat-square-dots', disabled=is_function_disabled('Agent Chatbot')),
						sac.MenuItem('Agent Management', icon='wrench', disabled=is_function_disabled('Agent Management')),
						sac.MenuItem('Data Management', icon='database-fill-up',disabled=is_function_disabled('Data Management')),
					]),
					sac.MenuItem('Knowledge Base Tools', icon='book', children=[
						sac.MenuItem('Files Management', icon='file-arrow-up', disabled=is_function_disabled('Files management')),
						sac.MenuItem('Knowledge Base Editor', icon='database-fill-up',disabled=is_function_disabled('KB management')),
					]),
					sac.MenuItem('GenAI Application', icon='book', children=[
						sac.MenuItem('AI Analytics', icon='chat-square-dots', disabled=is_function_disabled('AI Analytics')),
						#sac.MenuItem('Audio Analytics', icon='file-arrow-up', disabled=is_function_disabled('Audio Analytics')),
						sac.MenuItem('Knowledge Map Generator', icon='database-fill-up',disabled=is_function_disabled('Knowledge Map Generator')),
					]),
					sac.MenuItem('Organisation Tools', icon='buildings', children=[
						sac.MenuItem('Org Management', icon='building-gear', disabled=is_function_disabled('Organisation Management')),
						sac.MenuItem('Users Management', icon='house-gear', disabled=is_function_disabled('School Users Management')),
					]),
					sac.MenuItem(type='divider'),
					sac.MenuItem('Profile Settings', icon='gear'),
					sac.MenuItem('Application Info', icon='info-circle'),
					sac.MenuItem('Logout', icon='box-arrow-right'),
				], index=1, format_func='title', open_all=False)

		if st.session_state.option == 'Users login':
				col1, col2 = st.columns([3,4])
				placeholder2 = st.empty()
				with placeholder2:
					with col1:
						if login_function() == True:
							placeholder2.empty()
							st.session_state.login = True
							st.session_state.user = load_user_profile(st.session_state.user)
							pre_load_variables(st.session_state.user['id'])
							load_and_fetch_vectorstore_for_user(st.session_state.user['id'])
							load_bot_settings(st.session_state.user['id'])
							st.rerun()
					with col2:
						pass
		
		#Personal Dashboard
		elif st.session_state.option == 'Personal Dashboard':
			st.subheader(f":green[{st.session_state.option}]")
			if st.session_state.user['profile_id'] == SA:
				sch_id, msg = process_user_profile(st.session_state.user["profile_id"])
				st.write(msg)
				download_data_table_csv(st.session_state.user["id"], sch_id, st.session_state.user["profile_id"])
			else:
				download_data_table_csv(st.session_state.user["id"], st.session_state.user["school_id"], st.session_state.user["profile_id"])
			display_vectorstores()
			vectorstore_selection_interface(st.session_state.user['id'])
		
		elif st.session_state.option == 'Prototype Application':
			my_first_app(PROTOTYPE)
			pass
		elif st.session_state.option == 'Prototype Settings':
			prototype_settings()
			pass

		elif st.session_state.option == 'Machine Learning':
			
			st.subheader(f":green[{st.session_state.option}]")
			df = upload_csv()
			if df is not None:
				plot_prices(df)
				if st.checkbox('Start Predictive Model'):
					df_predict, tree, lr, column_name, future_days, X, Sucess =  prepare_data_and_train(df)
					if Sucess:
						plot_predictions(df_predict, tree, lr, column_name, future_days, X)
					else:
						st.warning("Please fill in all the fields in the machine learning form")
		
		elif st.session_state.option == 'Deep Learning':
			st.subheader(f":green[{st.session_state.option}]")
			load_teachable_machines()
		elif st.session_state.option == 'Rule Based Chatbot':
			pass
		elif st.session_state.option == 'Open AI API Call':
			st.subheader(f":green[{st.session_state.option}]")
			call_api()
		elif st.session_state.option == 'AI Analytics':
			st.subheader(f":green[{st.session_state.option}]")
			pandas_ai(st.session_state.user['id'], st.session_state.user['school_id'], st.session_state.user['profile_id'])
			pass
		elif st.session_state.option == 'Agent Chatbot':
			if st.session_state.tools == []:
				st.warning("Please set your tool under Agent Management")
			else:
				if st.session_state.memoryless:
					agent_bot()
		elif st.session_state.option == 'Agent Management':
			agent_management()

		elif st.session_state.option == "AI Chatbot":
			st.subheader(f":green[{st.session_state.option}]")
			sac.divider(label='Chatbot Settings', icon='robot', align='center', direction='horizontal', dashed=False, bold=False)
			#check if API key is entered
			with st.expander("Chatbot Settings"):
				vectorstore_selection_interface(st.session_state.user['id'])
				if st.session_state.vs:#chatbot with knowledge base
					raw_search = sac.switch(label='Raw Search', value=False, align='start', position='left')
				clear = sac.switch(label='Clear Chat', value=False, align='start', position='left')
				if clear == True:	
					clear_session_states()
				mem = sac.switch(label='Enable Memory', value=True, align='start', position='left')
				if mem == True:	
					st.session_state.memoryless = False
				else:
					st.session_state.memoryless = True
				rating = sac.switch(label='Rate Response', value=True, align='start', position='left')
				if rating == True:	
					st.session_state.rating = True
				else:
					st.session_state.rating = False
			if st.session_state.vs:#chatbot with knowledge base
				if raw_search == True:
					search_bot()
				else:
					if st.session_state.memoryless: #memoryless chatbot with knowledge base but no memory
						basebot_qa(QA_BOT)
					else:
						basebot_qa_memory(QA_BOT) #chatbot with knowledge base and memory
			else:#chatbot with no knowledge base
				if st.session_state.memoryless: #memoryless chatbot with no knowledge base and no memory
					basebot(QA_BOT)
				else:
					basebot_memory(QA_BOT) #chatbot with no knowledge base but with memory
		
		#Dialogic Agent
				
		elif st.session_state.option == 'Chatbot Management': #ensure that it is for administrator or super_admin
			if st.session_state.user['profile_id'] == SA or st.session_state.user['profile_id'] == AD:
				st.subheader(f":green[{st.session_state.option}]")
				create_prompt_template(st.session_state.user['id'])
				update_prompt_template(st.session_state.user['profile_id'])
				st.subheader("OpenAI Chatbot Parameters Settings")
				bot_settings_interface(st.session_state.user['profile_id'], st.session_state.user['school_id'])
			else:
				st.subheader(f":red[This option is accessible only to administrators only]")
		
		#Knowledge Base Tools
		elif st.session_state.option == 'Files Management':
			st.subheader(f":green[{st.session_state.option}]") 
			display_files()
			docs_uploader()
			delete_files()

		elif st.session_state.option == "Knowledge Base Editor":
			st.subheader(f":green[{st.session_state.option}]") 
			options = sac.steps(
				items=[
					sac.StepsItem(title='Step 1', description='Create a new knowledge base'),
					sac.StepsItem(title='Step 2', description='Assign a knowledge base to a user'),
					sac.StepsItem(title='Step 3', description='Delete a knowledge base (Optional)'),
				],
				format_func='title',
				placement='vertical',
				size='small'
			)
			if options == "Step 1":
				st.subheader("KB created in the repository")
				display_vectorstores()
				st.subheader("Files available in the repository")
				display_files()
				create_vectorstore()
			elif options == "Step 2":
				st.subheader("KB created in the repository")
				display_vectorstores()
				vectorstore_selection_interface(st.session_state.user['id'])
				link_profiles_to_vectorstore_interface(st.session_state.user['id'])
	
			elif options == "Step 3":
				st.subheader("KB created in the repository")
				display_vectorstores()
				delete_vectorstores()

		#Organisation Tools
		elif st.session_state.option == "Users Management":
			st.subheader(f":green[{st.session_state.option}]") 
			sch_id, msg = process_user_profile(st.session_state.user["profile_id"])
			rows = has_at_least_two_rows()
			if rows >= 2:
				#Password Reset
				st.subheader("User accounts information")
				df = display_accounts(sch_id)
				st.warning("Password Management")
				st.subheader("Reset passwords of users")
				reset_passwords(df)
		
		elif st.session_state.option == "Org Management":
			if st.session_state.user['profile_id'] == SA:
				st.subheader(f":green[{st.session_state.option}]") 
				#direct_vectorstore_function()
				
				if check_password(st.session_state.user["username"], SUPER_PWD):
						st.write("To start creating your teachers account, please change the default password of your administrator account under profile settings")
				else:
					sch_id, msg = process_user_profile(st.session_state.user["profile_id"])
					create_flag = False
					rows = has_at_least_two_rows()
					if rows >= 2:
						create_flag = check_multiple_schools()
					st.markdown("###")
					st.write(msg)
					st.markdown("###")
					steps_options = sac.steps(
								items=[
									sac.StepsItem(title='step 1', description='Create Students and Teachers account of a new school', disabled=create_flag),
									sac.StepsItem(title='step 2', description='Remove/Assign Teachers to Classes'),
									sac.StepsItem(title='step 3', description='Change Teachers Profile'),
									sac.StepsItem(title='step 4', description='Setting function access for profiles'),
									sac.StepsItem(title='step 5', description='Reassign Students to Classes(Optional)'),
									sac.StepsItem(title='step 6', description='Managing SQL Schema Tables',icon='radioactive'),
								], format_func='title', placement='vertical', size='small'
							)
					if steps_options == "step 1":
						if create_flag:
							st.write("School created, click on Step 2")
						else:
							create_org_structure()
					elif steps_options == "step 2":
						remove_or_reassign_teacher_ui(sch_id)
					elif steps_options == "step 3":
						change_teacher_profile_ui(sch_id)
					elif steps_options == "step 4":
						link_users_to_app_function_ui(sch_id)
					elif steps_options == "step 5":
						reassign_student_ui(sch_id)
					elif steps_options == "step 6":
						st.subheader(":red[Managing SQL Schema Tables]")
						st.warning("Please do not use this function unless you know what you are doing")
						if st.checkbox("I know how to manage SQL Tables"):
							st.subheader(":red[Zip Database - Download and upload a copy of the database]")
							download_database()
							upload_database()
							if check_aws_secrets_exist():
								st.subheader(":red[Upload Database to S3 - Upload a copy of the database to S3]")
								upload_s3_database()
								download_from_s3_and_unzip()
							st.subheader(":red[Display and Edit Tables - please do so if you have knowledge of the current schema]")
							manage_tables()
							st.subheader(":red[Delete Table - Warning please use this function with extreme caution]")
							delete_tables()
							
			else:
				st.subheader(f":red[This option is accessible only to super administrators only]")

		elif st.session_state.option == "Knowledge Map Generator":
			st.subheader(f":green[{st.session_state.option}]") 
			mode = sac.switch(label='Generative Mode :', value=True, checked='Coloured Map', unchecked='Process Chart', align='center', position='left', size='default', disabled=False)
			subject, topic, levels = map_creation_form()
			prompt = False
			if subject and topic and levels:
				if mode:
					prompt = map_prompter_with_plantuml_form(subject, topic, levels)
				else:
					prompt = map_prompter(subject, topic, levels)
			if prompt:
				with st.spinner("Generating mindmap"):
					st.write(f"Mindmap generated from the prompt: :orange[**{subject} {topic} {levels}**]")
					if mode:
						uml = generate_plantuml_mindmap(prompt)
						image = render_diagram(uml)
						st.image(image)
					else:
						syntax = generate_mindmap(prompt)
						if syntax:
							output_mermaid_diagram(syntax)
						

		# elif st.session_state.option == "Audio Analytics":
		# 	st.subheader(f":green[{st.session_state.option}]") 
		# 	# Create form
		# 	subject = st.text_input("Subject:")
		# 	topic = st.text_input("Topic:")
		# 	assessment_type = st.selectbox("Type of Assessment:", ["Oral Assessment", "Content Assessment", "Transcribing No Assessment"])
		# 	result = record_myself()
		# 	if result is not None:
		# 		transcript, language = result
		# 		if assessment_type == "Transcribing No Assessment":
		# 			st.write(f"Transcript: {transcript}")
		# 			st.session_state.msg.append({"role": "assistant", "content": transcript})
		# 		else:
		# 			if subject and topic :
		# 				assessment_prompt(transcript, assessment_type, subject, topic, language)
		# 			else:
		# 				st.warning("Please fill in all the fields in the oral submission form")
						
		
		elif st.session_state.option == "Profile Settings":
			st.subheader(f":green[{st.session_state.option}]") 
			#direct_vectorstore_function()
			password_settings(st.session_state.user["username"])
		
		
		elif st.session_state.option == 'Application Info':
			st.subheader(f":green[{st.session_state.option}]") 
			st.markdown("Application Information here")
			pass

		elif st.session_state.option == 'Logout':
			if db_was_modified(DEFAULT_DB):
				if check_aws_secrets_exist():
					backup_s3_database()
					for key in st.session_state.keys():
						del st.session_state[key]
					st.rerun()
				elif st.session_state.user['profile_id'] == SA:
					on = st.toggle('I do not want to download a copy of the database')
					if on:
						for key in st.session_state.keys():
							del st.session_state[key]
						st.rerun()
					else:
						download_database()
						for key in st.session_state.keys():
							del st.session_state[key]
						st.rerun()
				else:
					for key in st.session_state.keys():
						del st.session_state[key]
					st.rerun()
			else:
				for key in st.session_state.keys():
					del st.session_state[key]
				st.rerun()
			#check if SA or AD wants to save the database locally 
			
			pass
	except Exception as e:
		st.exception(e)

if __name__ == "__main__":
	main()
