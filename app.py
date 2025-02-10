from flask import Flask, request, jsonify, render_template

import tdee

app = Flask(__name__)
app.json.sort_keys = False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', activity_levels=tdee.ACTIVITY_LEVELS.keys())

    payload = request.json
    weight = payload.get('weight')
    weight_unit = payload.get('weight_unit')
    height = payload.get('height')
    height_unit = payload.get('height_unit')
    age = payload.get('age')
    sex = payload.get('sex')
    activityLevel = payload.get('activityLevel')

    result = []
    if not weight:
        result.append({'Error(s)': 'Enter weight.'})
    if not height:
        result.append({'Error(s)': 'Enter height.'})
    if not age:
        result.append({'Error(s)': 'Enter age.'})
    if result:
        return result

    params = dict(
        weight=float(weight),
        weight_unit=weight_unit,
        height=float(height),
        height_unit=height_unit,
        age=float(age),
        sex=sex,
        activity_level=activityLevel,
    )
    scenarios_with_modified_params = {
        'As entered': params,
        'After 10 lb loss': tdee.change_weight(**params, weight_change=-10),
        'After 20 lb loss': tdee.change_weight(**params, weight_change=-20),
        'If 6 in taller': tdee.change_height(**params, height_change=6),
        'If 6 in shorter': tdee.change_height(**params, height_change=-6),
        'If 10y younger': tdee.change_age(**params, age_change=-10),
        'If 10y older': tdee.change_age(**params, age_change=10),
        'If other sex': tdee.change_sex(**params),
        'At +1 activity level': tdee.get_changed_activity_level(0, **params),
        'At +2 activity level': tdee.get_changed_activity_level(1, **params),
        'At +3 activity level': tdee.get_changed_activity_level(2, **params),
    }

    actual_bmr, actual_tdee = tdee.calculate_bmr_and_tdee(**params)
    for scenario_label, modified_params in scenarios_with_modified_params.items():
        scenario_bmr, scenario_tdee = tdee.calculate_bmr_and_tdee(**modified_params)
        result.extend([{
            'Scenario': scenario_label,
            'BMR': scenario_bmr,
            'TDEE': scenario_tdee,
            'ΔTDEE': scenario_tdee - actual_tdee,
        }])

    return jsonify(result)


if __name__ == '__main__':
    app.run()
