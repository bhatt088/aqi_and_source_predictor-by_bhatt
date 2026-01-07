import pandas as pd

df = pd.read_csv(r"C:\Users\Himanshu Bhatt\Desktop\code\ML project\AQI and source predictor\aqi_clean.csv")
print(df.head())

# Remove rows with missing values
df = df.dropna()

print(df.isnull().sum())

df = df.drop(['City', 'Station', 'Date'], axis=1)

def calculate_aqi(row):
    sub_indices = []

    if not pd.isna(row['PM2.5']):
        sub_indices.append(row['PM2.5'] * 1.5)

    if not pd.isna(row['PM10']):
        sub_indices.append(row['PM10'] * 0.7)

    if not pd.isna(row['NO2']):
        sub_indices.append(row['NO2'] * 1.2)

    if not pd.isna(row['SO2']):
        sub_indices.append(row['SO2'] * 1.0)

    if not pd.isna(row['CO']):
        sub_indices.append(row['CO'] * 10)

    if not pd.isna(row['OZONE']):
        sub_indices.append(row['OZONE'] * 0.8)

    if not pd.isna(row['NH3']):
        sub_indices.append(row['NH3'] * 0.6)

    return max(sub_indices)

df['AQI'] = df.apply(calculate_aqi, axis=1)
X = df[['PM2.5', 'PM10', 'SO2', 'CO', 'OZONE', 'NO2', 'NH3']]
y = df['AQI']

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
from sklearn.ensemble import RandomForestRegressor

aqi_model = RandomForestRegressor()
aqi_model.fit(X_train, y_train)


from sklearn.metrics import mean_absolute_error

predictions = aqi_model.predict(X_test)
error = mean_absolute_error(y_test, predictions)

print("Average AQI Error:", error)

def pollution_source(row):
    if row['NO2'] > 70 and row['CO'] > 1:
        return "Vehicle"
    elif row['SO2'] > 40:
        return "Industry"
    elif row['PM10'] > 200:
        return "Dust"
    elif row['PM2.5'] > 150:
        return "Burning"
    else:
        return "Mixed"

df['Source'] = df.apply(pollution_source, axis=1)


new_data = pd.DataFrame([{
    'PM2.5': 120,
    'PM10': 220,
    'SO2': 20,
    'CO': 1.2,
    'OZONE': 30,
    'NO2': 80,
    'NH3': 25
}])

predicted_aqi = aqi_model.predict(new_data)
print("Predicted AQI:", predicted_aqi[0])

import joblib

joblib.dump(aqi_model, "aqi_model.pkl")
