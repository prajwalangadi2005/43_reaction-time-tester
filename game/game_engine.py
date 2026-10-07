import pygame
from .round import Round


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (180, 50, 50)
YELLOW = (220, 180, 50)


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

        # Difficulty settings
        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.current_difficulty = "Medium"

        # Current round
        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        # Valid reaction times only
        self.reaction_times = []

        # Number of rounds completed
        self.rounds_completed = 0

        # Result timing
        self.result_shown_at = None
        self.result_pause_ms = 800

        # Game states:
        #
        # playing
        # game_over
        # difficulty
        self.game_state = "playing"

        # Fonts
        self.font = pygame.font.SysFont(
            "Arial",
            30
        )

        self.big_font = pygame.font.SysFont(
            "Arial",
            46
        )

        self.small_font = pygame.font.SysFont(
            "Arial",
            24
        )

    # --------------------------------------------------
    # EVENT HANDLING
    # --------------------------------------------------

    def handle_event(self, event):

        # --------------------------------------------------
        # GAME OVER SCREEN
        # --------------------------------------------------

        if self.game_state == "game_over":

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):
                # Space moves to difficulty selection
                self.game_state = "difficulty"

            return

        # --------------------------------------------------
        # DIFFICULTY SCREEN
        # --------------------------------------------------

        if self.game_state == "difficulty":

            if event.type == pygame.KEYDOWN:

                # Easy
                if event.key == pygame.K_1:

                    self.start_new_game(
                        "Easy",
                        rounds_total=3,
                        min_wait_ms=500,
                        max_wait_ms=1500
                    )

                # Medium
                elif event.key == pygame.K_2:

                    self.start_new_game(
                        "Medium",
                        rounds_total=5,
                        min_wait_ms=1000,
                        max_wait_ms=3000
                    )

                # Hard
                elif event.key == pygame.K_3:

                    self.start_new_game(
                        "Hard",
                        rounds_total=7,
                        min_wait_ms=1500,
                        max_wait_ms=4000
                    )

                # Exit
                elif event.key in (
                    pygame.K_4,
                    pygame.K_ESCAPE
                ):

                    pygame.event.post(
                        pygame.event.Event(
                            pygame.QUIT
                        )
                    )

            return

        # --------------------------------------------------
        # NORMAL GAMEPLAY
        # --------------------------------------------------

        is_click = (
            event.type == pygame.MOUSEBUTTONDOWN
        )

        is_space = (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        )

        if (
            (is_click or is_space)
            and self.round.state != "result"
        ):

            reaction_ms = self.round.register_input()

            # Valid reaction
            if reaction_ms is not None:

                self.reaction_times.append(
                    reaction_ms
                )

            # Every input finishes the round.
            # This includes a false start.
            self.rounds_completed += 1

            self.result_shown_at = (
                pygame.time.get_ticks()
            )

    # --------------------------------------------------
    # START NEW GAME
    # --------------------------------------------------

    def start_new_game(
        self,
        difficulty,
        rounds_total,
        min_wait_ms,
        max_wait_ms
    ):

        self.current_difficulty = difficulty

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        # Clear old results
        self.reaction_times = []

        # Reset round counter
        self.rounds_completed = 0

        # Create first round
        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        # Start playing
        self.game_state = "playing"

        self.result_shown_at = None

    # --------------------------------------------------
    # INPUT
    # --------------------------------------------------

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update(self):

        # Nothing to update on these screens
        if self.game_state != "playing":
            return

        # Update current round
        self.round.update()

        # Check whether result should disappear
        if self.round.state == "result":

            now = pygame.time.get_ticks()

            if (
                self.result_shown_at is not None
                and
                now - self.result_shown_at
                >= self.result_pause_ms
            ):

                self.start_next_round()

    # --------------------------------------------------
    # NEXT ROUND
    # --------------------------------------------------

    def start_next_round(self):

        # If all rounds are completed,
        # show the final results.
        if (
            self.rounds_completed
            >= self.rounds_total
        ):

            self.game_state = "game_over"
            return

        # Otherwise start another round
        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        self.result_shown_at = None

    # --------------------------------------------------
    # AVERAGE
    # --------------------------------------------------

    def average_reaction_ms(self):

        if not self.reaction_times:
            return 0

        return round(
            sum(self.reaction_times)
            / len(self.reaction_times)
        )

    # --------------------------------------------------
    # RENDER
    # --------------------------------------------------

    def render(self, screen):

        # --------------------------------------------------
        # GAME OVER SCREEN
        # --------------------------------------------------

        if self.game_state == "game_over":

            screen.fill(BLACK)

            title = self.big_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            title_rect = title.get_rect(
                center=(
                    self.width // 2,
                    45
                )
            )

            screen.blit(
                title,
                title_rect
            )

            difficulty_text = self.font.render(
                f"Difficulty: {self.current_difficulty}",
                True,
                WHITE
            )

            difficulty_rect = (
                difficulty_text.get_rect(
                    center=(
                        self.width // 2,
                        85
                    )
                )
            )

            screen.blit(
                difficulty_text,
                difficulty_rect
            )

            # Results
            y = 125

            for index, reaction_time in enumerate(
                self.reaction_times,
                start=1
            ):

                result_text = (
                    self.small_font.render(
                        f"Round {index}: "
                        f"{reaction_time} ms",
                        True,
                        WHITE
                    )
                )

                result_rect = (
                    result_text.get_rect(
                        center=(
                            self.width // 2,
                            y
                        )
                    )
                )

                screen.blit(
                    result_text,
                    result_rect
                )

                y += 30

            # Average
            average_text = self.font.render(
                f"Average: "
                f"{self.average_reaction_ms()} ms",
                True,
                YELLOW
            )

            average_rect = (
                average_text.get_rect(
                    center=(
                        self.width // 2,
                        y + 10
                    )
                )
            )

            screen.blit(
                average_text,
                average_rect
            )

            # Continue instruction
            instruction = (
                self.small_font.render(
                    "Press SPACE to choose difficulty",
                    True,
                    WHITE
                )
            )

            instruction_rect = (
                instruction.get_rect(
                    center=(
                        self.width // 2,
                        self.height - 35
                    )
                )
            )

            screen.blit(
                instruction,
                instruction_rect
            )

            return

        # --------------------------------------------------
        # DIFFICULTY SCREEN
        # --------------------------------------------------

        if self.game_state == "difficulty":

            screen.fill(BLACK)

            title = self.big_font.render(
                "SELECT DIFFICULTY",
                True,
                WHITE
            )

            title_rect = title.get_rect(
                center=(
                    self.width // 2,
                    65
                )
            )

            screen.blit(
                title,
                title_rect
            )

            easy = self.font.render(
                "1. EASY   - 3 rounds",
                True,
                WHITE
            )

            medium = self.font.render(
                "2. MEDIUM - 5 rounds",
                True,
                WHITE
            )

            hard = self.font.render(
                "3. HARD   - 7 rounds",
                True,
                WHITE
            )

            exit_text = self.font.render(
                "4. EXIT",
                True,
                WHITE
            )

            screen.blit(
                easy,
                (180, 130)
            )

            screen.blit(
                medium,
                (180, 180)
            )

            screen.blit(
                hard,
                (180, 230)
            )

            screen.blit(
                exit_text,
                (180, 280)
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
                message = (
                    f"{self.round.reaction_ms} ms"
                )

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

        # Difficulty
        difficulty_text = (
            self.small_font.render(
                self.current_difficulty,
                True,
                WHITE
            )
        )

        screen.blit(
            difficulty_text,
            (10, 10)
        )

        # Round counter
        round_number = (
            self.rounds_completed + 1
        )

        if round_number > self.rounds_total:
            round_number = self.rounds_total

        round_text = self.small_font.render(
            f"Round {round_number}/"
            f"{self.rounds_total}",
            True,
            WHITE
        )

        round_rect = round_text.get_rect(
            top=10,
            right=self.width - 10
        )

        screen.blit(
            round_text,
            round_rect
        )

        # Running average
        avg_text = self.small_font.render(
            f"Avg: "
            f"{self.average_reaction_ms()} ms",
            True,
            WHITE
        )

        avg_rect = avg_text.get_rect(
            center=(
                self.width // 2,
                self.height - 20
            )
        )

        screen.blit(
            avg_text,
            avg_rect
        )