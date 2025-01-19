import streamlit as st
from match import InvestorMatcher


def main():
    st.title("Investor-Startup Matching Platform")

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
        if st.button("Find Matches"):
            results = matcher.find_matches()
            investor_matches = results[results['Investor'] == selected_investor].sort()

            st.subheader(f"Matches for {selected_investor}")
            st.dataframe(investor_matches)

    else:
        selected_startup = st.selectbox(
            "Select Startup",
            startup_names
        )
        if st.button("Find Matches"):
            results = matcher.find_matches()
            startup_matches = results[results['Startup'] == selected_startup].sort()

            st.subheader(f"Matches for {selected_startup}")
            st.dataframe(startup_matches)


if __name__ == "__main__":
    main()
