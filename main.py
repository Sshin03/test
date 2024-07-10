import pygame
import sys
from psychopy import core
import os

# 기본 설정
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = pygame.display.get_surface().get_size()
pygame.display.set_caption("Tower of Hanoi")
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
DISC_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128), (0, 255, 255)]

# 폰트 설정
font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")  # NanumGothic.ttf 파일 경로
try:
    font = pygame.font.SysFont("malgungothic", 36)
except FileNotFoundError:
    print("폰트 파일을 찾을 수 없습니다. NanumGothic.ttf 파일이 올바른 경로에 있는지 확인해 주세요.")
    sys.exit()

# 하노이탑 상태
towers = []
num_discs = 3
move_count = 0
selected_disc = None
selected_tower = None
game_started = False

# 피드백 메시지
feedback_message = ""
feedback_time = 0

# 측정 시작
start_time = None
elapsed_time = 0

# 버튼 텍스트 및 위치 설정
button_texts = ["3", "5", "6", "7"]
button_positions = [(screen_width // 2 - 150, screen_height // 2),
                    (screen_width // 2 - 50, screen_height // 2),
                    (screen_width // 2 + 50, screen_height // 2),
                    (screen_width // 2 + 150, screen_height // 2)]


def draw_towers():
    screen.fill(WHITE)

    tower_height = 300
    base_height = 20
    disc_base_y = screen_height - 150
    tower_top_y = disc_base_y - tower_height  # 기둥이 바닥에 맞닿도록 조정

    for i, tower in enumerate(towers):
        x = screen_width // 4 * (i + 1)
        # 기둥 그리기
        pygame.draw.rect(screen, ORANGE, (x - 5, tower_top_y, 10, tower_height))
        pygame.draw.rect(screen, BLACK, (x - 5, tower_top_y, 10, tower_height), 2)
        # 기둥 바닥 그리기
        pygame.draw.rect(screen, ORANGE, (x - 150, disc_base_y, 300, base_height))
        pygame.draw.rect(screen, BLACK, (x - 150, disc_base_y, 300, base_height), 2)
        for j, disc in enumerate(tower):
            y = disc_base_y - base_height - j * 30 - 10  # 원반 위치를 조정하여 기둥 바닥과 겹치지 않도록 함
            if selected_disc and selected_tower == i and j == len(tower) - 1:
                y -= 50  # 위로 띄우기
            color = DISC_COLORS[disc % len(DISC_COLORS)]
            pygame.draw.rect(screen, color, (x - 20 * disc, y, 40 * disc, 30))
            pygame.draw.rect(screen, BLACK, (x - 20 * disc, y, 40 * disc, 30), 2)  # 테두리 추가

    time_elapsed = core.getTime() - start_time if start_time else 0
    time_text = font.render(f"Time: {time_elapsed:.2f}", True, BLACK)
    move_text = font.render(f"Moves: {move_count}", True, BLACK)

    screen.blit(time_text, (screen_width - 200, 20))
    screen.blit(move_text, (screen_width - 200, 60))

    # 피드백 메시지 표시
    if feedback_message and core.getTime() - feedback_time < 2:
        feedback_text = font.render(feedback_message, True, BLACK)
        feedback_rect = feedback_text.get_rect(center=(screen_width // 2, 120))
        screen.blit(feedback_text, feedback_rect)

    pygame.display.flip()


def draw_results():
    screen.fill(WHITE)
    time_text = font.render(f"걸린 시간: {elapsed_time:.2f} 초", True, BLACK)
    moves_text = font.render(f"이동 횟수: {move_count}", True, BLACK)

    screen.blit(time_text, time_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50)))
    screen.blit(moves_text, moves_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50)))

    pygame.display.flip()


def get_tower_from_pos(pos):
    x, y = pos
    if screen_width // 4 - 150 <= x <= screen_width // 4 + 150:
        return 0
    elif screen_width // 2 - 150 <= x <= screen_width // 2 + 150:
        return 1
    elif screen_width // 4 * 3 - 150 <= x <= screen_width // 4 * 3 + 150:
        return 2
    return None


def is_valid_move(from_tower, to_tower):
    if not towers[from_tower]:
        return False
    if not towers[to_tower] or towers[from_tower][-1] < towers[to_tower][-1]:
        return True
    return False


def move_disc(from_tower, to_tower):
    global move_count, feedback_message, feedback_time
    if is_valid_move(from_tower, to_tower):
        disc = towers[from_tower].pop()
        towers[to_tower].append(disc)
        move_count += 1
        return True
    else:
        feedback_message = "옮길 수 없는 기둥입니다!"
        feedback_time = core.getTime()
        return False


def check_win():
    return len(towers[2]) == num_discs


def draw_start_screen():
    screen.fill(WHITE)
    options_text = font.render("원반 개수를 숫자키 또는 마우스로 선택해주세요", True, BLACK)
    options_rect = options_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
    screen.blit(options_text, options_rect)

    buttons = []

    for text, pos in zip(button_texts, button_positions):
        button_surface = font.render(text, True, BLACK)
        button_rect = button_surface.get_rect(center=pos)
        buttons.append((button_surface, button_rect))
        screen.blit(button_surface, button_rect)

    pygame.display.flip()

    return buttons


def start_game_with_discs(discs):
    global towers, num_discs, move_count, selected_disc, selected_tower, game_started, start_time
    num_discs = discs
    towers = [list(range(num_discs, 0, -1)), [], []]
    move_count = 0
    selected_disc = None
    selected_tower = None
    game_started = True
    start_time = core.getTime()


def main():
    global selected_disc, selected_tower, game_started, elapsed_time

    state = "select_discs"
    buttons = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif state == "select_discs":
                    if event.key == pygame.K_3:
                        start_game_with_discs(3)
                        state = "playing"
                    elif event.key == pygame.K_5:
                        start_game_with_discs(5)
                        state = "playing"
                    elif event.key == pygame.K_6:
                        start_game_with_discs(6)
                        state = "playing"
                    elif event.key == pygame.K_7:
                        start_game_with_discs(7)
                        state = "playing"
                elif state == "results":
                    if event.key == pygame.K_SPACE:
                        state = "select_discs"
                        game_started = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == "select_discs":
                    for i, button in enumerate(buttons):
                        if button[1].collidepoint(event.pos):
                            discs = int(button_texts[i])
                            start_game_with_discs(discs)
                            state = "playing"
                            break
                elif game_started and state == "playing":
                    tower = get_tower_from_pos(pygame.mouse.get_pos())
                    if tower is not None:
                        if selected_disc is None:
                            if towers[tower]:
                                selected_tower = tower
                                selected_disc = towers[tower][-1]
                        else:
                            if tower == selected_tower or move_disc(selected_tower, tower):
                                selected_disc = None
                                selected_tower = None
                            if check_win():
                                elapsed_time = core.getTime() - start_time
                                state = "results"
                                game_started = False

        if state == "select_discs":
            buttons = draw_start_screen()
        elif state == "playing":
            draw_towers()
        elif state == "results":
            draw_results()

        clock.tick(30)


if __name__ == "__main__":
    main()
