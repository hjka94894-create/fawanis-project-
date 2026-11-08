from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'fawanis_secret_key_2026'

# إنشاء قاعدة البيانات وتطوير الهيكل
def init_db():
    conn = sqlite3.connect('fawanis.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            national_id TEXT UNIQUE,
            full_name TEXT,
            phone TEXT,
            supervisor TEXT,
            status TEXT DEFAULT 'قيد الانتظار',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    national_id = data.get('national_id')
    full_name = data.get('full_name')
    phone = data.get('phone')
    supervisor = data.get('supervisor')

    conn = sqlite3.connect('fawanis.db')
    cursor = conn.cursor()
    
    # التحقق من وجود الرقم الوطني مسبقاً
    cursor.execute('SELECT id FROM requests WHERE national_id = ?', (national_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': 'تم التقديم بهذا الرقم الوطني مسبقاً!'}), 400

    cursor.execute('''
        INSERT INTO requests (national_id, full_name, phone, supervisor)
        VALUES (?, ?, ?, ?)
    ''', (national_id, full_name, phone, supervisor))
    
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    
    # توليد رقم عضوية فريد
    member_no = f"FK-2026-{request_id:04d}"
    return jsonify({'status': 'success', 'member_no': member_no})

# لوحة تحكم المشرفين الخاصة (محمية)
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'fawanis@2026':  # كلمة السر الخاصة بالمشرفين
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
    return '''
        <form method="post" style="text-align:center; margin-top:50px; font-family:sans-serif;">
            <h2>تسجيل دخول المشرفين - منظمة فوانيس الخير</h2>
            <input type="password" name="password" placeholder="كلمة المرور" required style="padding:10px;"><br><br>
            <button type="submit" style="padding:10px 20px;">دخول</button>
        </form>
    '''

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('fawanis.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, national_id, full_name, phone, supervisor, status FROM requests')
    rows = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', requests=rows)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
