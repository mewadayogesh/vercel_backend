import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from collections import Counter

# 1. Use relative import because models.py is in the same folder as app.py
#from models import db, DDEntry 
from .models import db, DDEntry

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- DATABASE CONFIGURATION ---
# Using Neon PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    "postgresql://neondb_owner:npg_QF7DZA3zxbcp@ep-flat-salad-att912kq-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Helper to convert DB objects to dictionary
def entry_to_dict(entry):
    return {
        "id": entry.id,
        "department": entry.department,
        "workType": entry.work,
        "date": entry.date,
        "globalId": entry.Global,
        "purpose": entry.purpose,
        "material": entry.material,
        "otherMaterial": entry.other_material,
        "itemType": entry.item_type,
        "otherType": entry.other_type,
        "frequency": entry.frequency,
        "quantity": entry.quantity,
        "projectName": entry.project,
        "description": entry.description,
        "priority": entry.priority,
        "status": entry.item,
        "task": entry.task
    }

# --- ROUTES ---

@app.route('/api/check-global-id/<global_id>', methods=['GET'])
def check_global_id(global_id):
    exists = DDEntry.query.filter_by(Global=global_id).first() is not None
    return jsonify({"exists": exists}), 200

@app.route('/api/entries', methods=['POST'])
def save():
    data = request.json or {}
    global_id = (data.get('global_id') or '').strip()

    if global_id and DDEntry.query.filter_by(Global=global_id).first():
        return jsonify({"success": False, "error": "Global ID already exists"}), 409

    try:
        new_entry = DDEntry(
            department=data.get('department', ''),
            work=data.get('work_type', ''),
            date=data.get('date', ''),
            Global=global_id,
            purpose=data.get('purpose', ''),
            material=data.get('material', ''),
            other_material=data.get('material') if data.get('material') == 'Other' else "",
            item_type=data.get('type', ''),
            other_type=data.get('type') if data.get('type') == 'Other' else "",
            frequency=data.get('frequency', ''),
            quantity=str(data.get('quantity', '')),
            project=data.get('project_name', ''),
            description=data.get('description', ''),
            priority=data.get('priority', ''),
            item=data.get('item_status', ''),
            task=data.get('task', '')
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"success": True, "message": "Record saved!"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/entries', methods=['GET'])
def get_all_records():
    entries = DDEntry.query.order_by(DDEntry.id.desc()).all()
    return jsonify([entry_to_dict(e) for e in entries]), 200

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    entries = DDEntry.query.all()
    dept_counts = Counter((e.department or 'Unspecified') for e in entries)
    priority_counts = Counter((e.priority or 'Unspecified') for e in entries)
    return jsonify({
        "total_records": len(entries),
        "dept_labels": list(dept_counts.keys()),
        "dept_values": list(dept_counts.values()),
        "priority_labels": list(priority_counts.keys()),
        "priority_values": list(priority_counts.values()),
    }), 200

@app.route('/')
def home():
    return "API is active"

if __name__ == '__main__':
    app.run(debug=True)
# old code working
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# from models import db, DDEntry
# import io
# from collections import Counter
# from openpyxl import Workbook

# app = Flask(__name__)
# CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# def can_edit():
#     return True


# # Checks whether a Global ID already exists in the database.
# # Used by the Flutter "New Entry" form before it submits, so the user
# # gets an immediate "Global ID already exists" message.
# @app.route('/api/check-global-id/<global_id>', methods=['GET'])
# def check_global_id(global_id):
#     # Search for an existing record with the same Global ID
#     exists = DDEntry.query.filter_by(Global=global_id).first() is not None
#     return jsonify({"exists": exists}), 200


# @app.route('/api/entries', methods=['POST'])
# def save():
#     if not can_edit():
#         return jsonify({"error": "Unauthorized access"}), 403

#     data = request.json or {}
#     work_type = data.get('work_type', '')
#     global_id = (data.get('global_id') or '').strip()

#     # Server-side duplicate guard: protects against race conditions where
#     # two submissions pass the client-side check at nearly the same time.
#     if global_id and DDEntry.query.filter_by(Global=global_id).first() is not None:
#         return jsonify({
#             "success": False,
#             "error": "Global ID already exists"
#         }), 409

#     if work_type == "Mechanical Design Related":
#         material = item_type = frequency = quantity = other_material = other_type = ""
#         chosen_purpose  = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')
#     else:
#         material        = data.get('material', '')
#         item_type       = data.get('type', '')
#         frequency       = data.get('frequency', '')
#         quantity        = str(data.get('quantity', ''))
#         other_material  = data.get('material', '') if data.get('material') == 'Other' else ""
#         other_type      = data.get('type', '') if data.get('type') == 'Other' else ""
#         chosen_purpose  = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')

#     entry = DDEntry(
#         department=data.get('department', ''),
#         work=work_type,
#         date=data.get('date', ''),
#         Global=global_id,
#         purpose=chosen_purpose,
#         material=material, 
#         other_material=other_material,
#         item_type=item_type, 
#         other_type=other_type,
#         frequency=frequency, 
#         quantity=quantity,
#         project=data.get('project_name', ''),
#         description=data.get('description', ''),
#         priority=chosen_priority,
#         item=data.get('item_status', ''),
#         task=data.get('task', '')
#     )
    
#     try:
#         db.session.add(entry)
#         db.session.commit()
#         return jsonify({"success": True, "message": "Record written successfully!"}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/api/entries', methods=['GET'])
# def get_all_records():
#     try:
#         entries = DDEntry.query.order_by(DDEntry.id.desc()).all()
#         return jsonify([entry.to_dict() for entry in entries]), 200
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
# def delete_entry(entry_id):
#     if not can_edit():
#         return jsonify({"error": "Unauthorized access"}), 403

#     entry = db.session.get(DDEntry, entry_id)
#     if not entry:
#         return jsonify({"success": False, "error": "Record not found"}), 404

#     try:
#         db.session.delete(entry)
#         db.session.commit()
#         return jsonify({"success": True, "message": "Record deleted"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500


# # Fetches a single record by id, used to pre-fill the Edit screen
# @app.route('/api/entries/<int:entry_id>', methods=['GET'])
# def get_entry(entry_id):
#     entry = db.session.get(DDEntry, entry_id)
#     if not entry:
#         return jsonify({"success": False, "error": "Record not found"}), 404
#     return jsonify(entry.to_dict()), 200


# # Updates a single record by id, used by the Edit screen's Save button
# @app.route('/api/entries/<int:entry_id>', methods=['PUT'])
# def update_entry(entry_id):
#     if not can_edit():
#         return jsonify({"error": "Unauthorized access"}), 403

#     entry = db.session.get(DDEntry, entry_id)
#     if not entry:
#         return jsonify({"success": False, "error": "Record not found"}), 404

#     data = request.json or {}
#     work_type = data.get('work_type', '')
#     new_global_id = (data.get('global_id') or entry.Global or '').strip()

#     # Server-side duplicate guard: only blocks if the new Global ID belongs
#     # to a *different* record. Editing an entry without changing its own
#     # Global ID (or leaving it as-is) is still allowed.
#     if new_global_id:
#         clash = DDEntry.query.filter(
#             DDEntry.Global == new_global_id,
#             DDEntry.id != entry_id
#         ).first()
#         if clash is not None:
#             return jsonify({
#                 "success": False,
#                 "error": "Global ID already exists"
#             }), 409

#     if work_type == "Mechanical Design Related":
#         material = item_type = frequency = quantity = other_material = other_type = ""
#         chosen_purpose = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')
#     else:
#         material = data.get('material', '')
#         item_type = data.get('type', '')
#         frequency = data.get('frequency', '')
#         quantity = str(data.get('quantity', ''))
#         other_material = data.get('material', '') if data.get('material') == 'Other' else ""
#         other_type = data.get('type', '') if data.get('type') == 'Other' else ""
#         chosen_purpose = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')

#     try:
#         entry.department = data.get('department', entry.department)
#         entry.work = work_type or entry.work
#         entry.date = data.get('date', entry.date)
#         entry.Global = new_global_id
#         entry.purpose = chosen_purpose
#         entry.material = material
#         entry.other_material = other_material
#         entry.item_type = item_type
#         entry.other_type = other_type
#         entry.frequency = frequency
#         entry.quantity = quantity
#         entry.project = data.get('project_name', entry.project)
#         entry.description = data.get('description', entry.description)
#         entry.priority = chosen_priority
#         entry.item = data.get('item_status', entry.item)
#         entry.task = data.get('task', entry.task)

#         db.session.commit()
#         return jsonify({"success": True, "message": "Record updated successfully!"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500


# # Search records by Global ID, used by the Master Tracker screen
# @app.route('/api/entries/search', methods=['GET'])
# def search_entries():
#     global_id = request.args.get('global_id', '').strip()
#     if not global_id:
#         return jsonify({"success": False, "error": "global_id query param is required"}), 400

#     entries = DDEntry.query.filter(DDEntry.Global.ilike(f"%{global_id}%")).order_by(DDEntry.id.desc()).all()
#     return jsonify([e.to_dict() for e in entries]), 200


# # Aggregated counts for the Dashboard's bar + pie charts
# @app.route('/api/dashboard-stats', methods=['GET'])
# def dashboard_stats():
#     entries = DDEntry.query.all()

#     dept_counts = Counter((e.department or 'Unspecified') for e in entries)
#     priority_counts = Counter((e.priority or 'Unspecified') for e in entries)

#     return jsonify({
#         "total_records": len(entries),
#         "dept_labels": list(dept_counts.keys()),
#         "dept_values": list(dept_counts.values()),
#         "priority_labels": list(priority_counts.keys()),
#         "priority_values": list(priority_counts.values()),
#     }), 200

# @app.route('/api/entries/excel', methods=['GET'])
# def download_excel():
#     try:
#         entries = DDEntry.query.order_by(DDEntry.id.desc()).all()
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "D&D Records"

#         headers = [
#             'S.No', 'Department', 'Work Type', 'Date', 'Global ID', 'Purpose',
#             'Material', 'Material (Other)', 'Type', 'Type (Other)',
#             'Frequency', 'Quantity', 'Project Name', 'Description',
#             'Priority', 'Item Status', 'Task'
#         ]
#         ws.append(headers)

#         # Use a sequential serial number (1, 2, 3, ...) rather than the raw
#         # database id, since deleting records leaves gaps in the id sequence
#         # (e.g. 5, 4, 3, 2) — this matches the "S.No" column the Flutter
#         # Reports table already shows.
#         for index, e in enumerate(entries, start=1):
#             row = e.to_dict()
#             ws.append([
#                 index, row.get('department', ''), row.get('workType', ''), row.get('date', ''),
#                 row.get('globalId', ''), row.get('purpose', ''), row.get('material', ''),
#                 row.get('otherMaterial', ''), row.get('itemType', ''), row.get('otherType', ''),
#                 row.get('frequency', ''), row.get('quantity', ''), row.get('projectName', ''),
#                 row.get('description', ''), row.get('priority', ''), row.get('status', ''), row.get('task', '')
#             ])

#         buffer = io.BytesIO()
#         wb.save(buffer)
#         buffer.seek(0)
#         return send_file(
#             buffer,
#             as_attachment=True,
#             download_name='dd_department_records.xlsx',
#             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/api/entries/clear', methods=['DELETE'])
# def clear_all():
#     try:
#         db.session.query(DDEntry).delete()
#         db.session.commit()
#         return jsonify({"success": True, "message": "Database wiped clean"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500

# with app.app_context():
#     db.create_all()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True, port=5000)
#old code
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# from models import db, DDEntry
# import io
# from collections import Counter
# from openpyxl import Workbook

# app = Flask(__name__)
# CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# def can_edit():
#     return True

# @app.route('/api/entries', methods=['POST'])
# def save():
#     if not can_edit():
#         return jsonify({"error": "Unauthorized access"}), 403

#     data = request.json or {}
#     work_type = data.get('work_type', '')
    
#     if work_type == "Mechanical Design Related":
#         material = item_type = frequency = quantity = other_material = other_type = ""
#         chosen_purpose  = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')
#     else:
#         material        = data.get('material', '')
#         item_type       = data.get('type', '')
#         frequency       = data.get('frequency', '')
#         quantity        = str(data.get('quantity', ''))
#         other_material  = data.get('material', '') if data.get('material') == 'Other' else ""
#         other_type      = data.get('type', '') if data.get('type') == 'Other' else ""
#         chosen_purpose  = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')

#     entry = DDEntry(
#         department=data.get('department', ''),
#         work=work_type,
#         date=data.get('date', ''),
#         Global=data.get('global_id', ''),
#         purpose=chosen_purpose,
#         material=material, 
#         other_material=other_material,
#         item_type=item_type, 
#         other_type=other_type,
#         frequency=frequency, 
#         quantity=quantity,
#         project=data.get('project_name', ''),
#         description=data.get('description', ''),
#         priority=chosen_priority,
#         item=data.get('item_status', ''),
#         task=data.get('task', '')
#     )
    
#     try:
#         db.session.add(entry)
#         db.session.commit()
#         return jsonify({"success": True, "message": "Record written successfully!"}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/api/entries', methods=['GET'])
# def get_all_records():
#     try:
#         entries = DDEntry.query.order_by(DDEntry.id.desc()).all()
#         return jsonify([entry.to_dict() for entry in entries]), 200
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
# def delete_entry(entry_id):
#     if not can_edit():
#         return jsonify({"error": "Unauthorized access"}), 403

#     entry = db.session.get(DDEntry, entry_id)
#     if not entry:
#         return jsonify({"success": False, "error": "Record not found"}), 404

#     try:
#         db.session.delete(entry)
#         db.session.commit()
#         return jsonify({"success": True, "message": "Record deleted"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500


# # Fetches a single record by id, used to pre-fill the Edit screen
# @app.route('/api/entries/<int:entry_id>', methods=['GET'])
# def get_entry(entry_id):
#     entry = db.session.get(DDEntry, entry_id)
#     if not entry:
#         return jsonify({"success": False, "error": "Record not found"}), 404
#     return jsonify(entry.to_dict()), 200


# # Updates a single record by id, used by the Edit screen's Save button
# @app.route('/api/entries/<int:entry_id>', methods=['PUT'])
# def update_entry(entry_id):
#     if not can_edit():
#         return jsonify({"error": "Unauthorized access"}), 403

#     entry = db.session.get(DDEntry, entry_id)
#     if not entry:
#         return jsonify({"success": False, "error": "Record not found"}), 404

#     data = request.json or {}
#     work_type = data.get('work_type', '')

#     if work_type == "Mechanical Design Related":
#         material = item_type = frequency = quantity = other_material = other_type = ""
#         chosen_purpose = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')
#     else:
#         material = data.get('material', '')
#         item_type = data.get('type', '')
#         frequency = data.get('frequency', '')
#         quantity = str(data.get('quantity', ''))
#         other_material = data.get('material', '') if data.get('material') == 'Other' else ""
#         other_type = data.get('type', '') if data.get('type') == 'Other' else ""
#         chosen_purpose = data.get('purpose', '')
#         chosen_priority = data.get('priority', '')

#     try:
#         entry.department = data.get('department', entry.department)
#         entry.work = work_type or entry.work
#         entry.date = data.get('date', entry.date)
#         entry.Global = data.get('global_id', entry.Global)
#         entry.purpose = chosen_purpose
#         entry.material = material
#         entry.other_material = other_material
#         entry.item_type = item_type
#         entry.other_type = other_type
#         entry.frequency = frequency
#         entry.quantity = quantity
#         entry.project = data.get('project_name', entry.project)
#         entry.description = data.get('description', entry.description)
#         entry.priority = chosen_priority
#         entry.item = data.get('item_status', entry.item)
#         entry.task = data.get('task', entry.task)

#         db.session.commit()
#         return jsonify({"success": True, "message": "Record updated successfully!"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500


# # Search records by Global ID, used by the Master Tracker screen
# @app.route('/api/entries/search', methods=['GET'])
# def search_entries():
#     global_id = request.args.get('global_id', '').strip()
#     if not global_id:
#         return jsonify({"success": False, "error": "global_id query param is required"}), 400

#     entries = DDEntry.query.filter(DDEntry.Global.i like(f"%{global_id}%")).order_by(DDEntry.id.desc()).all()
#     return jsonify([e.to_dict() for e in entries]), 200


# # Aggregated counts for the Dashboard's bar + pie charts
# @app.route('/api/dashboard-stats', methods=['GET'])
# def dashboard_stats():
#     entries = DDEntry.query.all()

#     dept_counts = Counter((e.department or 'Unspecified') for e in entries)
#     priority_counts = Counter((e.priority or 'Unspecified') for e in entries)

#     return jsonify({
#         "total_records": len(entries),
#         "dept_labels": list(dept_counts.keys()),
#         "dept_values": list(dept_counts.values()),
#         "priority_labels": list(priority_counts.keys()),
#         "priority_values": list(priority_counts.values()),
#     }), 200

# @app.route('/api/entries/excel', methods=['GET'])
# def download_excel():
#     try:
#         entries = DDEntry.query.order_by(DDEntry.id.desc()).all()
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "D&D Records"

#         headers = [
#             'S.No', 'Department', 'Work Type', 'Date', 'Global ID', 'Purpose',
#             'Material', 'Material (Other)', 'Type', 'Type (Other)',
#             'Frequency', 'Quantity', 'Project Name', 'Description',
#             'Priority', 'Item Status', 'Task'
#         ]
#         ws.append(headers)

#         # Use a sequential serial number (1, 2, 3, ...) rather than the raw
#         # database id, since deleting records leaves gaps in the id sequence
#         # (e.g. 5, 4, 3, 2) — this matches the "S.No" column the Flutter
#         # Reports table already shows.
#         for index, e in enumerate(entries, start=1):
#             row = e.to_dict()
#             ws.append([
#                 index, row.get('department', ''), row.get('workType', ''), row.get('date', ''),
#                 row.get('globalId', ''), row.get('purpose', ''), row.get('material', ''),
#                 row.get('otherMaterial', ''), row.get('itemType', ''), row.get('otherType', ''),
#                 row.get('frequency', ''), row.get('quantity', ''), row.get('projectName', ''),
#                 row.get('description', ''), row.get('priority', ''), row.get('status', ''), row.get('task', '')
#             ])

#         buffer = io.BytesIO()
#         wb.save(buffer)
#         buffer.seek(0)
#         return send_file(
#             buffer,
#             as_attachment=True,
#             download_name='dd_department_records.xlsx',
#             mimetype='application/vnd.open xml formats-office document.spread sheet ml.sheet'
#         )
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route('/api/entries/clear', methods=['DELETE'])
# def clear_all():
#     try:
#         db.session.query(DDEntry).delete()
#         db.session.commit()
#         return jsonify({"success": True, "message": "Database wiped clean"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500

# with app.app_context():
#     db.create_all()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True, port=5000)
