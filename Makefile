all: gui
	python __init__.py

FORCE:

clean:
	sh scripts/recursiverm.sh
	
pydoc:
	sh scripts/recursivepydoc.sh

gui: FORCE
	pyuic4 -x gui/WAVtoMIDI.ui -o gui/WAVtoMIDI_gui.py