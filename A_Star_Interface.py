from __future__ import annotations

import pygame
import FolderCreator as fc


def get_user_input() -> tuple:
    pygame.init()
    screen_size = [fc.get_size_constant(), fc.get_size_constant()]
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Pathfinding Interface")

    done = False
    clock = pygame.time.Clock()

    start_pos: tuple | None = None
    goal_pos: tuple | None = None

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_pos is None:
                    start_pos = pygame.mouse.get_pos()
                    print("Start pos set as: ", start_pos)
                elif goal_pos is None:
                    goal_pos = pygame.mouse.get_pos()
                    print("Goal pos set as: ", goal_pos)
                    pygame.quit()
                    return start_pos, goal_pos
                else:
                    print("something else happened")
                    pygame.quit()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    get_user_input()
