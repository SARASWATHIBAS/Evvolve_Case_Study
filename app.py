import streamlit as st
from match import InvestorMatcher


def main():
    st.title("Investor-Startup Matching Platform")

    matcher = InvestorMatcher()

    # Sidebar for inputs
    st.sidebar.header("Enter Details")

    # Investor Details
    st.sidebar.subheader("Investor Details")
    investor_domain = st.sidebar.text_input("Investor Domain")
    investor_funds = st.sidebar.number_input("Available Funds ($)", min_value=0)

    # Startup Details
    st.sidebar.subheader("Startup Details")
    startup_domain = st.sidebar.text_input("Startup Domain")
    startup_deal = st.sidebar.number_input("Required Funding ($)", min_value=0)

    if st.sidebar.button("Calculate Match"):
        investor = {"Domain": investor_domain, "Fund_Available": investor_funds}
        startup = {"Domain": startup_domain, "Deal": startup_deal}

        # Calculate scores
        domain_score = matcher.calculate_domain_similarity_score(investor_domain, startup_domain)
        fund_score = matcher.calculate_fund_match_score(investor_funds, startup_deal)
        total_score = matcher.get_total_match_score(investor, startup)

        # Display results
        st.header("Matching Results")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Domain Match Score", f"{domain_score}%")
        with col2:
            st.metric("Fund Match Score", f"{fund_score}%")
        with col3:
            st.metric("Overall Match Score", f"{total_score:.1f}%")

        # Compatibility level
        if total_score >= 80:
            st.success("High Compatibility Match! 🌟")
        elif total_score >= 60:
            st.info("Medium Compatibility Match 👍")
        else:
            st.warning("Low Compatibility Match 🤔")

        # Additional insights
        st.subheader("Match Insights")
        st.write(f"- Domain Alignment: {investor_domain} ↔️ {startup_domain}")
        st.write(f"- Funding Gap Analysis: ${investor_funds:,} ↔️ ${startup_deal:,}")


if __name__ == "__main__":
    main()
