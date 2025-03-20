from datetime import datetime, timedelta

# Initialize variables
START_DATE = datetime(2025, 3, 20)  # First day of the audit
END_DATE = datetime(2029, 1, 20)  # End day of the audit

INITIAL_VALUE = 1_250_361.00  # First day's value
INCREMENT_PERCENT = 0.0051  # 0.51%

DATA_FILE_PATH = "data/audit_data.csv"
