import pygame
import pygame_gui

import entity

entities = {}

def add_entity(id, rect, color):
    entities[id] = pygame.draw.rect(display, color, pygame.Rect(rect))
    return entities[id]

def move_entity(id, location, color):
    global head_rect
    rect = entities[id]
    rect.move_ip(location[0] * field_cell_size - rect.x, location[1] * field_cell_size - rect.y)

    drawn = pygame.draw.rect(display, color, entities[id])
    if id == head.id:
        head_rect = drawn

def gen_possible_fields(field_size, field_cell_size):
    possible_fields = []
    for x in range(field_size[0]):
        for y in range(field_size[1]):
            possible_fields.append((x * field_cell_size, y * field_cell_size))
    for taken in entities.values():
        try:
            possible_fields.remove((taken.x, taken.y))
        except:
            print("Snake ate its tail!")
            pass
    return possible_fields

def start_game():
    global running, is_paused, tick_speed, tick, head, head_rect, apple, apple_rect, time_delta, current_score
    running = True
    is_paused = False
    tick_speed = 15.0
    tick = 0
    current_score = 0

    entities.clear()
    display.fill('#FFFFFF')

    head = entity.Head((0, 1), field_size)
    head_rect = add_entity(head.id, head.rect(field_cell_size), "blue")
    apple_rect = pygame.draw.rect(display, "blue", head_rect)
    head.food = 0

    apple = entity.Apple(gen_possible_fields(field_size, field_cell_size), (100, 100))
    apple_rect = pygame.draw.rect(display, "red", apple.rect(field_cell_size))

    time_delta = 0
    start_button.hide()
    last_score_text.hide()

    pygame.display.update()

if __name__ == '__main__':
    pygame.init()
    field_cell_size = 100
    field_size = (8, 6)
    high_score = 0
    current_score = 0

    display = pygame.display.set_mode((field_cell_size * field_size[0], field_cell_size * field_size[1]))
    pygame.display.set_caption("SNAKE")
    background = pygame.Surface((field_cell_size * 8, field_cell_size * 6))
    background.fill(pygame.Color('#FFFFFF'))

    manager = pygame_gui.UIManager((800, 600))

    clock = pygame.time.Clock()
    running = True
    is_paused = True
    tick_speed = 15.0
    tick = 0

    display.fill('#FFFFFF')

    head = entity.Head((0, 1), field_size)
    head_rect = add_entity(head.id, head.rect(field_cell_size), "blue")
    head.food = 0

    apple = entity.Apple(gen_possible_fields(field_size, field_cell_size), (100, 100))
    apple_rect = pygame.draw.rect(display, "red", apple.rect(field_cell_size))

    time_delta = 0

    #UI
    start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Start!', manager=manager)
    last_score_text = pygame_gui.elements.UITextBox("Last score: 0", relative_rect=pygame.Rect((250, 225), (200, 50)), manager=manager)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    start_game()
                    continue
            manager.process_events(event)
        if not is_paused:
            try:
                apple_rect = pygame.draw.rect(display, "red", apple.rect(field_cell_size))
            except:
                pass
            x, y = 0, 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                y = -1
                x = 0
            if keys[pygame.K_s]:
                y = 1
                x = 0
            if keys[pygame.K_a]:
                y = 0
                x = -1
            if keys[pygame.K_d]:
                y = 0
                x = 1
            if x != 0 or y != 0:
                head.direction = (x, y)

            if tick > tick_speed:
                display.fill('#FFFFFF')
                try:
                    apple_rect = pygame.draw.rect(display, "red", apple.rect(field_cell_size))
                except:
                    pass
                tick = 0
                head.tick()

                for task in head.changelist:
                    if task.type == entity.EAType.MOVE:
                        move_entity(task.kwargs["id"], task.kwargs["location"], task.kwargs["color"])
                    if task.type == entity.EAType.CREATE:
                        add_entity(task.kwargs["id"], task.kwargs["rectangle"], task.kwargs["color"])
                head.changelist.clear()
                if apple is None:
                    empty_fields = gen_possible_fields(field_size, field_cell_size)

                    apple = entity.Apple(empty_fields, (100, 100))
                    apple_rect = pygame.draw.rect(display, "red", apple.rect(field_cell_size))
                    if apple_rect.collidelist(list(entities.values())) is not -1:
                        print("COLLIDES! ",apple_rect)
                        print(empty_fields)
                        print(entities.values())


                snake_parts = list(entities.values())
                snake_parts.remove(head_rect)

                if head_rect.collidelist(snake_parts) is not -1:
                    is_paused = True
                    high_score = max(high_score, current_score)
                    continue

                if head_rect.colliderect(apple_rect):
                    head.food += 1
                    tick_speed -= 0.5
                    current_score += 1
                    apple = None
            else:
                tick += 1
        else:
            last_score_text.set_text("Best score: %s" % high_score)
            start_button.show()
            last_score_text.show()
            manager.update(time_delta)
            manager.draw_ui(display)
        pygame.display.update()
        time_delta = clock.tick(30) / 1000