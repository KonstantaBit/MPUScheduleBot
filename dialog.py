from transitions import Machine


class Dialog:
    states = ['disabled', 'menu', 'recv_timetable', 'recv_session_timetable']

    def __init__(self):
        self.machine = Machine(model=self, states=Dialog.states, initial="disabled")
        self.machine.add_transition('started', 'disabled', 'menu')
        self.machine.add_transition('to_menu', '*', 'menu')
        self.machine.add_transition('get_timetable', 'menu', 'recv_timetable')
        self.machine.add_transition('get_session_timetable', 'menu', 'recv_session_timetable')
