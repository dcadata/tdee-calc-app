import pandas as pd


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


def read_activity_levels() -> pd.DataFrame:
    activity_levels = pd.read_json('activity_levels.json', dtype=dict(id=int, label=str, value=float))
    return activity_levels


def calculate_bmr_and_tdee(**kwargs) -> tuple[int, int]:
    weight: float = kwargs.get('weight')
    weight_unit: str = kwargs.get('weight_unit')
    height: float = kwargs.get('height')
    height_unit: str = kwargs.get('height_unit')
    age: float = kwargs.get('age')
    sex: str = kwargs.get('sex')
    activity_level: str | int = kwargs.get('activity_level')
    sex_adjustment: int = 0

    # get activity adjustment from activity level input
    activity_levels: pd.DataFrame = read_activity_levels()
    if type(activity_level) == str:
        activity_adjustment: pd.DataFrame = activity_levels[activity_levels.label == activity_level]
    elif type(activity_level) == int:
        activity_adjustment: pd.DataFrame = activity_levels[activity_levels.id == activity_level]
    else:
        activity_adjustment: pd.DataFrame = activity_levels[activity_levels.value == activity_level]
    activity_adjustment: float = activity_adjustment.iloc[0].value

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


def get_changed_activity_level(idx: int = 0, **kwargs) -> dict[str, float]:
    current_activity_level = kwargs.get('activity_level')
    activity_levels = list(read_activity_levels()[['id', 'label']].to_records(index=False))
    new_activity_level: tuple = (None, None)
    while current_activity_level not in new_activity_level:
        new_activity_level = activity_levels.pop(0)
    new_activity_level = activity_levels.pop(idx)
    return change_activity_level(**kwargs, changed_activity_level=new_activity_level[0])


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

    df.to_csv('bmr_and_tdee_table.csv', index=False)
    return df
