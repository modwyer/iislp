#MVC_Template_01
#2014 May 23  by Steven Lipton http://makeAppPie.com
#Controller initializing MVC -- simplest version possible.
import os
from tkinter import *
from tkinter.ttk import Style
#~ import tkinter as tk
#~ import tkinter.ttk as ttk
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
	def __init__(self,parent):
		print ("Init m and v...")
		self.parent = parent
		self.config = ConfigMgr()
		
		self.view = MainView(self)
		self.model = IISLPViewModel(self)
		
		#initalize properties in model, if any
		print ("Init properties in model...")		
		self.model.set_procd_logs_list()		# Get the processed logs list.
		
		#initialize properties in view, if any
		print ("Init properties in view...")
		#~ self.load_procd_logs()		# Load the processed logs into view.
		#~ pass
	
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
		
	def set_procd_logs(self, log_list):
		list_len = len(log_list)
		self.view.set_procd_logs(log_list)					# Update processed logs list.
		self.view.set_total_procd_logs(list_len)	
		self.view.set_oldest_procd_log(log_list[0])
		self.view.set_newest_procd_log(log_list[list_len - 1])
		
	def set_unprocd_logs(self, log_list):
		print ("set_unprocd_logs_info: ")
		log_done_path = self.config.get_value(ConfigKeys.log_done)
		print ("log_done_path: ", log_done_path)
		#~ file = ([f for f in os.listdir(log_done_path) 
			#~ if f.endswith('.log') and os.path.isfile(os.path.join(log_done_path, f))])
		all_log_files = ([f for f in os.listdir(log_done_path) 
			if f.endswith('.log')])
		all_log_files_len = len(all_log_files)		
			
			
		print ("file count (all_log_files_len): ", all_log_files_len)
		print ("all_log_files[0]: ", all_log_files[0])
		print ("all_log_files[len]: ", all_log_files[all_log_files_len - 1])
		print ("log_list[0]: ", log_list[0])
		filenames = [s[-13:] for s in log_list]		# Slice out the filenames from each string in log_list.
		print ("done filenames[0]: ", filenames[0])
		filenames_len = len(filenames)
		print ("filenames len: ", filenames_len)
		print ("done filenames[len]: ", filenames[filenames_len - 1])
		
		print ("all_log_files[0] in filenames[0]: ", (all_log_files[0] in filenames[0]))
		
		
		
		
		
		#~ done_set = iter(filenames)
		#~ new_set = reduce(set.intersection, map(files, done_set))
		#~ new_set = set(filenames).intersection(all_log_files)
		#~ new_set = any(map(lambda v: v in filenames, all_log_files))
		
		#~ new_set = []
		#~ for n in all_log_files:
			#~ if n not in filenames:				
				#~ print ("n: ", n)
				#~ new_set.append(n)
				
		#~ new_set = list(set(all_log_files) - set(filenames))
		#~ start = len(filenames)
		#~ sublist_len = len(all_log_files) - start
		#~ print ("start: ", start)
		#~ print ("sublist_len: ", sublist_len)
		'''
		The items found in the new_set are the difference between all the 
		log file names found in the log_done directory and the names of 
		the log files that have been parsed already.
		The list 'all_log_files' in ascending order as is the list 'filenames'.
		The length of the list of parsed log files 
		'''
		if filenames_len == all_log_files_len:
			print ("filenames_len == all_log_files_len: ", (filenames_len == all_log_files_len))
		else:
			print ("filenames_len != all_log_files_len: ", (filenames_len != all_log_files_len))
		new_set = all_log_files[len(filenames):]
			
		print ("new_set count: ", len(new_set))
		print ("new_set: ", new_set)
		
		# Tell the view to update its uprocessed logs list.
		list_len = len(new_set)
		self.view.set_unprocd_logs(new_set)
		self.view.set_total_unprocd_logs(list_len)	
		self.view.set_oldest_unprocd_log(new_set[0])
		self.view.set_newest_unprocd_log(new_set[list_len - 1])
		

#delegates -- add functions called by delegtes in model or view
	def procd_logs_list_changeDelegate(self, lst):
		# Update view widgets showing 'processed logs' info.
		print ("List did change delegate...")
		
		self.set_procd_logs(lst)	# Update the processed logs' info fields.
		self.set_unprocd_logs(lst)	# Update unprocessed logs list.
		
#View : User interface elements.
#       --Controller can send messages to it.
#       --View can call methods from Controller vc when an event happens.
#       --NEVER communicates with Model.
#       --Has setters and getters to communicate with controller
 
