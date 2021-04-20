import pygame
from tkinter import *
from tkinter import filedialog
import re
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk

past_data = dict()
recent_songs = []
most_play_songs = {}


class create_playlist:
	def __init__(self,master,playlist_name):
		self.song_location = []
		self.app = Toplevel(master)
		self.app.geometry("600x600")
		self.app.title(playlist_name)
		pygame.mixer.init()

		self.bg = PhotoImage(file="images/music.png")
		self.bg_label = Label(self.app, image=self.bg)
		self.bg_label.place(x=0,y=90, relwidth=1, relheight=1)

		#Create Playlist
		self.song_box = Listbox(self.app,bg="black", fg="white",height=17 ,width=80, selectbackground="gray", selectforeground="blue")
		self.song_box.pack(pady=20)
		
		#create status bar
		self.status_bar = Label(self.app, text = 'Time Elapsed: 00:00 of 00:00',bd = 1, relief=GROOVE)
		self.status_bar.pack(ipady = 2)

		#create slider
		self.time_slider = ttk.Scale(self.app, from_=0, to=100, orient=HORIZONTAL, value=0, command=self.slide_music, length=360)
		self.time_slider.pack(pady=20)

		#create player frame
		self.controls_frame = Frame(self.app)
		self.controls_frame.pack(pady=10)
		
		#define images
		back_btn_image   = PhotoImage(file='images/new_1.resized.png')
		play_btn_image    = PhotoImage(file='images/new_2.resized.png')
		pause_btn_image   = PhotoImage(file='images/new_3.resized.png')
		fwd_btn_image  = PhotoImage(file='images/new_4.resized.png')

		#create buttons
		self.back_btn = Button(self.controls_frame,image=back_btn_image , borderwidth=0, command = self.play_prev_song)
		self.play_btn = Button(self.controls_frame,image=play_btn_image , borderwidth=0, command = self.play_song)
		self.pause_btn = Button(self.controls_frame,image=pause_btn_image , borderwidth=0, command = self.pause_song)
		self.fwd_btn = Button(self.controls_frame,image=fwd_btn_image , borderwidth=0, command = self.play_next_song)

		#arrange buttons
		self.back_btn.grid(row=0, column=0 , padx=10)
		self.play_btn.grid(row=0, column=1 , padx=10)
		self.pause_btn.grid(row=0, column=2 , padx=10)
		self.fwd_btn.grid(row=0, column=3 , padx=10)

		#temporary slider label
		# self.slider_label = Label(self.app, text="0")
		# self.slider_label.pack(pady=10)

		#create Menu
		main_menu = Menu(self.app)
		self.app.config(menu = main_menu)

		# #create playlist menu
		# create_playlist_menu = Menu(main_menu)
		# main_menu.add_cascade(label = "create new playlist", menu = create_playlist_menu)
		# create_playlist_menu.add_command(label = "create a playlist",command = self.create_playlist)
		# create_playlist_menu.add_command(label = "open playlist",command = self.open_playlist)
		#Add Songs Menu
		add_song_menu = Menu(main_menu)
		if (playlist_name not in ["Recently Played Songs", "Most Played Songs"]) :
			main_menu.add_cascade(label = "Add Songs", menu = add_song_menu)
			# add_song_menu.add_command(label = "Add a Song", command = self.add_song)

			#Add many songs
			add_song_menu.add_command(label = "Add Songs", command = self.add_many_songs)
		#Detlete Songs Menu
			remove_song_menu = Menu(main_menu)
			main_menu.add_cascade(label = "Remove Songs", menu = remove_song_menu)
			remove_song_menu.add_command(label = "Delete song", command = self.delete_one_song)
			remove_song_menu.add_command(label = "Delete all songs", command = self.delete_all_songs)

		#Pass Variable
		self.paused = False
		self.song_len = 100
		self.stopped = False
		self.playlist = []
		self.playlist_name = playlist_name
		self.loop_counter = 0

		if(len(past_data[playlist_name])):
			self.add_many_songs(2)

		self.app.mainloop()
	
	def play_time(self):
		if self.stopped: return
		current_time = pygame.mixer.music.get_pos() /1000
		conv_current_time = time.strftime('%M:%S',time.gmtime(current_time))

		cur_song = self.song_box.curselection()
		song = self.song_box.get(cur_song)
		song = self.get_full_path(song)
		
		#Song length by Mutagen
		song = MP3(song)
		#cuz need to be accessed in slide_music function
		self.song_len = song.info.length
		conv_song_len = time.strftime('%M:%S',time.gmtime(self.song_len))
		# print(song_len)
		if int(self.time_slider.get()) == int(self.song_len)+1:
			self.play_next_song()
		elif self.paused:
			pass
		elif int(self.time_slider.get()) == current_time-1:
			#slider hasn't moved
			slider_pos = int(self.song_len)
			self.time_slider.config(to=slider_pos, value = int(current_time)+1)
		else:
			#slider has moved
			slider_pos = int(self.song_len)
			self.time_slider.config(to=slider_pos, value = int(self.time_slider.get()))
			conv_current_time = time.strftime('%M:%S',time.gmtime(int(self.time_slider.get())))
			self.status_bar.config(text = f'Time Elapsed: {conv_current_time}  of  {conv_song_len} ')
			self.time_slider.config(value = int(self.time_slider.get())+1)
		# self.status_bar.config(text = f'Time Elapsed: {conv_current_time}  of  {conv_song_len} ')
		
		#update slider pos
		# self.time_slider.config(value = int(current_time))

		self.status_bar.after(1000, self.play_time)
	
	def slide_music(self,x):
		# txt = str(int(self.time_slider.get()))+" of "+str(int(self.song_len))
		# self.slider_label.config(text=txt)
		#play cur selection
		song = self.song_box.curselection()
		song = self.song_box.get(song)
		song = self.get_full_path(song)
		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0, start=int(self.time_slider.get()))



	def get_song(self,song):
		song = song.split('/')[-1][:-4]
		return song

	# def add_song(self):
	# 	song = filedialog.askopenfilename(initialdir='songs/', title="Choose Song", filetypes=(("mp3 files","*.mp3"),))
	# 	past_data[self.playlist_name].append(song)
	# 	song = self.get_song(song)
	# 	self.song_box.insert(END,song)
	# 	self.song_box.activate(0)
	# 	self.song_box.select_set(0, last=None) #last = None cuz to highlight only one box not range
	
	def add_many_songs(self,arg=1):
		if arg == 1:
			songs = filedialog.askopenfilenames(initialdir='songs/', title="Choose Song", filetypes=(("mp3 files","*.mp3"),))
		else:
			songs = past_data[self.playlist_name]
			past_data[self.playlist_name] = []
		for i in songs:
			past_data[self.playlist_name].append(i)
			if i in self.song_location:
				return
			self.song_location.append(i)
			song = self.get_song(i)
			self.song_box.insert(END,song)
		self.song_box.activate(0)
		self.song_box.select_set(0, last=None) #last = None cuz to highlight only one box not range

	def add_to_recent(self,song):
		global recent_songs
		if song in recent_songs:
			recent_songs.remove(song)
		recent_songs.insert(0,song)
		if song in past_data["Recently Played Songs"]:
			past_data["Recently Played Songs"].remove(song)
		past_data["Recently Played Songs"].insert(0,song)
	
	def add_to_most_played(self,song):
		global most_play_songs
		try:
			most_play_songs[song] += 1
		except:
			most_play_songs[song] = 1
		sorted_dict = dict(sorted(most_play_songs.items(), key=lambda item: item[1]))
		sorted_list_names = list(sorted_dict.keys())[::-1]
		past_data["Most Played Songs"] = sorted_list_names
		# past_data["Most Played Songs"]

	def play_song(self):
		self.reset_info()
		self.stopped = False
		# self.stop_song()
		# song = self.song_box.get(ACTIVE)
		song = self.song_box.curselection()
		song = self.song_box.get(song)
		#get full path of song
		song = self.get_full_path(song)

		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0)

		self.add_to_recent(song)
		self.add_to_most_played(song)
		# print(recent_songs)
		if self.loop_counter == 0:
			self.play_time()
			self.loop_counter+=1

		#update slider pos
		# slider_pos = int(self.song_len)
		# self.time_slider.config(to=slider_pos, value = 0)
	
	def play_next_song(self):
		self.reset_info()
		cur_song = self.song_box.curselection()
		# print(cur_song)
		next_song = cur_song[0] + 1
		if len(self.song_location) == 1: return
		if next_song == len(self.song_location):
			next_song = 0
		song = self.song_box.get(next_song)
		# print(song)
		song = self.get_full_path(song)
		self.add_to_recent(song)
		self.add_to_most_played(song)

		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0)

		#move active selection
		self.song_box.select_clear(0, END)
		self.song_box.activate(next_song)
		self.song_box.select_set(next_song, last=None) #last = None cuz to highlight only one box not range

	def play_prev_song(self):
		self.reset_info()
		cur_song = self.song_box.curselection()
		# print(cur_song)
		next_song = cur_song[0] - 1
		if len(self.song_location) == 1: return
		if next_song == -1:
			next_song = len(self.song_location)-1
		song = self.song_box.get(next_song)
		# print(song)
		song = self.get_full_path(song)
		self.add_to_recent(song)
		self.add_to_most_played(song)
		
		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0)

		#move active selection
		self.song_box.select_clear(0, END)
		self.song_box.activate(next_song)
		self.song_box.select_set(next_song, last=None)	

	def stop_song(self):
		self.reset_info()
		pygame.mixer.music.stop()
		self.song_box.selection_clear(ACTIVE)

		self.stopped = True
	
	def pause_song(self):
		if self.paused == False:
			pygame.mixer.music.pause()
		else:
			pygame.mixer.music.unpause()
		self.paused = (not self.paused)

	def delete_one_song(self):
		cur_song = self.song_box.curselection()
		song = self.song_box.get(cur_song)
		song = self.get_full_path(song)
		self.stop_song()
		self.song_box.delete(cur_song[0])
		past_data[self.playlist_name].remove(song)
		self.song_location.remove(song)
		pygame.mixer.music.stop()
		self.loop_counter = 0

	def delete_all_songs(self):
		past_data[self.playlist_name] = []
		self.song_location = []
		self.stop_song()
		self.song_box.delete(0,END)
		pygame.mixer.music.stop()
		self.loop_counter = 0
	
	def reset_info(self):
		#Reset slider and status bar
		self.status_bar.config(text='Time Elapsed: 00:00 of 00:00')
		self.time_slider.config(value=0)

	def get_full_path(self,song):
		for i in self.song_location:
			if re.search(song,i):
				return i
		return song
	
	def close():
		self.app.destroy()

	# def create_playlist(self):
	# 	temp_frame = Frame(self.app,width=100,height=50)
	# 	e = Entry(temp_frame,width = 50)
	# 	e.pack()
	# 	playlist_name_button = Button(temp_frame, text="Enter Name of Playlist",command=lambda:self.get_playlist_name(e,temp_frame))
	# 	playlist_name_button.pack()
	# 	temp_frame.pack(fill = "both", expand=1)
		# file_new_frame = Frame(self.song_box, width = 400, height = 300,bg = "red")
		# file_new_frame.pack(fill = "both", expand=1)
		# self.playlist.append(file_new_frame)

	# def get_playlist_name(self,e,temp_frame):
	# 	self.song_box.insert(END, "playlist "+e.get())
	# 	self.playlist.append("playlist "+e.get())
	# 	temp_frame.pack_forget()

	# def open_playlist(self):
	# 	playlist = self.song_box.curselection()
	# 	playlist = self.song_box.get(playlist)
	# 	if playlist not in self.playlist:
	# 		return
	# 	# file_new_frame = Frame(self.song_box, width = 400, height = 300,bg = "red")
	# 	# file_new_frame.pack(fill = "both", expand=1)
	# 	# self.playlist.append(file_new_frame)

