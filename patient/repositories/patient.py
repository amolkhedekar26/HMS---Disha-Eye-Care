from ..models import Patient


class PatientRepository:
    def __init__(self):
        self.model = Patient

    def create(self, data):
        if self.model.objects.filter(phone_no=data['phone_no']).exists():
            return self.model.objects.get(phone_no=data['phone_no'])
        else:
            return self.model.objects.create(**data)

    def update(self, id, data):
        self.model.objects.filter(id=id).update(**data)

    def delete(self, id):
        self.model.objects.filter(id=id).delete()

    def get(self, id):
        return self.model.objects.get(id=id)

    def get_all(self):
        return self.model.objects.all()

    def get_by_phone_no(self, phone_no):
        return self.model.objects.filter(phone_no=phone_no).last()
