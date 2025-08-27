# your_app/factories.py
import factory
from faker import Faker
from django.contrib.auth import get_user_model
from users.models import Profile
from courses.models import Course, Department

# Get the User model
User = get_user_model()
fake = Faker('th_TH')

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True
    
    username = factory.LazyFunction(lambda: fake.unique.user_name())
    email = factory.LazyFunction(lambda: fake.unique.email())

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted if extracted else '123456789'
        self.set_password(password)
        if create:
            self.save()

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    first_name_th = factory.LazyFunction(lambda: fake.first_name())
    last_name_th = factory.LazyFunction(lambda: fake.last_name())
    user_type = Profile.UserType.STUDENT
    job_title = factory.LazyFunction(lambda: fake.job())

class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
    
    name = factory.LazyFunction(lambda: fake.unique.company())