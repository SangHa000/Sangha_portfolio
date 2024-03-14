from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import json

app = Flask(__name__)

# 카카오톡 플러스친구 API 요청 주소
KAKAO_API_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

# 플러스친구 API 인증 토큰
KAKAO_API_TOKEN = "YOUR_KAKAO_API_TOKEN"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'  # SQLite 데이터베이스 사용
db = SQLAlchemy(app)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/keyboard')
def keyboard():
    return jsonify({
        'type': 'buttons',
        'buttons': ['계산서 발행', '비밀번호 조회', '비밀번호 초기화', '안내서류 발송', '앱 업데이트 후 알림이 오지 않을 때']
    })

@app.route('/message', methods=['POST'])
def message():
    data_received = request.get_json()
    content = data_received['content']

    if content == '계산서 발행':
        response = {
            'message': {
                'text': '발행 방식을 선택해주세요.',
                'message_button': {
                    'label': '발행 방식 선택',
                    'url': '카카오톡 링크 URL'  # 나중에 카카오링크 넣어야함
                }
            }
        }
    elif content == '발행 방식 선택 링크 클릭':
        response = {
            'message': {
                'text': '발행 방식을 선택해주세요.',
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['1년치 66만원 발행', '특정 월당 6만원 발행']
                }
            }
        }
    elif content == '1년치 66만원 발행':
        response = {
            'message': {
                'text': '1년치 66만원 발행 서비스를 선택했습니다.'
            }
        }
    elif content == '특정 월당 6만원 발행':
        response = {
            'message': {
                'text': '특정 월당 6만원 발행 서비스를 선택했습니다.'
            }
        }
    elif content == '비밀번호 조회':
        response = {
            'message': {
                'text': '비밀번호 조회 서비스를 선택했습니다.'
            }
        }
    elif content == '비밀번호 초기화':
        response = {
            'message': {
                'text': '비밀번호 초기화 서비스를 선택했습니다.'
            }
        }
    elif content == '안내서류 발송':
        response = {
            'message': {
                'text': '서류를 받을 이메일 주소를 알려주십시오.'
            },
            'keyboard': {
                'type': 'text'
            }
        }
    elif content == '앱 업데이트 후 알림이 오지 않을 때':
        response = {
            'message': {
                'text': '안녕하세요, tcall 교원안심번호서비스입니다.\n\n'
                        '앱 업데이트 완료 후에도 문자 알림이 오지 않을 경우 설정 방법입니다.\n\n'
                        '1. 절전모드 해제\n'
                        '2. 휴대폰 설정 => 애플리케이션 => Tcall 교원안심번호 => 저장공간 => 데이터 삭제, 캐쉬 삭제\n'
                        '3. 앱 재실행(권한 허용 재설정)\n'
                        '4. 기본전화 앱 설정 알림이 표시될때 - Tcall 교원안심번호 기본앱으로 설정 적용'
            }
        }
    else:
        response = {
            'message': {
                'text': '올바른 선택이 아닙니다. 다시 선택해주세요.'
            }
        }

    # 다른 질문은 5~10분 내에 처리될 예정임을 알려주는 메시지 추가
    response['message']['text'] += '\n\n기타 문의 사항은 5~10분 내에 답변될 예정입니다.'

    @app.route('/email', methods=['POST'])
    def save_email():
        data_received = request.get_json()
        email_address = data_received['email']

        # 이메일 주소를 데이터베이스에 저장
        new_email = Email(address=email_address)
        db.session.add(new_email)
        db.session.commit()

        return jsonify({'message': '이메일 주소가 저장되었습니다.'})

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_key = data['userRequest']['user']['id']
    content = data['userRequest']['utterance']

    response = process_message(content)

    send_kakao_message(user_key, response)

    return jsonify({'success': True})


# 받은 메시지를 처리하는 함수
def process_message(content):
    # 여기에 메시지 처리 로직을 추가
    response = "당신이 보낸 메시지: " + content
    return response

# 카카오톡 메시지를 전송하는 함수
def send_kakao_message(user_key, message):
    headers = {
        "Authorization": "Bearer " + KAKAO_API_TOKEN
    }
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "http://your-website.com",
            },
        })
    }
    response = requests.post(KAKAO_API_URL, headers=headers, data=data)
    return response


if __name__ == '__main__':
    app.run(debug=True)
