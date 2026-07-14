from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DDEntry(db.Model):
    __tablename__ = 'dd_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), default="")
    work = db.Column(db.String(100), default="")
    date = db.Column(db.String(50), default="")
    Global = db.Column(db.String(100), default="")  # Matches request.form.get('Global')
    purpose = db.Column(db.String(100), default="")
    material = db.Column(db.String(100), default="")
    other_material = db.Column(db.String(100), default="")
    item_type = db.Column(db.String(100), default="")
    other_type = db.Column(db.String(100), default="")
    frequency = db.Column(db.String(100), default="")
    quantity = db.Column(db.String(50), default="")
    project = db.Column(db.String(200), default="")
    description = db.Column(db.Text, default="")
    priority = db.Column(db.String(100), default="")
    item = db.Column(db.String(50), default="")  # Status field ('In'/'Out')
    task = db.Column(db.String(100), default="")

    def to_dict(self):
        """Helper method to convert database records into JSON for your Flutter Reports view"""
        return {
            'id': self.id,
            'department': self.department,
            'workType': self.work, # Mapped to match frontend naming expectations
            'date': self.date,
            'globalId': self.Global,
            'purpose': self.purpose,
            'material': self.material,
            'otherMaterial': self.other_material,
            'itemType': self.item_type,
            'otherType': self.other_type,
            'frequency': self.frequency,
            'quantity': self.quantity,
            'projectName': self.project,
            'description': self.description,
            'priority': self.priority,
            'status': self.item,
            'task': self.task
        }