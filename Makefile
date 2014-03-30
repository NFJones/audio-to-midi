all: gui
	python __init__.py

FORCE:

clean:
	sh scripts/recursiverm.sh
	
pydoc:
	sh scripts/recursivepydoc.sh

gui: FORCE
	pyuic4 -x gui/fftMIDI.ui -o gui/fftMIDI_gui.py