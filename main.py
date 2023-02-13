import pygame
import random
import os
import threading
import pytweening as tween

clock = pygame.time.Clock()
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# COLORS

WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)

# UI SETTINGS

test = False
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fighter")

speaker_box = pygame.image.load("IMAGES/DIALOGUE/speaker_box.png")
text_box = pygame.image.load("IMAGES/DIALOGUE/rsz.png")
# speaker_box = pygame.transform.scale(speaker_box, (speaker_box.get_width() * 0.15, speaker_box.get_height() * 0.15))

TEXT_BOX_POS = (SCREEN_WIDTH / 2, 640)
SPEAKER_BOX_POS = (180, 100)
ADVANCE_DIALOGUE_RECT = pygame.Rect(1117, 680, 40, 30)
TEXT_FONT_TYPE = pygame.font.Font("MISC/MS Gothic.ttf", 25)
SPEAKER_FONT_TYPE = pygame.font.Font("MISC/baron.otf", 35)
TEXT_FONT_COLOR = (200, 200, 200)
SPEAKER_FONT_COLOR = WHITE
CHARACTER_UNFOCUS_TRANSPARENCY = 150

text_box_rect = text_box.get_rect(center=TEXT_BOX_POS)
speaker_box_rect = speaker_box.get_rect(center=SPEAKER_BOX_POS)

def tween_value(current_value, goal_value, step_amount, direction):
    if direction == "positive":
        return current_value + (tween.easeOutSine(current_value / step_amount) * goal_value)
    elif direction == "negative":
        return current_value - (tween.linear(current_value / step_amount) * goal_value)

