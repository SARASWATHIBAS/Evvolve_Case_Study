import streamlit as st
from streamlit_feedback import streamlit_feedback
import pandas as pd
from match import InvestorMatcher
import matplotlib
import plotly.graph_objects as go
import plotly.express as px

# Initialize session state for feedback
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = set()


def display_beautiful_interpretation(interpretation):
    """
    Creates an elegant display for the chart interpretation
    """
    st.markdown("---")
    st.markdown("### 📈 Data Insights")

    # Create an expander for detailed analysis
    with st.expander("View Detailed Analysis", expanded=True):
        # Split the interpretation into bullet points
        points = [point.strip() for point in interpretation.split('•') if point.strip()]

        # Display each point in a clean format
        for point in points:
            st.markdown(f"🔹 {point}")

    st.markdown("---")

def provide_dynamic_interpretation(viz_type, data, selected_data=None):
    """
    Provides dynamic interpretation based on visualization type and data patterns
    """
    if viz_type == "Heatmap":
        # Calculate key metrics
        high_matches = len(data[data['Match_Score'] >= 80])
        avg_score = data['Match_Score'].mean()
        top_pair = data.loc[data['Match_Score'].idxmax()]

        interpretation = f"""
        📊 Heatmap Analysis:
        • Found {high_matches} strong matches (80%+ compatibility)
        • Average match score across all pairs: {avg_score:.1f}%
        • Strongest match: {top_pair['Investor']} - {top_pair['Startup']} ({top_pair['Match_Score']:.1f}%)
        • Market concentration is highest in {data.groupby('Sector')['Match_Score'].mean().idxmax()} sector
        """

    elif viz_type == "Radar Chart":
        # Analyze component scores
        scores = selected_data[['Domain', 'Sector', 'Fund', 'Risk']]
        strongest = scores.idxmax()
        weakest = scores.idxmin()

        interpretation = f"""
        🎯 Radar Chart Analysis:
        • Strongest dimension: {strongest} ({scores[strongest]:.1f}%)
        • Area for improvement: {weakest} ({scores[weakest]:.1f}%)
        • Overall balance score: {scores.std():.1f} (lower is better)
        • Match quality is {scores.mean():.1f}% on average across all dimensions
        """

    elif viz_type == "Bubble Chart":
        # Analyze distribution
        excellent = len(data[data['Match_Score'] >= 90])
        good = len(data[data['Match_Score'].between(70, 90)])
        avg_score = data['Match_Score'].mean()

        interpretation = f"""
        💫 Bubble Chart Analysis:
        • {excellent} excellent matches (90%+ compatibility)
        • {good} good matches (70-90% compatibility)
        • Market average match score: {avg_score:.1f}%
        • Most active investor: {data.groupby('Investor').size().idxmax()}
        • Most sought-after startup: {data.groupby('Startup').size().idxmax()}
        """

    return interpretation



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
            avg_rating = relevant_feedback['rating'].mean()
            # Convert 1-5 rating to percentage adjustment (0-100)
            return (avg_rating / 5) * 100
    except FileNotFoundError:
        pass
    return 0


