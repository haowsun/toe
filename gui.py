#! /usr/bin/python3

# Import the GUI library Tkinter
import tkinter
# Import the messagebox module explicitly
from tkinter import messagebox
# Import the webbroswer module for opening a link
import webbrowser
# Import multi-threading module
import threading
import time
# Import socket
import socket
import random
import functools
import collections
import os
import numpy as np
import tensorflow as tf

from games.tic_tac_toe import TicTacToeGameSpec, human_player,available_moves,apply_move,has_winner
from common.network_helpers import load_network, get_stochastic_network_move,create_network
from games.test import simpleAI


# Constants 
C_WINDOW_WIDTH = 640
C_WINDOW_HEIGHT = 480
C_WINDOW_MIN_WIDTH = 480
C_WINDOW_MIN_HEIGHT = 360
C_COLOR_BLUE_LIGHT = "#e4f1fe"
C_COLOR_BLUE_DARK = "#304e62"
C_COLOR_BLUE = "#a8d4f2"

class CanvasWidget:
	"""(Abstract) The base class for all the canvas widgets."""

	__count = 0# Count the number of widgets initialized

	def __init__(self, canvas):
		"""Initializes the widget."""
		self.canvas = canvas
		# Generate a unique id for each widget (for tags)
		self.id = str(CanvasWidget.__count)
		CanvasWidget.__count = CanvasWidget.__count + 1
		# Generate a unique tag for each widget
		self.tag_name = self.__class__.__name__ + self.id
		# Initialize instance variables
		self.__disabled__ = False
		# Set default colors
		self.normal_color = C_COLOR_BLUE
		self.hovered_color = C_COLOR_BLUE_DARK

	def set_clickable(self, clickable):
		"""Sets if the widget can be clicked."""
		if(clickable):
			self.canvas.tag_bind(self.tag_name, "<Button-1>", 
				self.__on_click__)
		else:
			self.canvas.tag_unbind(self.tag_name, "<Button-1>")

	def __on_click__(self, event):
		"""(Private) This function will be called when the user clicks on 
		the widget."""
		if(self.__disabled__):
			return False
		if self.command is not None:
			self.command()
			return True
		else:
			print("Error: " + self.__class__.__name__ + " " + 
				self.id + " does not have a command")
			raise AttributeError
		return False

	def set_hoverable(self, hoverable):
		"""Sets if the widget can be hovered."""
		if(hoverable):
			self.canvas.tag_bind(self.tag_name, "<Enter>", 
				self.__on_enter__)
			self.canvas.tag_bind(self.tag_name, "<Leave>", 
				self.__on_leave__)
		else:
			self.canvas.tag_unbind(self.tag_name, "<Enter>")
			self.canvas.tag_unbind(self.tag_name, "<Leave>")

	def __on_enter__(self, event):
		"""(Private) This function will be called when the mouse enters
		into the widget."""
		if(self.__disabled__):
			return False
		self.canvas.itemconfig(self.tag_name, fill=self.hovered_color)
		return True

	def __on_leave__(self, event):
		"""(Private) This function will be called when the mouse leaves
		the widget."""
		if(self.__disabled__):
			return False
		self.canvas.itemconfig(self.tag_name, fill=self.normal_color)
		return True

	def disable(self):
		"""Disables the widget so it won't respond to any events."""
		self.__disabled__ = True

	def enable(self):
		"""Enables the widget so it starts to respond to events."""
		self.__disabled__ = False

	def is_enabled(self):
		"""Returns True if the widget is disabled."""
		return self.__disabled__

	def config(self, **kwargs):
		"""Configures the widget's options."""
		return self.canvas.itemconfig(self.tag_name, **kwargs)

	def delete(self):
		self.canvas.delete(self.tag_name)

class CanvasClickableLabel(CanvasWidget):
	"""A clickable label that shows text and can respond to user 
	click events."""

	def __init__(self, canvas, x, y, label_text, normal_color, 
		hovered_color):
		"""Initializes the clickable label object."""

		# Initialize super class
		CanvasWidget.__init__(self, canvas)

		# Set color scheme for different states
		self.normal_color = normal_color
		self.hovered_color = hovered_color
		
		# Create the clickable label text
		canvas.create_text(x, y, font="Helvetica 14 underline", 
			text=label_text, fill=self.normal_color, tags=(self.tag_name))
		
		# Bind events
		self.set_hoverable(True)
		self.set_clickable(True)

