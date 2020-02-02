import pathlib
import math
import pygame as pg
# bd is short for board
bd_size = 900
grid_size = bd_size // 19
stone_radius = grid_size // 2
cross_half_len = stone_radius // 3
center_circle = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15),
                    (15, 3), (15, 9), (15, 15)]
circle_radius = stone_radius // 5
base_dir = pathlib.Path(__file__).parent.parent
resource_dir = base_dir / 'resource'
bg_img_path = resource_dir / 'img' / 'back.png'
bg_music_path = resource_dir / 'music' / 'back.flac'
bg_music_volume = 0.6
bg_music_diff = 0.15
white_id = 0
black_id = 1

notice_width_grids = 8
notice_height_grids = 10
notice_width = grid_size * notice_width_grids
notice_height = grid_size * notice_height_grids
notice_leftup_coord = (5, 4)

header_font = pg.font.get_default_font()
header_size = grid_size
text_font = pg.font.get_default_font()
text_size = grid_size

class QuitException(Exception):
    pass