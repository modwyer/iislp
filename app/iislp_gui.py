import os
import time
import threading
import queue
import tkinter as tk
import tkinter.ttk as ttk
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys

def get_subset(set, start, end):
	if len(set) < end:
		return set
		
	subset = []	
	for x in range(start, end):
		subset.append(set[x])
		
	return subset

class Controller():
	def __init__(self, 
			parent, 
			queue, 
			pause_runlog_thread,
			start_runlog_thread):
		
		self.parent = parent
		self.queue = queue
		
		# Access methods from parent.
		self.pause_runlog_thread = pause_runlog_thread
		self.start_runlog_thread = start_runlog_thread
		
		self.is_processing = 0
		self.runtime_log_count = 0
		
		self.final_runlog_output = "Killing all processes"
		
		self.config = ConfigMgr()		
		self.view = MainView(self)		
		self.model = IISLPViewModel(self)
		
		self.unprocd_logs_list = []
				
		#initalize properties in model, if any	
		self.model.set_procd_logs_list()		# Get the processed logs list.
		
		
		#initialize properties in view, if any		
			
	def process_runtime_logs(self):
		while (self.queue.qsize()):
			try:
				log_info = self.queue.get(0)
				len_log_info = len(log_info)
				
				# While the app is running, we only display additional entries.
				# Removed entries will be ignored until more lines are saved.
				if len_log_info > self.runtime_log_count:
					self.runtime_log_count = len_log_info
					print ("GuiThread: self.runtime_log_count : ", self.runtime_log_count )
					self.view.set_runtime_output(log_info)
					
					# Auto-shutdown the runtime_log thread if the final line contains
					# 'Killing all processes'.
					if self.final_runlog_output in log_info[len_log_info - 1]:
						self.pause_runlog_thread()
			except Queue.Empty:
				pass
		
	def load_procd_logs(self):
		self.model.set_procd_logs_list()
		
	def runlogs_loaded(self):
		# Runtime logs are loaded.  Finish up.   
		if not self.is_processing:
			self.pause_runlog_thread()
		
#event handlers 	
	def bulk_process(self):
		self.view.show_log_processing_panel()		# Move scrollview to the bulk processing panel.
		
		if self.is_processing is 1: 
			return
		else: 
			#should we call methods in view to disable buttons??
			self.is_processing = 1					# Let be known we are in the middle of processing log files
			
		self.view.set_proc_output("Starting bulk processing...")
		self.view.set_proc_output("Starting runtime_log reading thread...")
		
		self.start_runlog_thread()					# Start displaying changes made to 'run_time.log'.		
		unprocd_log_count = len(self.unprocd_logs_list)	# How many unprocessed logs?
				
		# Put all of the logs into batches of 40.
		log_batches = {}
		start = 0
		end = 40
		post_fix = 0
		unprocd_log_count = 2
		iter_count = 40 % unprocd_log_count
		print ("iter_count: ", iter_count)
		
		if iter_count is 0:
			log_batches["batch_%s" % str(iter_count)] = self.unprocd_logs_list[:unprocd_log_count]
		else:		
			for x in range(0, iter_count):
				log_batches["batch_%s" % str(x)] = self.unprocd_logs_list[start:end]
				new_start = start + 40
				new_end = end + 40
				start = new_start if unprocd_log_count > new_start else unprocd_log_count - 1
				end = new_end if unprocd_log_count > new_end else unprocd_log_count
			
		self.view.set_proc_output("Unprocessed logs count: %s" % len(self.unprocd_logs_list))
		self.view.set_proc_output("Unprocessed log_batches: %s" % str(log_batches))
		
		
		
		
		# Need to take the first 40 logs (0 < logs < (40 if logs len > 40 else logs len)).
		#~ end = 40 if unprocd_log_count > 40 else unprocd_log_count
		#~ print ("end: ", end)
		#~ working_set = []
		#~ logs_left = []
		
		#~ for x in range(0, end):
			#~ working_set.append(self.unprocd_logs_list[x])
		
		#~ self.view.set_proc_output("Unprocessed logs: [%s]" % ', '.join(working_set))
		
		#~ if unprocd_log_count > 40:
			#~ logs_left = []
			#~ for x in range(40, end):
				#~ logs_left.append(self.unprocd_logs_list[x])
		
		#~ self.view.set_proc_output("Logs_left.count: %s" % len(logs_left))
		#~ self.view.set_proc_output("Logs_left: [%s]" % ', '.join(logs_left))
		
		
		
	def set_procd_logs(self, log_list):
		list_len = len(log_list)
		self.view.set_procd_logs(log_list)				# Update processed logs list.
		self.view.set_total_procd_logs(list_len)	
		self.view.set_oldest_procd_log(log_list[0])
		self.view.set_newest_procd_log(log_list[list_len - 1])
		
	def set_unprocd_logs(self, log_list):
		log_done_path = self.config.get_value(ConfigKeys.log_done)
		
		all_log_files = ([f for f in os.listdir(log_done_path) 
			if f.endswith('.log')])
		all_log_files_len = len(all_log_files)		
				
		filenames = [s[-13:] for s in log_list]				# Slice out the filenames from each string in log_list.
		filenames_len = len(filenames)				
		'''
		The items found in the new_set are the difference between all the 
		log file names found in the log_done directory and the names of 
		the log files that have been parsed already.
		The list 'all_log_files' in ascending order as is the list 'filenames'.
		The length of the list of parsed log files 
		'''
		new_set = all_log_files[len(filenames):]
		# Save a copy of the unprocessed logs.
		self.unprocd_logs_list = new_set
		
		# Tell the view to update its uprocessed logs list.
		list_len = len(new_set)
		self.view.set_unprocd_logs(new_set)
		self.view.set_total_unprocd_logs(list_len)	
		self.view.set_oldest_unprocd_log(new_set[0])
		self.view.set_newest_unprocd_log(new_set[list_len - 1])		

