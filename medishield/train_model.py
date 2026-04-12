import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# LOAD DATASET (LOW MEMORY FIX)
df = pd.read_csv("medicine_dataset.csv", low_memory=False)
df.columns = df.columns.str.strip()

# FIND SIDE EFFECT COLUMNS
side_cols = [col for col in df.columns if "sideEffect" in col]

data = []

# LIMIT DATA SIZE (IMPORTANT 🚨)
MAX_ROWS = 248218   # reduce load

for idx, row in df.iterrows():

    if idx > MAX_ROWS:
        break

    drug = str(row["name"]).lower().strip()

    for col in side_cols:
        effect = row[col]

        if pd.isna(effect):
            continue

        effect = str(effect).lower().strip()
        data.append([drug, effect])

# CREATE DATAFRAME
new_df = pd.DataFrame(data, columns=["drug", "side_effect"])

# ENCODE
le_drug = LabelEncoder()
le_side = LabelEncoder()

new_df["drug"] = le_drug.fit_transform(new_df["drug"])
new_df["side_effect"] = le_side.fit_transform(new_df["side_effect"])

X = new_df[["drug"]]
y = new_df["side_effect"]

# LIGHTWEIGHT MODEL (IMPORTANT 🚨)
model = RandomForestClassifier(
    n_estimators=20,   # ↓ reduced from 100
    max_depth=10       # ↓ prevents memory explosion
)

model.fit(X, y)

# SAVE
joblib.dump(model, "model.pkl", compress=3)
joblib.dump(le_drug, "le_drug.pkl")
joblib.dump(le_side, "le_side.pkl")

print("✅ Model trained successfully (optimized)")
