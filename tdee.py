import pandas as pd


class Filepath:
    MASS_BMR_AND_TDEE: str = 'data/mass_bmr_tdee.csv'
    ACTIVITY_LEVELS: str = 'activity_levels.json'


class Data:
    ACTIVITY_LEVELS: pd.DataFrame = pd.read_json(Filepath.ACTIVITY_LEVELS, dtype=dict(
        short_label=str, label=str, adjustment=float))


class Unit:
    LB: str = 'lb'
    IN: str = 'in'


class UnitConvMultiplier:
    LB_TO_KG: float = 0.453592
    IN_TO_CM: float = 2.54


class Sex:
    F: str = 'F'
    M: str = 'M'


class SexAdjustment:
    F: int = -161
    M: int = 5


def calculate_bmr_and_tdee(**kwargs) -> tuple[int, int]:
    weight: float = kwargs.get('weight')
    weight_unit: str = kwargs.get('weight_unit')
    height: float = kwargs.get('height')
    height_unit: str = kwargs.get('height_unit')
    age: float = kwargs.get('age')
    sex: str = kwargs.get('sex')
    activity_level: str = kwargs.get('activity_level')
    sex_adjustment: int = 0

    # get activity adjustment from activity level input
    try:
        activity_adjustment: float = Data.ACTIVITY_LEVELS[Data.ACTIVITY_LEVELS.label == activity_level].iloc[
            0].adjustment
    except IndexError:
        activity_adjustment: float = Data.ACTIVITY_LEVELS[Data.ACTIVITY_LEVELS.short_label == activity_level].iloc[
            0].adjustment

    if weight_unit == Unit.LB:
        weight *= UnitConvMultiplier.LB_TO_KG
    if height_unit == Unit.IN:
        height *= UnitConvMultiplier.IN_TO_CM

    if sex and sex.upper() == Sex.F:
        sex_adjustment = SexAdjustment.F
    elif sex and sex.upper() == Sex.M:
        sex_adjustment = SexAdjustment.M

    bmr = (10 * weight) + (6.25 * height) - (5 * age) + sex_adjustment
    tdee = bmr * activity_adjustment
    return int(round(bmr)), int(round(tdee))


def change_weight(**kwargs) -> dict[str, float]:
    weight_change: float = kwargs.get('weight_change')
    if weight_change:
        kwargs['weight'] += weight_change
    return kwargs


def change_height(**kwargs) -> dict[str, float]:
    height_change: float = kwargs.get('height_change')
    if height_change:
        kwargs['height'] += height_change
    return kwargs


def change_age(**kwargs) -> dict[str, float]:
    age_change: float = kwargs.get('age_change')
    if age_change:
        kwargs['age'] += age_change
    return kwargs


def change_sex(**kwargs) -> dict[str, float]:
    kwargs['sex'] = {Sex.F: Sex.M, Sex.M: Sex.F}.get(kwargs['sex'].upper())
    return kwargs


def change_activity_level(**kwargs) -> dict[str, float]:
    changed_activity_level: str = kwargs.get('changed_activity_level')
    if changed_activity_level:
        kwargs['activity_level'] = changed_activity_level
    return kwargs


def create_mass_bmr_and_tdee_table() -> pd.DataFrame:
    data = []
    for weight in range(100, 400, 10):
        for height in range(4 * 12 + 10, 6 * 12 + 10, 2):
            for age in range(20, 100, 10):
                for sex in (Sex.F, Sex.M):
                    for activity_level in range(4, 9):
                        bmr, tdee = calculate_bmr_and_tdee(
                            weight=weight,
                            weight_unit=Unit.LB,
                            height=height,
                            height_unit=Unit.IN,
                            age=age,
                            sex=sex,
                            activity_level=activity_level,
                        )
                        data.append(dict(
                            weight=weight,
                            height=height,
                            age=age,
                            sex=sex,
                            activity_level=activity_level,
                            bmr=bmr,
                            tdee=tdee,
                        ))

    df = pd.DataFrame(data).sort_values('tdee')
    df['bmi'] = df.weight / df.height ** 2 * 703

    df = df[(df.bmi >= 15) & (df.bmi < 60)].copy()
    df.loc[df.bmi >= 18.5, 'bmi_category'] = 'Healthy'
    df.loc[df.bmi >= 25, 'bmi_category'] = 'Overweight'
    for i in range(30, 55, 5):
        df.loc[df.bmi >= i, 'bmi_category'] = f'Obese>{i}'
    df.bmi_category = df.bmi_category.fillna('Underweight')

    df.to_csv(Filepath.MASS_BMR_AND_TDEE, index=False)
    return df


def read_mass_bmr_and_tdee_table() -> pd.DataFrame:
    return pd.read_csv(Filepath.MASS_BMR_AND_TDEE)


def get_people_with_similar_bmr_and_tdee(
        df: pd.DataFrame,
        activity_level: int,
        bmr: float = None,
        tdee: float = None,
        include_underweight: bool = True,
        include_overweight: bool = True,
        include_obese: bool = True,
) -> pd.DataFrame:
    band: float = 25

    if bmr:
        df = df[(df.bmr >= bmr - band) & (df.bmr <= bmr + band)]
    if tdee:
        df = df[(df.tdee >= tdee - band) & (df.tdee <= tdee + band)]

    if activity_level:
        df = df[df.activity_level == activity_level]

    if not include_underweight:
        df = df[df.bmi >= 18.5]
    if not include_overweight:
        df = df[df.bmi < 25]
    if not include_obese:
        df = df[df.bmi < 30]

    df = df.drop(columns='bmi_category')
    df.bmi = df.bmi.round(1)
    return df
