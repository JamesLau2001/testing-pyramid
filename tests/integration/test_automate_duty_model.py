from models.automate_duty import AutomateDuty
import pytest

@pytest.fixture
def duty_instance():
    return AutomateDuty("Duty Number", "Duty Description", "Duty KSBs")

def test_save_function_is_done_correctly(duty_instance):
    assert duty_instance.save() == "Duty saved"

def test_duty_is_created(duty_instance):
    assert duty_instance.number == duty_instance.create_duty().number
    assert duty_instance.description == duty_instance.create_duty().description
    assert duty_instance.ksbs == duty_instance.create_duty().ksbs
    assert duty_instance.complete == duty_instance.create_duty().complete

def test_duty_mark_complete_is_successful(duty_instance):
    duty_instance.mark_complete()
    assert duty_instance.complete == True

def test_duty_complete_status_message_is_correct(duty_instance):
    assert duty_instance.complete_status() == "Duty is complete"