class music_player:
	def __init__(self):
		#Variables
		self.playlist_names = []

		self.app = Tk()
		self.app.geometry("600x600")
		self.app.title("Music Player")

		self.bg = PhotoImage(file="images/music.png")
		self.bg_label = Label(self.app, image=self.bg)
		self.bg_label.place(x=0,y=90, relwidth=1, relheight=1)

		# Create Canvas
		# self.backgroud_img = PhotoImage(file = "images/music.jpg")
		# canvas1 = Canvas( self.app, width = 400,height = 400)
		# canvas1.pack(fill = "both", expand = True)
		# canvas1.create_image( 0, 0, image = self.backgroud_img, anchor = "nw")
		
		self.playlist_box = Listbox(self.app,bg="black", fg="white",height=17 ,width=80, selectbackground="gray", selectforeground="blue")
		self.playlist_box.pack(pady=20)


		main_menu = Menu(self.app)
		self.app.config(menu = main_menu)

		#Manage Playlist
		create_playlist_menu = Menu(main_menu)
		main_menu.add_cascade(label = "Manage playlists", menu = create_playlist_menu)
		create_playlist_menu.add_command(label = "open selected playlist",command = self.open_playlist)
		create_playlist_menu.add_command(label = "create New playlist",command = self.create_playlist)
		create_playlist_menu.add_command(label = "Delete playlist",command = self.delete_playlist)

		self.msg_frame = Frame(self.app,width=100,height=50)
		self.msg_box = Label(self.msg_frame, text="Welcome to music player",font=("Arial", 15))
		self.msg_box.pack()
		self.msg_frame.pack()

		#create default playlists
		self.playlist_box.insert(END,"Recently Played Songs")
		past_data["Recently Played Songs"] = []
		self.playlist_box.insert(END,"Most Played Songs")
		past_data["Most Played Songs"] = []

		self.app.mainloop()
	
	def create_playlist(self):
		self.msg_frame.pack_forget()
		temp_frame = Frame(self.app,width=100,height=50)
		e = Entry(temp_frame,width = 50)
		e.pack()
		playlist_name_button = Button(temp_frame, text="Enter Name of Playlist",command=lambda:self.get_playlist_name(e.get(),temp_frame))
		playlist_name_button.pack()
		temp_frame.pack(fill = "both", expand=1)
	
	def get_playlist_name(self,playlist_name,temp_frame):
		# self.playlist_names.append(playlist_name)
		temp_frame.pack_forget()
		print(self.playlist_names)
		if playlist_name in self.playlist_names:
			self.msg_box.config(text = "Playlist already present")
			self.msg_frame.pack()	
			return
		else:
			self.playlist_box.insert(END,playlist_name)
			past_data[playlist_name] = []
			self.playlist_names.append(playlist_name)
			create_playlist(self.app,playlist_name)
		# print(self.playlist_names[e.get()])

	def open_playlist(self):
		self.msg_frame.pack_forget()
		try:
			playlist_name = self.playlist_box.curselection()
			playlist_name = self.playlist_box.get(playlist_name)
		except:
			print("please select a playlist")
			self.msg_box.config(text = "Please select a playlist")
			self.msg_frame.pack()
			return
		self.playlist = create_playlist(self.app,playlist_name)
		# self.playlist.close()

	def delete_playlist(self):
		self.msg_frame.pack_forget()
		try:
			playlist_name_ind = self.playlist_box.curselection()
			playlist_name = self.playlist_box.get(playlist_name_ind)
			if playlist_name == "Recently Played Songs" or playlist_name == "Most Played Songs":
				self.msg_box.config(text = "Cannot Delete Playlist")
				self.msg_frame.pack()
				return
		except:
			print("please select a playlist")
			self.msg_box.config(text = "Please select a playlist")
			self.msg_frame.pack()
			return
		print("playlist "+playlist_name+" deleted !!!")
		self.msg_box.config(text = "playlist "+playlist_name+" deleted !!!")
		self.msg_frame.pack()
		del past_data[playlist_name]
		# print(self.playlist_names)
		self.playlist_names.remove(playlist_name)
		self.playlist_box.delete(playlist_name_ind[0])
		pygame.mixer.music.stop()
		# self.playlist_names[playlist_name].close()
		# del self.playlist_names[playlist_name]
		


def_playlist = music_player()
# music.func()