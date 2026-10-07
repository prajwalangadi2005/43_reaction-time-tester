import random
import pygame


class Round:

    def __init__(self, min_wait_ms=1000, max_wait_ms=3000):

        self.wait_delay_ms = random.randint(
            min_wait_ms,
            max_wait_ms
        )

        # waiting -> go -> result
        self.state = "waiting"

        self.start_time = pygame.time.get_ticks()

        # This is set when the screen turns green
        self.go_time = None

        self.reaction_ms = None

        # False-start flag
        self.false_start = False

    def update(self):

        if self.state == "waiting":

            now = pygame.time.get_ticks()

            if (
                now - self.start_time
                >= self.wait_delay_ms
            ):

                self.state = "go"

                # Exact moment the screen turns green
                self.go_time = now

    def register_input(self):

        now = pygame.time.get_ticks()

        # ==============================================
        # FALSE START
        # ==============================================

        if self.state == "waiting":

            self.state = "result"

            self.reaction_ms = None

            self.false_start = True

            return None

        # ==============================================
        # VALID REACTION
        # ==============================================

        if self.state == "go":

            self.reaction_ms = (
                now - self.go_time
            )

            self.state = "result"

            self.false_start = False

            return self.reaction_ms

        # ==============================================
        # IGNORE INPUT AFTER RESULT
        # ==============================================

        return None