class visual_novel_system():
    def __init__(self, dialogue_events, background=None):
        pygame.sprite.Sprite.__init__(self)

        # CHARACTER LIST

        self.character_list = {
            "left": None,
            "right": None
        }
        self.focused_side = None
        self.speaker_name = None
        self.obscure_speaker = False

        # BACKGROUNDS

        self.background_dict = {}
        self.dimmed_background = False
        self.dim_current_index = 0
        self.dim_goal_index = 0
        self.blind_current_transparency = 0
        self.blind_goal_transparency = 0
        for image in os.listdir(f"IMAGES/DIALOGUE/backgrounds"):
            if not ".DS_Store" in image:
                image_name = image.split(".")
                image_name = image_name[0]
                sprite = pygame.image.load(f"IMAGES/DIALOGUE/backgrounds/{image}")
                self.background_dict[image_name] = sprite
        if background != None:
            self.background = self.background_dict[background]
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # MUSIC

        self.music_dict = {}
        for music in os.listdir(f"SOUND/DIALOGUE/MUSIC"):
            if not ".DS_Store" in music:
                music_name = music.split(".")
                music_name = music_name[0]
                file = pygame.mixer.Sound(f"SOUND/DIALOGUE/MUSIC/{music}")
                self.music_dict[music_name] = file

        # DIALOGUE
        test = "test"
        file = open(f"MISC/DIALOGUE_TEXT/{dialogue_events}", "r")
        f = file.readlines()
        self.current_text = ""
        self.text_lines = []
        self.MAX_CHARACTERS = 50
        self.dialogue_events = []
        self.dialogue_text_index = 0
        self.able_to_update = True
        for line in f:
            if line[-1] == "\n":
                # omits last character which is /n
                self.dialogue_events.append(line[:-1])
            else:
                self.dialogue_events.append(line)

    def change_background(self, new_background):
        self.background = self.background_dict[new_background]
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def dim_background(self, goal_transparency, goal_ticks):
        self.dim_goal_index = goal_ticks
        self.blind_goal_transparency = goal_transparency
        if self.dimmed_background == False:
            self.dimmed_background = True
        else:
            self.dimmed_background = False

    def check_clicking_continue(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and self.able_to_update == False and ADVANCE_DIALOGUE_RECT.collidepoint(pygame.mouse.get_pos()):
                self.able_to_update = True
                self.play_music("transition", 0.3)

    def play_music(self, name, volume, looped=0):
        music = self.music_dict[name]
        music.set_volume(volume)
        music.play(looped)

    def stop_music(self, music):
        initial_volume = music.get_volume()
        FADE_SPEED = 20
        for current_tick in range(0, FADE_SPEED + 1):
            music.set_volume(initial_volume - (tween.linear(current_tick / FADE_SPEED) * initial_volume))
            if music.get_volume() <= 0:
                music.stop()
                break
            dt = clock.tick(60)
    def write(self, asdf):
        TEXT_SPEED = 30
        goal_text_list = [char for char in asdf]
        current_text_list = []
        current_text_index = 0
        self.text_lines = []
        text_offsets = {"0": 0}
        amount_of_lines = 1
        while current_text_index < len(goal_text_list):
            current_text_list.append(goal_text_list[current_text_index])
            if goal_text_list[current_text_index] != " ":
                self.play_music("text_blip", 0.02, 0)
            self.current_text = "".join(current_text_list)
            try:
                # check if text_offsets dictionary current slot is empty
                if str(amount_of_lines) in text_offsets.keys():
                    if amount_of_lines > 1:
                        self.text_lines[amount_of_lines - 1] = self.current_text[(self.MAX_CHARACTERS * (amount_of_lines - 1) + text_offsets[str(amount_of_lines - 1)]):self.MAX_CHARACTERS * amount_of_lines + text_offsets[str(amount_of_lines)]]
                    else:
                        self.text_lines[amount_of_lines - 1] = self.current_text[(self.MAX_CHARACTERS * (amount_of_lines - 1)):self.MAX_CHARACTERS * amount_of_lines + text_offsets[str(amount_of_lines)]]
                    # print("current line offset: ", text_offsets[str(amount_of_lines)])
                else:
                    text_offsets[str(amount_of_lines)] = 0
                    print("current line offset: ", text_offsets[str(amount_of_lines)])
                    # self.text_lines[amount_of_lines - 1] = self.current_text[self.MAX_CHARACTERS * (amount_of_lines - 1) + text_offsets[str(amount_of_lines - 1)]:self.MAX_CHARACTERS * amount_of_lines + text_offsets[str(amount_of_lines)]]
                    if amount_of_lines > 1:
                        self.text_lines[amount_of_lines - 1] = self.current_text[(self.MAX_CHARACTERS * (amount_of_lines - 1) + text_offsets[str(amount_of_lines - 1)]):self.MAX_CHARACTERS * amount_of_lines + text_offsets[str(amount_of_lines)]]
                    else:
                        self.text_lines[amount_of_lines - 1] = self.current_text[(self.MAX_CHARACTERS * (amount_of_lines - 1)):self.MAX_CHARACTERS * amount_of_lines + text_offsets[str(amount_of_lines)]]
            except IndexError:
                # if no current text on line, add slot
                self.text_lines.append(self.current_text)

            if (len(self.current_text) % self.MAX_CHARACTERS == 0 and len(self.current_text) != 0) or text_offsets[str(amount_of_lines)] > 0:
                # checking for next index
                # print("starting char: ", goal_text_list[current_text_index])
                try:
                    next_item = goal_text_list[current_text_index + 1]
                    if next_item != " ":
                        try:
                            text_offsets[str(amount_of_lines)] += 1
                        except IndexError:
                            text_offsets[str(amount_of_lines)] = 1
                        print("current line: ", amount_of_lines)
                        print("adding to offset: ", text_offsets[str(amount_of_lines)])
                        print("current char: ", goal_text_list[current_text_index])
                        print(text_offsets)
                    else:
                        print("went down line")
                        print(text_offsets[str(amount_of_lines)])
                        offset = text_offsets[str(amount_of_lines)]
                        if amount_of_lines == 1:
                            print("first line")
                            print(self.current_text[0:((self.MAX_CHARACTERS * amount_of_lines)) + offset])
                            self.text_lines.append(self.current_text[0:(self.MAX_CHARACTERS * amount_of_lines) + offset])
                        else:
                            print("more than one line")
                            self.text_lines.append(self.current_text[(self.MAX_CHARACTERS * (amount_of_lines - 1) + offset):(self.MAX_CHARACTERS * amount_of_lines)])
                        amount_of_lines += 1
                except IndexError:
                    # means the end of the current text
                    print("first statement new line")
                    # self.text_lines.append(self.current_text[(self.MAX_CHARACTERS * (amount_of_lines - 1) + text_offsets[str(amount_of_lines)]):(self.MAX_CHARACTERS * amount_of_lines)])
                    amount_of_lines += 1
                # self.text_lines[amount_of_lines - 1] = self.current_text[((amount_of_lines - 1) * self.MAX_CHARACTERS):amount_of_lines * self.MAX_CHARACTERS]
            current_text_index += 1
            dt = clock.tick(TEXT_SPEED)

    def draw(self):
        if self.background != None:
            screen.blit(self.background, (0, 0))
            if self.dimmed_background == True:
                blind = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # the size of your rect
                if self.blind_goal_transparency != self.blind_current_transparency and self.dim_current_index != self.dim_goal_index:
                    if self.blind_goal_transparency < self.blind_current_transparency:
                        self.blind_current_transparency = 0 - tween.easeOutSine(self.dim_current_index / self.dim_goal_index) * self.blind_goal_transparency
                    else:
                        self.blind_current_transparency = 0 + tween.easeOutSine(self.dim_current_index / self.dim_goal_index) * self.blind_goal_transparency
                    self.dim_current_index += 1

                blind.set_alpha(self.blind_current_transparency)  # alpha level
                blind.fill((GRAY))  # this fills the entire surface
                screen.blit(blind, (0, 0))  # (0,0) are the top-left coordinates

        # dont ask why this code is here instead of update()
        if self.character_list["left"] != None:
            self.character_list["left"].update(self)
        if self.character_list["right"] != None:
            # print("update right")
            self.character_list["right"].update(self)

        screen.blit(text_box, text_box_rect)

        for i in range(0, len(self.text_lines)):
            text = TEXT_FONT_TYPE.render(self.text_lines[i], True, TEXT_FONT_COLOR)
            screen.blit(text, (230, 625 + i * 30))

        if self.focused_side != None:
            if self.obscure_speaker == False and self.character_list[self.focused_side] != None:
                speaker_text = SPEAKER_FONT_TYPE.render(self.character_list[self.focused_side].char_name, True, SPEAKER_FONT_COLOR)
            else:
                speaker_text = SPEAKER_FONT_TYPE.render("???", True,SPEAKER_FONT_COLOR)
            speaker_text = pygame.transform.rotate(speaker_text, 6)
            speaker_text_rect = speaker_text.get_rect()
            speaker_text_rect.center = (180, 95)
            screen.blit(speaker_box, speaker_box_rect)
            screen.blit(speaker_text, speaker_text_rect)

    def update(self):
        self.draw()
        self.check_clicking_continue()
        if self.able_to_update == True:
            current_line_text = self.dialogue_events[self.dialogue_text_index]
            if "change sprite: " in current_line_text:
                splitted = current_line_text.replace("change sprite: ", "")
                character_events_list = splitted.split(", ")
                print(character_events_list[1], ": ", character_events_list[2])
                c = self.character_list[character_events_list[0]]
                if c == None:
                    new_char = visual_novel_system.character(character_events_list[1], character_events_list[0], character_events_list[2], character_events_list[3], self)
                    self.character_list[character_events_list[0]] = new_char
                else:
                    c.change_sprite(character_events_list[1], character_events_list[2], character_events_list[3], self)
            elif "toggle focus: " in current_line_text:
                splitted = current_line_text.replace("toggle focus: ", "")
                c = self.character_list[splitted]
                c.toggle_focus(self)
            elif "text: " in current_line_text:
                splitted = current_line_text.replace("text: ", "")
                threading.Thread(target=self.write, args=(splitted,)).start()
                # self.write(splitted)
                self.current_text = splitted
            elif "play music: " in current_line_text:
                splitted = current_line_text.replace("play music: ", "")
                sound_events_list = splitted.split(", ")
                self.play_music(sound_events_list[0], float(sound_events_list[1]), int(sound_events_list[2]))
            elif "stop music: " in current_line_text:
                splitted = current_line_text.replace("stop music: ", "")
                # no idea why the comma fixes it
                threading.Thread(target=self.stop_music, args=(self.music_dict[splitted],)).start()
            elif "change background: " in current_line_text:
                splitted = current_line_text.replace("change background: ", "")
                self.change_background(splitted)
            elif "dim background" in current_line_text:
                self.dim_background(100, 100)
            elif "obscure speaker: " in current_line_text:
                splitted = current_line_text.replace("obscure speaker: ", "")
                if splitted == "True":
                    self.obscure_speaker = True
                elif splitted == "False":
                    self.obscure_speaker = False
            elif "shake: " in current_line_text:
                splitted = current_line_text.replace("shake: ", "")
                shake_events_list = splitted.split(", ")
                threading.Thread(target=self.character_list[shake_events_list[0]].shake, args=(self, int(shake_events_list[1]))).start()
            elif "- - - - -" in current_line_text:
                self.able_to_update = False
            self.dialogue_text_index += 1

    class character():
        def __init__(self, char_name, type, current_sprite_name, sprite_pos, system_instance):
            pygame.sprite.Sprite.__init__(self)
            self.char_name = char_name
            self.type = type
            self.in_focus = False
            self.sprite_transparency = 0
            self.visible = True
            # default config
            if self.type == "left":
                self.direction = False
                # print(char_name, " is facing ", self.direction)
                if sprite_pos == "default":
                    self.sprite_pos_x = 300
                    self.sprite_pos_y = 550
                else:
                    splitted = sprite_pos.split("|")
                    self.sprite_pos_x = int(splitted[0])
                    self.sprite_pos_y = int(splitted[1])
            if self.type == "right":
                self.direction = True
                if sprite_pos == "default":
                    self.sprite_pos_x = 980
                    self.sprite_pos_y = 550
                else:
                    splitted = sprite_pos.split("|")
                    self.sprite_pos_x = int(splitted[0])
                    self.sprite_pos_y = int(splitted[1])
            self.sprite_dict = {}
            self.sprite_tween_index = 0

            # LOADING ALL CHARACTER SPRITES

            temp_dict = {}
            directory_contents = os.listdir(f"IMAGES/DIALOGUE")
            for item in directory_contents:
                dir_path = os.path.join(f"IMAGES/DIALOGUE", item)
                if os.path.isdir(dir_path) and item != "backgrounds":
                    for image in os.listdir(f"IMAGES/DIALOGUE/{item}"):
                        if ".png" in image:
                            image_name = image.split(".")
                            image_name = image_name[0]
                            sprite = pygame.image.load(f"IMAGES/DIALOGUE/{item}/{image}")
                            temp_dict[image_name] = sprite
                    # list of lists of animations
                    self.sprite_dict[item] = temp_dict
                    temp_dict = {}

            self.sprite_image = self.sprite_dict[self.char_name][current_sprite_name]
            self.sprite_rect = self.sprite_image.get_rect()
            self.sprite_rect.centerx = self.sprite_pos_x
            self.sprite_rect.centery = self.sprite_pos_y

        def toggle_focus(self, system_instance):
            self.in_focus = not self.in_focus
            if self.in_focus == True:
                if system_instance.obscure_speaker == False:
                    self.sprite_transparency = 255
                    print("transparency: ", self.sprite_transparency)
                else:
                    self.sprite_transparency = 0
                    print("transparency: ", self.sprite_transparency)
                if self.type == "left":
                    threading.Thread(target=self.tween_focus, args=(10, 0, 20, "right", 1)).start()
                elif self.type == "right":
                    threading.Thread(target=self.tween_focus, args=(10, 0, 20, "left", 1)).start()
                system_instance.focused_side = self.type
            else:
                if self.type == "left":
                    threading.Thread(target=self.tween_focus, args=(10, 150, 20, "left")).start()
                elif self.type == "right":
                    threading.Thread(target=self.tween_focus, args=(10, 150, 20, "right")).start()
                system_instance.focused_side = None

        def tween_focus(self, ticks, goal_transparency, goal_offset, pos_direction, transparency_direction = -1):
            initial_transparency = self.sprite_transparency
            initial_offset = self.sprite_rect.centerx
            for current_tick in range(0, ticks):
                self.sprite_transparency = initial_transparency + (transparency_direction * (tween.easeOutSine(current_tick / ticks) * goal_transparency))
                if pos_direction == "left":
                    self.sprite_pos_x = initial_offset - (tween.easeOutSine(current_tick / ticks) * goal_offset)
                elif pos_direction == "right":
                    self.sprite_pos_x = initial_offset + (tween.easeOutSine(current_tick / ticks) * goal_offset)
                dt = clock.tick(60)

        def shake(self, system_instance, magnitude):
            while system_instance.able_to_update == True:
                if system_instance.able_to_update == False:
                    break
                dt = clock.tick(60)
            initial_pos_x = self.sprite_pos_x
            initial_pos_y = self.sprite_pos_y
            while system_instance.able_to_update == False:
                random_shake_x = random.randint(-magnitude, magnitude)
                random_shake_y = random.randint(-magnitude, magnitude)
                self.sprite_pos_x = initial_pos_x + random_shake_x
                self.sprite_pos_y = initial_pos_y + random_shake_y
                dt = clock.tick(60)

        def change_sprite(self, new_char_name, new_sprite_name, new_sprite_pos, system_instance):
            if new_char_name != "REMOVE":
                self.char_name = new_char_name
                self.sprite_image = self.sprite_dict[self.char_name][new_sprite_name]
                self.sprite_rect = self.sprite_image.get_rect()
                if new_sprite_pos != "default":
                    splitted = new_sprite_pos.split("|")
                    self.sprite_pos_x = int(splitted[0])
                    self.sprite_pos_y = int(splitted[1])
                    self.sprite_rect.center = (int(splitted[0]), int(splitted[1]))
                else:
                    if self.type == "left":
                        self.direction = False
                        self.sprite_pos_x = 300
                        self.sprite_pos_y = 550
                    elif self.type == "right":
                        self.direction = True
                        self.sprite_pos_x = 980
                        self.sprite_pos_y = 550
                    self.sprite_rect.center = (self.sprite_pos_x, self.sprite_pos_y)
            else:
                system_instance.character_list[self.type] = None

        def draw(self, system_instance):
            converted = self.sprite_image.convert()
            converted.set_alpha(self.sprite_transparency)
            if system_instance.obscure_speaker == True:
                if self.in_focus == False:
                    # print("INVISIBLE: ", self.char_name)
                    screen.blit(pygame.transform.flip(converted, self.direction, False), self.sprite_rect)
            else:
                # print("test")
                screen.blit(pygame.transform.flip(converted, self.direction, False), self.sprite_rect)

        def update(self, system_instance):
            # if self.char_name == "dio":
                # print("dio: ", self.sprite_transparency)
            self.sprite_rect.centerx = self.sprite_pos_x
            self.sprite_rect.centery = self.sprite_pos_y
            if system_instance.obscure_speaker == True:
                if self.in_focus == True:
                    self.sprite_transparency = 0
                self.draw(system_instance)
            else:
                self.draw(system_instance)

def draw_bg():
    screen.fill((255,255,255))

test_system = visual_novel_system("opening_scene", "black_screen")
# test_system.dim_background(100, 30)

run = True

while run:
    draw_bg()
    test_system.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.flip()
    dt = clock.tick(60)