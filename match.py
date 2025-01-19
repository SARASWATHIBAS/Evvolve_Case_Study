import pandas as pd


def calculate_match_score(investor, startup, weights):
    """
    Calculate a match score between an investor and a startup based on weights.
    """
    score = 0

    # Domain match
    if investor.get('Domain') == startup.get('Domain'):
        score += weights['domain_match']

    # Fund availability match
    if investor.get('Fund_Available', 0) >= startup.get('Deal', 0):
        score += weights['fund_match']

    # Risk appetite match
    if investor.get('Risk_Appetite') == startup.get('Risk_Assessment'):
        score += weights['risk_match']

    return score


def find_matches(investors, startups, weights, match_threshold=100):
    """
    Find matches between investors and startups based on a scoring system.
    """
    matches = []

    for _, investor in investors.iterrows():
        for _, startup in startups.iterrows():
            score = calculate_match_score(investor, startup, weights)
            compatibility = (
                "High Compatibility"
                if score >= match_threshold
                else "Medium Compatibility"
                if score >= match_threshold * 0.75
                else "Low Compatibility"
            )
            matches.append({
                "Investor": investor.get('Investor_Group_Name', 'Unknown'),
                "Startup": startup.get('Company_Name', 'Unknown'),
                "Compatibility": compatibility,
                "Score": score
            })

    return pd.DataFrame(matches)


def main(investors_file, startups_file, output_file, weights, match_threshold):
    """
    Main function to process matchmaking between investors and startups.
    """
    # Load data
    investors = pd.read_csv(investors_file)
    startups = pd.read_csv(startups_file)

    # Find matches
    results = find_matches(investors, startups, weights, match_threshold)

    # Sort results by score in descending order
    results_sorted = results.sort_values('Score', ascending=False)

    # Display top matches
    print("High Compatibility Matches:")
    print(results_sorted[results_sorted['Compatibility'] == 'High Compatibility'])

    # Save results to CSV
    results_sorted.to_csv(output_file, index=False)
    print(f"Matchmaking results saved to {output_file}")


if __name__ == "__main__":
    # Define default weights for scoring
    weights = {
        "domain_match": 40,
        "fund_match": 30,
        "risk_match": 30
    }

    # File paths and settings
    investors_file = "investors.csv"
    startups_file = "startups.csv"
    output_file = "matchmaking_results.csv"
    match_threshold = 70  # Threshold for high compatibility

    # Run the matchmaking process
    main(investors_file, startups_file, output_file, weights, match_threshold)
