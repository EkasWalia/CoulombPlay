import math
import random
import arcade

# --- Simulation parameters ---
FPS = 60
DT = 1 / 60

WIDTH = 1280
HEIGHT = 720
SCREEN_CENTER = arcade.math.Vec2(WIDTH / 2, HEIGHT / 2)

E = 1.0
ME = 0.2
MP = 2.0

K_COULOMB = 5e3       # reduced so motion is stable
FIELD_SCALE = 30000.0


class Particle:
    def __init__(self, pos, vel, mass, charge):
        # pos, vel are Arcade Vec2, pos is relative to screen center
        self.pos = pos + SCREEN_CENTER
        self.vel = vel
        self.mass = mass
        self.charge = charge
        self.radius = math.sqrt(mass) * 20.0


class ElectricSimWindow(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Electric Interaction Sim", update_rate=1 / FPS)
        arcade.set_background_color(arcade.color.WHITE)

        self.view_field = True

        # electrons, proton, alpha
        self.particles = [
            Particle(arcade.math.Vec2(100, -200), arcade.math.Vec2(20, 60), ME, -E),
            Particle(arcade.math.Vec2(-200, -150), arcade.math.Vec2(-40, 60), ME, -E),
            Particle(arcade.math.Vec2(300, 200), arcade.math.Vec2(0, -120), ME, -E),
            Particle(arcade.math.Vec2(150, 40), arcade.math.Vec2(40, 0), MP, E),
            Particle(arcade.math.Vec2(-120, -80), arcade.math.Vec2(-30, 0), 4 * MP, 2 * E),
        ]

    # ------------- physics step -------------
    def on_update(self, delta_time: float):
        for i in range(len(self.particles)):
            f = arcade.math.Vec2(0, 0)
        for j in range(len(self.particles)):
            if i == j:
                continue
            s = self.particles[j].pos - self.particles[i].pos
            dist = max(s.length(), 5.0)
            f += K_COULOMB * self.particles[i].charge * self.particles[j].charge / (dist ** 3) * (-s)

        self.particles[i].vel += f / self.particles[i].mass * DT
        self.particles[i].pos += self.particles[i].vel * DT

        # keep inside window with simple bounce
        pos = self.particles[i].pos

        if pos.x < 0 or pos.x > WIDTH:
            self.particles[i].vel = arcade.math.Vec2(-self.particles[i].vel.x * 0.8,
                                                     self.particles[i].vel.y)
        if pos.y < 0 or pos.y > HEIGHT:
            self.particles[i].vel = arcade.math.Vec2(self.particles[i].vel.x,
                                                     -self.particles[i].vel.y * 0.8)

        # clamp by creating a new Vec2
        clamped_x = min(max(pos.x, 0), WIDTH)
        clamped_y = min(max(pos.y, 0), HEIGHT)
        self.particles[i].pos = arcade.math.Vec2(clamped_x, clamped_y)

    # ------------- keyboard -------------
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.view_field = not self.view_field

        if symbol == arcade.key.R:
            for part in self.particles:
                part.pos = arcade.math.Vec2(
                    (random.random() - 0.5) * 400,
                    (random.random() - 0.5) * 400,
                ) + SCREEN_CENTER
                part.vel = arcade.math.Vec2(
                    (random.random() - 0.5) * 150,
                    (random.random() - 0.5) * 150,
                )

    # ------------- drawing -------------
    def on_draw(self):
        self.clear()  # no start_render / finish_render in Window API

        arcade.draw_text(
            "Space: switch view   R: reset",
            10,
            HEIGHT - 35,
            arcade.color.BLACK,
            18,
        )

        # draw charges
        for part in self.particles:
            intens = part.charge / E * 60.0
            if part.charge > 0:
                color = (min(int(intens), 255), 0, 0, 255)
            else:
                color = (0, 0, min(int(-intens), 255), 255)
            arcade.draw_circle_filled(part.pos.x, part.pos.y, part.radius, color)

        if self.view_field:
            self.draw_vector_field()
        else:
            self.draw_field_lines()

    def draw_vector_field(self):
        freq = 80
        for x in range(freq, WIDTH - freq // 2, freq):
            for y in range(freq, HEIGHT - freq // 2, freq):
                p = arcade.math.Vec2(x, y)
                f = arcade.math.Vec2(0, 0)
                skip = False
                for part in self.particles:
                    s = part.pos - p
                    if s.length() < part.radius:
                        skip = True
                        break
                    dist = max(s.length(), 5.0)
                    f += part.charge / (dist ** 3) * (-s)
                if skip or f.length() == 0:
                    continue

                f_scaled = f * FIELD_SCALE
                end = p + f_scaled
                arcade.draw_line(p.x, p.y, end.x, end.y, arcade.color.BLACK, 1)
                arcade.draw_circle_filled(end.x, end.y, 2, arcade.color.BLACK)

    def draw_field_lines(self):
        for part in self.particles:
            if part.charge <= 0:
                continue
            for x in [-1, -0.5, 0, 0.5, 1]:
                for y in [-1, -0.5, 0, 0.5, 1]:
                    if x == 0 and y == 0:
                        continue
                    direction = arcade.math.Vec2(x, y)
                    if direction.length() == 0:
                        continue

                    p = part.pos + direction.normalize() * (part.radius + 0.1)
                    steps = 0
                    cont = True
                    while cont:
                        f = arcade.math.Vec2(0, 0)
                        for other in self.particles:
                            s = other.pos - p
                            if s.length() < other.radius:
                                cont = False
                            dist = max(s.length(), 5.0)
                            f += other.charge / (dist ** 3) * (-s)
                        if f.length() == 0:
                            break
                        np = p + f.normalize() * 8
                        arcade.draw_line(p.x, p.y, np.x, np.y, arcade.color.BLACK, 1)
                        p = np
                        steps += 1
                        if steps > 150:
                            break


def main():
    ElectricSimWindow()
    arcade.run()


if __name__ == "__main__":
    main()
