# Resize and place every mapped top-level window of the X display to fill the screen
# (there is no window manager to honour full screen); fails while there is none
import sys
from Xlib import display
d = display.Display()
s = d.screen()
found = False
for w in s.root.query_tree().children:
    if w.get_attributes().map_state == 2:
        w.configure(x=0, y=0, width=s.width_in_pixels, height=s.height_in_pixels, border_width=0)
        found = True
d.sync()
sys.exit(0 if found else 1)
