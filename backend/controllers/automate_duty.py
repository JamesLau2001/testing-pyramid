from models.automate_duty import AutomateDuty

class AutomateDutyController:
    @staticmethod
    def create_duties(number, description, ksbs):
        duty = AutomateDuty(number, description, ksbs)
        duty.save()
        duty.mark_complete()
        duty.complete_status()
        return duty

