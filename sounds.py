from os.path import join

# Lists or sets of voice lines

main_menu_sounds = [join("Assets", "Narrator", "Sounds", "mainmenu_1.mp3"),
                    join("Assets", "Narrator", "Sounds", "mainmenu_5.mp3")]

main_menu_return_sounds = [join("Assets", "Narrator", "Sounds", "mainmenu_2.mp3"),
                           join("Assets", "Narrator", "Sounds", "mainmenu_3.mp3"),
                           join("Assets", "Narrator", "Sounds", "mainmenu_6.mp3")]

level_with_only_player_sounds = [join("Assets", "Narrator", "Sounds", "level_n_1.mp3"),
                                join("Assets", "Narrator", "Sounds", "level_n_2.mp3"),
                                join("Assets", "Narrator", "Sounds", "level_n_4.mp3"),
                                join("Assets", "Narrator", "Sounds", "level_n_6.mp3"),
                                join("Assets", "Narrator", "Sounds", "level_n_7.mp3")]

level_containing_static_sounds = [join("Assets", "Narrator", "Sounds", "staticbeing_2.mp3"),
                                  join("Assets", "Narrator", "Sounds", "staticbeing_4.mp3"),
                                  join("Assets", "Narrator", "Sounds", "staticbeing_6.mp3")]

level_containing_dynamic_sounds = [join("Assets", "Narrator", "Sounds", "dynamicbeing_1.mp3"),
                                   join("Assets", "Narrator", "Sounds", "dynamicbeing_2.mp3"),
                                   join("Assets", "Narrator", "Sounds", "dynamicbeing_3.mp3"),
                                   join("Assets", "Narrator", "Sounds", "dynamicbeing_5.mp3")] 

lose_state_sounds = [join("Assets", "Narrator", "Sounds", "lose_1.mp3"),
                     join("Assets", "Narrator", "Sounds", "lose_2.mp3"),
                     join("Assets", "Narrator", "Sounds", "lose_3.mp3"),
                     join("Assets", "Narrator", "Sounds", "lose_4.mp3"),
                     join("Assets", "Narrator", "Sounds", "lose_5.mp3"),]

win_state_sounds = [join("Assets", "Narrator", "Sounds", "win_1.mp3"),
                     join("Assets", "Narrator", "Sounds", "win_2.mp3"),
                     join("Assets", "Narrator", "Sounds", "win_3.mp3"),
                     join("Assets", "Narrator", "Sounds", "win_4.mp3"),
                     join("Assets", "Narrator", "Sounds", "win_5.mp3"),]

effect_sounds = [join("Assets", "SFX", "button_press_back.mp3"),
                 join("Assets", "SFX", "button_press_forward.wav"),
                 join("Assets", "SFX", "level_select.wav"),
                 join("Assets", "SFX", "lose_sound.mp3"),
                 join("Assets", "SFX", "player_move.mp3"),
                 join("Assets", "SFX", "win_sound.mp3"),
                 join("Assets", "SFX", "dynamic_movement.wav")]

def change_volume(sounds: list, volume: float):
    """Changes the volume of sounds."""
    for sound in sounds: # For each sound...
        sound.set_volume(volume) # Set the volume to "volume"

