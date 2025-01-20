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
            if 'feedback_submitted' not in st.session_state:
                st.session_state.feedback_submitted = {}

            if 'current_ratings' not in st.session_state:
                st.session_state.current_ratings = {}

            if 'current_interactions' not in st.session_state:
                st.session_state.current_interactions = {}

            # In your feedback collection section
            for idx, match in investor_matches.iterrows():
                match_key = f"{match['Investor']}_{match['Startup']}"

                # Initialize values if not in session state
                if match_key not in st.session_state.current_ratings:
                    st.session_state.current_ratings[match_key] = 1
                if match_key not in st.session_state.current_interactions:
                    st.session_state.current_interactions[match_key] = "Initial Contact"

                with st.expander(f"Rate match with {match['Startup']}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        rating = st.slider(
                            "Rate this match (1-5)",
                            min_value=1,
                            max_value=5,
                            value=st.session_state.current_ratings[match_key],
                            key=f"rating_{match_key}"
                        )
                        st.session_state.current_ratings[match_key] = rating

                    with col2:
                        interaction = st.selectbox(
                            "Interaction Type",
                            ["Initial Contact", "Meeting Scheduled", "Deal Discussion", "Deal Closed"],
                            index=["Initial Contact", "Meeting Scheduled", "Deal Discussion", "Deal Closed"].index(
                                st.session_state.current_interactions[match_key]
                            ),
                            key=f"interaction_{match_key}"
                        )
                        st.session_state.current_interactions[match_key] = interaction

                    if st.button("Submit Feedback", key=f"submit_{match_key}"):
                        feedback_data = {
                            'investor_name': match['Investor'],
                            'startup_name': match['Startup'],
                            'match_score': match['Score'],
                            'user_rating': rating,
                            'interaction_type': interaction,
                            'timestamp': pd.Timestamp.now()
                        }
                        save_feedback(feedback_data)
                        st.session_state.feedback_submitted[match_key] = True
                        st.success("Feedback recorded successfully!")
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
