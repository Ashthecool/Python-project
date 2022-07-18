"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""
import random
import time

import arcade
import arcade.sound
import self as self

SPRITE_SCALING = 0.5
self.check = None
# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Variables controlling the player
PLAYER_LIVES = 3
PLAYER_SPEED_X = 5
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = 50
PLAYER_SHOT_SPEED = 4
ITEM_SPEED = -3
ITEM_GENERATE_COUNT = 1

FIRE_KEY = arcade.key.SPACE
slot_sound = arcade.load_sound("Sounds/Pew.wav")
collect_sound = arcade.load_sound("Sounds/Coin.wav")
power_up_sound = arcade.load_sound("Sounds/Win.wav")
charging = arcade.load_sound("Sounds/Charging....wav")
boom = arcade.load_sound("Sounds/BOOM!.wav")


class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, **kwargs):
        """
        Setup new Player object
        """

        # Graphics to use for Player
        kwargs['filename'] = "images/playerShip1_red.png"

        # How much to scale the graphics
        kwargs['scale'] = SPRITE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

        self.draw_hit_box()

    def update(self):
        """
        Move the sprite
        """

        # Update center_x
        self.center_x += self.change_x

        # Don't let the player move off-screen
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1


class PlayerShot(arcade.Sprite):
    """
    A shot fired by the Player
    """

    def __init__(self, center_x=0, center_y
    =0):
        """
        Setup new PlayerShot object
        """

        # Set the graphics to use for the bullets.
        graphics = [
            "images/Lasers/laserBlue01.png",
            "images/Lasers/laserRed01.png",
            "images/Lasers/laserGreen11.png"
        ]

        super().__init__(random.choice(graphics), SPRITE_SCALING)

        self.center_x = center_x
        self.center_y = center_y
        self.change_y = PLAYER_SHOT_SPEED

    def update(self):
        """
            Move the sprite
            """

        # Update y position

        self.center_x = self.center_x
        self.center_y += self.change_y
        self.change_y += 0.2

        # Remove shot when over top of screen
        if self.bottom > SCREEN_HEIGHT:
            self.kill()


class Items(arcade.Sprite):
    def __init__(self, center_x=0, center_y=150):
        stars = [
            "images/Power-ups/star_bronze.png",
            "images/Power-ups/star_silver.png",
            "images/Power-ups/star_gold.png"
        ]

        super().__init__(random.choice(stars), SPRITE_SCALING)

        self.center_x = center_x
        self.center_y = center_y
        self.angle = 90
        self.change_y = ITEM_SPEED
        self.change_angle = 4

    def update(self):
        # Update Y placement
        self.center_y += self.change_y
        self.angle += self.change_angle

        if self.center_y < -SCREEN_HEIGHT:
            self.kill()


class PowerUps(arcade.Sprite):
    def __init__(self, center_x=0, center_y=250):
        costume = random.randint(1, 3)

        if costume == 1:
            name = "images/Power-ups/bolt_gold.png"
        elif costume == 2:
            name = "images/Power-ups/bold_silver.png"
        else:
            name = "images/Power-ups/bolt_bronze.png"

        super().__init__(name, SPRITE_SCALING)

        self.center_x = center_x
        self.center_y = center_y
        self.change_y = ITEM_SPEED * 3

    def update(self):

        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.center_y < -SCREEN_HEIGHT:
            self.kill()


