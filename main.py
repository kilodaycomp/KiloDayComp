import os
import pandas as pd
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Any
from constants import START_DATE, END_DATE, INCREMENT_PERCENT, INITIAL_VALUE, DATA_FILE_PATH

# Set up logging
def setup_logging() -> None:
    """Configure logging to both file and console"""
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/log.log"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_formatter = logging.Formatter('%(message)s')
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# Initialize logger
logger = setup_logging()

# Calculate total weekdays between START_DATE and END_DATE
TOTAL_DAYS = sum(1 for day in range((END_DATE - START_DATE).days + 1) if (START_DATE + timedelta(days=day)).weekday() < 5)
TODAY = datetime.now().strftime("%Y-%m-%d")

def _get_current_time() -> str:
    """get current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Generate data
def generate_audit_report() -> None:
    logger.info("Starting audit report generation")
    os.makedirs("data", exist_ok=True)
    if "audit_data.csv" in os.listdir("data/"):
        logger.warning("audit_data.csv already exists")
        if input("Do you want to reset it? (y/n): ") != "y":
            logger.info("Exiting program")
            return
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.rename(DATA_FILE_PATH, f"{DATA_FILE_PATH}_{timestamp}.csv")
        logger.info(f"Backup of old file created: {DATA_FILE_PATH}_{timestamp}.csv")

    data: List[List[Any]] = [[TODAY, 0, TOTAL_DAYS, INCREMENT_PERCENT, '-', f"{INITIAL_VALUE:_.2f}", '-', '-', '-']]
    total = INITIAL_VALUE
    actual_day_count = 0  # Counter for actual days added to the report

    for day in range(1, (END_DATE - START_DATE).days + 1):
        date = START_DATE + timedelta(days=day)
        if date.weekday() < 5:  # 0-4 are Monday to Friday
            actual_day_count += 1  # Increment the actual day count
            increment = total * INCREMENT_PERCENT
            total += increment
            data.append([
                date.strftime("%Y-%m-%d"),
                actual_day_count,  # Use the actual day count
                f"{TOTAL_DAYS - actual_day_count}",
                f"{INCREMENT_PERCENT}",
                f"{increment:_.2f}",
                f"{total:_.2f}",
                "-",
                "-",
                "-",
            ])
    
    df = pd.DataFrame(
        data,
        columns=[
            "date",
            "day",
            "remaining_days",
            "increment_percent",
            "increment_value",
            "projected_balance",
            "actual_balance",
            "difference",  # difference between actual and projected_balance
            "difference_percent",  # percentage difference from projected balance
        ],
    )
    # Save to CSV file
    df.to_csv(DATA_FILE_PATH, index=False)
    logger.info(f"Audit report generation completed, file: {DATA_FILE_PATH}")


def _input_balance() -> float:
    """
    Input the balance on the current day.
    it can be 1,999,255 or 1_999_255
    """
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            user_input = input(f"Enter the balance on {TODAY}: ").strip()
            if not user_input:
                logger.warning("Input cannot be empty. Please enter a valid amount.")
                continue
            input_balance = float(user_input.replace(",", "").replace("_", ""))
            if input_balance < 0:
                logger.warning("Balance cannot be negative. Please enter a valid amount.")
                continue
            return input_balance
        except ValueError:
            remaining_attempts = max_attempts - attempt - 1
            if remaining_attempts > 0:
                logger.warning(f"Invalid input. Please enter a valid amount. {remaining_attempts} attempts remaining.")
            else:
                logger.error("Exiting program, invalid input 3 times")
                exit()


def update_today_balance() -> None:
    input_balance = _input_balance()
    df = pd.read_csv("data/audit_data.csv")
    df.loc[df["date"] == TODAY, "actual_balance"] = f"{input_balance:_.2f}"
    # Calculate and update difference
    today_row = df.loc[df["date"] == TODAY]
    if not today_row.empty:
        projected = float(today_row["projected_balance"].iloc[0].replace("_", ""))
        difference = input_balance - projected
        df.loc[df["date"] == TODAY, "difference"] = f"{difference:_.2f}"
        # Calculate and update difference percentage
        difference_percent = (difference / projected) * 100
        df.loc[df["date"] == TODAY, "difference_percent"] = f"{difference_percent:.2f}%"

    df.to_csv("data/audit_data.csv", index=False)
    logger.info(f"Today's ({TODAY}) balance updated to {input_balance:_.2f}")
    logger.info(f"Difference from projected: {difference:_.2f} ({difference_percent:.2f}%)")


def main():
    parser = argparse.ArgumentParser(description="Compound Growth Demo")
    parser.add_argument("--generate", action="store_true", help="Generate audit report")
    parser.add_argument("--update", action="store_true", help="Update today's balance")
    args = parser.parse_args()
    logger.info(f"{' Program started ':*^80}")
    if args.generate:
        generate_audit_report()
    elif args.update:
        update_today_balance()
    else:
        logger.warning(
            "No arguments provided. Please use --generate or --update, or "
            "check justfile for available commands"
        )
    logger.info(f"{' Program ended ':-^80}\n")


if __name__ == "__main__":
    main()
