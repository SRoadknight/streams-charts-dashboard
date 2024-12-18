from utils import fetch_weekly_data, create_report 
import argparse



def main():
    parser = argparse.ArgumentParser(description="Generate weekly data CSV.")
    parser.add_argument("year", type=int, help="The year for the data.")
    parser.add_argument("week_number", type=int, help="The week number for the data.")
    parser.add_argument("--overwrite", action='store_true', help="Whether the CSV should be overwritten")

    args = parser.parse_args()

    

    data = fetch_weekly_data(args.year, args.week_number, args.overwrite)
    create_report(data, args.year, args.week_number, args.overwrite)


if __name__ == "__main__":
    main()