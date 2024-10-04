import pandas as pd


class ValidationCheck:
    def __init__(self, data):
        self.validation_check_result_colors_df = pd.DataFrame()

        self.run_validation_checks(data)

    def run_validation_checks(self, data):
        self.validation_check_one(data)
        self.validation_check_two(data)

    def validation_check_one(self, data):
        validation_columns = {}

        for column in data.columns:
            validation_columns[f"{column}_Validation_Check"] = ['red' if val else 'green' for val in data[column].isnull()]

        # Create a new DataFrame with all validation columns
        validation_df = pd.DataFrame(validation_columns)

        # Concatenate the validation DataFrame with your original DataFrame (if needed)
        self.validation_check_result_colors_df = pd.concat([data, validation_df], axis=1)

    def validation_check_two(self, data):
        #data = data.fillna(0)

        act_lt_24hrs = (
            data["Malaria_treated_with_ACT_in_HTR_<_24hrs_2-59_m"].astype(float).fillna(0)[data.index[-1]] +
            data["Malaria_treated_with_ACT_in_HTR_<_24hrs_5-14_yrs"].astype(float).fillna(0)[data.index[-1]] +
            data["Malaria_treated_with_ACT_in_HTR_<_24hrs_15+_years"].astype(float).fillna(0)[data.index[-1]]
        )

        act_gt_24hrs = (
                data["Malaria_treated_with_ACT_in_HTR_>_24hrs_2-59_m"].astype(float).fillna(0)[data.index[-1]] +
                data["Malaria_treated_with_ACT_in_HTR_>_24hrs_5-14_yrs"].astype(float).fillna(0)[data.index[-1]] +
                data["Malaria_treated_with_ACT_in_HTR_>_24hrs_15+_years"].astype(float).fillna(0)[data.index[-1]]
        )

        pos_ref = data["Fever_case_tested_for_malaria_(RDT)_in_HTR_Positive_Referred"].astype(float).fillna(0)[data.index[-1]]

        pos_total = (
                data["Fever_case_(suspected_malaria)_in_HTR_&_ETR_2-59_m"].astype(float).fillna(0)[data.index[-1]] +
                data["Fever_case_(suspected_malaria)_in_HTR_&_ETR_5-14_yrs"].astype(float).fillna(0)[data.index[-1]] +
                data["Fever_case_(suspected_malaria)_in_HTR_&_ETR_15+_years"].astype(float).fillna(0)[data.index[-1]]
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
                if self.validation_check_result_colors_df.loc[self.validation_check_result_colors_df.index[-1],f"{column}_Validation_Check"] == "green":
                    self.validation_check_result_colors_df.loc[self.validation_check_result_colors_df.index[-1],f"{column}_Validation_Check"] = "yellow"

    def get_val_check_result_colors_df(self):
        return self.validation_check_result_colors_df