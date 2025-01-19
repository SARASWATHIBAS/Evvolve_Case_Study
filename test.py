import pandas as pd


def calculate_match_score(investor, startup):
    score = 0

    # Domain match
    if investor['Domain'] == startup['Domain']:
        score += 40

    # Fund availability
    if investor['Fund_Available'] >= startup['Deal']:
        score += 30

    # Risk appetite match
    if investor['Risk_Appetite'] == startup['Risk_Assessment']:
        score += 30

    return score


def find_matches(investors, startups):
    matches = []

    for _, investor in investors.iterrows():
        for _, startup in startups.iterrows():
            score = calculate_match_score(investor, startup)
            if score >= 100:  # Perfect match threshold
                matches.append({
                    "Investor": investor['Investor_Group_Name'],
                    "Startup": startup['Company_Name'],
                    "Compatible": "Yes",
                    "Score": score
                })
            else:
                matches.append({
                    "Investor": investor['Investor_Group_Name'],
                    "Startup": startup['Company_Name'],
                    "Compatible": "No",
                    "Score": score
                })

    return pd.DataFrame(matches)


# Load data
investors = pd.read_csv("investors.csv")
startups = pd.read_csv("startups.csv")

# Find matches
results = find_matches(investors, startups)

# Sort results by score in descending order
results_sorted = results.sort_values('Score', ascending=False)

# Display top matches
print(results_sorted[results_sorted['Compatible'] == 'Yes'])

# Save results to CSV
results_sorted.to_csv("matchmaking_results.csv", index=False)
