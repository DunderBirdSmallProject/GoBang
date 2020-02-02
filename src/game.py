import pygame as pg
from pygame.colordict import THECOLORS as col
import math
import pathlib
import params as c

win = None
bg = None
bg_rect = None # bg stands for background
left_up = None
last_stone_coord = None
volume = c.bg_music_volume

def coord_x2idx(coordx):
    return coordx * c.grid_size + left_up[0]

def coord_y2idx(coordy):
    return coordy * c.grid_size + left_up[1]
    
def coord2idx(coord):
    return (coord_x2idx(coord[0]), coord_y2idx(coord[1]))

def idx2coord(idx):
    global left_up
    grid_diff_x, grid_diff_y = (idx[0] - left_up[0]) / c.grid_size + 0.5, (idx[1] - left_up[1]) / c.grid_size + 0.5
    return (math.floor(grid_diff_x), math.floor(grid_diff_y))

def is_in_board(coord):
    return coord[0] < 19 and coord[0] >= 0 and coord[1] < 19 and coord[1] >= 0

def init_game():
    global win, bg, bg_rect, left_up, volume
    pg.init()
    win = pg.display.set_mode((c.bd_size, c.bd_size))
    pg.display.set_caption('五子棋')

    bg_img = pg.image.load(str(c.bg_img_path))
    bg = pg.transform.scale(bg_img, (c.bd_size, c.bd_size))
    bg_rect = bg.get_rect()

    left_up = (c.grid_size // 2, c.grid_size // 2)

    pg.mixer.init()
    pg.mixer.music.load(str(c.bg_music_path))
    volume = c.bg_music_volume
    pg.mixer.music.set_volume(volume)

def volume_change(diff):
    global volume
    volume = min(max(0, volume + diff), 1.0)
    pg.mixer.music.set_volume(volume)

def modify_volume(event):
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_UP:
            volume_change(c.bg_music_diff)
        elif event.key == pg.K_DOWN:
            volume_change(-c.bg_music_diff)

def start_music():
    pg.mixer.music.play(-1) # play the music infinitely

def draw_board():
    global win, bg, bg_rect, left_up
    win.blit(bg, bg_rect)
    right_bottom = left_up[0] + (19-1)*c.grid_size, left_up[1] + (19-1)*c.grid_size
    # rb stands for right-bottom
    horizon_lines = [left_up[0] + i * c.grid_size for i in range(19)]
    vertical_lines = [left_up[1] + i * c.grid_size for i in range(19)]

    for vl in vertical_lines:
        pg.draw.line(win, col['black'], (vl, left_up[1]), (vl, right_bottom[1]))
    for hl in horizon_lines:
        pg.draw.line(win, col['black'], (left_up[0], hl), (right_bottom[0], hl))

    for idx_x, idx_y in c.center_circle:
        pg.draw.circle(win, col['black'], coord2idx((idx_x, idx_y)), c.circle_radius)
    pg.display.update()

def darken_win(darken_factor=180, color=(0, 0, 0)):
    # thanks for https://www.pygame.org/pcr/screen_dimmer/index.php
    darken = pg.Surface(pg.display.get_surface().get_size())
    darken.fill(color)
    darken.set_alpha(darken_factor)
    pg.display.get_surface().blit(darken, (0, 0))
    pg.display.update()

def draw_stone(coord, color, update=True):
    global win
    pg.draw.circle(win, color, coord2idx(coord), c.stone_radius)
    if update:
        pg.display.update()

def draw_cross(coord, update=True):
    global win
    idx = coord2idx(coord)
    pg.draw.line(win, col['red'], (idx[0]-c.cross_half_len, idx[1]), (idx[0]+c.cross_half_len, idx[1]))
    pg.draw.line(win, col['red'], (idx[0], idx[1]-c.cross_half_len), (idx[0], idx[1]+c.cross_half_len))
    if update:
        pg.display.update()

def count_in_line(coord, turn, bd, direction):
    for i in range(1, 5):
        next_x, next_y = coord[0] + direction[0] * i, coord[1] + direction[1] * i
        if is_in_board((next_x, next_y)) and (bd[next_x][next_y] == turn):
            continue
        else:
            return i - 1
    return 4

def turn2color(turn):
    return col['white'] if turn == c.white_id else col['black']

def opposite_turn(turn):
    return c.white_id if turn == c.black_id else c.black_id

def check_five(coord, turn, bd):
    goes = [(1, 0), (-1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1), (0, 1), (0, -1)]
    stretch = [count_in_line(coord, turn, bd, direction) for direction in goes]
    for i in range(4):
        if stretch[2*i] + stretch[2*i+1] >= 4:
            return True
    return False

def put_stone(coord, turn, bd, cross=True, update=True):
    bd[coord[0]][coord[1]] = turn
    color = turn2color(turn)
    draw_stone(coord, color, update)
    if cross:
        draw_cross(coord, update)
    return check_five(coord, turn, bd)

def draw_notice_board(update=True):
    global win
    notice_leftup_idx = coord2idx(c.notice_leftup_coord)
    notice_rect = pg.Rect(*notice_leftup_idx, c.notice_width, c.notice_height)
    win.blit(bg, notice_rect, notice_rect)
    if update:
        pg.display.update()

def text_objects(text, font, color=col['black']):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def draw_text_center(text, font, center, color=col['black'], update=True):
    global win
    text_suf, text_rect = text_objects(text, font, color)
    text_rect.center = center
    win.blit(text_suf, text_rect)
    if update:
        pg.display.update()
    return text_suf, text_rect

def select_page(record=None, winner=None):
    darken_win()
    draw_notice_board()
    header_font = pg.font.Font(c.header_font, c.header_size)
    text_font = pg.font.Font(c.text_font, c.text_size)
    
    notice_leftup_x, notice_leftup_y = coord2idx(c.notice_leftup_coord)
    notice_mid_x, notice_mid_y = (notice_leftup_x + c.notice_width // 2), (notice_leftup_y + c.notice_height // 2)

    if winner == c.black_id:
        header_text = 'Black Win!'
        header_color = col['black']
        draw_stone((c.notice_leftup_coord[0]+1, c.notice_leftup_coord[1]+1), col['black'])
    elif winner == c.white_id:
        header_text = 'White Win'
        header_color = col['white']
        draw_stone((c.notice_leftup_coord[0]+1, c.notice_leftup_coord[1]+1), col['white'])
    else:
        header_text = 'Go Bang'
        header_color = col['black']
        draw_stone((c.notice_leftup_coord[0]+1, c.notice_leftup_coord[1]+1), col['black'])

    header_center = (notice_mid_x, coord_y2idx(c.notice_leftup_coord[1]+1))
    draw_text_center(header_text, header_font, header_center, header_color)

    start_text = 'Start'
    start_center = (notice_mid_x, coord_y2idx(c.notice_leftup_coord[1]+c.notice_height_grids//2))
    start_suf, start_rect = draw_text_center(start_text, text_font, start_center, col['black'])

    review_rect = None
    if record and record != []:
        review_text = 'Review'
        review_center = (notice_mid_x, coord_y2idx(c.notice_leftup_coord[1]+c.notice_height_grids//2+1))
        review_suf, review_rect = draw_text_center(review_text, text_font, review_center, col['black'])
    
    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(pg.mouse.get_pos()):
                    return False
                elif review_rect and review_rect.collidepoint(pg.mouse.get_pos()):
                    return True
            elif event.type == pg.QUIT:
                raise c.QuitException
            else:
                modify_volume(event)

def resume_record(record):
    bd = [[-1]*19 for i in range(19)]
    draw_board()
    finish = False
    next_turn = c.black_id
    idx = 0
    winner = -1
    for move in record:
        next_turn = opposite_turn(move[0])
        idx += 1
        if put_stone(move[1], move[0], bd, False, False):
            finish = True
            winner = opposite_turn
            break
    pg.display.flip()
    return finish, winner, idx, next_turn, bd
    
def run_game(record, review_flag=False, lock=False):
    finish, winner, idx, turn, bd = resume_record(record)
    while (not finish) or review_flag:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise c.QuitException
            elif event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]: # the left button of the mouse was pressed
                if lock:
                    continue
                click_pos = pg.mouse.get_pos()
                cur_coord = idx2coord(click_pos)
                if is_in_board(cur_coord) and bd[cur_coord[0]][cur_coord[1]] == -1:
                    if review_flag:
                        if finish:
                            continue
                        record = record[:idx]
                        review_flag = False
                    elif len(record) != 0:
                        # delete the cross of the last stone
                        draw_stone(record[-1][1], turn2color(opposite_turn(turn)))

                    finish = put_stone(cur_coord, turn, bd)
                    if finish:
                        winner = turn
                    record.append((turn, cur_coord))
                    idx += 1
                    turn = c.black_id if turn == c.white_id else c.white_id
                    break
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    if idx > 0:
                        if not review_flag:
                            # delete the cross of the last stone
                            draw_stone(record[-1][1], turn2color(opposite_turn(turn)))
                            review_flag = True
                        idx -= 1
                        finish, winner, idx, turn, bd = resume_record(record[:idx])
                elif event.key == pg.K_RIGHT:
                    if review_flag and idx < len(record):
                        move = record[idx]
                        idx += 1
                        turn = opposite_turn(move[0])
                        if put_stone(move[1], move[0], bd, False):
                            finish = True
                            winner = move[0]
                elif event.key == pg.K_ESCAPE:
                    if review_flag:
                        record = record[:idx]
                        review_flag = False
                    finish = True
                else:
                    modify_volume(event)
    return (winner, record)

if __name__ == "__main__":
    init_game()
    try:
        start_music()
        draw_board()
        select_page()
        record = []
        is_lock = False
        is_review = False
        while True:
            draw_board()
            winner, record = run_game(record, is_review, is_lock)
            pg.time.delay(200)
            is_review = select_page(record, winner)
            if not is_review:
                record = []
                is_lock = False
            else:
                is_lock = True
            winner = -1
    except c.QuitException:
        pg.mixer.music.fadeout(200)
        pg.quit()