class CanvasButton(CanvasWidget):
	"""A button that responds to mouse clicks."""

	# Define constant width and height
	WIDTH = 196*3
	HEIGHT = 32*3

	def __init__(self, canvas, x, y, button_text, normal_color, 
		hovered_color, normal_text_color, hovered_text_color):
		"""Initialize the button object."""

		# Initialize super class
		CanvasWidget.__init__(self, canvas)

		# Set color scheme for different states
		self.normal_color = normal_color
		self.hovered_color = hovered_color
		self.normal_text_color = normal_text_color
		self.hovered_text_color = hovered_text_color

		# Create the rectangle background
		canvas.create_rectangle(x - self.WIDTH/2 + self.HEIGHT/2, 
			y - self.HEIGHT/2, x + self.WIDTH/2 - self.HEIGHT/2, 
			y + self.HEIGHT/2, fill=self.normal_color, outline="", 
			tags=(self.tag_name, "rect" + self.id))

		# Create the two circles on both sides to create a rounded edge
		canvas.create_oval(x - self.WIDTH/2, y - self.HEIGHT/2, 
			x - self.WIDTH/2 + self.HEIGHT, y + self.HEIGHT/2, 
			fill=self.normal_color, outline="", 
			tags=(self.tag_name, "oval_l" + self.id))

		canvas.create_oval(x + self.WIDTH/2 - self.HEIGHT, 
			y - self.HEIGHT/2, x + self.WIDTH/2, y + self.HEIGHT/2,
			fill=self.normal_color, outline="", 
			tags=(self.tag_name, "oval_r" + self.id))

		# Create the button text
		canvas.create_text(x, y, font="Helvetica 24 bold", 
			text=button_text, fill=self.normal_text_color, 
			tags=(self.tag_name, "text" + self.id))

		# Bind events
		self.set_hoverable(True)
		self.set_clickable(True)

	def __on_enter__(self, event):
		"""(Override) Change the text to a different color when the 
		enter event is triggered."""
		if(super().__on_enter__(event)):
			self.canvas.itemconfig("text" + self.id, 
				fill=self.hovered_text_color)

	def __on_leave__(self, event):
		"""(Override) Change the text to a different color when the 
		leave event is triggered."""
		if(super().__on_leave__(event)):
			self.canvas.itemconfig("text" + self.id, 
				fill=self.normal_text_color)

class CanvasSquare(CanvasWidget):
	"""A square that responds to mouse click event. This is for the grid
	board."""

	def __init__(self, canvas, x, y, width, normal_color, hovered_color, 
		disabled_color):
		"""Initialize the square object."""

		# Initialize super class
		CanvasWidget.__init__(self, canvas)

		# Set color scheme for different states
		self.normal_color = normal_color
		self.hovered_color = hovered_color
		self.disabled_color = disabled_color

		# Create the circle background
		canvas.create_rectangle(x - width/2, y - width/2, x + width/2, 
			y + width/2, fill=self.normal_color, outline="", 
			tags=(self.tag_name, "oval" + self.id))

		# Bind events
		self.set_hoverable(True)
		self.set_clickable(True)

	def disable(self):
		"""(Override) Change the color when the square is disabled."""
		super().disable()
		self.canvas.itemconfig(self.tag_name, fill=self.disabled_color)

	def enable(self):
		"""(Override) Change the color back to normal when the square 
		is disabled."""
		super().enable()
		self.canvas.itemconfig(self.tag_name, fill=self.normal_color)

	def set_temp_color(self, color):
		self.canvas.itemconfig(self.tag_name, fill=color)

