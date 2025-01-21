import streamlit as st
import pandas as pd
from match import InvestorMatcher


def save_feedback(feedback_data):
    """Save feedback to CSV file"""
    try:
        existing_feedback = pd.read_csv('feedback.csv')
        updated_feedback = pd.concat([existing_feedback, pd.DataFrame([feedback_data])])
    except FileNotFoundError:
        updated_feedback = pd.DataFrame([feedback_data])

    updated_feedback.to_csv('feedback.csv', index=False)

def main():
    st.title("Investor-Startup Matching Platform")
    if 'current_ratings' not in st.session_state:
        st.session_state.current_ratings = {}
    if 'feedback_messages' not in st.session_state:
        st.session_state.feedback_messages = {}
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
            # At the top of your app
            # At the top of your app
            if 'current_ratings' not in st.session_state:
                st.session_state.current_ratings = {}

            # In your main display section after showing matches
            for idx, match in investor_matches.iterrows():
                match_key = f"{match['Investor']}_{match['Startup']}"

                # Retrieve the current rating from session state
                current_rating = st.session_state.current_ratings.get(match_key, 3)

                # Slider for rating
                rating = st.slider(
                    f"Rate match with {match['Startup']} (Investor: {match['Investor']})",
                    min_value=1,
                    max_value=5,
                    value=current_rating,
                    key=f"slider_{match_key}"
                )

                # Update session state when slider value changes
                if rating != current_rating:
                    st.session_state.current_ratings[match_key] = rating
                    feedback_data = {
                        'investor_name': match['Investor'],
                        'startup_name': match['Startup'],
                        'match_score': match['Score'],
                        'user_rating': rating,
                        'timestamp': pd.Timestamp.now()
                    }
                    save_feedback(feedback_data)
                    st.success(f"Rating of {rating}⭐ recorded for {match['Startup']} (Investor: {match['Investor']})")

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
