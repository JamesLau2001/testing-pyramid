import unittest
from morelia import run, verify
from models.automate_duty import AutomateDuty

class AutomateDutyTestCase(unittest.TestCase):
    duty = AutomateDuty("Random Number", "Random Description", "Random KSB")
    def test_duty_save_behaviour(self):
        verify('tests/automate_duty.feature', self)
    
    def step_I_save_a_duty(self):
        r'I save a duty'      
        self.duty.save()
  
    def step_the_result_should_be_duty_saved_on_the_display(self):
        r'the result should be \'Duty saved\' on the display'
        self.assertEqual(self.duty.save(), 'Duty saved')

