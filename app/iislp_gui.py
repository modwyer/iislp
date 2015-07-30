#MVC_Template_01
#2014 May 23  by Steven Lipton http://makeAppPie.com

import os
import time
import threading
import queue
import tkinter as tk
import tkinter.ttk as ttk
from functools import partial
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys

#
# A Model-View-Controller framework for TKinter.
# Model: Data Structure. Controller can send messages to it, and model can respond to message.
# View : User interface elements. Controller can send messages to it. View can call methods from Controller when an event happens.
# Controller: Ties View and Model together. turns UI responses into changes in data and vice versa.
 
#
#Controller: Ties View and Model together.
#       --Performs actions based on View events.
#       --Sends messages to Model and View and gets responses
#       --Has Delegates
#       --Controllers may talk to other controllers through delegates
 
class Controller():
	def __init__(self, 
			parent, 
			queue, 
			start_runlog_watch_cmd, 
			end_runlog_watch_cmd):
		print ("Init m and v...")
		
		self.parent = parent
		self.queue = queue
		
		self.start_runlog_watch_cmd = start_runlog_watch_cmd
		self.end_runlog_watch_cmd = end_runlog_watch_cmd
		
		self.config = ConfigMgr()
		self.toggle_switch = {'Start': 'Running', 'Stop': 'Stopped'}
		
		self.view = MainView(self)
		
		self.model = IISLPViewModel(self)
		
		
		#initalize properties in model, if any
		print ("Init properties in model...")		
		self.model.set_procd_logs_list()		# Get the processed logs list.
		
		#initialize properties in view, if any
		print ("Init properties in view...")
		#~ self.load_procd_logs()		# Load the processed logs into view.
		#~ pass
		
			
	def process_runtime_logs(self):
		while (self.queue.qsize()):
			try:
				msg = self.queue.get(0)
				print ("GuiThread: queue msg count: ", len(msg))
			except Queue.Empty:
				pass
	
	#~ def quitButtonPressed(self, text):
		#~ print("quit btn was pressed!")
		#~ self.view.set_lbl(text)
		#~ self.parent.update_idletasks()
		
	def load_procd_logs(self):
		print ("Loading processed logs list...")
		self.model.set_procd_logs_list()
		print ("Done loading...")
		
#event handlers -- add functions called by command attribute in view
	#~ def someHandelerMethod(self):
		#~ pass
		
	def bulk_process(self):
		self.view.show_bulk_process_panel()					# Move scrollview to the bulk processing panel.
		print ("about to start watcher")
		#~ self.model.start_watch_runtime()		# Start watching the runtime_log file.
		self.start_runlog_watch_cmd()
		#~ time.sleep(10)
		#~ self.model.stop_watch_runtime()		# Stop watching the runtime_log file.
		#~ self.model.start_watch_runtime()
		self.end_runlog_watch_cmd()
		
	def set_procd_logs(self, log_list):
		list_len = len(log_list)
		self.view.set_procd_logs(log_list)					# Update processed logs list.
		self.view.set_total_procd_logs(list_len)	
		self.view.set_oldest_procd_log(log_list[0])
		self.view.set_newest_procd_log(log_list[list_len - 1])
		
	def set_unprocd_logs(self, log_list):
		print ("set_unprocd_logs_info: ")
		log_done_path = self.config.get_value(ConfigKeys.log_done)
		
		all_log_files = ([f for f in os.listdir(log_done_path) 
			if f.endswith('.log')])
		all_log_files_len = len(all_log_files)		
				
		filenames = [s[-13:] for s in log_list]		# Slice out the filenames from each string in log_list.
		filenames_len = len(filenames)				
		'''
		The items found in the new_set are the difference between all the 
		log file names found in the log_done directory and the names of 
		the log files that have been parsed already.
		The list 'all_log_files' in ascending order as is the list 'filenames'.
		The length of the list of parsed log files 
		'''
		new_set = all_log_files[len(filenames):]
		
		# Tell the view to update its uprocessed logs list.
		list_len = len(new_set)
		self.view.set_unprocd_logs(new_set)
		self.view.set_total_unprocd_logs(list_len)	
		self.view.set_oldest_unprocd_log(new_set[0])
		self.view.set_newest_unprocd_log(new_set[list_len - 1])
		#***HERE.  just got the log file status section to work.
		# what is next?
		# need to add a command line/console output section to show the
		# output of the running process.  or maybe have another panel
		# that shows the runtime log file or the latest portion of it.
		# what else do you need to see?
		# what else needs to be interacted with?
		# an editable window that displays the config file.  allow easy changes?
		