class ChargeShot(arcade.Sprite):
    """
    The special charge shot.
    """

    def __init__(self, center_x=0, center_y=0):
        super().__init__(filename="images/Lasers/beams.png")

        self.center_x = center_x
        self.center_y = center_y
        self.change_y = PLAYER_SHOT_SPEED * 3

    def update(self):
        # Update Y placement
        self.center_y += self.change_y
        self.change_y += 0.3

        if self.center_y > SCREEN_HEIGHT:
            self.kill()


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height)

        # Variable that will hold a list of shots fired by the player
        self.cooldown = 0
        self.boom = None
        self.charging = None
        self.power = "Normal"
        self.shoot_mode = None
        self.power_up_list_effects = None
        self.player_power_up_sound = None
        self.player_collect_sound = None
        self.item_sprite_list = None
        self.space_pressed = None
        self.player_shot_list = None
        self.player_shot_sound = None
        self.power_up_sprite_list = None
        self.charge_shot_list = None

        # Set up the player info
        self.player_sprite = None
        self.player_score = None
        self.player_lives = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

            # self.joystick.
        # Set the background color
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # No points when the game starts
        self.player_score = 0

        # No of lives
        self.player_lives = PLAYER_LIVES

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()
        self.player_sprite = arcade.SpriteList()
        self.item_sprite_list = arcade.SpriteList()
        self.power_up_sprite_list = arcade.SpriteList()
        self.charge_shot_list = arcade.SpriteList()

        # Shooting Sound
        self.player_shot_sound = arcade.Sound("Sounds/Pew.wav")
        self.player_collect_sound = arcade.Sound("Sounds/Coin.wav")
        self.player_power_up_sound = arcade.Sound("Sounds/Win.wav")
        self.charging = arcade.Sound("Sounds/Charging....wav")
        self.boom = arcade.Sound("Sounds/BOOM!.wav")

        # Create a Player object
        self.player_sprite = Player(
            center_x=PLAYER_START_X,
            center_y=PLAYER_START_Y
        )

        for l in range(ITEM_GENERATE_COUNT):
            new_item = Items(
                center_x=random.randrange(SCREEN_WIDTH),
                center_y=SCREEN_HEIGHT
            )
            self.item_sprite_list.append(new_item)

        self.power_up_list_effects = [
            "charge",
            "reload",
            "double"
        ]

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the player shot
        self.player_shot_list.draw()

        # Draw the player sprite
        self.player_sprite.draw()

        # Draw the falling Items
        self.item_sprite_list.draw()

        # Draw players score on screen
        arcade.draw_text(
            "SCORE: {}".format(self.player_score),  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 20,  # Y position
            arcade.color.WHITE  # Color of text
        )

        self.power_up_sprite_list.draw()
        self.charge_shot_list.draw()

        arcade.draw_text(
            "MODE: {}".format(self.power),  # Text to show
            350,  # X position
            SCREEN_HEIGHT - 20,  # Y position
            arcade.color.WHITE  # Color of text
        )

        arcade.draw_text(
            "COOLDOWN: {}".format(self.cooldown),  # Text to show
            650,  # X position
            SCREEN_HEIGHT - 20,  # Y position
            arcade.color.WHITE  # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Calculate player speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Move player with keyboard
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_SPEED_X
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_SPEED_X

        # Move player with joystick if present
        if self.joystick:
            self.player_sprite.change_x = round(self.joystick.x) * PLAYER_SPEED_X

        # Update player sprite
        self.player_sprite.update()

        # Update the player shots
        self.player_shot_list.update()

        # Update the Items
        self.item_sprite_list.update()

        new_star = Items(
            center_x=random.randrange(SCREEN_WIDTH),
            center_y=SCREEN_HEIGHT
        )
        if random.randint(1, 10) == 3:
            self.item_sprite_list.append(new_star)

        # Check for collision with stars and spaceship.
        star_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.item_sprite_list)

        for stars in star_hit_list:
            stars.remove_from_sprite_lists()
            self.player_collect_sound.play()
            self.player_score += 10

        self.power_up_sprite_list.update()

        new_power_up = PowerUps(
            center_x=random.randrange(SCREEN_WIDTH),
            center_y=SCREEN_HEIGHT
        )

        new_shot = PlayerShot(
            center_x=self.player_sprite.center_x,
            center_y=self.player_sprite.center_y
        )

        if self.power == "reload":
            if random.randint(1, 30) == 3:
                self.player_shot_list.append(new_shot)
                self.player_shot_sound.play()

        if random.randint(1, 100) == 7:
            self.power_up_sprite_list.append(new_power_up)
        power_up_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.power_up_sprite_list)

        for hits in power_up_hit_list:
            self.power = random.choice(self.power_up_list_effects)
            hits.remove_from_sprite_lists()
            self.player_power_up_sound.play()
            self.player_score += 30
            if self.power == "charge":
                self.shoot_mode = "charge"
            elif self.power == "reload":
                self.shoot_mode = "reload"
            elif self.power == "double":
                self.shoot_mode = "double"

        self.charge_shot_list.update()

        if self.cooldown > 0:
            if random.randint(1, 25) == 1:
                self.cooldown -= 1

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # Track state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.space_pressed = True

        if key == FIRE_KEY:
            if self.power != "charge" and self.power != "double":
                new_shot = PlayerShot(
                    self.player_sprite.center_x,
                    self.player_sprite.center_y,
                )

                self.player_shot_list.append(new_shot)
                self.player_shot_sound.play()

            elif self.power == "double":

                new_shot1 = PlayerShot(
                    self.player_sprite.center_x + 7,
                    self.player_sprite.center_y,
                )
                new_shot2 = PlayerShot(
                    self.player_sprite.center_x - 7,
                    self.player_sprite.center_y,
                )
                self.player_shot_list.append(new_shot1)
                self.player_shot_sound.play()
                self.player_shot_list.append(new_shot2)
                self.player_shot_sound.play()

            else:
                if self.cooldown == 0:
                    self.charging.play()

    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.SPACE:
            self.space_pressed = False

        if key == FIRE_KEY and self.power == "charge" and self.cooldown == 0:
            charge_shot = ChargeShot(
                self.player_sprite.center_x,
                self.player_sprite.center_y,
            )
            self.charge_shot_list.append(charge_shot)
            self.boom.play()
            self.cooldown = 5

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(FIRE_KEY, [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


def main():
    """
    Main method
    """

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
