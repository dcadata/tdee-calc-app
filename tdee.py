import json

ACTIVITY_LEVELS: dict[str, float] = json.load(open('activity_levels.json'))


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


def calculate_bmr_and_tdee(**kwargs) -> dict[str, int]:
    weight: float = kwargs.get('weight')
    weight_unit: str = kwargs.get('weight_unit')
    height: float = kwargs.get('height')
    height_unit: str = kwargs.get('height_unit')
    age: float = kwargs.get('age')
    sex: str = kwargs.get('sex')
    activity_level: str = kwargs.get('activity_level')

    sex_adjustment: int = 0
    activity_adjustment: float = ACTIVITY_LEVELS.get(activity_level, 1)

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
    return dict(bmr=int(bmr), tdee=int(tdee))


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
    kwargs['sex'] = {Sex.F: Sex.M, Sex.M: Sex.F}[kwargs['sex'].upper()]
    return kwargs


def change_activity_level(**kwargs) -> dict[str, float]:
    changed_activity_level: str = kwargs.get('changed_activity_level')
    if changed_activity_level:
        kwargs['activity_level'] = changed_activity_level
    return kwargs
