from ..models import PatientProfile

class PatientProfileRepository:
    def __init__(self):
        self.model = PatientProfile
    
    def update(self, id, data):
        self.model.objects.filter(id=id).update(**data)
    
    def delete(self, id):
        self.model.objects.filter(id=id).delete()
    
    def get(self, id):
        return self.model.objects.get(id=id)

    def get_all(self):
        return self.model.objects.all()
    
    def get_by_patient(self, patient):
        return self.model.objects.filter(patient=patient).last()
    
    def update_by_patient(self, patient, data):
        self.model.objects.filter(patient=patient).update(**data)