#delegates -- add functions called by delegtes in model or view
	def procd_logs_list_changeDelegate(self, lst):
		# Update view widgets showing 'processed logs' info.
		print ("List did change delegate...")
		
		self.set_procd_logs(lst)	# Update the processed logs' info fields.
		self.set_unprocd_logs(lst)	# Update unprocessed logs list.
		
	def set_runtime_output_changeDelegate(self, output):
		print ("set_runtime_output_changeDelegate hit: output.count: ", len(output))
		self.view.set_runtime_output(output)
		
#View : User interface elements.
#       --Controller can send messages to it.
#       --View can call methods from Controller vc when an event happens.
#       --NEVER communicates with Model.
#       --Has setters and getters to communicate with controller
 
class MainView(tk.Frame):
	def load_procdlogs_panel(self, parent):
		#
		#lbl_log_stat_header: Header label for section that shows the status of processed/unprocessed logs.
		#
		#~ lbl_log_stat_header = Label(parent, 
							#~ background="white", 
							#~ text="Log File Status", 
							#~ width=20, 
							#~ anchor=CENTER)
		#~ lbl_log_stat_header.pack(side=TOP, expand=True, pady=10)
		#
		#procd_logs: Main container that displays info about the processed logs.
		#
		procd_logs = tk.Canvas(parent, width=25, height=650, 
						background="white", relief="ridge",
						highlightthickness=0)									
		procd_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		#
		#procd_logs_info_frame: Frame for the top half of the processed logs container.
		#
		procd_logs_info_frame = tk.Frame(procd_logs, bg="white", bd=0)
		procd_logs_info_frame.pack()
		#
		#procd_logs_info: Container that holds some stats about the processed logs.
		#
		procd_logs_info_container = tk.Canvas(procd_logs_info_frame,
									background="white",
									borderwidth=0,
									highlightthickness=0, 
									relief="ridge")
		procd_logs_info_container.pack(pady=5, padx=15)
		#
		#procd_logs_content_frame: Frame to hold a canvas and a vertical scrollbar connected to the canvas.
		#
		procd_logs_content_frame = tk.Frame(procd_logs, bg="white", bd=0)
		procd_logs_content_frame.pack(expand=True, fill=tk.Y, padx=15, pady=10)
		#
		#scr_proc_logs: Scroll through the list of processed logs.
		#
		scr_proc_logs = ttk.Scrollbar(procd_logs_content_frame, orient=tk.VERTICAL)
		scr_proc_logs.pack(side=tk.RIGHT, fill=tk.Y)
		#
		#self.procd_logs_listbox: Holds the content of the logs_done.txt file- all the processed logs.
		# This is filled in the method 'set_procd_logs'.
		#
		self.procd_logs_listbox = tk.Listbox(procd_logs_content_frame, selectmode=tk.EXTENDED)
		self.procd_logs_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=1)
		self.procd_logs_listbox.config(width=46, height=32)
		#
		#scr_proc_logs: Configure command		
		#
		scr_proc_logs.config(command=self.procd_logs_listbox.yview)
		#
		#procd_logs_listbox: Configure yscrollcommand.		
		#
		self.procd_logs_listbox.config(yscrollcommand=scr_proc_logs.set)
		#
		#lbl_proc_logs
		#
		lbl_proc_logs = tk.Label(procd_logs_info_container, 
						background="lightyellow", 
						text="Processed Log Files", 
						width=20, height=2, 
						anchor=tk.CENTER)
		lbl_proc_logs.grid(row=0, column=0,  columnspan=2, sticky="w", pady=10)
		#
		#lbl_total: Total number of logs that have been parsed.
		#
		lbl_total_proc_logs = tk.Label(procd_logs_info_container, background="white", text="Total")
		lbl_total_proc_logs.grid(sticky="w", pady=5, padx=5, row=1, column=0)
		#
		#tb_total_proc_logs
		#
		tb_total_proc_logs = tk.Entry(procd_logs_info_container, 
							width=40, 
							relief=tk.FLAT, 
							textvariable=self.total_procd_logs) # Binding textvariable to self StringVar
		tb_total_proc_logs.grid(sticky="w", pady=5, row=1, column=1)
		tb_total_proc_logs.config(state=tk.DISABLED)
		#
		#lbl_oldest_proc_log: The oldest log that has been parsed.
		#
		lbl_oldest_proc_log = tk.Label(procd_logs_info_container, 
							background="white", 
							text="Oldest")
		lbl_oldest_proc_log.grid(sticky="w", pady=5, padx=5, row=2, column=0)
		#
		#tb_oldest_proc_logs
		#		
		tb_oldest_proc_logs = tk.Entry(procd_logs_info_container, 
							width=40, 
							relief=tk.FLAT, 
							textvariable=self.oldest_procd_log)
		tb_oldest_proc_logs.grid(sticky="w", pady=5, row=2, column=1)
		tb_oldest_proc_logs.config(state=tk.DISABLED)
		#
		#lbl_newest_proc_log: The oldest log that has been parsed.
		#
		lbl_newest_proc_log = tk.Label(procd_logs_info_container, 
							background="white", 
							text="Newest")
		lbl_newest_proc_log.grid(sticky="w", pady=5, padx=5, row=3, column=0)
		#
		#tb_newest_proc_logs
		#
		tb_newest_proc_logs = tk.Entry(procd_logs_info_container, 
							width=40, 
							relief=tk.FLAT, 
							textvariable=self.newest_procd_log)
		tb_newest_proc_logs.grid(sticky="w", pady=5, row=3, column=1)	
		tb_newest_proc_logs.config(state=tk.DISABLED)
		
	def load_unprocdlogs_panel(self, parent):
		#
		#unprocd_logs: Main container that displays info about the unprocessed logs.
		#
		unprocd_logs = tk.Canvas(parent, width=25, height=650, 
						background="white", relief="ridge",
						highlightthickness=0)									
		unprocd_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		#
		#unprocd_logs_info_frame: Frame for the top half of the unprocessed logs container.
		#
		unprocd_logs_info_frame = tk.Frame(unprocd_logs, bg="white", bd=0)
		unprocd_logs_info_frame.pack()
		#
		#unprocd_logs_info: Container that holds some stats about the unprocessed logs.
		#
		unprocd_logs_info_container = tk.Canvas(unprocd_logs_info_frame,
									background="white",
									borderwidth=0,
									highlightthickness=0, 
									relief="ridge")
		unprocd_logs_info_container.pack(pady=5, padx=15)
		#
		#unprocd_logs_content_frame: Frame to hold a canvas and a vertical scrollbar connected to the canvas.
		#
		unprocd_logs_content_frame = tk.Frame(unprocd_logs, bg="white", bd=0)
		unprocd_logs_content_frame.pack(expand=True, fill=tk.Y, padx=15, pady=10)
		#
		#scr_unproc_logs: Scroll through the list of unprocessed logs.
		#
		scr_unproc_logs = ttk.Scrollbar(unprocd_logs_content_frame, orient=tk.VERTICAL)
		scr_unproc_logs.pack(side=tk.RIGHT, fill=tk.Y)
		#
		#self.unprocd_logs_listbox: Displays a list of all log files found in the log_done directory
		#				         that have not yet been processed.
		#				         This is filled in the method 'set_unprocd_logs'.
		#
		self.unprocd_logs_listbox = tk.Listbox(unprocd_logs_content_frame, selectmode=tk.EXTENDED)
		self.unprocd_logs_listbox.pack(side=tk.LEFT, fill=tk.Y)
		self.unprocd_logs_listbox.config(width=46, height=29)
		#
		#scr_unproc_logs: Configure command		
		#
		scr_unproc_logs.config(command=self.unprocd_logs_listbox.yview)
		#
		#unprocd_logs_listbox: Configure yscrollcommand.		
		#
		self.unprocd_logs_listbox.config(yscrollcommand=scr_unproc_logs.set)
		#
		#lbl_unproc_logs
		#
		lbl_unproc_logs = tk.Label(unprocd_logs_info_container, 
						background="lightyellow", 
						text="Unprocessed Log Files", 
						width=20, height=2, 
						anchor=tk.CENTER)
		lbl_unproc_logs.grid(row=0, column=0,  columnspan=2, sticky="w", pady=10)
		#
		#lbl_total_unproc_logs: Total number of logs that have NOT yet been parsed.
		#
		lbl_total_unproc_logs = tk.Label(unprocd_logs_info_container, background="white", text="Total")
		lbl_total_unproc_logs.grid(sticky="w", pady=5, padx=5, row=1, column=0)
		#
		#tb_total_unproc_logs
		#
		tb_total_unproc_logs = tk.Entry(unprocd_logs_info_container, 
								width=40, 
								relief=tk.FLAT, 
								textvariable=self.total_unprocd_logs) # Binding textvariable to self StringVar
		tb_total_unproc_logs.grid(sticky="w", pady=5, row=1, column=1)
		tb_total_unproc_logs.config(state=tk.DISABLED)
		#
		#lbl_oldest_unproc_log: The oldest log that has NOT yet been parsed.
		#
		lbl_oldest_unproc_log = tk.Label(unprocd_logs_info_container, background="white", text="Oldest")
		lbl_oldest_unproc_log.grid(sticky="w", pady=5, padx=5, row=2, column=0)
		#
		#tb_oldest_unproc_logs
		#		
		tb_oldest_unproc_logs = tk.Entry(unprocd_logs_info_container, 
								width=40, 
								relief=tk.FLAT, 
								textvariable=self.oldest_unprocd_log)
		tb_oldest_unproc_logs.grid(sticky="w", pady=5, row=2, column=1)
		tb_oldest_unproc_logs.config(state=tk.DISABLED)
		#
		#lbl_newest_unproc_log: The oldest log that has been parsed.
		#
		lbl_newest_unproc_log = tk.Label(unprocd_logs_info_container, background="white", text="Newest")
		lbl_newest_unproc_log.grid(sticky="w", pady=5, padx=5, row=3, column=0)
		#
		#tb_newest_unproc_logs
		#
		tb_newest_unproc_logs = tk.Entry(unprocd_logs_info_container, 
								width=40, 
								relief=tk.FLAT, 
								textvariable=self.newest_unprocd_log)
		tb_newest_unproc_logs.grid(sticky="w", pady=5, row=3, column=1)	
		tb_newest_unproc_logs.config(state=tk.DISABLED)
		
	def load_buttons_panel(self, parent):
		#
		#container: Holds all the widgets of this panel.
		#
		container = tk.Canvas(parent, 
					background="white", 
					width=220, height=722,
					highlightthickness=0)
		container.grid(row=0, column=3, sticky="nw", pady=15, padx=11)
		#
		#lbl_parsing: Label for section of view with buttons for parsing log files.
		#
		lbl_parsing = tk.Label(container, 
					text="LOG FILE PARSING", 
					width=27,  height=4, 
					background="aliceblue")
		lbl_parsing.pack(fill=tk.X, pady=2, padx=1)
		#
		#lbl_unprocessed: Label for section to parse unprocessed log files.
		#
		lbl_unprocessed = tk.Label(container, text="Unprocessed Log Files", 
						width=28, height=2, 
						background="lightyellow")
		lbl_unprocessed.pack(fill=tk.X, padx=1)
		lbl_unprocessed.bind("<Button-1>", self.show_unprocd_panel)
		#
		#bbtn: Process all unprocessed log files as a bulk processing.	
		#
		bbtn = ttk.Button(container, 
					text="Process All Bulk", 
					command=self.vc.bulk_process)
		bbtn.pack(fill=tk.X, pady=10)
		#
		#ibtn: Process all unproccessed log files one at a time.
		#
		ibtn = ttk.Button(container, text="Process All Individually")
		ibtn.pack(fill=tk.X)
		#
		#lbl_space: Spacer
		#
		lbl_space = tk.Label(container, height=2, background="white")
		lbl_space.pack(fill=tk.X, padx=1)
		#
		#lbl_processed: Label for section to parse processed log files.		
		#
		lbl_processed = tk.Label(container, 
						height=2, 
						text="Processed Log Files", 
						background="lightyellow")
		lbl_processed.pack(fill=tk.X, padx=1)
		lbl_processed.bind("<Button-1>", self.show_procd_panel)
		#
		#brbtn: Bulk re-parse all processed logs.
		#
		brbtn = ttk.Button(container, text="Re-process All Bulk")
		brbtn.pack(fill=tk.X, pady=10, padx=1)	
		#~ brbtn.pack(pady=10, padx=1)	
		#
		#lbl_space2: Spacer
		#
		lbl_space2 = tk.Label(container, height=25, background="white")
		lbl_space2.pack(padx=1)
		#
		#cfgbtn: Edit configuration 'settings.ini' button.
		#
		cfgbtn = ttk.Button(container, text="Edit Configuration")
		cfgbtn.pack(fill=tk.X, pady=1, padx=1)		
		#
		#hbtn: Show help info.
		#
		#~ hbtn = Button(self.frame, text="Help", width=30)
		#~ hbtn.grid(row=5, column=0)
		
		#
		#ecbtn: Edit the configuration file 'settings.ini'.
		#
		#~ ecbtn = Button(container, text="Edit Configuration", width=30)
		#~ ecbtn.grid(row=5, column=3, pady=4)
		
	#~ def populate(self, frame):
		#~ '''Put in some fake data'''
		#~ for row in range(100):
			#~ tk.Label(frame, 
				#~ text="%s" % row, 
				#~ width=3, 
				#~ borderwidth="1", 
				#~ relief="solid").grid(row=row, column=0)
			#~ t = "this is the second column for row %s" % row
			#~ tk.Label(frame, text=t).grid(row=row, column=1)
			
	#~ def onFrameConfigure(self, canvas):
		#~ '''Reset the scroll region to encompass the inner frame'''
		#~ canvas.configure(scrollregion=canvas.bbox("all"))
		
	def load_log_processing_panel(self, parent):
		#
		#frame: Holds the scrollbar and listbox.
		#
		frame = tk.Frame(parent, background="#ffffff")
		frame.pack()
		#
		#canvas: Main container for this panel.
		#
		#~ canvas = tk.Canvas(frame, borderwidth=0, background="#ffffff")
		#
		#vsb: Vertical scrollbar.
		#
		vsb = tk.Scrollbar(frame, orient="vertical")
		vsb.pack(side="right", fill="y", pady=5)
		#
		#listbox: Displays the contents of the runtime_log.
		#
		self.lb_runlog_data = tk.Listbox(frame, selectmode=tk.SINGLE)
		self.lb_runlog_data.pack(side=tk.LEFT, fill=tk.Y)
		self.lb_runlog_data.config(width=46, height=29)
		#
		#configure vsb command
		#
		vsb.configure(command=self.lb_runlog_data.yview)
		#
		#configure listbox yscrollcommand
		#
		self.lb_runlog_data.configure(yscrollcommand=vsb.set)
		
		
		#~ canvas.pack(side="left", fill="both", expand=True, pady=5)
		#~ canvas.create_window((4,4), window=frame, anchor="nw")
		
		#~ output = tk.Label(frame, textvariable=self.runtime_output)
		#~ output.pack()
		
		#~ frame.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigure(canvas))
		
		#~ self.populate(frame)
		
		
		#
		#lbl_bulk_proc: Label header for the bulk processing inf0.
		#
		#~ lbl_bulk_proc = Label(parent, 
						#~ background="lightyellow", 
						#~ text="Processing Log Files",
						#~ width=40, height=2)
		#~ lbl_bulk_proc.pack(fill=X, padx=5)
		#
		#frame: Frame to hold scrollbar and canvas.
		#
		#~ frame = tk.Frame(parent, bg="white", bd=0)
		#~ frame.pack(expand=True, fill=Y, padx=15, pady=10)
		#
		#scr
		#
		#~ scr = Scrollbar(frame, orient=VERTICAL)
		#~ scr.pack(side=RIGHT, fill=Y)
		#
		#container: Holds all the widgets of this panel.
		#
		#~ container = Canvas(frame, width=25, height=600, 
						#~ background="blue", relief="ridge",
						#~ highlightthickness=0)									
		#~ container.pack(side=LEFT, fill=BOTH, expand=YES)
		#~ container.config(scrollregion=[0,0,500,2000]) 			
		#~ container.config(yscrollcommand=scr.set)		
		#~ container.pack(side=LEFT, fill=BOTH, expand=YES)
		#~ container.create_window((0,0), window=layout_frame, anchor='nw')
		# Reset the view to home position.
		#~ container.yview_moveto(0)
		#
		#~ scr.config(command=container.yview)
		#
		#run_output: Console output of the bulk processing.
		#
		#~ run_output = Label(container,
					#~ width=50, height=100,
					#~ background="black",
					#~ textvariable=self.bulk_run_output)
		#~ run_output.pack(fill=X, pady=10, padx=5)
	
	def loadView(self):
		#
		#Styles
		#
		style = ttk.Style()
		style.configure("iislp.TFrame", background="white")
		#
		#self
		#
		self.frame.pack(fill=tk.BOTH, expand=1)	
		#~ self.frame.pack(expand=1)
		self.frame.columnconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)
		#
		#frame: This is the base container of all the display widgets.
		#
		base_frame = ttk.Frame(self.frame, borderwidth=1, style="iislp.TFrame")
		base_frame.grid(row=0, column=0, columnspan=2, rowspan=4, pady=10, padx=10, sticky="news")
		#
		#container (declaration): Container in the 'frame' that is scrollable.
		#
		self.container = tk.Canvas(base_frame,  width=500, height=600,
						background="lightsteelblue", 
						borderwidth=0,
						highlightthickness=0,
						relief="ridge")						
		#
		#layout_frame: Container that holds the widgets that display the app's info.
		#
		layout_frame = tk.Frame(self.container, bg="white", bd=0)
		layout_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)		
		#
		#layout_frame_bg: A blank white background for a frame.
		#
		layout_frame_bg = tk.Canvas(layout_frame, height=600, 
							background="white", 
							highlightthickness=0,  
							relief="ridge")
		layout_frame_bg.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, padx=5, pady=5)				
		#
		#scr_h1: Horizontal scrollbar that lives in 'frame' and moves 'container'.
		#
		scr_h1 = ttk.Scrollbar(base_frame, orient=tk.HORIZONTAL)
		scr_h1.pack(side=tk.BOTTOM, fill=tk.X)
		scr_h1.config(command=self.container.xview)
		#
		#container (init)
		#
		self.container.config(scrollregion=[0,0,2000,1000]) 			
		self.container.config(xscrollcommand=scr_h1.set)		
		self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		self.container.create_window((0,0), window=layout_frame, anchor='nw')
		# Reset the view to home position.
		self.container.xview_moveto(0)		
		#
		# Load in the panel that holds all of the buttons.
		#
		self.load_buttons_panel(self.frame)
		#
		# Load in the widgets that display the processed logs info.		
		#				
		self.load_procdlogs_panel(layout_frame_bg)
		#
		# Load in the widgets that display the unprocessed logs info.		
		#
		self.load_unprocdlogs_panel(layout_frame_bg)
		#
		# Load in the panel that shows Log Processing info when logs are bulk or indiv processed.
		#
		self.load_log_processing_panel(layout_frame_bg)
		

	def __init__(self, vc):
		#make the view
		self.frame = tk.Frame(bg="white")
		self.frame.grid(row=0,column=0)
		
		#set the delegate/callback pointer
		self.vc = vc
		
		#control variables go here. Make getters and setters for them below
		#~ self.entry_text = StringVar()
		#~ self.entry_text.set('nil')
		
		self.procd_logs_list 		= []
		self.unprocd_logs_list		= []
		# Processed log files.
		self.total_procd_logs 		= tk.StringVar()
		self.oldest_procd_log 		= tk.StringVar()
		self.newest_procd_log 	= tk.StringVar()
		# Unprocessed log files.
		self.total_unprocd_logs 	= tk.StringVar()
		self.oldest_unprocd_log 	= tk.StringVar()
		self.newest_unprocd_log 	= tk.StringVar()
		# Processing
		self.runtime_output		= tk.StringVar()
		
		#load the widgets
		self.loadView()
	
	#Getters and setters for the control variables.
	#~ def get_lbl_text(self):
		#~ #returns a string of the entry text
		#~ return self.entry_text.get()
	
	#~ def set_lbl(self, text):
		#~ #sets the entry text given a string
		#~ print ("set_lbl hit: ", text)
		#~ self.entry_text.set(text)
		
	#total procd logs
	def get_total_procd_logs(self):
		return self.total_procd_logs.get()	
		
	def set_total_procd_logs(self, text):
		self.total_procd_logs.set(text)
	
	# oldest procd log
	def get_oldest_procd_log(self):
		return self.oldest_procd_log.get()
		
	def set_oldest_procd_log(self, text):
		self.oldest_procd_log.set(text)
	
	# newest procd log
	def get_newest_procd_log(self):
		return self.newest_procd_log.get()
		
	def set_newest_procd_log(self, text):
		self.newest_procd_log.set(text)
		
	#total unprocd logs
	def get_total_unprocd_logs(self):
		return self.total_unprocd_logs.get()	
		
	def set_total_unprocd_logs(self, text):
		self.total_unprocd_logs.set(text)
	
	# oldest unprocd log
	def get_oldest_unprocd_log(self):
		return self.oldest_unprocd_log.get()
		
	def set_oldest_unprocd_log(self, text):
		self.oldest_unprocd_log.set(text)
	
	# newest unprocd log
	def get_newest_unprocd_log(self):
		return self.newest_unprocd_log.get()
		
	def set_newest_unprocd_log(self, text):
		self.newest_unprocd_log.set(text)
	
		
	def get_procd_logs_list(self):
		# Returns a list of processed logs
		return self.procd_logs_list	
		
	def set_procd_logs(self, proc_logs_list):
		print ("set_procd_logs: setting procd logs: list count ", len(proc_logs_list))		
		self.procd_logs_listbox.delete(0, tk.END)
		self.procd_logs_listbox.insert(tk.END, *proc_logs_list)
		self.procd_logs_listbox.update_idletasks()
		
	def get_unprocd_logs_list(self):
		return self.unprocd_logs_list
		
	def set_unprocd_logs(self, unprocd_logs_list):
		print ("set_unprocd_logs: count: ", len(unprocd_logs_list))
		self.unprocd_logs_listbox.delete(0, tk.END)
		self.unprocd_logs_listbox.insert(tk.END, *unprocd_logs_list)
		self.unprocd_logs_listbox.update_idletasks()
		
	def show_bulk_process_panel(self):
		self.container.xview_moveto(.331)	# Odd numbering for move.  Not sure what measurement is used.
		
	def get_runtime_output(self):
		return self.runtime_output.get()
		
	def set_runtime_output(self, text):
		#~ output_str = '\n'.join(text)  # Turn string into separate lines.
		#~ self.runtime_output.set(output_str)	
		print ("set_runtime_output: setting procd logs: list count ", len(text))		
		self.lb_runlog_data.delete(0, tk.END)
		self.lb_runlog_data.insert(tk.END, *text)
		self.lb_runlog_data.see(tk.END)
		self.lb_runlog_data.update_idletasks()
		print ("finished loading runtime_log info...")
		#~ print ("output_str: ", output_str)
		
	def show_unprocd_panel(self, *args):
		self.container.xview_moveto(.170)
		
	def show_procd_panel(self, *args):
		self.container.xview_moveto(0)
		#***HERE 
		#then start in on what happens in the bulk processing
		#and what gets shown in that panel.
		#also do the thing where the console output of a call to
		#iislp gets put into a textfile - which has an entry in ini file -
		# and a panel or a textbox in the bulk panel, that displays that
		# text file as it gets written
		# need to add some file watchers into the model i think
		# to keep an eye on the logs_done and other files and when
		# they change then call the controller methods that update the view.
		# need config editing screen too.
		
		
		