class BaseScene(tkinter.Canvas):
	"""(Abstract) The base class for all scenes. BaseScene deals with
	general widgets and handles window resizing event."""

	def __init__(self, parent):
		"""Initializes the scene."""

		# Initialize the superclass Canvas
		tkinter.Canvas.__init__(self, parent, bg=C_COLOR_BLUE_LIGHT, 
			width=C_WINDOW_WIDTH, height=C_WINDOW_HEIGHT)

		# Bind the window-resizing event
		self.bind("<Configure>", self.__on_resize__)

		# Set self.width and self.height for later use
		self.width = C_WINDOW_WIDTH
		self.height = C_WINDOW_HEIGHT

	def __on_resize__(self, event):
		"""(Private) This function is called when the window is being
		resied."""

		# Determine the ratio of old width/height to new width/height
		self.wscale = float(event.width)/self.width
		self.hscale = float(event.height)/self.height
		self.width = event.width
		self.height = event.height

		# Resize the canvas 
		self.config(width=self.width, height=self.height)

		# Rescale all the objects tagged with the "all" tag
		self.scale("all", 0, 0, self.wscale, self.hscale)

	def create_button(self, x, y, button_text, 
		normal_color=C_COLOR_BLUE, hovered_color=C_COLOR_BLUE_DARK, 
		normal_text_color=C_COLOR_BLUE_DARK, 
		hovered_text_color=C_COLOR_BLUE_LIGHT):
		"""Creates a button widget and returns it. Note this will
		return a CanvasButton object, not the ID as other standard 
		Tkinter canvas widgets usually returns."""

		return CanvasButton(self, x, y, button_text, 
			normal_color, hovered_color, 
			normal_text_color, hovered_text_color)

	def create_square(self, x, y, width,
		normal_color=C_COLOR_BLUE, hovered_color=None, 
		disabled_color=C_COLOR_BLUE_LIGHT):
		"""Creates a square widget and returns it. Note this will
		return a CanvasSquare object, not the ID as other standard 
		Tkinter canvas widgets usually returns."""

		return CanvasSquare(self, x, y, width,
			normal_color, hovered_color, disabled_color)

	def create_clickable_label(self, x, y, button_text, 
		normal_color=C_COLOR_BLUE_DARK, hovered_color=C_COLOR_BLUE_LIGHT):
		"""Creates a clickable label widget and returns it. Note this
		will return a CanvasClickableLabel object, not the ID as other 
		standard Tkinter canvas widgets usually returns."""

		return CanvasClickableLabel(self, x, y, button_text, 
			normal_color, hovered_color)

class WelcomeScene(BaseScene):
	"""WelcomeScene is the first scene to show when the GUI starts."""

	def __init__(self, parent):
		"""Initializes the welcome scene."""

		# Initialize BaseScene
		super().__init__(parent)

		# Create a blue arch at the top of the canvas
		self.create_arc((-64, -368, C_WINDOW_WIDTH + 64, 192), 
			start=0, extent=-180, fill=C_COLOR_BLUE, outline="")

		try:
			# From the logo image file create a PhotoImage object 
			self.logo_image = tkinter.PhotoImage(file="res/icon.png")
			# Create the logo image at the center of the canvas
			logo = self.create_image((C_WINDOW_WIDTH/2, 
				C_WINDOW_HEIGHT/2 - 96 - 96 - 96), image=self.logo_image)
			# From the title image file create a PhotoImage object 
			self.title_image = tkinter.PhotoImage(file="res/title.png")
			# Create the logo image at the center of the canvas
			title = self.create_image((C_WINDOW_WIDTH/2, 
				C_WINDOW_HEIGHT/2  -96), image=self.title_image)
		except:	
			# An error has been caught when creating the logo image
			tkinter.messagebox.showerror("Error", "Can't create images.\n" +
				"Please make sure the res folder is in the same directory" + 
				" as this script.")

		# Create the hard button
		hard_btn = self.create_button(C_WINDOW_WIDTH/2, 
			C_WINDOW_HEIGHT/2 + 100, "Hard")
		hard_btn.command = self.__on_hard_clicked__
		# Create the easy button
		easy_btn = self.create_button(C_WINDOW_WIDTH/2, 
			C_WINDOW_HEIGHT/2 + 192+96, "Easy")
		easy_btn.command = self.__on_easy_clicked__

		# Tag all of the drawn widgets for later reference
		self.addtag_all("all")

	def __on_hard_clicked__(self):
		"""(Private) Switches to the main game scene when the hard
		button is clicked."""
		self.pack_forget()
		self.main_game_scene_ai.pack()



	def __on_easy_clicked__(self):
		"""(Private) Switches to the about scene when the about	button 
		is clicked."""
		
		self.pack_forget()

		self.main_game_scene_random.pack()
		
