from raspi.puzzles.puzzle import BOCSPuzzle
from raspi.arduino_comm import ArduinoCommEventType as EventType
from raspi.io_states.keypad_state import KeypadState
from raspi.available_io import *


class SevenEightNinePuzzle(BOCSPuzzle):

    PUZZLE_ID = '789 PUZZLE'  # Used by stat server

    PROMPT = "jul jnf fvk nsenvq bs frira?"
    LINE_2_PREFIX = "Input: "
    guess = ""
    ANSWER = "789"

    def __init__(self, init_bundle, register_callback):
        """
        Runs once, when the puzzle is first started.
        :param update_io_state: a callback function to update the state of an I/O device
        :param register_callback: a callback function to register the function that should be called anytime a BOCS
            user input event occurs
        """
        # Perform some standard initialization defined by the BOCSPuzzle base class
        BOCSPuzzle.__init__(self, init_bundle)

        # Register our `event_received` function to be called whenever there is a BOCS input event (e.g. key press)
        register_callback(self.user_input_event_received)

        # Show the keypad
        self.keypad_state = KeypadState(visible=True)
        self.update_io_state(ARDUINO1, self.keypad_state)

        # Display the prompt on the display
        self.eink.set_text('{}\n\n{}'.format(self.PROMPT, self.LINE_2_PREFIX))

        # Play the prompt audio
        self.play_sound('789Riddle.m4a')

    def user_input_event_received(self, event):
        """
        This function is called whenever the user triggers an input event on the BOCS. The majority of your puzzle logic
        should probably be here (or be in another function called from here), as this will run every time the user does
        something to the box.
        :param event: an object with attributes `id` (which event happened), `data` (what was the primary data
        associated with the event, e.g. which key/number) and `options` (extra data, usually empty)
        """

        if event.id == EventType.NUMERIC_KEYPAD_PRESS:  # See if the event was a start button press
            key = event.data
            if key == '#':
                if self.guess == self.ANSWER:
                    self.eink.set_text('Correct!')
                    self.report_attempt(self.PUZZLE_ID)
                    self.keypad_state.set_visible(False)
                    self.update_io_state(ARDUINO1, self.keypad_state)
                    self.is_solved = True
                else:
                    self.report_attempt(self.PUZZLE_ID, self.guess)
                    self.eink.set_text("Sorry, that's incorrect!")
                    self.pause(3)
                    self.eink.set_text(self.PROMPT)

            else:
                if key == '*':  # Backspace
                    self.guess = self.guess[0:-1]
                else:  # Digit entry
                    self.guess += str(key)

                self.eink.set_text('{}\n\n{} {}'.format(self.PROMPT, self.LINE_2_PREFIX, self.guess))
