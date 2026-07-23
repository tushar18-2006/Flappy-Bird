import random
import tkinter as tk


class Bird:
    """Represents the player-controlled bird."""

    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = 16
        self.velocity = 0
        self.gravity = 0.42
        self.flap_strength = -7.2

        # Draw the bird with simple shapes.
        self.body_id = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill="yellow",
            outline="orange",
            width=2,
        )
        self.eye_id = canvas.create_oval(
            x + 5,
            y - 7,
            x + 11,
            y - 1,
            fill="white",
            outline="black",
            width=1,
        )
        self.pupil_id = canvas.create_oval(
            x + 8,
            y - 5,
            x + 10,
            y - 3,
            fill="black",
        )
        self.beak_id = canvas.create_polygon(
            x + 16,
            y,
            x + 28,
            y - 5,
            x + 28,
            y + 5,
            fill="orange",
            outline="darkorange",
        )
        self.wing_id = canvas.create_oval(
            x - 3,
            y + 2,
            x + 12,
            y + 12,
            fill="gold",
            outline="orange",
            width=1,
        )

    def flap(self):
        """Give the bird an upward push when the player presses Space."""
        self.velocity = self.flap_strength

    def update(self):
        """Apply gravity and update the bird position."""
        self.velocity += self.gravity
        self.y += self.velocity

    def draw(self):
        """Move all bird parts together on the canvas."""
        self.canvas.coords(
            self.body_id,
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
        )
        self.canvas.coords(
            self.eye_id,
            self.x + 5,
            self.y - 7,
            self.x + 11,
            self.y - 1,
        )
        self.canvas.coords(
            self.pupil_id,
            self.x + 8,
            self.y - 5,
            self.x + 10,
            self.y - 3,
        )
        self.canvas.coords(
            self.beak_id,
            self.x + 16,
            self.y,
            self.x + 28,
            self.y - 5,
            self.x + 28,
            self.y + 5,
        )
        self.canvas.coords(
            self.wing_id,
            self.x - 3,
            self.y + 2,
            self.x + 12,
            self.y + 12,
        )

    def get_bbox(self):
        """Return a simple bounding box for collision detection."""
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
        )

    def delete(self):
        """Remove all bird drawing parts from the canvas."""
        self.canvas.delete(self.body_id)
        self.canvas.delete(self.eye_id)
        self.canvas.delete(self.pupil_id)
        self.canvas.delete(self.beak_id)
        self.canvas.delete(self.wing_id)


class Pipe:
    """Represents one vertical pipe pair."""

    WIDTH = 60
    GAP_HEIGHT = 160
    SPEED = 3.5

    def __init__(self, canvas, game_width, game_height, gap_y):
        self.canvas = canvas
        self.game_width = game_width
        self.game_height = game_height
        self.x = game_width + 20
        self.gap_y = gap_y
        self.top_height = gap_y - self.GAP_HEIGHT // 2
        self.bottom_y = gap_y + self.GAP_HEIGHT // 2

        self.top_id = canvas.create_rectangle(
            self.x,
            0,
            self.x + self.WIDTH,
            self.top_height,
            fill="green",
            outline="darkgreen",
            width=2,
        )
        self.bottom_id = canvas.create_rectangle(
            self.x,
            self.bottom_y,
            self.x + self.WIDTH,
            self.game_height,
            fill="green",
            outline="darkgreen",
            width=2,
        )

        self.passed = False

    def update(self):
        """Move the pipe to the left by a constant speed."""
        self.x -= self.SPEED

    def draw(self):
        """Update the pipe drawing position."""
        self.canvas.coords(
            self.top_id,
            self.x,
            0,
            self.x + self.WIDTH,
            self.top_height,
        )
        self.canvas.coords(
            self.bottom_id,
            self.x,
            self.bottom_y,
            self.x + self.WIDTH,
            self.game_height,
        )

    def is_off_screen(self):
        """Remove pipes once they have completely moved left."""
        return self.x + self.WIDTH < 0

    def get_top_bbox(self):
        return (self.x, 0, self.x + self.WIDTH, self.top_height)

    def get_bottom_bbox(self):
        return (self.x, self.bottom_y, self.x + self.WIDTH, self.game_height)


