from collections import deque
import pyaudio
import math

notes_in_order_expanded = deque(['A', 'A#/Bb', 'B', 'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab'])
fret_board_key = ['E', 'B', 'G', 'D', 'A', 'E']

dir_add = {-4: "#", -3: "b"}

open_string_frequencies = {
    1: 329.63,
    2: 246.94,
    3: 196.00,
    4: 146.83,
    5: 110.00,
    6: 82.41
}


def get_the_scale(key):
    notes = deque(["C", "D", "E", "F", "G", "A", "B"])
    s_k = ["C", "G", "D", "A", "E", "B"]  # sharp direction of circle of fifths

    if "#" in key or key in s_k:  # add sharps
        dir = -4
    else:  # else add flats
        dir = -3

    while notes[0] != key:
        notes.rotate(dir)
        if dir == -4:
            notes[-1] += dir_add[dir]
        elif dir == -3:
            notes[-dir] += dir_add[dir]
    return notes


def get_the_mode(key, mode):
    modes = {
        "Ionian": [],
        "Dorian": ["b3", "b7"],
        "Phrygian": ["b2", "b3", "b6", "b7"],
        "Lydian": ["#4"],
        "Mixolydian": ["b7"],
        "Aeolian": ["b3", "b6", "b7"],
        "Locrian": ["b2", "b3", "b5", "b6", "b7"]
    }
    notes = get_the_scale(key)
    for modifier in modes[mode]:
        sf, deg = modifier
        deg = int(deg) - 1
        note = notes[deg]
        if "#" in note:
            if sf == "b":
                notes[deg] = notes[deg][:-1]
            else:
                notes[deg] += "#"
        elif "b" in note:
            if sf == "#":
                notes[deg] = notes[deg][:-1]
            else:
                notes[deg] += "b"
        else:
            notes[deg] += sf
    return notes


def fb(scale):
    next_from = {
        "A": ("B", 2),
        "B": ("C", 1),
        "C": ("D", 2),
        "D": ("E", 2),
        "E": ("F", 1),
        "F": ("G", 2),
        "G": ("A", 2)
    }
    board = [["" for _ in range(25)] for _ in range(6)]
    for i in range(6):
        board[i][0] = fret_board_key[i]
    for i in range(6):
        for j in range(25):
            if board[i][j] != "":
                next_note, next_pos = next_from[board[i][j]]
                if j+next_pos < 25:
                    board[i][j+next_pos] = next_note
    return board


def mod_and_populate_fb(scale):
    board = fb("A")
    to_go = {
        "#": 1,
        "##": 2,
        "b": -1,
        "bb": -2
    }
    # E string
    e_string_orig = deque(board[0])
    e_string = ["" for _ in range(25)]
    for fret in range(25):
        if e_string_orig[fret] != "":
            for note in scale:
                if e_string_orig[fret] in note and len(note) > 1:
                    modifier = note[1:]
                    go = to_go[modifier]
                    if fret + go < 25:
                        e_string[fret+go] = note
                elif e_string_orig[fret] == note:
                    e_string[fret] = note

    board = [[], [], [], [], [], []]
    board[5] = e_string[:13]  # full length
    e_string = deque(e_string[:12]+e_string[:12])
    for string in range(5):
        if string == 3:
            e_string.rotate(-4)
        else:
            e_string.rotate(-5)
        e_list = list(e_string)
        board[4 - string] = e_list[:13]
    return board


def play_note(string, fret):
    note = open_string_frequencies[string]
    if fret > 0:
        note = note*(1.0595**fret)
    print("Playing frequency: ", note)
    p = pyaudio.PyAudio()
    wave_data = ""
    for x in range(16000):
        wave_data = wave_data+chr(int(math.sin(x/((16000/note)/math.pi))*127+128))

    for x in range(1):
        wave_data = wave_data+chr(128)
    stream = p.open(format=p.get_format_from_width(1),
                    channels=1,
                    rate=16000,
                    output=True)

    stream.write(wave_data)
    stream.stop_stream()
    stream.close()
    p.terminate()

