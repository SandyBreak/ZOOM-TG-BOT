# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
     
    
class ControlPanelStates(StatesGroup):
    enter_pass = State()
    
    launch_newsletter = State()
    
    launch_targeted_newsletter = State()