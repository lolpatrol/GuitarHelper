from tkinter import *
import MusicTools as mt
from PIL import ImageTk, Image, ImageFont, ImageDraw

# main window
window = Tk()
window.title("GH")
window.geometry("1200x400")

# frame
frame = Frame(window)
frame.grid(column=0, row=0, sticky=(N, W, E, S))
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)
frame.pack(pady=10, padx=10)

# fretboard image frame
img_frame = Frame(window, width=1140, height=255)
img = Image.open("fretboard_good.PNG")
tk_img = ImageTk.PhotoImage(img)

strings = 6
frets = 12
fretboard_dimensions = (1140, 255)

# canvas for holding image
canvas = Canvas(img_frame, width=1140, height=255)
canvas.grid(row=0, column=0, sticky=N+S+E+W)
canvas.pack(fill=BOTH, expand=False)
img_frame.pack(expand=False)
image_on_canvas = canvas.create_image(0, 0, image=tk_img, anchor="nw")


# key drop-down menu
drop_down_key = StringVar(window)
keys = ['Ab', 'A', 'A#', 'Bb', 'B', 'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#']
drop_down_key.set('C')

# scale drop-down menu
drop_down_scale = StringVar(window)
scales = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian',
          'Major Pentatonic', 'Minor Pentatonic', 'Major Blues (Hexatonic)', 'Minor Blues (Hexatonic)',
          'Major Blues (Heptatonic)']
drop_down_scale.set('Ionian')

orig_guitar = mt.mod_and_populate_fb(mt.get_the_mode("C", "Ionian"))


def change_drop_down(*args):
    """
    Update the fretboard image with new scales as they are chosen from the drop down menus.
    """
    s = drop_down_scale.get()
    k = drop_down_key.get()
    notes = mt.get_the_mode(k, s)
    guitar = mt.mod_and_populate_fb(notes)
    note_img = img.copy()
    font = ImageFont.truetype("arial.ttf", 15)
    draw = ImageDraw.Draw(note_img)
    for string in range(6):
        for fret in range(len(guitar[0])):
            if fret == 0:
                co = (0, 10+string*38)
            else:
                co = (65+(fret-1)*(105-fret), 10+string*38)
            note = guitar[string][fret]
            if note == k:
                text_size = font.getsize(note)
                draw.ellipse([co[0]-4, co[1]-4, co[0]+text_size[0]+4, co[1]+text_size[1]+4], fill="black")
                note_color = "white"
            else:
                note_color = "black"
            draw.text(co, note, font=font, fill=note_color)
    #note_img.save('note_fb.png')
    tk_n_img = ImageTk.PhotoImage(note_img)
    canvas.itemconfig(image_on_canvas, image=tk_n_img)
    canvas.img = tk_n_img
    canvas.pack()
    label_text = "This scale contains the notes: "+' '.join(notes)
    scale_label.configure(text=label_text)
    scale_label.place(x=600, y=365, anchor="center")


popupMenu = OptionMenu(frame, drop_down_key, *keys)
Label(frame, text="Choose a key").grid(row=1, column=0)
popupMenu.grid(row=1, column=1)

popupMenu2 = OptionMenu(frame, drop_down_scale, *scales)
Label(frame, text="Choose a mode").grid(row=2, column=0)
popupMenu2.grid(row=2, column=1)

drop_down_scale.trace('w', change_drop_down)
drop_down_key.trace('w', change_drop_down)

# Display the scale in the window
scale_label = Label(window, text="")


def coords(event):
    """
    Get coordinates of mouse click on the fretboard and play the corresponding frequency.
    """
    # Polynomial regression of the span of the strings in the image.
    string = int(1+2.221766438*(10**(-6))*(event.y**2)+0.026266286*event.y+1.407731511*(10**(-2)))
    # From polynomial regression, as the frets aren't equally, nor standard spaced.
    fret = int(1+1.386188513*(10**(-6))*(event.x**2)+9.254865544*(10**(-3))*event.x - 1.868150227*(10**(-1)))
    if string <= 6 and fret <= 12:
        mt.play_note(string, fret)


canvas.bind("<Button 1>", coords)

window.mainloop()