class MainGameSceneAI(BaseScene):
	"""MainGameScene deals with the game logic."""

	def __init__(self, parent):
		"""Initializes the main game scene object."""

		# Initialize the base scene
		super().__init__(parent)

		#create tag for squares
		self.square_num = -1
		# Initialize instance variables
		self.board_grids_power = 3 # Make it a 3x3 grid board
		self.board_width = 512+256 # The board is 256x256 wide

		# Create a blue arch at the bottom of the canvas
		self.create_arc((-128, C_WINDOW_HEIGHT - 128, C_WINDOW_WIDTH + 128, 
			C_WINDOW_HEIGHT + 368), start=0, extent=180, fill=C_COLOR_BLUE, 
			outline="")

		# Create the return button
		return_btn = self.create_button(C_WINDOW_WIDTH - 320, 64, "Go back") 
		return_btn.command = self.__on_return_clicked__

		self.squares = [None] * self.board_grids_power ** 2
		
		self.draw_board()
		

		self.squares[0].command = self.__on_squares_0_clicked__
		self.squares[1].command = self.__on_squares_1_clicked__
		self.squares[2].command = self.__on_squares_2_clicked__
		self.squares[3].command = self.__on_squares_3_clicked__
		self.squares[4].command = self.__on_squares_4_clicked__
		self.squares[5].command = self.__on_squares_5_clicked__
		self.squares[6].command = self.__on_squares_6_clicked__
		self.squares[7].command = self.__on_squares_7_clicked__
		self.squares[8].command = self.__on_squares_8_clicked__
		self.player_turn = 1
		self.board_string = "000000000"
		self.board_state = ((0, 0, 0),
							(0, 0, 0),
							(0, 0, 0))
		self.isHumanFirst = False
		if bool(random.getrandbits(1)):
			self.isHumanFirst = True

		self.AI()
		# Set restart button to None so it won't raise AttributeError
		self.restart_btn = None

		# Tag all of the drawn widgets for later reference
		self.addtag_all("all")
	
	def AI(self):
		
		NETWORK_FILE_PATH ='current_network.p' #保存数据的位置

		game_spec = TicTacToeGameSpec()
		create_network_func = functools.partial(create_network, game_spec.board_squares(), (100, 100, 100))

		input_layer, output_layer, variables = create_network_func()

		with tf.Session() as session:
			session.run(tf.global_variables_initializer())
			if NETWORK_FILE_PATH and os.path.isfile(NETWORK_FILE_PATH):
				print("loading pre-existing network")
				load_network(session, variables, NETWORK_FILE_PATH)

			mini_batch_board_states, mini_batch_moves = [], []

			def make_training_move(board_state, side):
				mini_batch_board_states.append(np.ravel(board_state) * side)
				move = get_stochastic_network_move(session, input_layer, output_layer, board_state, side)
				mini_batch_moves.append(move)
				return game_spec.flat_move_to_tuple(move.argmax())
		
			_available_moves = list(available_moves(self.board_state))


			if(not self.isHumanFirst):
				move = make_training_move(self.board_state, self.player_turn)
				#print(move)
				_available_moves = list(available_moves(self.board_state))
				if(move not in _available_moves):
					if((2,1) in _available_moves):
						move = (2,1)
					else:
						move = random.choice(_available_moves)
				self.board_state = apply_move(self.board_state, move, self.player_turn)
				self.board_string =self.State_to_Str(self.board_state)
				self.update_board_content(self.board_string)
				self.player_turn = -self.player_turn
			self.isHumanFirst = False	
	

			
	def State_to_Str(self,board_state):
		result = ""
		for i in range(3):
			for j in range(3):
				result+=str(2 if board_state[i][j]==-1 else  board_state[i][j])
		return result
	def Str_to_State(self,board_string):
		s = board_string
		result = ((-1 if int(s[0]) == 2 else int(s[0]),-1 if int(s[1]) == 2 else int(s[1]),-1 if int(s[2]) == 2 else int(s[2])),
				  (-1 if int(s[3]) == 2 else int(s[3]),-1 if int(s[4]) == 2 else int(s[4]),-1 if int(s[5]) == 2 else int(s[5])),
				  (-1 if int(s[6]) == 2 else int(s[6]),-1 if int(s[7]) == 2 else int(s[7]),-1 if int(s[8]) == 2 else int(s[8])))
		return result

	def pack(self):
		"""(Override) When the scene packs, start the client thread."""
		super().pack()
		# Start a new thread to deal with the client communication


	def draw_board(self, board_line_width = 4):
		"""Draws the board at the center of the screen, parameter 
		board_line_width determines the border line width."""

		# Create squares for the grid board
		for i in range(0, self.board_grids_power):
			for j in range(0, self.board_grids_power):
				self.squares[i+j*3] = self.create_square(
					(C_WINDOW_WIDTH - self.board_width)/2 + 
					self.board_width/self.board_grids_power * i + 
					self.board_width / self.board_grids_power / 2,
					(C_WINDOW_HEIGHT - self.board_width)/2 + 
					self.board_width/self.board_grids_power * j + 
					self.board_width / self.board_grids_power / 2,
					self.board_width / self.board_grids_power)
				# Disable those squares to make them unclickable
		

		# Draw the border lines
		for i in range(1, self.board_grids_power):
			# Draw horizontal lines
			self.create_line((C_WINDOW_WIDTH - self.board_width)/2, 
				(C_WINDOW_HEIGHT - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				(C_WINDOW_WIDTH + self.board_width)/2, 
				(C_WINDOW_HEIGHT - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				fill=C_COLOR_BLUE_DARK, width=board_line_width)
			# Draw vertical lines
			self.create_line((C_WINDOW_WIDTH - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				(C_WINDOW_HEIGHT - self.board_width)/2, 
				(C_WINDOW_WIDTH - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				(C_WINDOW_HEIGHT + self.board_width)/2, 
				fill=C_COLOR_BLUE_DARK, width=board_line_width)
		

	def __on_return_clicked__(self):
		"""(Private) Switches back to the welcome scene when the return 
		button is clicked."""
		# Clear screen
		self.__clear_screen()
		
		# Set the client to None so the client thread will stop due to error
		#self.client.client_socket = None;
		#self.client = None
		# Switch to the welcome scene
		self.pack_forget()
		self.welcome_scene.pack()
	def Human(self,i):
		if(self.board_string[i]=='0'):
			if(self.player_turn == 1):
				str =self.board_string[:i]+'1'+self.board_string[i+1:]
				self.board_string = str
				#print(self.board_string)
			elif(self.player_turn == -1):
				str =self.board_string[:i]+'2'+self.board_string[i+1:]
				self.board_string = str
				#print(self.board_string)
			else:
				raise EnvironmentError
			self.board_state = self.Str_to_State(self.board_string)
			self.update_board_content(self.board_string)
			self.player_turn = -self.player_turn
			if(self.checkWinner()==0):
				self.checkDraw()		
				self.AI()
				self.checkWinner()
				self.checkDraw()	
			
	def checkWinner(self):
		winner,str1 = has_winner(self.board_state)
		if (winner != 0):
			for i in range(9):
				self.squares[i].disable()
			self.draw_winning_path(str1)
			self.show_restart()
			return 1
		return 0
	def checkDraw(self):
		if (not len(list(available_moves(self.board_state)))):
			self.show_restart()
	def __on_squares_0_clicked__(self):
		self.Human(0)

	def __on_squares_1_clicked__(self):
		self.Human(1)

	def __on_squares_2_clicked__(self):
		self.Human(2)

	def __on_squares_3_clicked__(self):
		self.Human(3)

	def __on_squares_4_clicked__(self):
		self.Human(4)

	def __on_squares_5_clicked__(self):
		self.Human(5)  

	def __on_squares_6_clicked__(self):
		self.Human(6)

	def __on_squares_7_clicked__(self):
		self.Human(7)

	def __on_squares_8_clicked__(self):
		self.Human(8)

	def update_board_content(self, board_string):
		"""Redraws the board content with new board_string."""
		if(len(board_string) != self.board_grids_power ** 2):
			# If board_string is in valid
			print("The board string should be " + 
				str(self.board_grids_power ** 2) + " characters long.")
			# Throw an error
			raise Exception

		# Delete everything on the board
		self.delete("board_content")

		p = 48 # Padding

		# Draw the board content
		for i in range(0, self.board_grids_power):
			for j in range(0, self.board_grids_power):

				if(board_string[i+j*3] == "2"):
					# If this is an "O"
					self.create_oval(
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * i + p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * j + p,
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (i + 1) - p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (j + 1) - p,
						fill="", outline=C_COLOR_BLUE_DARK, width=4,
						tags="board_content")
				elif(board_string[i+j*3] == "1"):
					# If this is an "X"
					self.create_line(
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * i + p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * j + p,
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (i + 1) - p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (j + 1) - p,
						fill=C_COLOR_BLUE_DARK, width=4,
						tags="board_content")
					self.create_line(
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (i + 1) - p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * j + p,
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * i + p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (j + 1) - p,
						fill=C_COLOR_BLUE_DARK, width=4,
						tags="board_content")

	def draw_winning_path(self, winning_path):
		"""Marks on the board the path that leads to the win result."""
		# Loop through the board
		for i in range(0, self.board_grids_power ** 2):
			if str(i) in winning_path: 
				# If the current item is in the winning path

				self.squares[i].set_temp_color("#db2631")



	def show_restart(self):
		"""Creates a restart button for the user to choose to restart a 
		new game."""
		self.restart_btn = self.create_button(C_WINDOW_WIDTH/2, C_WINDOW_HEIGHT - 32-32, 
			"Restart", C_COLOR_BLUE_DARK, C_COLOR_BLUE_LIGHT, C_COLOR_BLUE_LIGHT, 
			C_COLOR_BLUE_DARK)
		self.restart_btn.command = self.__on_restart_clicked__

	def __clear_screen(self):
		"""(Private) Clears all the existing content from the old game."""
		# Clear everything from the past game
		for i in range(0, self.board_grids_power ** 2):
			self.squares[i].set_temp_color(C_COLOR_BLUE)
			self.squares[i].enable()
		self.update_board_content(" " * self.board_grids_power ** 2)

		# Delete the button from the scene
		if self.restart_btn is not None:
			self.restart_btn.delete()
		self.restart_btn = None
		self.player_turn = 1
		self.board_string = "000000000"
		self.board_state = ((0, 0, 0),
							(0, 0, 0),
							(0, 0, 0))
		self.isHumanFirst = False
		if bool(random.getrandbits(1)):
			self.isHumanFirst = True

		self.AI()

	def __on_restart_clicked__(self):
		"""(Private) Switches back to the welcome scene when the return 
		button is clicked."""
		# Clear screen
		self.__clear_screen()

class MainGameSceneRandom(BaseScene):
	"""MainGameScene deals with the game logic."""

	def __init__(self, parent):
		"""Initializes the main game scene object."""

		# Initialize the base scene
		super().__init__(parent)

		#create tag for squares
		self.square_num = -1
		# Initialize instance variables
		self.board_grids_power = 3 # Make it a 3x3 grid board
		self.board_width = 256 + 512 # The board is 256x256 wide

		# Create a blue arch at the bottom of the canvas
		self.create_arc((-128, C_WINDOW_HEIGHT - 128, C_WINDOW_WIDTH + 128, 
			C_WINDOW_HEIGHT + 368), start=0, extent=180, fill=C_COLOR_BLUE, 
			outline="")

		# Create the return button
		return_btn = self.create_button(C_WINDOW_WIDTH - 320, 32+32, "Go back") 
		return_btn.command = self.__on_return_clicked__

		self.squares = [None] * self.board_grids_power ** 2
		
		self.draw_board()
		

		self.squares[0].command = self.__on_squares_0_clicked__
		self.squares[1].command = self.__on_squares_1_clicked__
		self.squares[2].command = self.__on_squares_2_clicked__
		self.squares[3].command = self.__on_squares_3_clicked__
		self.squares[4].command = self.__on_squares_4_clicked__
		self.squares[5].command = self.__on_squares_5_clicked__
		self.squares[6].command = self.__on_squares_6_clicked__
		self.squares[7].command = self.__on_squares_7_clicked__
		self.squares[8].command = self.__on_squares_8_clicked__
		self.player_turn = 1
		self.board_string = "000000000"
		self.board_state = ((0, 0, 0),
							(0, 0, 0),
							(0, 0, 0))
		self.isHumanFirst = False
		if bool(random.getrandbits(1)):
			self.isHumanFirst = True

		self.Random()
		# Set restart button to None so it won't raise AttributeError
		self.restart_btn = None

		# Tag all of the drawn widgets for later reference
		self.addtag_all("all")

	def Random(self):
		if(not self.isHumanFirst):
			_available_moves = list(available_moves(self.board_state))
			move = random.choice(_available_moves)
			self.board_state = apply_move(self.board_state, move, self.player_turn)
			self.board_string =self.State_to_Str(self.board_state)
			self.update_board_content(self.board_string)
			self.player_turn = -self.player_turn
		self.isHumanFirst = False	
		
		
		
	def State_to_Str(self,board_state):
		result = ""
		for i in range(3):
			for j in range(3):
				result+=str(2 if board_state[i][j]==-1 else  board_state[i][j])
		return result
	def Str_to_State(self,board_string):
		s = board_string
		result = ((-1 if int(s[0]) == 2 else int(s[0]),-1 if int(s[1]) == 2 else int(s[1]),-1 if int(s[2]) == 2 else int(s[2])),
				  (-1 if int(s[3]) == 2 else int(s[3]),-1 if int(s[4]) == 2 else int(s[4]),-1 if int(s[5]) == 2 else int(s[5])),
				  (-1 if int(s[6]) == 2 else int(s[6]),-1 if int(s[7]) == 2 else int(s[7]),-1 if int(s[8]) == 2 else int(s[8])))
		return result

	def pack(self):
		"""(Override) When the scene packs, start the client thread."""
		super().pack()
		# Start a new thread to deal with the client communication


	def draw_board(self, board_line_width = 4):
		"""Draws the board at the center of the screen, parameter 
		board_line_width determines the border line width."""
		print(C_WINDOW_WIDTH,C_WINDOW_HEIGHT)
		# Create squares for the grid board
		for i in range(0, self.board_grids_power):
			for j in range(0, self.board_grids_power):
				self.squares[i+j*3] = self.create_square(
					(C_WINDOW_WIDTH - self.board_width)/2 + 
					self.board_width/self.board_grids_power * i + 
					self.board_width / self.board_grids_power / 2,
					(C_WINDOW_HEIGHT - self.board_width)/2 + 
					self.board_width/self.board_grids_power * j + 
					self.board_width / self.board_grids_power / 2,
					self.board_width / self.board_grids_power)
		
		

		# Draw the border lines
		for i in range(1, self.board_grids_power):
			# Draw horizontal lines
			self.create_line((C_WINDOW_WIDTH - self.board_width)/2, 
				(C_WINDOW_HEIGHT - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				(C_WINDOW_WIDTH + self.board_width)/2, 
				(C_WINDOW_HEIGHT - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				fill=C_COLOR_BLUE_DARK, width=board_line_width)
			# Draw vertical lines
			self.create_line((C_WINDOW_WIDTH - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				(C_WINDOW_HEIGHT - self.board_width)/2, 
				(C_WINDOW_WIDTH - self.board_width)/2 + 
				self.board_width/self.board_grids_power * i, 
				(C_WINDOW_HEIGHT + self.board_width)/2, 
				fill=C_COLOR_BLUE_DARK, width=board_line_width)

	def update_board_content(self, board_string):
		"""Redraws the board content with new board_string."""
		if(len(board_string) != self.board_grids_power ** 2):
			# If board_string is in valid
			print("The board string should be " + 
				str(self.board_grids_power ** 2) + " characters long.")
			# Throw an error
			raise Exception

		# Delete everything on the board
		self.delete("board_content")

		p = 48 # Padding

		# Draw the board content
		for i in range(0, self.board_grids_power):
			for j in range(0, self.board_grids_power):

				if(board_string[i+j*3] == "2"):
					# If this is an "O"
					self.create_oval(
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * i + p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * j + p,
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (i + 1) - p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (j + 1) - p,
						fill="", outline=C_COLOR_BLUE_DARK, width=4,
						tags="board_content")
				elif(board_string[i+j*3] == "1"):
					# If this is an "X"
					self.create_line(
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * i + p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * j + p,
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (i + 1) - p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (j + 1) - p,
						fill=C_COLOR_BLUE_DARK, width=4,
						tags="board_content")
					self.create_line(
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (i + 1) - p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * j + p,
						(C_WINDOW_WIDTH - self.board_width)/2 + 
						self.board_width/self.board_grids_power * i + p,
						(C_WINDOW_HEIGHT - self.board_width)/2 + 
						self.board_width/self.board_grids_power * (j + 1) - p,
						fill=C_COLOR_BLUE_DARK, width=4,
						tags="board_content")
		

	def __on_return_clicked__(self):
		"""(Private) Switches back to the welcome scene when the return 
		button is clicked."""
		# Clear screen
		self.__clear_screen()
		
		# Set the client to None so the client thread will stop due to error
		#self.client.client_socket = None;
		#self.client = None
		# Switch to the welcome scene
		self.pack_forget()
		self.welcome_scene.pack()
	def Human(self,i):
		if(self.board_string[i]=='0'):
			if(self.player_turn == 1):
				str =self.board_string[:i]+'1'+self.board_string[i+1:]
				self.board_string = str

			elif(self.player_turn == -1):
				str =self.board_string[:i]+'2'+self.board_string[i+1:]
				self.board_string = str

			else:
				raise EnvironmentError
			self.board_state = self.Str_to_State(self.board_string)
			self.update_board_content(self.board_string)
			self.player_turn = -self.player_turn
			if(self.checkWinner()==0):
				self.checkDraw()		
				self.Random()
				self.checkWinner()
				self.checkDraw()	
			
	def checkWinner(self):
		winner,str1 = has_winner(self.board_state)
		if (winner != 0):
			for i in range(9):
				self.squares[i].disable()
			self.draw_winning_path(str1)
			self.show_restart()

			return 1
		return 0
	def checkDraw(self):
		if (not len(list(available_moves(self.board_state)))):
			self.show_restart()
	def __on_squares_0_clicked__(self):
		self.Human(0)

	def __on_squares_1_clicked__(self):
		self.Human(1)

	def __on_squares_2_clicked__(self):
		self.Human(2)

	def __on_squares_3_clicked__(self):
		self.Human(3)

	def __on_squares_4_clicked__(self):
		self.Human(4)

	def __on_squares_5_clicked__(self):
		self.Human(5)  

	def __on_squares_6_clicked__(self):
		self.Human(6)

	def __on_squares_7_clicked__(self):
		self.Human(7)

	def __on_squares_8_clicked__(self):
		self.Human(8)

	

	def draw_winning_path(self, winning_path):
		"""Marks on the board the path that leads to the win result."""
		# Loop through the board
		for i in range(0, self.board_grids_power ** 2):
			if str(i) in winning_path: 
				# If the current item is in the winning path
				self.squares[i].set_temp_color("#db2631")


	def show_restart(self):
		"""Creates a restart button for the user to choose to restart a 
		new game."""
		self.restart_btn = self.create_button(C_WINDOW_WIDTH/2, C_WINDOW_HEIGHT - 64, 
			"Restart", C_COLOR_BLUE_DARK, C_COLOR_BLUE_LIGHT, C_COLOR_BLUE_LIGHT, 
			C_COLOR_BLUE_DARK)
		self.restart_btn.command = self.__on_restart_clicked__

	def __clear_screen(self):
		"""(Private) Clears all the existing content from the old game."""
		# Clear everything from the past game
		for i in range(0, self.board_grids_power ** 2):
			self.squares[i].enable()
			self.squares[i].set_temp_color(C_COLOR_BLUE)
		self.update_board_content(" " * self.board_grids_power ** 2)
		self.itemconfig("player_self_text", text="")
		self.itemconfig("player_match_text", text="")
		# Delete the button from the scene
		if self.restart_btn is not None:
			self.restart_btn.delete()
			self.restart_btn = None
		self.player_turn = 1
		self.board_string = "000000000"
		self.board_state = ((0, 0, 0),
							(0, 0, 0),
							(0, 0, 0))
		self.isHumanFirst = False
		if bool(random.getrandbits(1)):
			self.isHumanFirst = True

		self.Random()

	def __on_restart_clicked__(self):
		"""(Private) Switches back to the welcome scene when the return 
		button is clicked."""
		# Clear screen
		self.__clear_screen()


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.root = master
        # self.tk.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        self.frame = tkinter.Frame(self.root)
        self.frame.pack()
        self.state = True
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.root.attributes("-fullscreen", False)
        return "break"


# Define the main program
def main():
	# Create a Tkinter object
	root = tkinter.Tk()
	# Set window title
	root.title("Tic Tac Toe")
	# Set window minimun size
	root.minsize(C_WINDOW_MIN_WIDTH, C_WINDOW_MIN_HEIGHT)
	# Set window size
	#root.geometry(str(C_WINDOW_WIDTH) + "x" + str(C_WINDOW_HEIGHT))
	FullScreenApp(root)
	global C_WINDOW_WIDTH 
	C_WINDOW_WIDTH = root.winfo_screenwidth()
	global C_WINDOW_HEIGHT 
	C_WINDOW_HEIGHT = root.winfo_screenheight()

	#root.geometry("%dx%d" %(C_WINDOW_WIDTH, C_WINDOW_HEIGHT))	
	root.attributes("-fullscreen", True)
	try:
		# Set window icon
		root.iconbitmap("res/icon.ico")
	except:	
		# An error has been caught when setting the icon
		# tkinter.messagebox.showerror("Error", "Can't set the window icon.");
		print("Can't set the window icon.")

	# Initialize the welcome scene
	welcome_scene = WelcomeScene(root)
	# Initialize the about scene
	main_game_scene_random = MainGameSceneRandom(root)
	# Initialize the main game scene
	main_game_scene_ai = MainGameSceneAI(root)

	# Give a reference for switching between scenes
	welcome_scene.main_game_scene_random = main_game_scene_random
	welcome_scene.main_game_scene_ai = main_game_scene_ai 
	main_game_scene_random.welcome_scene = welcome_scene
	main_game_scene_ai.welcome_scene = welcome_scene

	# Start showing the welcome scene
	welcome_scene.pack()
	    
	# Main loop
	root.mainloop()

if __name__ == "__main__":
	# If this script is running as a standalone program,
	# start the main program.
	main();