from controllers.automate_duty import AutomateDutyController
import pytest

@pytest.fixture
def duty_instance():
    return AutomateDutyController()

def test_create_duty_function_in_controller_calls_save_function_in_model(duty_instance, mocker):
    mock_save = mocker.patch('models.automate_duty.AutomateDuty.save', return_value="Duty saved")
    duty_instance.create_duties("Number","Descripton","KSBs")
    assert mock_save.call_count == 1

def test_create_duty_function_in_controller_calls_mark_complete_function_in_model(duty_instance, mocker):
    mock_complete = mocker.patch('models.automate_duty.AutomateDuty.mark_complete')
    duty_instance.create_duties("Number","Descripton","KSBs")
    assert mock_complete.call_count == 1

def test_create_duty_function_in_controller_calls_complete_status_function_in_model(duty_instance, mocker):
    mock_complete_status = mocker.patch('models.automate_duty.AutomateDuty.complete_status', return_value = "Duty is complete")
    duty_instance.create_duties("Number","Descripton","KSBs")
    assert mock_complete_status.call_count == 1