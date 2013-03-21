#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# cymbaline - a simple GTK+3 mixer application
# Copyright (C) 2013  Eugenio "g7" Paolantonio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This is the main executable.
#

from gi.repository import Gtk, GObject

import alsaaudio

import t9n.library

import os

_ = t9n.library.translation_init("cymbaline")

GLADEFILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cymbaline.glade")
if not os.path.exists(GLADEFILE):
	# fallback to the package one
	GLADEFILE = "/usr/share/cymbaline/cymbaline.glade"

cards = alsaaudio.cards()

class GUI:
	def quit(self, caller=None):
		Gtk.main_quit()
	
	def setvalue(self, scale, mixer, channel, mixerdict):
		""" Called when a slider is changed. """
				
		scale.set_fill_level(scale.get_value())
		mixer.setvolume(int(scale.get_value()), channel)
		
		# Check if we are locked...
		if ("isLocked" in mixerdict and mixerdict["isLocked"]) and not self.processinglock:
			self.processinglock = True
			# yes, adjust other controls...
			for control in mixerdict["controls"]:
				control.set_value(scale.get_value())
			self.processinglock = False
	
	def mute(self, caller, mixer, img, donotset=False):
		""" Called when we should mute/unmute something. """
		
		if not donotset: mixer.setmute(caller.get_active())
		if caller.get_active():
			# Set icon to volume-muted
			img.set_from_icon_name(
				"audio-volume-muted",
				Gtk.IconSize.MENU)
			caller.set_tooltip_text(_("Click to unmute."))
		else:
			# Set icon to volume-high
			img.set_from_icon_name(
				"audio-volume-high",
				Gtk.IconSize.MENU)
			caller.set_tooltip_text(_("Click to mute."))
	
	def rec(self, caller, mixer, img, donotset=False):
		""" Called when we should stop/start recording. """
		
		if not donotset: mixer.setrec(caller.get_active())
		if caller.get_active():
			# Set icon to record
			img.set_from_icon_name(
				"media-record",
				Gtk.IconSize.MENU)
			caller.set_tooltip_text(_("Click to disable capturing."))
		else:
			# Set icon to playback-stop
			img.set_from_icon_name(
				"media-playback-stop",
				Gtk.IconSize.MENU)
			caller.set_tooltip_text(_("Click to enable capturing."))
	
	def lock(self, caller, mixerdict, img):
		""" Called when we should lock/unlock something. """
				
		if caller.get_active():
			mixerdict["isLocked"] = True
			# Set icon to locked
			img.set_from_icon_name(
				"locked",
				Gtk.IconSize.MENU)
			# Reset all channels with the value of the first...
			self.setvalue(mixerdict["control0"],
				mixerdict["mixer"],
				0,
				mixerdict)
			caller.set_tooltip_text(_("Click to unlock."))
		else:
			mixerdict["isLocked"] = False
			# Set icon to unlocked
			img.set_from_icon_name(
			#	"unlocked",
				"lock", # This is for the Faenza icon set.
				Gtk.IconSize.MENU)
			caller.set_tooltip_text(_("Click to lock."))
	
	def build_cards(self):
		""" Builds cards pages. """
		
		for card in cards:
			self.objects[card] = {}
			
			# Scrolledwindow
			self.objects[card]["scroll"] = Gtk.ScrolledWindow()
			
			# Frame
			self.objects[card]["frame"] = Gtk.Frame()
			self.objects[card]["frame_label"] = Gtk.Label()
			self.objects[card]["label"] = Gtk.Label(card)
			self.objects[card]["frame_label"].set_markup("<b>%s</b>" % card)
			self.objects[card]["frame"].set_label_widget(self.objects[card]["frame_label"])
			
			# Mixers
			self.objects[card]["mixers"] = {}
			self.objects[card]["mixers"]["container"] = Gtk.HBox()
			self.objects[card]["mixers"]["container"].grab_focus()
			self.objects[card]["mixers"]["container"].pack_start(Gtk.Alignment(),
				True,
				True,
				0)
			self.objects[card]["mixers"]["container"].set_spacing(30)
			for mixer in alsaaudio.mixers(cards.index(card)):
				mixero = alsaaudio.Mixer(control=mixer, cardindex=cards.index(card))
				self.objects[card]["mixers"][mixer] = {}
				self.objects[card]["mixers"][mixer]["mixer"] = mixero
				
				# Create the main vbox and add it to the container
				self.objects[card]["mixers"][mixer]["vbox"] = Gtk.VBox()
				self.objects[card]["mixers"][mixer]["vbox"].grab_focus()
				self.objects[card]["mixers"][mixer]["vbox"].set_spacing(5)
				self.objects[card]["mixers"]["container"].pack_start(
					self.objects[card]["mixers"][mixer]["vbox"],
					False,
					False,
					0)
				self.objects[card]["mixers"]["container"].pack_start(
					Gtk.VSeparator(),
					True,
					True,
					0)
				# Create the main label and add it to the vbox
				self.objects[card]["mixers"][mixer]["vbox"].pack_start(Gtk.Label(mixer), False, False, 5)
				# Create the control hbox, add controls and add them to the vbox
				self.objects[card]["mixers"][mixer]["controlhbox"] = Gtk.HBox()
				self.objects[card]["mixers"][mixer]["controlhbox"].set_spacing(20)
				self.objects[card]["mixers"][mixer]["controlhbox"].set_halign(Gtk.Align.CENTER)
				# controls list
				self.objects[card]["mixers"][mixer]["controls"] = []
				chancount = -1
				chanlist = mixero.getvolume()
				for chanvol in chanlist:
					chancount += 1
					self.objects[card]["mixers"][mixer]["control%s" % chancount] = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
					# add to controls
					self.objects[card]["mixers"][mixer]["controls"].append(
						self.objects[card]["mixers"][mixer]["control%s" % chancount])
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_range(0, 100)
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_digits(0)
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_value_pos(Gtk.PositionType.BOTTOM)
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_inverted(True)
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_show_fill_level(True)
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_fill_level(chanvol)
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_restrict_to_fill_level(False)
					#self.objects[card]["mixers"][mixer]["control%s" % chancount].set_update_policy(Gtk.UPDATE_CONTINUOUS)
					# Set volume
					self.objects[card]["mixers"][mixer]["control%s" % chancount].set_value(chanvol)
					# Connect it
					self.objects[card]["mixers"][mixer]["control%s" % chancount].connect(
						"value-changed", self.setvalue,
						mixero, chancount, self.objects[card]["mixers"][mixer])
					# Add to controlhbox
					self.objects[card]["mixers"][mixer]["controlhbox"].pack_start(
						self.objects[card]["mixers"][mixer]["control%s" % chancount],
						False,
						True,
						0)
				self.objects[card]["mixers"][mixer]["vbox"].pack_start(
					self.objects[card]["mixers"][mixer]["controlhbox"],
					True,
					True,
					0)
				
				# Create a buttonbox...
				atleastone = False # If it remains false, fill the space with an alignment.
				self.objects[card]["mixers"][mixer]["bbox"] = Gtk.HBox()
				self.objects[card]["mixers"][mixer]["bbox"].set_spacing(10)
				self.objects[card]["mixers"][mixer]["bbox"].set_halign(Gtk.Align.CENTER)
				# Generate required buttons
				
				# Mute button
				try:
					mutestate = mixero.getmute() # will except if mic
					self.objects[card]["mixers"][mixer]["mute"] = Gtk.ToggleButton()
					self.objects[card]["mixers"][mixer]["muteimg"] = Gtk.Image()
					self.objects[card]["mixers"][mixer]["muteimg"].set_size_request(20,20)
					self.objects[card]["mixers"][mixer]["mute"].add(
						self.objects[card]["mixers"][mixer]["muteimg"])
						
					# check mutestate
					for channel in mutestate:
						if channel == 1:
							# Check only mute (yes)
							self.objects[card]["mixers"][mixer]["mute"].set_active(True)

					# Connect to self.mute
					self.objects[card]["mixers"][mixer]["mute"].connect(
						"toggled", self.mute,
						mixero,
						self.objects[card]["mixers"][mixer]["muteimg"])
					
					# Fire up self.mute
					self.mute(self.objects[card]["mixers"][mixer]["mute"],
						mixero,
						self.objects[card]["mixers"][mixer]["muteimg"],
						donotset=True)
					
					self.objects[card]["mixers"][mixer]["bbox"].pack_start(
						self.objects[card]["mixers"][mixer]["mute"],
						False,
						False,
						0)
					atleastone = True
				except alsaaudio.ALSAAudioError:
					# Rec button?
					try:
						recstate = mixero.getrec()
						self.objects[card]["mixers"][mixer]["rec"] = Gtk.ToggleButton()
						self.objects[card]["mixers"][mixer]["recimg"] = Gtk.Image()
						self.objects[card]["mixers"][mixer]["recimg"].set_size_request(20,20)
						self.objects[card]["mixers"][mixer]["rec"].add(
							self.objects[card]["mixers"][mixer]["recimg"])

						# Check recstate
						for channel in recstate:
							if channel == 1:
								# Check only rec (yes)
								self.objects[card]["mixers"][mixer]["rec"].set_active(True)

						# Connect to self.rec
						self.objects[card]["mixers"][mixer]["rec"].connect(
							"toggled", self.rec,
							mixero,
							self.objects[card]["mixers"][mixer]["recimg"])

						# Fire up self.rec
						self.rec(self.objects[card]["mixers"][mixer]["rec"],
							mixero,
							self.objects[card]["mixers"][mixer]["recimg"],
							donotset=True)

						self.objects[card]["mixers"][mixer]["bbox"].pack_start(
							self.objects[card]["mixers"][mixer]["rec"],
							False,
							False,
							0)
						atleastone = True
					except alsaaudio.ALSAAudioError:
						pass

				# Lock button
				if (len(chanlist) > 1):
					self.objects[card]["mixers"][mixer]["lock"] = Gtk.ToggleButton()
					self.objects[card]["mixers"][mixer]["lockimg"] = Gtk.Image()
					self.objects[card]["mixers"][mixer]["lock"].set_size_request(0,10)
					self.objects[card]["mixers"][mixer]["lockimg"].set_size_request(20,20)
					self.objects[card]["mixers"][mixer]["lock"].add(
						self.objects[card]["mixers"][mixer]["lockimg"])
					# connect to self.lock
					self.objects[card]["mixers"][mixer]["lock"].connect(
						"toggled", self.lock,
						self.objects[card]["mixers"][mixer],
						self.objects[card]["mixers"][mixer]["lockimg"])
					# Check if the channels are at the same level, if
					# yes lock, otherwise leave them unlocked.
					if chanlist.count(chanlist[0]) == len(chanlist):
						# lock
						self.objects[card]["mixers"][mixer]["lock"].set_active(True)
					else:
						# unlock
						self.objects[card]["mixers"][mixer]["lock"].set_active(False)
						# FIXME: fire up self.lock as it seems to be not
						# triggered by set_active()...
						self.lock(self.objects[card]["mixers"][mixer]["lock"],
							self.objects[card]["mixers"][mixer],
							self.objects[card]["mixers"][mixer]["lockimg"])
					self.objects[card]["mixers"][mixer]["bbox"].pack_start(
						self.objects[card]["mixers"][mixer]["lock"],
						False,
						False,
						0)
					atleastone = True
				if not atleastone:
					# fill the space.
					align = Gtk.Alignment(yscale=0.0)
					align.set_size_request(26.5,26.5)
					self.objects[card]["mixers"][mixer]["bbox"].pack_start(
						align,
						True,
						True,
						0)
					
				self.objects[card]["mixers"][mixer]["vbox"].pack_start(
					self.objects[card]["mixers"][mixer]["bbox"],
					False,
					False,
					20)

			self.objects[card]["scroll"].add_with_viewport(self.objects[card]["mixers"]["container"])
			self.notebook.append_page(self.objects[card]["scroll"], tab_label=self.objects[card]["label"])	
	
	def __init__(self):
		""" Initialize the GUI. """
		
		# avoid overhead by changing only one time locked items
		self.processinglock = False
		
		self.objects = {}
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(GLADEFILE)
		
		self.main = self.builder.get_object("main")
		self.main.connect("destroy", self.quit)
		
		self.close = self.builder.get_object("close")
		self.close.connect("clicked", self.quit)
		
		self.notebook = self.builder.get_object("card_notebook")
		# Do not show tabs if only one card...
		if len(cards) == 1:
			self.notebook.set_show_tabs(False)
			self.notebook.set_show_border(False)
		
		self.build_cards()
				
		self.main.show_all()

if __name__ == "__main__":
	g = GUI()
	Gtk.main()
