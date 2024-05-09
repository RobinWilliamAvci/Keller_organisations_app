from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import uuid

app = Flask(__name__)

# Laden und Speichern von Daten
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"Räume": {}}

def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Hauptseite
@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', räume=data["Räume"])

# Routen für Räume
@app.route('/add_raum', methods=['POST'])
def add_raum():
    raum_name = request.form.get('raum_name')
    if raum_name:
        data = load_data()
        if raum_name not in data['Räume']:
            data['Räume'][raum_name] = {"Regale": {}}
            save_data(data)
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/delete_raum/<raum_name>', methods=['POST'])
def delete_raum(raum_name):
    data = load_data()
    if raum_name in data['Räume']:
        del data['Räume'][raum_name]
        save_data(data)
    return redirect(url_for('index'))

@app.route('/edit_raum/<raum_name>', methods=['POST'])
def edit_raum(raum_name):
    data = load_data()
    new_name = request.json.get('new_name')
    if new_name and new_name not in data['Räume']:
        data['Räume'][new_name] = data['Räume'].pop(raum_name)
        save_data(data)
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400

@app.route('/raum/<raum_name>')
def raum(raum_name):
    data = load_data()
    if raum_name in data['Räume']:
        return render_template('raum.html', raum_name=raum_name, regale=data['Räume'][raum_name]['Regale'])
    return 'Raum nicht gefunden', 404

# Routen für Regale
@app.route('/raum/<raum_name>/add_regal', methods=['POST'])
def add_regal(raum_name):
    regal_name = request.form.get('regal_name')
    if regal_name:
        data = load_data()
        if raum_name in data['Räume'] and regal_name not in data['Räume'][raum_name]['Regale']:
            data['Räume'][raum_name]['Regale'][regal_name] = {'Boxen': {}}
            save_data(data)
        return redirect(url_for('raum', raum_name=raum_name))
    return redirect(url_for('raum', raum_name=raum_name))

@app.route('/raum/<raum_name>/delete_regal/<regal_name>', methods=['POST'])
def delete_regal(raum_name, regal_name):
    data = load_data()
    if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale']:
        del data['Räume'][raum_name]['Regale'][regal_name]
        save_data(data)
    return redirect(url_for('raum', raum_name=raum_name))

@app.route('/edit_regal/<raum_name>/<regal_name>', methods=['POST'])
def edit_regal(raum_name, regal_name):
    data = load_data()
    new_name = request.json.get('new_name')
    if new_name and new_name not in data['Räume'][raum_name]['Regale']:
        data['Räume'][raum_name]['Regale'][new_name] = data['Räume'][raum_name]['Regale'].pop(regal_name)
        save_data(data)
        return jsonify(success=True), 200
    return jsonify(success=False), 400

@app.route('/raum/<raum_name>/<regal_name>')
def regal(raum_name, regal_name):
    data = load_data()
    if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale']:
        return render_template('regal.html', raum_name=raum_name, regal_name=regal_name, boxen=data['Räume'][raum_name]['Regale'][regal_name]['Boxen'])
    return 'Regal nicht gefunden', 404

# Routen für Boxen
@app.route('/raum/<raum_name>/<regal_name>/add_box', methods=['POST'])
def add_box(raum_name, regal_name):
    box_name = request.form.get('box_name')
    if box_name:
        data = load_data()
        if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale'] and box_name not in data['Räume'][raum_name]['Regale'][regal_name]['Boxen']:
            data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][box_name] = {'Objekte': []}
            save_data(data)
        return redirect(url_for('regal', raum_name=raum_name, regal_name=regal_name))
    return redirect(url_for('regal', raum_name=raum_name, regal_name=regal_name))

@app.route('/raum/<raum_name>/<regal_name>/delete_box/<box_name>', methods=['POST'])
def delete_box(raum_name, regal_name, box_name):
    data = load_data()
    if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale'] and box_name in data['Räume'][raum_name]['Regale'][regal_name]['Boxen']:
        del data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][box_name]
        save_data(data)
    return redirect(url_for('regal', raum_name=raum_name, regal_name=regal_name))

@app.route('/edit_box/<raum_name>/<regal_name>/<box_name>', methods=['POST'])
def edit_box(raum_name, regal_name, box_name):
    data = load_data()
    box_data = data['Räume'][raum_name]['Regale'][regal_name]['Boxen'].get(box_name, None)

    if not box_data:
        return jsonify(success=False, error="Box not found"), 404

    try:
        new_name = request.json.get('new_name', box_data['name'])  # Neuer Name aus der JSON-Anfrage
        new_description = request.json.get('new_description', box_data['beschreibung'])  # Neue Beschreibung aus der JSON-Anfrage

        # Prüfe, ob der neue Name gültig und nicht bereits vorhanden ist
        if new_name != box_name and new_name in data['Räume'][raum_name]['Regale'][regal_name]['Boxen']:
            return jsonify(success=False, error="New name already exists"), 400

        # Aktualisiere Name und Beschreibung
        if new_name != box_name:
            data['Räume'][raum_name]['Regale'][regal_name]['Boxen'].pop(box_name)
            data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][new_name] = box_data
        box_data['name'] = new_name
        box_data['beschreibung'] = new_description

        save_data(data)
        return jsonify(success=True), 200
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route('/raum/<raum_name>/<regal_name>/<box_name>')
def box(raum_name, regal_name, box_name):
    data = load_data()
    if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale'] and box_name in data['Räume'][raum_name]['Regale'][regal_name]['Boxen']:
        return render_template('box.html', raum_name=raum_name, regal_name=regal_name, box_name=box_name, objekte=data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][box_name]['Objekte'])
    return 'Box nicht gefunden', 404


