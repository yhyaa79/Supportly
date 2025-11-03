
from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify, flash
from flask import send_from_directory




app = Flask(__name__)
app.secret_key = 'my_secret_key'  # باید یه مقدار تصادفی و امن باشه

# Update the index route to call process_free_charge
@app.route('/')
def index():
  

    return send_from_directory('static/html', 'index.html')



@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'پیام یافت نشد'}), 400

        user_message = data['message']
        link_web = data['linkWeb']
        print("پیام کاربر:", user_message)
        print(link_web)

        # اینجا می‌تونی به مدل هوش مصنوعی بفرستی یا هر پاسخی بخوای
        ai_reply = "دریافت شد: " + user_message  # موقت

        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"خطا: {e}")
        return jsonify({'error': 'خطای سرور'}), 500





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8060, debug=True)