class MainView(Frame):
	def load_procdlogs_panel(self, parent):
		#
		#lbl_log_stat_header: Header label for section that shows the status of processed/unprocessed logs.
		#
		lbl_log_stat_header = Label(parent, background="white", text="Log File Status", width=20, anchor=CENTER)
		lbl_log_stat_header.pack(side=TOP, expand=True, pady=10)
		#
		#procd_logs: Main container that displays info about the processed logs.
		#
		procd_logs = Canvas(parent, width=25, height=650, 
						background="white", relief="ridge",
						highlightthickness=0)									
		procd_logs.pack(side=LEFT, fill=BOTH, expand=YES)
		#
		#procd_logs_info_frame: Frame for the top half of the processed logs container.
		#
		procd_logs_info_frame = Frame(procd_logs, bg="white", bd=0)
		procd_logs_info_frame.pack()
		#
		#procd_logs_info: Container that holds some stats about the processed logs.
		#
		procd_logs_info_container = Canvas(procd_logs_info_frame,
									background="white",
									borderwidth=0,
									highlightthickness=0, 
									relief="ridge")
		procd_logs_info_container.pack(pady=5, padx=15)
		#
		#procd_logs_content_frame: Frame to hold a canvas and a vertical scrollbar connected to the canvas.
		#
		procd_logs_content_frame = Frame(procd_logs, bg="white", bd=0)
		procd_logs_content_frame.pack(expand=True, fill=Y, padx=15, pady=10)
		#
		#scr_proc_logs: Scroll through the list of processed logs.
		#
		scr_proc_logs = Scrollbar(procd_logs_content_frame, orient=VERTICAL)
		scr_proc_logs.pack(side=RIGHT, fill=Y)
		#
		#self.procd_logs_listbox: Holds the content of the logs_done.txt file- all the processed logs.
		# This is filled in the method 'set_procd_logs'.
		#
		self.procd_logs_listbox = Listbox(procd_logs_content_frame, selectmode=EXTENDED)
		self.procd_logs_listbox.pack(side=LEFT, fill=Y, expand=YES)
		self.procd_logs_listbox.config(width=46)
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
		lbl_proc_logs = Label(procd_logs_info_container, 
						background="lightyellow", 
						text="Processed Log Files", 
						width=20, height=2, 
						anchor=CENTER)
		lbl_proc_logs.grid(row=0, column=0,  columnspan=2, sticky=W, pady=10)
		#
		#lbl_total: Total number of logs that have been parsed.
		#
		lbl_total_proc_logs = Label(procd_logs_info_container, background="white", text="Total")
		lbl_total_proc_logs.grid(sticky=W, pady=5, padx=5, row=1, column=0)
		#
		#tb_total_proc_logs
		#
		tb_total_proc_logs = Entry(procd_logs_info_container, width=40, relief=FLAT, textvariable=self.total_procd_logs) # Binding textvariable to self StringVar
		tb_total_proc_logs.grid(sticky=W, pady=5, row=1, column=1)
		tb_total_proc_logs.config(state=DISABLED)
		#
		#lbl_oldest_proc_log: The oldest log that has been parsed.
		#
		lbl_oldest_proc_log = Label(procd_logs_info_container, background="white", text="Oldest")
		lbl_oldest_proc_log.grid(sticky=W, pady=5, padx=5, row=2, column=0)
		#
		#tb_oldest_proc_logs
		#		
		tb_oldest_proc_logs = Entry(procd_logs_info_container, width=40, relief=FLAT, textvariable=self.oldest_procd_log)
		tb_oldest_proc_logs.grid(sticky=W, pady=5, row=2, column=1)
		tb_oldest_proc_logs.config(state=DISABLED)
		#
		#lbl_newest_proc_log: The oldest log that has been parsed.
		#
		lbl_newest_proc_log = Label(procd_logs_info_container, background="white", text="Newest")
		lbl_newest_proc_log.grid(sticky=W, pady=5, padx=5, row=3, column=0)
		#
		#tb_newest_proc_logs
		#
		tb_newest_proc_logs = Entry(procd_logs_info_container, width=40, relief=FLAT, textvariable=self.newest_procd_log)
		tb_newest_proc_logs.grid(sticky=W, pady=5, row=3, column=1)	
		tb_newest_proc_logs.config(state=DISABLED)
		
	def load_unprocdlogs_panel(self, parent):
		#
		#unprocd_logs: Main container that displays info about the unprocessed logs.
		#
		unprocd_logs = Canvas(parent, width=25, height=650, 
						background="white", relief="ridge",
						highlightthickness=0)									
		unprocd_logs.pack(side=RIGHT, fill=BOTH, expand=YES)
		#
		#unprocd_logs_info_frame: Frame for the top half of the unprocessed logs container.
		#
		unprocd_logs_info_frame = Frame(unprocd_logs, bg="white", bd=0)
		unprocd_logs_info_frame.pack()
		#
		#unprocd_logs_info: Container that holds some stats about the unprocessed logs.
		#
		unprocd_logs_info_container = Canvas(unprocd_logs_info_frame,
									background="white",
									borderwidth=0,
									highlightthickness=0, 
									relief="ridge")
		unprocd_logs_info_container.pack(pady=5, padx=15)
		#
		#unprocd_logs_content_frame: Frame to hold a canvas and a vertical scrollbar connected to the canvas.
		#
		unprocd_logs_content_frame = Frame(unprocd_logs, bg="white", bd=0)
		unprocd_logs_content_frame.pack(expand=True, fill=Y, padx=15, pady=10)
		#
		#scr_unproc_logs: Scroll through the list of unprocessed logs.
		#
		scr_unproc_logs = Scrollbar(unprocd_logs_content_frame, orient=VERTICAL)
		scr_unproc_logs.pack(side=RIGHT, fill=Y)
		#
		#self.unprocd_logs_listbox: Displays a list of all log files found in the log_done directory
		#				         that have not yet been processed.
		#				         This is filled in the method 'set_unprocd_logs'.
		#
		self.unprocd_logs_listbox = Listbox(unprocd_logs_content_frame, selectmode=EXTENDED)
		self.unprocd_logs_listbox.pack(side=LEFT, fill=Y)
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
		lbl_unproc_logs = Label(unprocd_logs_info_container, 
						background="lightyellow", 
						text="Unprocessed Log Files", 
						width=20, height=2, 
						anchor=CENTER)
		lbl_unproc_logs.grid(row=0, column=0,  columnspan=2, sticky=W, pady=10)
		#
		#lbl_total_unproc_logs: Total number of logs that have NOT yet been parsed.
		#
		lbl_total_unproc_logs = Label(unprocd_logs_info_container, background="white", text="Total")
		lbl_total_unproc_logs.grid(sticky=W, pady=5, padx=5, row=1, column=0)
		#
		#tb_total_unproc_logs
		#
		tb_total_unproc_logs = Entry(unprocd_logs_info_container, width=40, relief=FLAT, textvariable=self.total_unprocd_logs) # Binding textvariable to self StringVar
		tb_total_unproc_logs.grid(sticky=W, pady=5, row=1, column=1)
		tb_total_unproc_logs.config(state=DISABLED)
		#
		#lbl_oldest_unproc_log: The oldest log that has NOT yet been parsed.
		#
		lbl_oldest_unproc_log = Label(unprocd_logs_info_container, background="white", text="Oldest")
		lbl_oldest_unproc_log.grid(sticky=W, pady=5, padx=5, row=2, column=0)
		#
		#tb_oldest_unproc_logs
		#		
		tb_oldest_unproc_logs = Entry(unprocd_logs_info_container, width=40, relief=FLAT, textvariable=self.oldest_unprocd_log)
		tb_oldest_unproc_logs.grid(sticky=W, pady=5, row=2, column=1)
		tb_oldest_unproc_logs.config(state=DISABLED)
		#
		#lbl_newest_unproc_log: The oldest log that has been parsed.
		#
		lbl_newest_unproc_log = Label(unprocd_logs_info_container, background="white", text="Newest")
		lbl_newest_unproc_log.grid(sticky=W, pady=5, padx=5, row=3, column=0)
		#
		#tb_newest_unproc_logs
		#
		tb_newest_unproc_logs = Entry(unprocd_logs_info_container, width=40, relief=FLAT, textvariable=self.newest_unprocd_log)
		tb_newest_unproc_logs.grid(sticky=W, pady=5, row=3, column=1)	
		tb_newest_unproc_logs.config(state=DISABLED)
	
	def loadView(self):
		#
		#self
		#
		self.frame.pack(fill=BOTH, expand=1)	
		#~ self.frame.columnconfigure(1, weight=1)
		#~ self.frame.columnconfigure(3, pad=7)
		#~ self.frame.rowconfigure(3, weight=1)
		#~ self.frame.rowconfigure(5, pad=7)
		
		self.frame.columnconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)
		#~ content.columnconfigure(0, weight=3)
		#~ content.columnconfigure(1, weight=3)
		#~ content.columnconfigure(2, weight=3)
		#~ content.columnconfigure(3, weight=1)
		#~ content.columnconfigure(4, weight=1)
		#~ content.rowconfigure(1, weight=1)
		#
		#frame: This is the base container of all the display widgets.
		#
		base_frame = Frame(self.frame, borderwidth=0, bg="white", bd=1)
		base_frame.grid(row=0, column=0, columnspan=2, rowspan=4, pady=10, padx=10, sticky=E+W+S+N)
		#
		#container (declaration): Container in the 'frame' that is scrollable.
		#
		container = Canvas(base_frame,  width=500, height=600,
						background="lightsteelblue", 
						borderwidth=0,
						highlightthickness=0,
						relief="ridge")						
		#
		#layout_frame: Container that holds the widgets that display the app's info.
		#
		layout_frame = Frame(container, bg="white", bd=0)
		#~ layout_frame.grid(row=0, column=0, sticky=E+S)
		#~ layout_frame.rowconfigure(0, weight=1)
		#~ layout_frame.columnconfigure(0, weight=1)
		layout_frame.pack(side=LEFT, fill=BOTH, expand=YES)
		#~ layout_frame.pack(side=LEFT)
		#~ layout_frame.config(width=3000)	
		#
		#layout_frame_bg: A blank white background for a frame.
		#
		layout_frame_bg = Canvas(layout_frame, height=600, 
							background="white", 
							highlightthickness=1,  
							relief="ridge")
		layout_frame_bg.pack(side=LEFT, fill=BOTH, expand=YES, padx=5, pady=5)		
		#
		#scr_h1: Horizontal scrollbar that lives in 'frame' and moves 'container'.
		#
		scr_h1 = Scrollbar(base_frame, orient=HORIZONTAL)
		scr_h1.pack(side=BOTTOM, fill=X)
		scr_h1.config(command=container.xview)
		#
		#container (init)
		#
		container.config(scrollregion=[0,0,2000,1000]) 			
		container.config(xscrollcommand=scr_h1.set)		
		container.pack(side=LEFT, fill=BOTH, expand=YES)
		container.create_window((0,0), window=layout_frame, anchor='nw')
		# Reset the view to home position.
		container.xview_moveto(0)
		#
		#bbtn: Process all unprocessed log as a bulk processing.	
		#
		bbtn = Button(self.frame, text="Process All Bulk", width=30)
		bbtn.grid(row=0, column=3, pady=10)
		#
		#hbtn: Show help info.
		#
		hbtn = Button(self.frame, text="Help", width=30)
		hbtn.grid(row=5, column=0)
		#
		#cbtn: Close the app.
		#
		cbtn = Button(self.frame, text="Close", width=30)
		cbtn.grid(row=5, column=3, pady=4)
		#
		# Load in the widgets that display the processed logs info.		
		#				
		self.load_procdlogs_panel(layout_frame_bg)
		#
		#Load in the widgets that display the unprocessed logs info.		
		#
		self.load_unprocdlogs_panel(layout_frame_bg)

	def __init__(self, vc):
		#make the view
		self.frame = Frame(bg="white")
		self.frame.grid(row=0,column=0)
		
		#set the delegate/callback pointer
		self.vc = vc
		
		#control variables go here. Make getters and setters for them below
		#~ self.entry_text = StringVar()
		#~ self.entry_text.set('nil')
		
		self.procd_logs_list 		= []
		self.unprocd_logs_list		= []
		# Processed log files.
		self.total_procd_logs 		= StringVar()
		self.oldest_procd_log 		= StringVar()
		self.newest_procd_log 	= StringVar()
		# Unprocessed log files.
		self.total_unprocd_logs 	= StringVar()
		self.oldest_unprocd_log 	= StringVar()
		self.newest_unprocd_log 	= StringVar()
		
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
		self.procd_logs_listbox.delete(0, END)
		self.procd_logs_listbox.insert(END, *proc_logs_list)
		self.procd_logs_listbox.update_idletasks()
		
	def get_unprocd_logs_list(self):
		return self.unprocd_logs_list
		
	def set_unprocd_logs(self, unprocd_logs_list):
		print ("set_unprocd_logs: count: ", len(unprocd_logs_list))
		self.unprocd_logs_listbox.delete(0, END)
		self.unprocd_logs_listbox.insert(END, *unprocd_logs_list)
		self.unprocd_logs_listbox.update_idletasks()
		
		
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
		
		#~ self.model = 0	
		
#Delegate goes here. Model would call this on internal change
	def modelDidChange(self):
		print ("model did change...")
		self.vc.procd_logs_list_changeDelegate(self.procd_logs_list)
		
	#Setters and getters for the model
	#~ def getModel(self):
		#~ return self.model
	
	def get_procd_logs_list(self):
		return self.procd_logs_list
	
	def set_procd_logs_list(self):
		print ("setting procd logs from logs_done.txt...")
		# Need to retrieve logs done list and save it locally.
		with open(self.log_done_path, 'r') as file:
			for line in file:
				#~ print ("line: ", line)
				self.procd_logs_list.append(line)
		
		print ("read in logs_done.txt...")
		self.modelDidChange() #delegate called on change
		
	#Any internal processing for the model        


def main():
	root = Tk()
	root.geometry("908x768+100+100")
	root.maxsize(0, 768)
	root.minsize(908, 768)
	root.iconbitmap(default='logo2.ico')
	root.title('iislp - IIS Log Parser')
	#~ root.style = Style()
	#~ root.style.theme_use("clam")
	
	frame = Frame(root, bg="white")
	app = Controller(root)
	
	root.mainloop()

if __name__ == '__main__':
	main()
	