# Routen für Objekte
@app.route('/raum/<raum_name>/<regal_name>/<box_name>/add_item', methods=['POST'])
def add_item(raum_name, regal_name, box_name):
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_anzahl = request.form.get('item_anzahl', 0)  # Default auf 0, falls nicht gesetzt

    if item_name and item_description:
        data = load_data()
        if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale'] and box_name in data['Räume'][raum_name]['Regale'][regal_name]['Boxen']:
            neues_objekt = {
                'id': str(uuid.uuid4()),  # Generiere eine zufällige UUID
                'name': item_name,
                'beschreibung': item_description,
                'anzahl': int(item_anzahl) if item_anzahl.isdigit() else 0
            }
            data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][box_name]['Objekte'].append(neues_objekt)
            save_data(data)
        return redirect(url_for('box', raum_name=raum_name, regal_name=regal_name, box_name=box_name))
    return redirect(url_for('box', raum_name=raum_name, regal_name=regal_name, box_name=box_name))

@app.route('/raum/<raum_name>/<regal_name>/<box_name>/delete_item/<string:item_id>', methods=['POST'])
def delete_item(raum_name, regal_name, box_name, item_id):
    data = load_data()
    if raum_name in data['Räume'] and regal_name in data['Räume'][raum_name]['Regale'] and box_name in data['Räume'][raum_name]['Regale'][regal_name]['Boxen']:
        objekte = data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][box_name]['Objekte']
        objekt_index = next((index for (index, d) in enumerate(objekte) if d['id'] == item_id), None)
        if objekt_index is not None:
            del objekte[objekt_index]
            save_data(data)
    return redirect(url_for('box', raum_name=raum_name, regal_name=regal_name, box_name=box_name))


@app.route('/raum/<raum_name>/<regal_name>/<box_name>/update_item/<string:item_id>', methods=['POST'])
def update_item(raum_name, regal_name, box_name, item_id):
    action = request.form.get('action')
    item_anzahl = int(request.form.get('item_anzahl', 0))

    data = load_data()
    objekte = data['Räume'][raum_name]['Regale'][regal_name]['Boxen'][box_name]['Objekte']
    objekt = next((obj for obj in objekte if obj['id'] == item_id), None)

    if objekt:
        try:
            if action == 'increase':
                objekt['anzahl'] += 1
            elif action == 'decrease' and objekt['anzahl'] > 0:
                objekt['anzahl'] -= 1
            else:
                objekt['anzahl'] = item_anzahl
            save_data(data)
        except (KeyError, ValueError):
            pass  # Fehlerbehandlung hier verbessern
    return redirect(url_for('box', raum_name=raum_name, regal_name=regal_name, box_name=box_name))


@app.route('/edit_item/<string:item_id>', methods=['POST'])
def edit_item(item_id):
    try:
        data = load_data()
        item_info = request.get_json()
        objekt = find_item_by_id(data, item_id)
        if objekt:
            objekt[item_info['field']] = item_info['value']
            save_data(data)
            return jsonify(success=True), 200
        else:
            current_app.logger.error(f"Objekt mit ID {item_id} nicht gefunden.")
            return jsonify(success=False, error="Item not found"), 404
    except Exception as e:
        current_app.logger.error(f"Ein Fehler ist aufgetreten: {e}")
        return jsonify(success=False, error=str(e)), 500



def find_item_by_id(data, item_id):
    for raum_name, raum in data['Räume'].items():
        for regal_name, regal in raum['Regale'].items():
            for box_name, box in regal['Boxen'].items():
                for objekt in box['Objekte']:
                    if objekt['id'] == item_id:
                        return objekt
    return None

@app.route('/suchen', methods=['GET'])
def suchen():
    suchtext = request.args.get('suchtext', '').lower()  # Suchtext aus der Anfrage holen und in Kleinbuchstaben umwandeln
    ergebnisse = []

    data = load_data()  # Daten laden

    # Durch die Hierarchie der Räume, Regale und Boxen navigieren
    for raum_name, raum in data['Räume'].items():
        for regal_name, regal in raum['Regale'].items():
            for box_name, box in regal['Boxen'].items():
                for objekt in box['Objekte']:
                    # Überprüfen, ob der Suchtext im Namen oder in der Beschreibung des Objekts enthalten ist
                    if suchtext in objekt['name'].lower() or suchtext in objekt['beschreibung'].lower():
                        ergebnisse.append({
                            'raum': raum_name,
                            'regal': regal_name,
                            'box': box_name,
                            'objekt': objekt
                        })

    # Ergebnisse an eine Vorlage senden, um sie anzuzeigen
    return render_template('suchergebnisse.html', ergebnisse=ergebnisse)


# Start der App
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5002)
