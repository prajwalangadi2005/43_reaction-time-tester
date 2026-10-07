import pygame
from .round import Round


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (180, 50, 50)


class GameEngine:
    def __init__(
        self,
        width,
        height,
        rounds_total=5,
        min_wait_ms=1000,
        max_wait_ms=3000
    ):
        self.width = width
        self.height = height

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        # Store only valid reaction times.
        # False starts are not added.
        self.reaction_times = []

        self.result_shown_at = None
        self.result_pause_ms = 800

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 46)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.game_over = False

    def handle_event(self, event):

        # When the game is over, wait for Space.
        if self.game_over:

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):
                # For Task 2, Space simply closes the results screen.
                # Replay/difficulty selection belongs to Task 3.
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )

            return

        is_click = event.type == pygame.MOUSEBUTTONDOWN

        is_space = (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        )

        if (is_click or is_space) and self.round.state != "result":

            reaction_ms = self.round.register_input()

            # Only valid reactions are stored.
            if reaction_ms is not None:
                self.reaction_times.append(reaction_ms)

            self.result_shown_at = pygame.time.get_ticks()

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    def update(self):

        if self.game_over:
            return

        self.round.update()

        if self.round.state == "result":

            now = pygame.time.get_ticks()

            if now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()

    def _start_next_round(self):

        # Number of completed valid reactions determines
        # whether all rounds have finished.
        #
        # For Task 2 we keep the existing behavior where
        # each valid reaction completes a round.
        if len(self.reaction_times) >= self.rounds_total:

            self.game_over = True
            return

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

    def average_reaction_ms(self):

        if not self.reaction_times:
            return 0

        return round(
            sum(self.reaction_times)
            / len(self.reaction_times)
        )

    def render(self, screen):

        # --------------------------------------------------
        # GAME OVER / RESULTS SCREEN
        # --------------------------------------------------

        if self.game_over:

            screen.fill(BLACK)

            # Title
            title = self.big_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            title_rect = title.get_rect(
                center=(self.width // 2, 60)
            )

            screen.blit(title, title_rect)

            # Subtitle
            subtitle = self.font.render(
                "FINAL RESULTS",
                True,
                WHITE
            )

            subtitle_rect = subtitle.get_rect(
                center=(self.width // 2, 110)
            )

            screen.blit(subtitle, subtitle_rect)

            # Display every reaction time
            y = 155

            for index, reaction_time in enumerate(
                self.reaction_times,
                start=1
            ):

                result_text = self.small_font.render(
                    f"Round {index}: {reaction_time} ms",
                    True,
                    WHITE
                )

                result_rect = result_text.get_rect(
                    center=(self.width // 2, y)
                )

                screen.blit(
                    result_text,
                    result_rect
                )

                y += 32

            # Average
            average_text = self.font.render(
                f"Average: {self.average_reaction_ms()} ms",
                True,
                WHITE
            )

            average_rect = average_text.get_rect(
                center=(self.width // 2, y + 15)
            )

            screen.blit(
                average_text,
                average_rect
            )

            # Instruction
            instruction = self.small_font.render(
                "Press SPACE to continue",
                True,
                WHITE
            )

            instruction_rect = instruction.get_rect(
                center=(
                    self.width // 2,
                    self.height - 50
                )
            )

            screen.blit(
                instruction,
                instruction_rect
            )

            return

        # --------------------------------------------------
        # NORMAL GAME SCREEN
        # --------------------------------------------------

        if self.round.state == "waiting":

            bg = GRAY
            message = "Wait for green..."

        elif self.round.state == "go":

            bg = GREEN
            message = "Click now!"

        else:

            if getattr(
                self.round,
                "false_start",
                False
            ):

                bg = RED
                message = "False Start!"

            else:

                bg = BLUE
                message = f"{self.round.reaction_ms} ms"

        screen.fill(bg)

        # Main message
        text_surf = self.big_font.render(
            message,
            True,
            WHITE
        )

        text_rect = text_surf.get_rect(
            center=(
                self.width // 2,
                self.height // 2
            )
        )

        screen.blit(
            text_surf,
            text_rect
        )

        # Round counter
        round_num = min(
            len(self.reaction_times) + 1,
            self.rounds_total
        )

        round_text = self.font.render(
            f"Round {round_num}/{self.rounds_total}",
            True,
            WHITE
        )

        screen.blit(
            round_text,
            (10, 10)
        )

        # Running average
        avg_text = self.font.render(
            f"Avg: {self.average_reaction_ms()} ms",
            True,
            WHITE
        )

        screen.blit(
            avg_text,
            (
                self.width - 190,
                10
            )
        )