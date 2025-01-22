import streamlit as st
from streamlit_feedback import streamlit_feedback
import pandas as pd
from match import InvestorMatcher

# Initialize session state for feedback
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = set()

def save_feedback_to_csv(feedback_data):
    """Save feedback to CSV file"""
    csv_file = 'feedback.csv'
    try:
        existing_feedback = pd.read_csv(csv_file)
        updated_feedback = pd.concat([existing_feedback, pd.DataFrame([feedback_data])], ignore_index=True)
    except FileNotFoundError:
        updated_feedback = pd.DataFrame([feedback_data])
    updated_feedback.to_csv(csv_file, index=False)

def handle_feedback(investor, startup, score, rating, comment):
    feedback_data = {
        'investor_name': investor,
        'startup_name': startup,
        'match_score': score,
        'user_rating': rating,
        'comment': comment,
        'timestamp': pd.Timestamp.now()
    }
    save_feedback_to_csv(feedback_data)
    st.session_state.feedback_submitted.add((investor, startup))
def calculate_feedback_adjustment(investor, startup):
    try:
        feedback_df = pd.read_csv('feedback.csv')
        relevant_feedback = feedback_df[
            (feedback_df['investor_name'] == investor) &
            (feedback_df['startup_name'] == startup)
        ]
        if not relevant_feedback.empty:
            positive_ratio = (relevant_feedback['user_rating'] == '👍').mean()
            return 20 * (positive_ratio - 0.5)  # Adjust score by ±20 based on feedback
    except FileNotFoundError:
        pass
    return 0


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
            # Get original results
            original_results = matcher.find_matches(value_criteria=value_criteria,
                                                    attribute_criteria=attribute_criteria)

            # Create adjusted results
            adjusted_results = original_results.copy()
            for idx, row in adjusted_results.iterrows():
                adjustment = calculate_feedback_adjustment(row['Investor'], row['Startup'])
                adjusted_results.loc[idx, 'Score'] = min(100, max(0, row['Score'] + adjustment))

            # Filter and display results
            investor_matches_original = original_results[original_results['Investor'] == selected_investor].sort_values(
                by='Score', ascending=False)
            investor_matches_adjusted = adjusted_results[adjusted_results['Investor'] == selected_investor].sort_values(
                by='Score', ascending=False)

            col1, col2 = st.columns(2)
            with col1:
                st.write("Original Matches")
                st.dataframe(investor_matches_original)
            with col2:
                st.write("Feedback-Adjusted Matches")
                st.dataframe(investor_matches_adjusted)

            # Comparison view
            st.subheader("Score Comparison")
            comparison_df = pd.DataFrame({
                'Startup': investor_matches_original['Startup'],
                'Original Score': investor_matches_original['Score'].round(2),
                'Adjusted Score': investor_matches_adjusted['Score'].round(2),
                'Score Difference': (investor_matches_adjusted['Score'] - investor_matches_original['Score']).round(2)
            })
            st.dataframe(comparison_df)
            st.subheader("Provide Feedback")

            for idx, match in original_results.iterrows():
                match_key = f"{match['Investor']}_{match['Startup']}"

                if (match['Investor'], match['Startup']) not in st.session_state.feedback_submitted:
                    with st.expander(f"Rate match with {match['Startup']}"):
                        feedback = streamlit_feedback(
                            feedback_type="thumbs",
                            optional_text_label="[Optional] Please provide an explanation",
                            align="flex-start",
                            key=f"feedback_{match_key}"
                        )

                        if feedback:
                            try:
                                handle_feedback(
                                    match['Investor'],
                                    match['Startup'],
                                    match['Score'],
                                    "👍" if feedback['score'] == 1 else "👎",
                                    feedback.get('text', '')
                                )
                                st.success("Thank you for your feedback! It has been saved and pushed to Git.")
                            except Exception as e:
                                st.error(f"An error occurred while saving feedback: {str(e)}")
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
