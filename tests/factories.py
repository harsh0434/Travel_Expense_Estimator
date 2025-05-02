import factory
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

class UserFactory(factory.Factory):
    class Meta:
        model = dict

    email = factory.LazyFunction(fake.email)
    password = factory.LazyFunction(lambda: fake.password(length=12))
    display_name = factory.LazyFunction(fake.name)
    created_at = factory.LazyFunction(datetime.now)
    last_login = factory.LazyFunction(datetime.now)

class TravelDataFactory(factory.Factory):
    class Meta:
        model = dict

    destination = factory.LazyFunction(fake.city)
    duration = factory.LazyFunction(lambda: fake.random_int(min=1, max=30))
    travelers = factory.LazyFunction(lambda: fake.random_int(min=1, max=10))
    accommodation = factory.LazyFunction(lambda: fake.random_element(elements=('budget', 'mid-range', 'luxury')))
    activities = factory.LazyFunction(lambda: fake.random_elements(
        elements=('sightseeing', 'dining', 'shopping', 'adventure', 'relaxation', 'cultural'),
        length=fake.random_int(min=1, max=4)
    ))
    transportation = factory.LazyFunction(lambda: fake.random_element(
        elements=('public', 'rental', 'taxi', 'private')
    ))

class TravelHistoryFactory(factory.Factory):
    class Meta:
        model = dict

    user_id = factory.Sequence(lambda n: f'user_{n}')
    destination = factory.LazyFunction(fake.city)
    duration = factory.LazyFunction(lambda: fake.random_int(min=1, max=30))
    travelers = factory.LazyFunction(lambda: fake.random_int(min=1, max=10))
    accommodation = factory.LazyFunction(lambda: fake.random_element(elements=('budget', 'mid-range', 'luxury')))
    total_cost = factory.LazyFunction(lambda: round(fake.random_number(digits=4, fix_len=True), 2))
    created_at = factory.LazyFunction(datetime.now)
    travel_date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=fake.random_int(min=7, max=180)))
    status = factory.LazyFunction(lambda: fake.random_element(elements=('planned', 'completed', 'cancelled')))
    
    @factory.lazy_attribute
    def cost_breakdown(self):
        total = self.total_cost
        accommodation = round(total * 0.4, 2)
        transportation = round(total * 0.2, 2)
        food = round(total * 0.2, 2)
        activities = round(total * 0.15, 2)
        misc = round(total - (accommodation + transportation + food + activities), 2)
        
        return {
            'accommodation': accommodation,
            'transportation': transportation,
            'food': food,
            'activities': activities,
            'miscellaneous': misc
        }

class EstimateRequestFactory(factory.Factory):
    class Meta:
        model = dict

    destination = factory.LazyFunction(fake.city)
    duration = factory.LazyFunction(lambda: fake.random_int(min=1, max=30))
    travelers = factory.LazyFunction(lambda: fake.random_int(min=1, max=10))
    accommodation = factory.LazyFunction(lambda: fake.random_element(elements=('budget', 'mid-range', 'luxury')))
    travel_date = factory.LazyFunction(lambda: (datetime.now() + timedelta(days=fake.random_int(min=7, max=180))).strftime('%Y-%m-%d'))
    activities = factory.LazyFunction(lambda: fake.random_elements(
        elements=('sightseeing', 'dining', 'shopping', 'adventure', 'relaxation', 'cultural'),
        length=fake.random_int(min=1, max=4)
    ))

class FirebaseUserFactory(factory.Factory):
    class Meta:
        model = dict

    uid = factory.Sequence(lambda n: f'firebase_user_{n}')
    email = factory.LazyFunction(fake.email)
    email_verified = factory.LazyFunction(fake.boolean)
    display_name = factory.LazyFunction(fake.name)
    photo_url = factory.LazyFunction(fake.image_url)
    disabled = False
    metadata = factory.LazyAttribute(lambda _: {
        'creation_timestamp': fake.unix_time(),
        'last_sign_in_timestamp': fake.unix_time()
    })
    custom_claims = factory.LazyAttribute(lambda _: {
        'premium_user': fake.boolean(),
        'last_login': fake.iso8601()
    }) 