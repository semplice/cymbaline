#!/usr/bin/env python
# cymbaline setup (using distutils)
# Copyright (C) 2013 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL license, version 3.

from distutils.core import setup

setup(name='cymbaline',
	version='1.0.3',
	description='a simple GTK+3 mixer application',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='https://github.com/semplice/cymbaline',
	scripts=['cymbaline.py'],
	data_files=[("/usr/share/cymbaline", ["cymbaline.glade"]),("/usr/share/applications", ["cymbaline.desktop"])],
	requires=['gi.repository.Gtk', 'gi.repository.GObject', 'gi.repository.Gdk', 't9n', 'os', 'alsaaudio'],
)
