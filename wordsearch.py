#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from random import randint, shuffle, sample, choice
from math import floor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas

# WORDCOUNT, WORDLENGTH, WORDS_PER_LINE, DIM = 40, 5, 6, (14, 14)
WORDCOUNT, WORDLENGTH, WORDS_PER_LINE, DIM = 40, 5, 3, (7, 7)

canvas = Canvas('booklet_' + str(WORDLENGTH) + '.pdf', pagesize=A4)
canvas.setFont("Times-Roman", 18)
canvas.drawString(2 * cm, 28 * cm, "Sõnamäng")



RETRY_COUNT = 1000
PLACEHOLDER = '_'
DIRECTIONS = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
E_WORD_TOO_LONG = 'Nii pikk sõna ei mahu ära'

WORDS = ''
for word in sample(list(open('et/' + str(WORDLENGTH) + '.txt')), WORDCOUNT):
    WORDS += word
WORDS = WORDS.rstrip("\n").split('\n')
WORDS.sort()
print(WORDS)
# WORDS.sort(key = len, reverse = True)

def new_matrix():
    width, height = DIM
    return [[PLACEHOLDER for x in range(width)] for y in range(height)]

def print_matrix(matrix):
    text = '<pre>'
    for row in matrix:
        text += '\n    ' + ' '.join(row).upper()
    text += '\n</pre>'
    return text

def print_words(words):
    words.sort(key = len)
    while (len(words) % WORDS_PER_LINE) != 0:
        words.append('')

    text = '<pre>'
    while len(words):
        text += '\n    ' + '  '.join(words[:WORDS_PER_LINE])
        words = words[WORDS_PER_LINE:]
    text += '\n</pre>'
    return text

def write_vector(word, vector, matrix, yes_words, all_letters):
    x = vector[0][0]
    y = vector[0][1]
    dx = vector[1][0]
    dy = vector[1][1]
    for letter in word:
        matrix[y][x] = letter # NB 
        x += dx
        y += dy
    yes_words.append(word)
    for letter in word:
        all_letters.append(letter)

def random_fit(word, matrix):
    width, height = DIM
    word_length = len(word)
    if word_length > width and word_length > height:
        raise Exception(E_WORD_TOO_LONG)
    rand_dirs = list(DIRECTIONS)
    shuffle(rand_dirs)
    direction_choices = []
    for direction_x, direction_y in rand_dirs:
        if direction_x != 0 and word_length > width:
            continue
        if direction_y != 0 and word_length > height:
            continue
        start_x = randint(0, width - 1)
        start_y = randint(0, height - 1)
        if direction_x < 0:
            start_x = randint(word_length - 1, width - 1)
        elif direction_x > 0:
            start_x = randint(0, width - word_length)
        if direction_y < 0:
            start_y = randint(word_length - 1, height - 1)
        elif direction_y > 0:
            start_y = randint(0, height - word_length)
        direction_choices.append(((start_x, start_y), (direction_x, direction_y)))
    
    vector = direction_choices[randint(0, len(direction_choices) - 1)]
    return vector

def fill_blanks(all_letters, matrix):
    for r_ix, row in enumerate(matrix):
        for c_ix, char in enumerate(row):
            if char == PLACEHOLDER:
                matrix[r_ix][c_ix] = all_letters[randint(0, len(all_letters) - 1)].upper()

def locate_letter(letter, matrix):
    found = []
    for r_ix, row in enumerate(matrix):
        for c_ix, char in enumerate(row):
            if letter == char:
                found.append((r_ix, c_ix))
    return found

def fit_word(word, matrix):
    max_match = 0
    best_vector = False
    for letter_ix, letter in enumerate(word):
        found_locations = locate_letter(letter, matrix)
        shuffle(found_locations)
        rand_dirs = list(DIRECTIONS)
        shuffle(rand_dirs)
        for loc_x, loc_y in found_locations:
            for dir_x, dir_y in rand_dirs:
                start_x = loc_x - letter_ix * dir_x
                start_y = loc_y - letter_ix * dir_y
                vector = ((start_x, start_y), (dir_x, dir_y))
                # print('v', vector)
                matches = test_vector(word, vector, matrix)
                if matches > max_match:
                    max_match = matches
                    best_vector = vector

    return best_vector

def test_vector(word, vector, matrix):
    matches = 0
    width, height = DIM
    word_length = len(word)
    x = vector[0][0]
    y = vector[0][1]
    # print('testing', vector)
    if x > width - 1 or x < 0 or y > height - 1 or y < 0:
        return -1
    dx = vector[1][0]
    dy = vector[1][1]
    if x + word_length * dx > width or x + word_length * dx < 0 or y + word_length * dy > height or y + word_length * dy < 0:
        return -1
    for letter in word:
        if matrix[y][x] not in (letter, PLACEHOLDER):
            return -1
        if matrix[y][x] == letter:
            matches += 1
        x += dx
        y += dy
    return matches

def to_canvas(matrix, words, canvas):
    for ix, row in enumerate(matrix):
        canvas.setFont("Courier", 16)
        canvas.drawString(2 * cm, (26 - ix) * cm, '  '.join(row).upper())

    words.sort()
    while (len(words) % WORDS_PER_LINE) != 0:
        words.append('')

    line = 0
    while len(words):
        canvas.setFont("Courier", 16)
        canvas.drawString(2 * cm, (26 - ix - line - 2) * cm, '  '.join(words[:WORDS_PER_LINE]))
        words = words[WORDS_PER_LINE:]
        line += 1


matrix = new_matrix()
yes_words = []
no_words = []
all_letters = []
overlaps = 0
skipped = 0
for word in WORDS:
    # print(word)
    vector = fit_word(word, matrix)
    if vector:
        matches = test_vector(word, vector, matrix)
        # print('FITTED', word, 'matches', matches, vector)
        write_vector(word, vector, matrix, yes_words, all_letters)
        overlaps += matches
        continue
    try_nr = 0
    while True:  
        vector = random_fit(word, matrix)
        matches = test_vector(word, vector, matrix)
        # print('placing', word, 'matches', matches)
        if matches > -1:
            # print('placed', word, 'matches', matches, vector)
            write_vector(word, vector, matrix, yes_words, all_letters)
            overlaps += matches
            break
        try_nr += 1
        if try_nr > RETRY_COUNT:
            no_words.append(word)
            # print(word, ' - Could not place')
            skipped += 1
            break

# print(all_letters, matrix)
fill_blanks(all_letters, matrix)
print(__file__, 'skipped', skipped, 'overlaps', overlaps)
# text = '<html><body>'
# text += '\n' + print_matrix(matrix)
# text += '\n' + print_words(yes_words)
# text += '\n</body></html>'
# f = open("sõnamäng.html", "w")
# f.write(text)
# f.close()

to_canvas(matrix, yes_words, canvas)

canvas.save()