#Model: Data Structure.
#   --Controller can send messages to it, and model can respond to message.
#   --Uses delegates from vc to send messages to the Controller of internal change
#   --NEVER communicates with View
#   --Has setters and getters to communicate with Controller
 
class IISLPViewModel():
	def __init__(self,vc):
		#set delegate/callback pointer
		self.vc = vc
		
		#initialize model		
		self.log_done_path = self.vc.config.get_value(ConfigKeys.logsdone_log)
		
		self.procd_logs_list = []
		self.runtime_log_output = []		
		
		# Start up any watchers.
		self.runtime_watcher_status = "Stopped"
		#~ self.watch_runtime_log()
		
		#~ self.model = 0	
		
#Delegate goes here. Model would call this on internal change
	#~ def modelDidChange(self):
		#~ print ("model did change...")
		#~ self.vc.procd_logs_list_changeDelegate(self.procd_logs_list)
		#~ self.vc.set_runtime_output_changeDelegate(self.runtime_output)
		
	#Setters and getters for the model
	#~ def getModel(self):
		#~ return self.model
	
	def get_procd_logs_list(self):
		return self.procd_logs_list
	
	# This needs to be a watcher too.
	# Watch the logs_done.txt file for changes and alert controller if it changes.
	def set_procd_logs_list(self):
		print ("set_procd_logs_list: setting procd logs from logs_done.txt...")
		# Need to retrieve logs done list and save it locally.
		with open(self.log_done_path, 'r') as file:
			for line in file:
				#~ print ("line: ", line)
				self.procd_logs_list.append(line)
		
		print ("set_procd_logs_list: read in logs_done.txt...")
		self.vc.procd_logs_list_changeDelegate(self.procd_logs_list)
		#~ self.modelDidChange() #delegate called on change
		
	def start_watch_runtime(self):
		watcher_status = self.runtime_watcher_status
		print ("watcher status: ", watcher_status)
		if watcher_status is "Running":
			# Already running.
			return 
		
		if watcher_status is "Stopped":
			# Change the watcher status.
			self.runtime_watcher_status = "Running"
			# Start the watcher
			print ("Starting up the watcher...")
			self.watch_runtime_log()
			
	def stop_watch_runtime(self):
		self.watch_runtime_log = "Stopped"
	
	#Any internal processing for the model    
	def watch_runtime_log(self):
		print ("watch_runtime_log hit")	
		
		while (self.runtime_watcher_status == "Running"):
			cur_line_count = len(self.runtime_log_output)
			print ("cur_line_count: ", cur_line_count)
			with open(self.vc.config.get_value(ConfigKeys.runtime_log), 'r') as log:
				new_lines = []
				for line in log:
					new_lines.append(line)
			
			new_lines_count = len(new_lines)
			print ("new_lines_count: ", new_lines_count)
			if new_lines_count > cur_line_count:
				self.runtime_log_output = new_lines
				#~ print ("self.runtime_log_output: ", self.runtime_log_output)
				#Notify the controller.
				self.vc.set_runtime_output_changeDelegate(self.runtime_log_output)
				# Get out of here.
				print ("Leaving the watcher...")
				self.runtime_watcher_status = "Stopped"
				print ("self.runtime_watcher_status: ", self.runtime_watcher_status)
				
		print ("Leaving watch_runtime_log...")

