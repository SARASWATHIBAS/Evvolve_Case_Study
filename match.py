import pandas as pd

def calculate_fund_match_score(investor_funds, startup_deal):
    """
    Calculate a fund match score out of 100 based on how close the available funds are to the deal size
    """
    if investor_funds >= startup_deal:
        # Perfect score (100) if funds are within 150% of deal size
        if investor_funds <= startup_deal * 1.5:
            return 100
        # 80 points if funds are within 200% of deal size
        elif investor_funds <= startup_deal * 2:
            return 80
        # 60 points if funds are within 300% of deal size
        elif investor_funds <= startup_deal * 3:
            return 60
        # 40 points for any larger amount
        else:
            return 40
    else:
        # 50 points if investor has at least 75% of required funds
        if investor_funds >= startup_deal * 0.75:
            return 50
        # 25 points if investor has at least 50% of required funds
        elif investor_funds >= startup_deal * 0.5:
            return 25
        # 0 points if less than 50% of required funds
        return 0

def Risk_appetite_score(investor, startup):
    """
    Calculate a match score between an investor and a startup based on risk appetite.
    """
    score = 0

    # Risk appetite match
    if investor.get('Risk_Appetite') == startup.get('Risk_Assessment'):
        score += 100
    elif investor.get('Risk_Appetite') == 'High' and startup.get('Risk_Assessment') == 'Medium':
        score += 50
    elif investor.get('Risk_Appetite') == 'Medium' and startup.get('Risk_Assessment') == 'Low':
        score += 50
    elif investor.get('Risk_Appetite') == 'High' and startup.get('Risk_Assessment') == 'Low':
        score += 25
    elif investor.get('Risk_Appetite') == 'Low' and startup.get('Risk_Assessment') == 'Medium':
        score += 50
    elif investor.get('Risk_Appetite') == 'Medium' and startup.get('Risk_Assessment') == 'High':
        score += 50
    elif investor.get('Risk_Appetite') == 'Low' and startup.get('Risk_Assessment') == 'High':
        score += 25
    return score


def calculate_match_score(investor, startup, weights):
    """
    Calculate a match score between an investor and a startup based on weights.
    """
    score = 0

    # Domain match
    if investor.get('Domain') == startup.get('Domain'):
        score += weights['domain_match']

    # Fund availability match
    score += (weights['fund_match'] * (calculate_fund_match_score(
        investor.get('Fund_Available', 0),
        startup.get('Deal', 0))
    )/100)

    # Risk appetite match
    score += (weights['risk_match'] * Risk_appetite_score(investor, startup))/100
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
