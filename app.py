import streamlit as st
import pandas as pd
from match import InvestorMatcher
from git import Repo

def save_feedback_to_git(feedback_data):
    """Save feedback to CSV and push to Git repository"""
    csv_file = 'feedback.csv'
    try:
        existing_feedback = pd.read_csv(csv_file)
        updated_feedback = pd.concat([existing_feedback, pd.DataFrame([feedback_data])])
    except FileNotFoundError:
        updated_feedback = pd.DataFrame([feedback_data])
    updated_feedback.to_csv(csv_file, index=False)

    # Push CSV to Git repository
    repo_path = '.'  # Assuming the script is running in the Git repo directory
    repo = Repo(repo_path)
    repo.git.add(csv_file)
    repo.index.commit("Update feedback CSV")
    origin = repo.remote(name='origin')
    origin.push()

# Initialize session state for feedback
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = set()

def save_feedback_to_git(feedback_data):
    """Save feedback to CSV and push to Git repository"""
    csv_file = 'feedback.csv'
    if os.path.exists(csv_file):
        existing_feedback = pd.read_csv(csv_file)
        updated_feedback = pd.concat([existing_feedback, pd.DataFrame([feedback_data])])
    else:
        updated_feedback = pd.DataFrame([feedback_data])
    updated_feedback.to_csv(csv_file, index=False)

    # Push CSV to Git repository
    repo_path = '.'  # Assuming the script is running in the Git repo directory
    repo = Repo(repo_path)
    repo.git.add(csv_file)
    repo.index.commit("Update feedback CSV")
    origin = repo.remote(name='origin')
    origin.push()

def handle_feedback(investor, startup, score, rating, comment):
    feedback_data = {
        'investor_name': investor,
        'startup_name': startup,
        'match_score': score,
        'user_rating': rating,
        'comment': comment,
        'timestamp': pd.Timestamp.now()
    }
    save_feedback(feedback_data)
    st.session_state.feedback_submitted.add((investor, startup))

def main():
    st.title("Investor-Startup Matching Platform")
    # Initialize session states
    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = set()

    value_criteria = {}
    attribute_criteria = []
    # Initialize matcher
    matcher = InvestorMatcher(
        investors_file="investors.csv",
        startups_file="startups.csv"
    )

    # Create selection options from actual data
    investor_names = matcher.investors['Investor_Group_Name'].tolist()
    startup_names = matcher.startups['Company_Name'].tolist()

    # Selection type radio button
    search_type = st.radio(
        "Select search type:",
        ["Find matches for an Investor", "Find matches for a Startup"]
    )

    if search_type == "Find matches for an Investor":
        selected_investor = st.selectbox(
            "Select Investor",
            investor_names
        )
        # Add radio buttons for preference
        preference_type = st.radio(
            "Select preference type:",
            ["By Value", "By Attributes"]
        )
        if preference_type == "By Value":
            st.write("Select Value Criteria:")
            growth_potential = st.checkbox("Growth Potential")
            roi = st.checkbox("ROI")
            investment_stage = st.checkbox("Investment Stage")
            
            if growth_potential:
                value_criteria["Growth Potential"] = st.text_input("Enter value for Growth Potential (High, Medium, Low):")
            if roi:
                value_criteria["ROI"] = st.text_input("Enter value for ROI:")
            if investment_stage:
                value_criteria["Investment Stage"] = st.text_input("Enter value for Investment Stage (Growth, Seed, Series A, Series B):")
        elif preference_type == "By Attributes":
            st.write("Select Attribute Criteria:")
            market_size = st.checkbox("Domain")
            team_experience = st.checkbox("Fund Availability")
            product_uniqueness = st.checkbox("Risk Appetitie")
            
            if market_size:
                attribute_criteria.append("Domain")
            if team_experience:
                attribute_criteria.append("Fund Availability")
            if product_uniqueness:
                attribute_criteria.append("Risk Appetitie")
        if st.button("Find Matches"):
            results = matcher.find_matches(value_criteria=value_criteria, attribute_criteria=attribute_criteria)
            investor_matches = results[results['Investor'] == selected_investor].sort_values(by='Score',ascending=False)

            st.subheader(f"Matches for {selected_investor}")
            st.dataframe(investor_matches)

            st.subheader("Provide Feedback")

            for idx, match in results.iterrows():
                match_key = f"{match['Investor']}_{match['Startup']}"

                if (match['Investor'], match['Startup']) not in st.session_state.feedback_submitted:
                    with st.expander(f"Rate match with {match['Startup']}"):
                        rating = st.radio(
                            "Rating",
                            options=['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'],
                            key=f"rating_{match_key}",
                            horizontal=True
                        )
                        comment = st.text_area(
                            "Additional Comments (optional)",
                            key=f"comment_{match_key}"
                        )

                        if st.button("Submit Feedback", key=f"submit_{match_key}"):
                            rating_value = len(rating)
                            handle_feedback(
                                match['Investor'],
                                match['Startup'],
                                match['Score'],
                                rating_value,
                                comment
                            )
                            st.success("Thank you for your feedback!")
                else:
                    st.info("✓ Feedback submitted")

    else:
                selected_startup = st.selectbox(
                    "Select Startup",
                    startup_names
                )
                if st.button("Find Matches"):
                    results = matcher.find_matches()
                    startup_matches = results[results['Startup'] == selected_startup].sort_values(by='Score',ascending=False)

                    st.subheader(f"Matches for {selected_startup}")
                    st.dataframe(startup_matches)


if __name__ == "__main__":
    main()
