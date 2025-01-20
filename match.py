
import pandas as pd

class InvestorMatcher:
    def __init__(self, investors_file, startups_file):

        self.investors = pd.read_csv(investors_file)
        self.startups = pd.read_csv(startups_file)
        self.weights = {
            "domain_match": 20,
            "sector_match":20,
            "fund_match": 30,
            "risk_match": 30
        }
        self.match_threshold = 70

    def calculate_fund_match_score(self,investor_funds, startup_deal):
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

    def Risk_appetite_score(self,investor, startup):
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

    def calculate_portfolio_fit_score(self, investor_portfolio, startup):
        """
        Calculate portfolio fit score based on historical investments
        """
        portfolio_sectors = {
            'FinTech': ['payments', 'banking', 'insurance', 'lending', 'wealth management'],
            'HealthTech': ['biotech', 'medical devices', 'healthcare', 'telemedicine'],
            'AI/ML': ['machine learning', 'deep learning', 'computer vision', 'nlp'],
            'E-commerce': ['retail tech', 'marketplace', 'd2c', 'logistics'],
            'Enterprise SaaS': ['b2b software', 'cloud services', 'automation']
        }

        score = 0
        flag=0
        startup_sector = startup.lower()

        # Check sector alignment
        for sector, keywords in portfolio_sectors.items():
            if sector in investor_portfolio:
                if any(keyword in startup_sector for keyword in keywords):
                    score = 100
        return score


    def calculate_match_score(self,investor, startup, weights):
        """
        Calculate a match score between an investor and a startup based on weights.
        """
        score = 0
        # Domain match
        if investor.get('Domain') == startup.get('Domain'):
            score += weights['domain_match']
        investor_past_portfolio = investor.get('Past_Portfolio', 0).split(',')
        # Sector match
        score += (weights['sector_match'] * (self.calculate_portfolio_fit_score(
            investor_past_portfolio,
            startup.get('Sector',0))
        ) / 100)
        # Fund availability match
        score += (weights['fund_match'] * (self.calculate_fund_match_score(
            investor.get('Fund_Available', 0),
            startup.get('Deal', 0))
        )/100)
        # Risk appetite match
        score += (weights['risk_match'] * self.Risk_appetite_score(investor, startup))/100
        return score


    def find_matches(self, value_criteria=None, attribute_criteria=None):
        """
        Find matches between investors and startups based on a scoring system.
        """
        matches = []

        for _, investor in self.investors.iterrows():
            filtered_startups = self.startups
            if value_criteria is not None:
                for key, value in value_criteria.items():
                    # do only if the value is not empty
                    if value:
                        if key == 'Growth Potential':
                            if value == 'High':
                                filtered_startups = filtered_startups[filtered_startups['Growth_Potential'] == 'High']
                            elif value == 'Medium':
                                filtered_startups = filtered_startups[filtered_startups['Growth_Potential'] == 'Medium']
                            elif value == 'Low':
                                filtered_startups = filtered_startups[filtered_startups['Growth_Potential'] == 'Low']
                        elif key == 'ROI':
                            filtered_startups = filtered_startups[filtered_startups['ROI'] >= float(value)]
                        elif key == 'Investment Stage':
                            filtered_startups = filtered_startups[filtered_startups['Investment_Stage'] == value]

            for _, startup in filtered_startups.iterrows():
                altered_weights = self.weights
                print(len(attribute_criteria))
                if attribute_criteria is not None:
                    if 'Domain' in attribute_criteria:
                        altered_weights['domain_match'] = 100/len(attribute_criteria)
                    else:
                        altered_weights['domain_match'] = 0
                    if 'Fund Availability' in attribute_criteria:
                        altered_weights['fund_match'] = 100/len(attribute_criteria)
                    else:
                        altered_weights['fund_match'] = 0
                    if 'Risk Appetitie' in attribute_criteria:
                        altered_weights['risk_match'] = 100/len(attribute_criteria)
                    else:
                        altered_weights['risk_match'] = 0
                score = self.calculate_match_score(investor, startup, altered_weights)
                compatibility = (
                    "High Compatibility"
                    if score >= self.match_threshold
                    else "Medium Compatibility"
                    if score >= self.match_threshold * 0.75
                    else "Low Compatibility"
                )
                matches.append({
                    "Investor": investor.get('Investor_Group_Name', 'Unknown'),
                    "Startup": startup.get('Company_Name', 'Unknown'),
                    "Compatibility": compatibility,
                    "Score": score
                })

        return pd.DataFrame(matches)