class Game:
    """Main game controller that runs the full Flappy Bird loop."""

    WIDTH = 420
    HEIGHT = 600
    GROUND_HEIGHT = 80
    SPAWN_INTERVAL = 95

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flappy Bird Clone")
        self.root.resizable(False, False)

        # Make the window look clean and centered on screen.
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg="sky blue",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.spawn_counter = 0
        self.pipes = []

        self.bird = Bird(self.canvas, 100, self.HEIGHT // 2)

        # Draw the ground.
        self.canvas.create_rectangle(
            0,
            self.HEIGHT - self.GROUND_HEIGHT,
            self.WIDTH,
            self.HEIGHT,
            fill="brown",
        )

        # Draw a small clear area at the top so the score panel is always visible.
        self.canvas.create_rectangle(
            0,
            0,
            self.WIDTH,
            48,
            fill="sky blue",
            outline="",
        )

        # Scoreboard text is stored so it can be updated live.
        self.score_text_id = self.canvas.create_text(
            20,
            20,
            text="Score: 0",
            anchor="w",
            font=("Arial", 14, "bold"),
            fill="black",
        )
        self.best_text_id = self.canvas.create_text(
            self.WIDTH - 20,
            20,
            text="Best: 0",
            anchor="e",
            font=("Arial", 14, "bold"),
            fill="black",
        )

        self.game_over_text_id = None

        # Keyboard controls.
        self.root.bind("<space>", self.on_key_action)
        self.root.bind("<Up>", self.on_key_action)
        self.root.bind("<r>", self.restart_game)
        self.root.bind("<Escape>", self.exit_game)

        self.loop()
        self.root.mainloop()

    def on_key_action(self, event):
        """Let Space or Up flap, and restart after game over."""
        if self.game_over:
            self.reset_game()
        else:
            self.bird.flap()

    def restart_game(self, event):
        """Restart the entire state after a collision."""
        self.reset_game()

    def exit_game(self, event):
        """Close the window with the Esc key."""
        self.root.destroy()

    def reset_game(self):
        """Reset the bird, score, and pipes for a new round."""
        self.score = 0
        self.game_over = False
        self.spawn_counter = 0

        # Remove any existing pipes from the canvas.
        for pipe in self.pipes:
            self.canvas.delete(pipe.top_id)
            self.canvas.delete(pipe.bottom_id)
        self.pipes.clear()

        # Remove the previous bird before drawing a new one.
        if self.bird is not None:
            self.bird.delete()

        # Reset the bird to the start position.
        self.bird = Bird(self.canvas, 100, self.HEIGHT // 2)
        self.bird.velocity = 0

        # Remove game over text if it exists.
        if self.game_over_text_id is not None:
            self.canvas.delete(self.game_over_text_id)
            self.game_over_text_id = None

        self.update_scoreboard()

    def update_scoreboard(self):
        """Refresh the current and best score text."""
        self.canvas.itemconfig(self.score_text_id, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.best_text_id, text=f"Best: {self.best_score}")

        # Keep the score labels above the pipes every time the scoreboard updates.
        self.canvas.tag_raise(self.score_text_id)
        self.canvas.tag_raise(self.best_text_id)

    def spawn_pipe(self):
        """Create a new pipe with a random gap height."""
        min_gap = 140
        max_gap = self.HEIGHT - self.GROUND_HEIGHT - 140
        gap_y = random.randint(min_gap, max_gap)
        pipe = Pipe(self.canvas, self.WIDTH, self.HEIGHT, gap_y)
        self.pipes.append(pipe)

    def update_pipes(self):
        """Move all active pipes and remove those that go off screen."""
        for pipe in self.pipes:
            pipe.update()
            pipe.draw()

            # Score only once when the bird passes the pipe.
            if not pipe.passed and pipe.x + pipe.WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
                self.best_score = max(self.best_score, self.score)
                self.update_scoreboard()

        # Remove pipes that are no longer visible.
        self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]

    def check_collision(self):
        """Check for collisions with pipes, ground, and top of the screen."""
        bird_bbox = self.bird.get_bbox()

        # Bird must stay inside the top of the screen.
        if bird_bbox[1] <= 0:
            self.end_game()
            return

        # Bird must stay above the ground.
        ground_y = self.HEIGHT - self.GROUND_HEIGHT
        if bird_bbox[3] >= ground_y:
            self.end_game()
            return

        # Check the bird against each pipe piece.
        for pipe in self.pipes:
            top_bbox = pipe.get_top_bbox()
            bottom_bbox = pipe.get_bottom_bbox()

            if self.rectangles_overlap(bird_bbox, top_bbox) or self.rectangles_overlap(
                bird_bbox, bottom_bbox
            ):
                self.end_game()
                return

    def rectangles_overlap(self, bbox_a, bbox_b):
        """Helper for simple AABB rectangle collision detection."""
        return not (
            bbox_a[2] < bbox_b[0]
            or bbox_a[0] > bbox_b[2]
            or bbox_a[3] < bbox_b[1]
            or bbox_a[1] > bbox_b[3]
        )

    def end_game(self):
        """Stop the live gameplay and show Game Over."""
        self.game_over = True

        if self.game_over_text_id is None:
            self.game_over_text_id = self.canvas.create_text(
                self.WIDTH // 2,
                self.HEIGHT // 2,
                text="Game Over",
                font=("Arial", 24, "bold"),
                fill="red",
            )

    def loop(self):
        """Game loop using tkinter's after() method for smooth animation."""
        if not self.game_over:
            self.bird.update()
            self.bird.draw()
            self.spawn_counter += 1

            if self.spawn_counter >= self.SPAWN_INTERVAL:
                self.spawn_pipe()
                self.spawn_counter = 0

            self.update_pipes()
            self.check_collision()

        self.root.after(16, self.loop)


if __name__ == "__main__":
    Game()