#delegates 
	def procd_logs_list_changeDelegate(self, lst):
		# Update view widgets showing 'processed logs' info.		
		self.set_procd_logs(lst)	# Update the processed logs' info fields.
		self.set_unprocd_logs(lst)	# Update unprocessed logs list.
		
	def set_runtime_output_changeDelegate(self, output):
		self.view.set_runtime_output(output)

class MainView(tk.Frame):
	def load_procdlogs_panel(self, parent):
		#
		#procd_logs: Main container that displays info about the processed logs.
		#
		procd_logs = tk.Canvas(parent, width=25, height=650, 
						background="#ffffff", relief="ridge",
						highlightthickness=0)									
		procd_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		#
		#procd_logs_info_frame: Frame for the top half of the processed logs container.
		#
		procd_logs_info_frame = tk.Frame(procd_logs, bg="#ffffff", bd=0)
		procd_logs_info_frame.pack()
		#
		#procd_logs_info: Container that holds some stats about the processed logs.
		#
		procd_logs_info_container = tk.Canvas(procd_logs_info_frame,
									background="#ffffff",
									borderwidth=0,
									highlightthickness=0, 
									relief="ridge")
		procd_logs_info_container.pack(pady=5, padx=15)
		#
		#procd_logs_content_frame: Frame to hold a canvas and a vertical scrollbar connected to the canvas.
		#
		procd_logs_content_frame = tk.Frame(procd_logs, bg="#ffffff", bd=0)
		procd_logs_content_frame.pack(expand=True, fill=tk.Y, padx=15, pady=10)
		#
		#scr_proc_logs: Scroll through the list of processed logs.
		#
		scr_proc_logs = ttk.Scrollbar(procd_logs_content_frame, orient=tk.VERTICAL)
		scr_proc_logs.pack(side=tk.RIGHT, fill=tk.Y)
		#
		#self.procd_logs_listbox: Holds the content of the logs_done.txt file- all the processed logs.
		# 				     This is filled in the method 'set_procd_logs'.
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
		lbl_total_proc_logs = tk.Label(procd_logs_info_container, background="#ffffff", text="Total")
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
							background="#ffffff", 
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
							background="#ffffff", 
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
						background="#ffffff", relief="ridge",
						highlightthickness=0)									
		unprocd_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		#
		#unprocd_logs_info_frame: Frame for the top half of the unprocessed logs container.
		#
		unprocd_logs_info_frame = tk.Frame(unprocd_logs, bg="#ffffff", bd=0)
		unprocd_logs_info_frame.pack()
		#
		#unprocd_logs_info: Container that holds some stats about the unprocessed logs.
		#
		unprocd_logs_info_container = tk.Canvas(unprocd_logs_info_frame,
									background="#ffffff",
									borderwidth=0,
									highlightthickness=0, 
									relief="ridge")
		unprocd_logs_info_container.pack(pady=5, padx=15)
		#
		#unprocd_logs_content_frame: Frame to hold a canvas and a vertical scrollbar connected to the canvas.
		#
		unprocd_logs_content_frame = tk.Frame(unprocd_logs, bg="#ffffff", bd=0)
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
		lbl_total_unproc_logs = tk.Label(unprocd_logs_info_container, background="#ffffff", text="Total")
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
		lbl_oldest_unproc_log = tk.Label(unprocd_logs_info_container, background="#ffffff", text="Oldest")
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
		lbl_newest_unproc_log = tk.Label(unprocd_logs_info_container, background="#ffffff", text="Newest")
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
					background="#ffffff", 
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
		lbl_space = tk.Label(container, height=2, background="#ffffff")
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
		#
		#lbl_space2: Spacer
		#
		lbl_space2 = tk.Label(container, height=25, background="#ffffff")
		lbl_space2.pack(padx=1)
		#
		#cfgbtn: Edit configuration 'settings.ini' button.
		#
		cfgbtn = ttk.Button(container, text="Edit Configuration")
		cfgbtn.pack(fill=tk.X, pady=1, padx=1)
		'''
		***TODO: Need to create new window to be able to edit the config.
		'''
		
	def load_log_processing_panel(self, parent):
		#
		#m: PanedWindow
		#
		m = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
		m.pack(fill=tk.BOTH, expand=1)
		#
		#frame: Holds the widgets displaying output of a processing job.
		#
		frame = tk.Frame(m, background="lightgray")
		frame.pack()
		#
		#lbl_proc_output: Header for processing output.
		#
		lbl_proc_output = tk.Label(frame, text="Processing Output", background="lightyellow", height=2)
		lbl_proc_output.pack(fill=tk.X)
		#
		#self.tb_proc_output: Output from the gui kicking off log file processing.
		#
		self.tb_proc_output = tk.Text(frame, wrap=tk.WORD)
		self.tb_proc_output.pack(side=tk.LEFT, fill=tk.Y)
		self.tb_proc_output.config(width=40, height=29)
		#
		#frame: Holds the scrollbar and listbox.
		#
		frame2 = tk.Frame(m, background="#ffffff", relief=tk.SUNKEN)
		frame2.pack()
		#
		#lbl_runlog:  Header for the runtime_log output.
		#
		lbl_text = self.vc.config.get_value(ConfigKeys.runtime_log)
		lbl_runlog = tk.Label(frame2, text="'" + lbl_text +"'", background="lightyellow", height=2)
		lbl_runlog.pack(fill=tk.X)
		#
		#vsb: Vertical scrollbar.
		#
		vsb = tk.Scrollbar(frame2, orient="vertical")
		vsb.pack(side="right", fill="y", pady=5)
		#
		#self.lb_runlog_data: Displays the contents of the runtime_log.
		#
		self.lb_runlog_data = tk.Listbox(frame2, selectmode=tk.SINGLE)
		self.lb_runlog_data.pack(side=tk.LEFT, fill=tk.Y)
		self.lb_runlog_data.config(width=110, height=29)
		#
		#configure vsb command
		#
		vsb.configure(command=self.lb_runlog_data.yview)
		#
		#configure listbox yscrollcommand
		#
		self.lb_runlog_data.configure(yscrollcommand=vsb.set)		
		#
		# Add the frames to the panedwindow.
		#
		m.add(frame)
		m.add(frame2)
			
	def loadView(self):
		#
		#Styles
		#
		style = ttk.Style()
		style.configure("iislp.TFrame", background="#ffffff")
		#
		#self
		#
		self.frame.pack(fill=tk.BOTH, expand=1)	
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
		layout_frame = tk.Frame(self.container, bg="#ffffff", bd=0)
		layout_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)		
		#
		#layout_frame_bg: A blank white background for a frame.
		#
		layout_frame_bg = tk.Canvas(layout_frame, height=600, 
							background="#ffffff", 
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
		self.frame = tk.Frame(bg="#ffffff")
		self.frame.grid(row=0,column=0)
		
		#set the delegate/callback pointer
		self.vc = vc
		
		#control variables go here. Make getters and setters for them below		
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
		print ("GuiThread: Processed logs list count: ", len(proc_logs_list))
		self.procd_logs_listbox.delete(0, tk.END)
		self.procd_logs_listbox.insert(tk.END, *proc_logs_list)
		self.procd_logs_listbox.update_idletasks()
		
	def get_unprocd_logs_list(self):
		return self.unprocd_logs_list
		
	def set_unprocd_logs(self, unprocd_logs_list):
		print ("GuiThread: Unprocessed logs list count: ", len(unprocd_logs_list))
		self.unprocd_logs_listbox.delete(0, tk.END)
		self.unprocd_logs_listbox.insert(tk.END, *unprocd_logs_list)
		self.unprocd_logs_listbox.update_idletasks()
		
	def show_log_processing_panel(self):
		self.container.xview_moveto(.331)	# Odd numbering for move.  Not sure what measurement is used.
	
	def set_proc_output(self, output, clear=None):
		print ("GuiThread: Set Processing output...", output)
		if clear is True:
			self.tb_proc_output.delete(0, tk.END)
		self.tb_proc_output.insert(tk.END, output)
		self.tb_proc_output.insert(tk.END, "\n")
		self.tb_proc_output.update_idletasks()
	
	def get_runtime_output(self):
		return self.runtime_output.get()
		
	def set_runtime_output(self, text):	
		self.lb_runlog_data.delete(0, tk.END)
		self.lb_runlog_data.insert(tk.END, *text)
		self.lb_runlog_data.see(tk.END)
		self.lb_runlog_data.update_idletasks()
		
	def show_unprocd_panel(self, *args):
		self.container.xview_moveto(.170)
		
	def show_procd_panel(self, *args):
		self.container.xview_moveto(0)

class IISLPViewModel():
	def __init__(self,vc):
		#set delegate/callback pointer
		self.vc = vc
		
		#initialize model		
		self.log_done_path = self.vc.config.get_value(ConfigKeys.logsdone_log)
		
		self.procd_logs_list = []
		self.runtime_log_output = []	
		
#Delegate goes here. Model would call this on internal change
		
	#Setters and getters 
	def get_procd_logs_list(self):
		return self.procd_logs_list
	
	'''
	***TODO.  THIS NEEDS TO BE A THREAD!!!!!!!!!!!!!!!!
	'''
	def set_procd_logs_list(self):
		# Need to retrieve logs done list and save it locally.
		with open(self.log_done_path, 'r') as file:
			for line in file:
				self.procd_logs_list.append(line)
		
		self.vc.procd_logs_list_changeDelegate(self.procd_logs_list)
		
class iislpThread(threading.Thread):
	def __init__(self, cmd):
		threading.Thread.__init__(self)
		self.run_command = cmd
		self.daemon = True
		self.paused = False
		self.state = threading.Condition()
		
	def run(self):
		while True:
			with self.state:
				if self.paused:
					self.state.wait()	# block
				else: 
					self.run_command()
	
	def resume(self):
		with self.state:
			self.paused = False
			self.state.notify() # unblock
			print ("Resume running thread...")
			
	def pause(self):
		with self.state:
			self.paused = True # make self block and wait

class ThreadedClient:
	'''Adapted from: http://code.activestate.com/recipes/82965-threads-tkinter-and-asynchronous-io/'''
	def __init__(self, master):
		self.master = master		
		self.config = ConfigMgr()
		self.call_interval = 100
		self.queue = queue.Queue()		
		self.gui = Controller(master, 
					self.queue,  
					self.pause_runlog_thread,
					self.start_runlog_thread)
		
		self.running = 1
		self.thread1 = iislpThread(self.worker_thread_1)		
		self.thread1.start()
		
		self.periodic_call()
		
	def periodic_call(self):
		self.gui.process_runtime_logs()		
		self.master.after(100, self.periodic_call)
	
	def worker_thread_1(self):
		while(self.running):
			with open(self.config.get_value(ConfigKeys.runtime_log), 'r') as log:
				new_lines = []
				for line in log:
					new_lines.append(line)
			
			# Add the log info to the queue.
			self.queue.put(new_lines)
	
	def start_runlog_thread(self):
		print ("Start runtime log thread...")
		self.running = 1
		self.thread1.resume()		
	
	def pause_runlog_thread(self):
		print ("End runtime log thread...")
		self.running = 0
		self.thread1.pause()
		
	def on_closing(self):
		# Clean up.
		self.pause_runlog_thread()
		self.master.destroy()

def main():
	#
	#root
	#
	root = tk.Tk()
	root.geometry("1280x768+100+100")
	root.maxsize(0, 735)
	root.minsize(908, 735)
	root.iconbitmap(default='logo2.ico')
	root.title('iislp - IIS Log Parser')
	#
	#frame: Main frame of application.
	#
	frame = tk.Frame(root, background="#ffffff")
	#
	#client: Handles multi-threading for application.
	#
	client = ThreadedClient(root)		
	
	root.protocol("WM_DELETE_WINDOW", client.on_closing)	
	root.mainloop()

if __name__ == '__main__':
	main()
	