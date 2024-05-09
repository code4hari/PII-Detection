from faker import Faker
import pandas as pd

fake = Faker()

data = []
for _ in range(100):  # Generate 100 rows
    data.append({
        "user": fake.name(),
        "phone_number": fake.phone_number(),
        "email": fake.email(),
        "address": fake.address(),
        "ssn": fake.ssn(),
    })

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv("sample_data.csv", index=False)