def main():
    st.title("Investor-Startup Matching Platform")
    tab1, tab2 = st.tabs(["Matching", "Visualization"])
    with tab1:
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
                "Select Investors Group",
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

                # Create adjusted results with 100-scale weights
                adjusted_results = original_results.copy()
                for idx, row in adjusted_results.iterrows():
                    feedback_weight = calculate_feedback_adjustment(row['Investor'], row['Startup'])
                    original_weight = row['Score']

                    # Combine original score and feedback score with equal weights
                    adjusted_score = (original_weight + feedback_weight) / 2
                    adjusted_results.loc[idx, 'Score'] = min(100, max(0, adjusted_score))

                # Display results
                investor_matches_original = original_results[
                    original_results['Investor'] == selected_investor
                    ].sort_values(by='Score', ascending=False)

                investor_matches_adjusted = adjusted_results[
                    adjusted_results['Investor'] == selected_investor
                    ].sort_values(by='Score', ascending=False)

                col1, col2 = st.columns(2)
                with col1:
                    st.write("Original Matches (0-100)")
                    st.dataframe(
                        investor_matches_original.style.background_gradient(
                            subset=['Score'],
                            cmap='YlOrRd',
                            vmin=0,
                            vmax=100
                        )
                    )

                with col2:
                    st.write("Feedback-Adjusted Matches (0-100)")
                    st.dataframe(
                        investor_matches_adjusted.style.background_gradient(
                            subset=['Score'],
                            cmap='YlOrRd',
                            vmin=0,
                            vmax=100
                        )
                    )

                # Score comparison with percentage differences
                st.subheader("Score Comparison")
                comparison_df = pd.DataFrame({
                    'Startup': investor_matches_original['Startup'],
                    'Original Score': investor_matches_original['Score'].round(2),
                    'Adjusted Score': investor_matches_adjusted['Score'].round(2),
                    'Score Difference (%)': (
                    (investor_matches_adjusted['Score'] - investor_matches_original['Score'])).round(2)
                })

                st.dataframe(
                    comparison_df.style.background_gradient(
                        subset=['Score Difference (%)'],
                        cmap='RdYlGn'
                    )
                )

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
                "Select Startups",
                startup_names
            )
            if st.button("Find Matches"):
                results = matcher.find_matches()
                startup_matches = results[results['Startup'] == selected_startup].sort_values(by='Score',ascending=False)

                st.subheader(f"Matches for {selected_startup}")
                st.dataframe(startup_matches)
    with tab2:
        st.header("Investor-Startup Match Visualization")
        matcher.find_matches()
        # Get the toVisualize dataframe from the InvestorMatcher class
        df_to_visualize = matcher.toVisualize
        
        # Dropdown for selecting visualization type
        viz_type = st.selectbox("Select Visualization Type", ["Heatmap", "Radar Chart", "Bubble Chart"])
        
        if viz_type == "Heatmap":
            st.subheader("Investor-Startup Match Heatmap")
            
            # Calculate overall match score
            df_to_visualize['Match_Score'] = df_to_visualize[['Domain', 'Sector', 'Fund', 'Risk']].mean(axis=1)
            
            # Pivot the data to create a matrix of investors and startups
            heatmap_data = df_to_visualize.pivot(index="Investor", columns="Startup", values="Match_Score")
            
            # Create heatmap using Plotly
            fig = px.imshow(heatmap_data, 
                            labels=dict(x="Startup", y="Investor", color="Match Score"),
                            x=heatmap_data.columns,
                            y=heatmap_data.index,
                            color_continuous_scale="YlOrRd")
            
            st.plotly_chart(fig)
            interpretation = provide_dynamic_interpretation(viz_type, df_to_visualize)
            display_beautiful_interpretation(interpretation)
        
        elif viz_type == "Radar Chart":
            st.subheader("Investor-Startup Match Radar Chart")
            
            investors = df_to_visualize['Investor'].unique()
            startups = df_to_visualize['Startup'].unique()
            
            selected_investor = st.selectbox("Select Investor", investors)
            selected_startup = st.selectbox("Select Startup", startups)
            
            # Get match scores for selected investor and startup
            match_scores = df_to_visualize[
                (df_to_visualize['Investor'] == selected_investor) & 
                (df_to_visualize['Startup'] == selected_startup)
            ][['Domain', 'Sector', 'Fund', 'Risk']].iloc[0]
            
            # Create radar chart using Plotly
            categories = list(match_scores.index)
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(match_scores.values),
                theta=categories,
                fill='toself',
                name='Match Scores'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=False
            )
            
            st.plotly_chart(fig)
            selected_data = df_to_visualize[
                (df_to_visualize['Investor'] == selected_investor) &
                (df_to_visualize['Startup'] == selected_startup)
                ].iloc[0]
            interpretation = provide_dynamic_interpretation(viz_type, df_to_visualize, selected_data)
            st.write(interpretation)
            display_beautiful_interpretation(interpretation)

        elif viz_type == "Bubble Chart":
            st.subheader("Investor-Startup Match Bubble Chart")
            
            # Calculate overall match score
            df_to_visualize['Match_Score'] = df_to_visualize[['Domain', 'Sector', 'Fund', 'Risk']].mean(axis=1)
            
            # Create bubble chart using Plotly
            fig = px.scatter(df_to_visualize, 
                            x="Investor", 
                            y="Startup", 
                            size="Match_Score", 
                            color="Match_Score",
                            hover_name="Startup", 
                            size_max=60,
                            color_continuous_scale="YlOrRd")
            
            fig.update_layout(
                xaxis_title="Investors",
                yaxis_title="Startups",
                coloraxis_colorbar=dict(title="Match Score")
            )
            
            st.plotly_chart(fig)
            interpretation = provide_dynamic_interpretation(viz_type, df_to_visualize)
            display_beautiful_interpretation(interpretation)

if __name__ == "__main__":
    main()
