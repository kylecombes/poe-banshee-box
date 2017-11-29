from raspi.puzzles.puzzle import BOCSPuzzle
from raspi.arduino_comm import ArduinoCommEventType as EventType
from raspi.available_io import *
from raspi.io_states.rotary_state import RotaryState
from datetime import datetime

class FortyTwo(BOCSPuzzle):

    PUZZLE_ID = 'forty_two!'  # A unique ID (can be anything) to use when reporting puzzle stats to the server

    PROMPT = ""
    scale = 1
    error = 200  # +||- in millisecons
    count1 = 0
    count2 = 0
    w, h = 9, 2;
    input = [[0 for x in range(w)] for y in range(h)]
    # the array of input time values the switch is open and closed for
    model = scale*[1000,1000,1000,1000,3000,1000,3000,3000,3000,3000][1000,1000,1000,1000,1000,3000,1000,1000,1000,1000]
    # the array of model time values to compare the input to
    is_solved = False  # Set this to True when you want the BOCS to progress to the next puzzle

    def __init__(self, old_state_json=None):
        """
        Runs once, when the puzzle is first started.
        :param update_io_state: a callback function to update the state of an I/O device
        :param register_callback: a callback function to register the function that should be called anytime a BOCS
            user input event occurs
        """
        # Perform some standard initialization defined by the BOCSPuzzle base class
        BOCSPuzzle.__init__(self, stat_server, update_io_state)

        # Register our `event_received` function to be called whenever there is a BOCS input event (e.g. key press)
        register_callback(self.user_input_event_received)

        self.rotary_state = RotaryState()
        self.rotary_state.set_mode(RotaryState.TELEGRAPH)
        self.update_io_state(ARDUINO1, self.rotary_state)
        self.last_press_time = datetime.now()

    def user_input_event_received(self, event):
        """
        This function is called whenever the user triggers an input event on the BOCS. The majority of your puzzle logic
        should probably be here (or be in another function called from here), as this will run every time the user does
        something to the box.
        :param event: an object with attributes `id` (which event happened), `data` (what was the primary data
        associated with the event, e.g. which key/number) and `options` (extra data, usually empty)
        """



        if event.id == EventType.TELEGRAPH_BUTTON_PRESS:  # See if the event was a start button press
            duration = event.data  # The amount of time the button was held down for (in ms)
            time_open = ((datetime.now() - self.last_press_time).total_seconds)/1000-duration
            if time_open>scale*(3000+error):
                input = [[0 for x in range(w)] for y in range(h)]
                count1 = 0
            input[count1][0]=duration
            input[count1][1]=time_open
            count1+=1
            self.last_press_time = datetime.now()

            if count1==9:
                for x in range (0,9):
                    for y in range (0,1):
                        if input[x][y]>=model[x][y]-error && input[x][y]<=model[x][y]+error:
                            count2+=1
                #input is complete sweep and compare two arrays
                #increment count2 if input value within model value

            if count2>=18: #arrays match within tolerances
                self.is_solved = True  # Exits this puzzle
                #Yay you solved it
            else:
                #Nope try again
            input=[[0 for x in range(w)] for y in range(h)]
            count1=0