class ThreadedClient:
	def __init__(self, master):
		self.master = master
		
		self.config = ConfigMgr()
		
		self.queue = queue.Queue()
		
		self.gui = Controller(master, 
					self.queue, 
					self.start_runtime_log_watcher, 
					self.end_runtime_log_watcher)
		
		self.running = 1
		self.thread1 = threading.Thread(target=self.worker_thread_1)
		self.thread1.start()
		
		self.periodic_call()
		
	def periodic_call(self):
		print ("TheadedClient: Entering periodic_call...")
		self.gui.process_runtime_logs()
		if not self.running:
			#~ import sys
			print ("AHHHHHHHH!!!!!!!!!!")
			#~ sys.exit(1)
		self.master.after(10, self.periodic_call)
		print ("TheadedClient: Leaving periodic_call...")
	
	def worker_thread_1(self):
		print ("TheadedClient: Entering worker_thread_1...")
		while (self.running):
			#~ cur_line_count = len(self.runtime_log_output)
			#~ print ("cur_line_count: ", cur_line_count)
			with open(self.config.get_value(ConfigKeys.runtime_log), 'r') as log:
				new_lines = []
				for line in log:
					new_lines.append(line)
			
			new_lines_count = len(new_lines)
			#~ print ("new_lines_count: ", new_lines_count)
			self.queue.put(new_lines)
			#~ if new_lines_count > cur_line_count:
				#~ self.runtime_log_output = new_lines
				#~ print ("self.runtime_log_output: ", self.runtime_log_output)
				#~ #Notify the controller.
				#~ self.vc.set_runtime_output_changeDelegate(self.runtime_log_output)
				#~ # Get out of here.
				#~ print ("Leaving the watcher...")
				#~ self.runtime_watcher_status = "Stopped"
				#~ print ("self.runtime_watcher_status: ", self.runtime_watcher_status)
				
		print ("TheadedClient: Leaving worker_thread_1...")
	
	def start_runtime_log_watcher(self):
		self.running = 1
	
	def end_runtime_log_watcher(self):
		self.running = 0
		
	def on_closing(self):
		# Clean up.
		self.end_runtime_log_watcher()
		self.master.destroy()

def main():
	root = tk.Tk()
	root.geometry("1280x768+100+100")
	root.maxsize(0, 735)
	root.minsize(1280, 735)
	root.iconbitmap(default='logo2.ico')
	root.title('iislp - IIS Log Parser')
	
	frame = tk.Frame(root, background="white")
	client = ThreadedClient(root)		
	
	root.protocol("WM_DELETE_WINDOW", client.on_closing)	
	root.mainloop()

if __name__ == '__main__':
	main()
	