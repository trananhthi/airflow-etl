import datetime
import os

from faker import Faker
import random
import pandas as pd
from faker.providers import DynamicProvider

us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California",
    "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

gender_provider = DynamicProvider(
    provider_name="gender",
    elements=["male", "female"],
)

fake = Faker()
fake.add_provider(gender_provider)


def generate_fake_dataset_idcard(num_records):
    dataset = []
    for _ in range(num_records):
        record = {
            'id card': fake.uuid4(),
            'name': fake.name(),
            'gender': fake.gender(),
            'state': random.randint(1, 50),
            'birth_year': random.randint(1980, 2020),
            'position': fake.job()
        }
        dataset.append(record)
    return dataset


def generate_fake_dataset_states():
    dataset = []
    for _ in range(len(us_states)):
        record = {
            'id': _ + 1,
            'state': us_states[_]
        }
        dataset.append(record)
    return dataset


# Số lượng bản ghi bạn muốn tạo
num_records = 1000

# folder lưu
current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
current_directory = os.path.dirname(__file__)

# Tạo generate-dataset giả
fake_dataset_CMND = generate_fake_dataset_idcard(num_records)
fake_dataset_provinces = generate_fake_dataset_states()
df_CMND = pd.DataFrame(fake_dataset_CMND)
df_provinces = pd.DataFrame(fake_dataset_provinces)

df_CMND.to_excel(os.path.join(current_directory, f'dataset\\fake_dataset_card_{current_datetime}.xlsx'), index=False)
df_provinces.to_excel(os.path.join(current_directory, f'dataset\\fake_dataset_state_{current_datetime}.xlsx'), index=False)
print("success")
