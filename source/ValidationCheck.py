import pandas as pd


class ValidationCheck:
    def __init__(self, data):
        self.validation_check_result_colors_df = pd.DataFrame()

        self.run_validation_checks(data)

    def run_validation_checks(self, data):
        self.validation_check_one(data)
        self.validation_check_two(data)

    def validation_check_one(self, data):
        for column in data.columns:
            self.validation_check_result_colors_df[f"{column}_Validation_Check"] = ['red' if val else 'green' for val in data[column].isnull()]

    def validation_check_two(self, data):
        act_lt_24hrs = (
            data["Malaria_treated_with_ACT_in_HTR_<_24hrs_2-59_m"].fillna(0)[data.index[-1]] +
            data["Malaria_treated_with_ACT_in_HTR_<_24hrs_5-14_yrs"].fillna(0)[data.index[-1]] +
            data["Malaria_treated_with_ACT_in_HTR_<_24hrs_15+_years"].fillna(0)[data.index[-1]]
        )

        act_gt_24hrs = (
                data["Malaria_treated_with_ACT_in_HTR_>_24hrs_2-59_m"].fillna(0)[data.index[-1]] +
                data["Malaria_treated_with_ACT_in_HTR_>_24hrs_5-14_yrs"].fillna(0)[data.index[-1]] +
                data["Malaria_treated_with_ACT_in_HTR_>_24hrs_15+_years"].fillna(0)[data.index[-1]]
        )

        pos_ref = data["Fever_case_tested_for_malaria_(RDT)_in_HTR_Positive_Referred"].fillna(0)[data.index[-1]]

        pos_total = (
                data["Fever_case_(suspected_malaria)_in_HTR_&_ETR_2-59_m"].fillna(0)[data.index[-1]] +
                data["Fever_case_(suspected_malaria)_in_HTR_&_ETR_5-14_yrs"].fillna(0)[data.index[-1]] +
                data["Fever_case_(suspected_malaria)_in_HTR_&_ETR_15+_years"].fillna(0)[data.index[-1]]
        )

        if not (act_lt_24hrs + act_gt_24hrs + pos_ref) == pos_total:
            column_to_change_color = [
                "Malaria_treated_with_ACT_in_HTR_<_24hrs_2-59_m",
                "Malaria_treated_with_ACT_in_HTR_<_24hrs_5-14_yrs",
                "Malaria_treated_with_ACT_in_HTR_<_24hrs_15+_years",
                "Malaria_treated_with_ACT_in_HTR_>_24hrs_2-59_m",
                "Malaria_treated_with_ACT_in_HTR_>_24hrs_5-14_yrs",
                "Malaria_treated_with_ACT_in_HTR_>_24hrs_15+_years",
                "Fever_case_tested_for_malaria_(RDT)_in_HTR_Positive_Referred",
                "Fever_case_(suspected_malaria)_in_HTR_&_ETR_2-59_m",
                "Fever_case_(suspected_malaria)_in_HTR_&_ETR_5-14_yrs",
                "Fever_case_(suspected_malaria)_in_HTR_&_ETR_15+_years"
            ]

            for column in column_to_change_color:
                if self.validation_check_result_colors_df[f"{column}_Validation_Check"][self.validation_check_result_colors_df.index[-1]] == "green":
                    self.validation_check_result_colors_df[f"{column}_Validation_Check"][self.validation_check_result_colors_df.index[-1]] = "yellow"

    def get_val_check_result_colors_df(self):
        return self.validation_check_result_colors_df