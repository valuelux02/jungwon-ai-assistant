from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCEDURES_FILE = os.path.join(DATA_DIR, 'procedures.json')
NOTICES_FILE = os.path.join(DATA_DIR, 'notices.json')

# Multilingual UI Dictionary (KO / EN / KM)
TRANSLATIONS = {
    'ko': {
        'title': '중원대학교 AI 학생 어시스턴트',
        'subtitle': 'Step 8 통합 프로토타입 (AI 챗봇 · 행정 가이드 · 공지사항 검색)',
        'tab_all': '통합 홈 / 전체',
        'tab_chat': '🤖 AI 챗봇',
        'tab_procedures': '📋 학생 행정 가이드',
        'tab_notices': '📢 대학 공지사항',
        'search_placeholder': '검색어를 입력하세요 (예: 휴학, 복학, 장학금, 기숙사, 졸업...)',
        'chat_placeholder': '학사 행정, 장학금, 공지 등에 관해 자유롭게 질문하세요...',
        'search_btn': '검색',
        'send_btn': '전송',
        'all_categories': '전체 카테고리',
        'no_results': '일치하는 결과가 없습니다.',
        'view_detail': '상세보기 →',
        'category': '분류',
        'date': '작성일',
        'author': '담당부서',
        'purpose': '목적',
        'who': '대상',
        'timing': '신청 기간',
        'required_docs': '제출 서류',
        'steps': '진행 절차',
        'office': '담당 부서 / 문의',
        'notes': '중요 안내',
        'source': '출처',
        'back_home': '← 메인으로 돌아가기',
        'quick_questions': '💡 추천 질문',
        'sample_q1': '휴학 신청은 어떻게 하나요?',
        'sample_q2': '장학금 신청 자격과 기간을 알려주세요.',
        'sample_q3': '기숙사 입사 절차와 필요 서류가 궁금해요.',
        'sample_q4': '재학증명서와 성적증명서는 어떻게 발급받나요?',
        'bot_welcome': '안녕하세요! 중원대학교 AI 학생 어시스턴트입니다. 행정 절차, 장학금, 기숙사, 최신 공지사항 등 궁금한 점을 편하게 물어보세요!',
        'health_check': '시스템 상태 정상'
    },
    'en': {
        'title': 'Jungwon University AI Student Assistant',
        'subtitle': 'Step 8 Integrated Prototype (AI Chatbot · Administrative Guide · Notice Search)',
        'tab_all': 'Unified Home',
        'tab_chat': '🤖 AI Chatbot',
        'tab_procedures': '📋 Administrative Guide',
        'tab_notices': '📢 University Notices',
        'search_placeholder': 'Enter keywords (e.g. leave, return, scholarship, dormitory, graduation...)',
        'chat_placeholder': 'Ask any questions about academic procedures, notices, or campus life...',
        'search_btn': 'Search',
        'send_btn': 'Send',
        'all_categories': 'All Categories',
        'no_results': 'No matching results found.',
        'view_detail': 'View Details →',
        'category': 'Category',
        'date': 'Date',
        'author': 'Office',
        'purpose': 'Purpose',
        'who': 'Eligibility',
        'timing': 'Period / Timing',
        'required_docs': 'Required Documents',
        'steps': 'Steps',
        'office': 'Department / Contact',
        'notes': 'Important Notes',
        'source': 'Source',
        'back_home': '← Back to Home',
        'quick_questions': '💡 Suggested Questions',
        'sample_q1': 'How do I apply for a leave of absence?',
        'sample_q2': 'What are the scholarship requirements and application dates?',
        'sample_q3': 'What is the dormitory application procedure and required documents?',
        'sample_q4': 'How can I get enrollment or transcript certificates issued?',
        'bot_welcome': 'Hello! I am the Jungwon University AI Student Assistant. Feel free to ask about administrative procedures, scholarships, dormitories, and university notices!',
        'health_check': 'System Status: Healthy'
    },
    'km': {
        'title': 'ជំនួយការនិស្សិត AI សាកលវិទ្យាល័យ Jungwon',
        'subtitle': 'គំរូរួមបញ្ចូលគ្នាជំហានទី ៨ (AI Chatbot · ការណែនាំរដ្ឋបាល · ស្វែងរកសេចក្តីជូនដំណឹង)',
        'tab_all': 'ទំព័រដើមរួមបញ្ចូលគ្នា',
        'tab_chat': '🤖 AI Chatbot',
        'tab_procedures': '📋 ការណែនាំរដ្ឋបាលនិស្សិត',
        'tab_notices': '📢 សេចក្តីជូនដំណឹងសាកលវិទ្យាល័យ',
        'search_placeholder': 'បញ្ចូលពាក្យស្វែងរក (ឧទាហរណ៍៖ ព្យួរការសិក្សា, អាហារូបករណ៍, អន្តេវាសិកដ្ឋាន...)',
        'chat_placeholder': 'សួរសំណួរទាក់ទងនឹងការសិក្សា នីតិវិធីរដ្ឋបាល ឬសេចក្តីជូនដំណឹង...',
        'search_btn': 'ស្វែងរក',
        'send_btn': 'ផ្ញើ',
        'all_categories': 'ប្រភេទទាំងអស់',
        'no_results': 'រកមិនឃើញលទ្ធផលដែលត្រូវគ្នាទេ។',
        'view_detail': 'មើលលម្អិត →',
        'category': 'ប្រភេទ',
        'date': 'កាលបរិច្ឆេទ',
        'author': 'ការិយាល័យ',
        'purpose': 'គោលបំណង',
        'who': 'សិទ្ធិទទួលបាន',
        'timing': 'កាលបរិច្ឆេទ',
        'required_docs': 'ឯកសារចាំបាច់',
        'steps': 'ជំហានអនុវត្ត',
        'office': 'ការិយាល័យ / ទំនាក់ទំនង',
        'notes': 'ចំណាំសំខាន់ៗ',
        'source': 'ប្រភព',
        'back_home': '← ត្រឡប់ទៅទំព័រដើម',
        'quick_questions': '💡 សំណួរដែលបានស្នើ',
        'sample_q1': 'តើខ្ញុំត្រូវដាក់ពាក្យសុំព្យួរការសិក្សាដោយរបៀបណា?',
        'sample_q2': 'តើលក្ខខណ្ឌនិងកាលបរិច្ឆេទអាហារូបករណ៍មានអ្វីខ្លះ?',
        'sample_q3': 'តើនីតិវិធីចូលស្នាក់នៅអន្តេវាសិកដ្ឋានយ៉ាងដូចម្តេច?',
        'sample_q4': 'តើខ្ញុំអាចស្នើសុំលិខិតបញ្ជាក់ការសិក្សាដោយរបៀបណា?',
        'bot_welcome': 'សួស្តី! ខ្ញុំជាជំនួយការនិស្សិត AI សាកលវិទ្យាល័យ Jungwon។ សូមសួរសំណួរអំពីនីតិវិធីរដ្ឋបាល អាហារូបករណ៍ អន្តេវាសិកដ្ឋាន និងសេចក្តីជូនដំណឹង។',
        'health_check': 'ស្ថានភាពម៉ាស៊ីនបម្រើ៖ ប្រក្រតី'
    }
}

def load_procedures():
    if os.path.exists(PROCEDURES_FILE):
        with open(PROCEDURES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_notices():
    if os.path.exists(NOTICES_FILE):
        with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_current_lang():
    lang = request.args.get('lang', 'ko').lower()
    return lang if lang in TRANSLATIONS else 'ko'

@app.route('/')
def index():
    lang = get_current_lang()
    t = TRANSLATIONS[lang]
    
    procedures = load_procedures()
    notices = load_notices()
    
    q = request.args.get('q', '').strip()
    active_tab = request.args.get('tab', 'all')
    category = request.args.get('category', '').strip()
    
    # Filtering procedures
    filtered_procedures = procedures
    if q:
        filtered_procedures = [p for p in filtered_procedures if q.lower() in json.dumps(p, ensure_ascii=False).lower()]
    if category and active_tab == 'procedures':
        filtered_procedures = [p for p in filtered_procedures if p.get('category') == category]
        
    # Filtering notices
    filtered_notices = notices
    if q:
        filtered_notices = [n for n in filtered_notices if q.lower() in json.dumps(n, ensure_ascii=False).lower()]
    if category and active_tab == 'notices':
        filtered_notices = [n for n in filtered_notices if n.get('category') == category]
        
    proc_categories = sorted({p.get('category') for p in procedures if p.get('category')})
    notice_categories = sorted({n.get('category') for n in notices if n.get('category')})
    
    return render_template(
        'index.html',
        lang=lang,
        t=t,
        procedures=filtered_procedures,
        notices=filtered_notices,
        proc_categories=proc_categories,
        notice_categories=notice_categories,
        q=q,
        active_tab=active_tab,
        selected_category=category
    )

@app.route('/procedure/<int:pid>')
def procedure_detail(pid):
    lang = get_current_lang()
    t = TRANSLATIONS[lang]
    procedures = load_procedures()
    item = next((p for p in procedures if p.get('id') == pid), None)
    if not item:
        return 'Procedure not found', 404
    return render_template('procedure.html', p=item, lang=lang, t=t)

@app.route('/notice/<int:nid>')
def notice_detail(nid):
    lang = get_current_lang()
    t = TRANSLATIONS[lang]
    notices = load_notices()
    item = next((n for n in notices if n.get('id') == nid), None)
    if not item:
        return 'Notice not found', 404
    return render_template('notice.html', n=item, lang=lang, t=t)

@app.route('/health')
def health():
    procedures = load_procedures()
    notices = load_notices()
    return jsonify({
        'status': 'healthy',
        'service': 'Jungwon University AI Student Assistant',
        'step': 8,
        'port': 5008,
        'procedures_count': len(procedures),
        'notices_count': len(notices),
        'supported_languages': ['ko', 'en', 'km']
    })

@app.route('/api/procedures')
def api_procedures():
    return jsonify(load_procedures())

@app.route('/api/notices')
def api_notices():
    return jsonify(load_notices())

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip().lower()
    procedures = load_procedures()
    notices = load_notices()
    
    if q:
        proc_matches = [p for p in procedures if q in json.dumps(p, ensure_ascii=False).lower()]
        notice_matches = [n for n in notices if q in json.dumps(n, ensure_ascii=False).lower()]
    else:
        proc_matches = procedures
        notice_matches = notices
        
    return jsonify({
        'query': q,
        'procedures': proc_matches,
        'notices': notice_matches,
        'total': len(proc_matches) + len(notice_matches)
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    lang = data.get('lang', 'ko').lower()
    if lang not in TRANSLATIONS:
        lang = 'ko'
        
    if not message:
        return jsonify({'reply': '질문을 입력해 주세요.' if lang == 'ko' else 'Please enter your question.'})
        
    msg_lower = message.lower()
    procedures = load_procedures()
    notices = load_notices()
    
    # Simple semantic rule-matching / RAG prototype search
    matched_procs = [p for p in procedures if any(k in msg_lower for k in [p['title'].lower(), p['category'].lower()[:2]])]
    if not matched_procs:
        matched_procs = [p for p in procedures if any(term in json.dumps(p, ensure_ascii=False).lower() for term in msg_lower.split())]
        
    matched_notices = [n for n in notices if any(k in msg_lower for k in [n['title'].lower(), n['category'].lower()])]
    if not matched_notices:
        matched_notices = [n for n in notices if any(term in json.dumps(n, ensure_ascii=False).lower() for term in msg_lower.split())]
        
    sources = []
    
    # Constructing intelligent prototype response
    if lang == 'en':
        if matched_procs:
            p = matched_procs[0]
            sources.append(f"Guide: {p['title']}")
            reply = f"Here is the guidance for **{p['title']}** ({p['category']}):\n\n"
            reply += f"• **Purpose**: {p['purpose']}\n"
            reply += f"• **Eligibility**: {p['who']}\n"
            reply += f"• **Required Documents**: {', '.join(p.get('documents', []))}\n"
            reply += f"• **Steps**: {' → '.join(p.get('steps', []))}\n"
            reply += f"• **Notice**: {p.get('timing', '')} (Contact: {p.get('office', 'Academic Affairs')})\n\n"
            reply += "*(Note: Prototype placeholder data. Please refer to official school regulations for exact dates.)*"
        elif matched_notices:
            n = matched_notices[0]
            sources.append(f"Notice: {n['title']}")
            reply = f"Found university notice related to your question:\n\n"
            reply += f"📢 **[{n['category']}] {n['title']}** (Date: {n['date']}, Dept: {n['author']})\n\n"
            reply += f"{n['content']}\n\n"
            reply += f"Check full notice on the university board."
        else:
            reply = f"I couldn't find an exact match for '{message}'. You can ask about leave of absence, return to school, certificates, scholarships, graduation requirements, or dormitory policies. You can also contact the relevant university academic office for direct assistance."
    elif lang == 'km':
        if matched_procs:
            p = matched_procs[0]
            sources.append(f"ការណែនាំ: {p['title']}")
            reply = f"នេះជាព័ត៌មានណែនាំទាក់ទងនឹង **{p['title']}** ({p['category']}):\n\n"
            reply += f"• **គោលបំណង**: {p['purpose']}\n"
            reply += f"• **សិទ្ធិទទួលបាន**: {p['who']}\n"
            reply += f"• **ឯកសារចាំបាច់**: {', '.join(p.get('documents', []))}\n"
            reply += f"• **ជំហានអនុវត្ត**: {' → '.join(p.get('steps', []))}\n"
            reply += f"• **កាលបរិច្ឆេទ**: {p.get('timing', '')} (ការិយាល័យ: {p.get('office', 'កិច្ចការសិក្សា')})\n\n"
            reply += "*(សម្គាល់៖ នេះជាទិន្នន័យគំរូបឋម។ សូមពិនិត្យបទប្បញ្ញត្តិផ្លូវការរបស់សាកលវិទ្យាល័យ។)*"
        elif matched_notices:
            n = matched_notices[0]
            sources.append(f"សេចក្តីជូនដំណឹង: {n['title']}")
            reply = f"បានរកឃើញសេចក្តីជូនដំណឹងរបស់សាកលវិទ្យាល័យដែលពាក់ព័ន្ធ៖\n\n"
            reply += f"📢 **[{n['category']}] {n['title']}** (កាលបរិច្ឆេទ៖ {n['date']}, ផ្នែក៖ {n['author']})\n\n"
            reply += f"{n['content']}"
        else:
            reply = f"ខ្ញុំមិនអាចស្វែងរកចម្លើយច្បាស់លាស់សម្រាប់ '{message}' បានទេ។ អ្នកអាចសួរអំពីការសុំព្យួរការសិក្សា, ការចូលរៀនវិញ, លិខិតបញ្ជាក់, អាហារូបករណ៍, លក្ខខណ្ឌបញ្ចប់ការសិក្សា ឬអន្តេវាសិកដ្ឋាន។"
    else:  # Korean default
        if matched_procs:
            p = matched_procs[0]
            sources.append(f"행정 가이드: {p['title']}")
            reply = f"**{p['title']}** ({p['category']}) 관련 안내입니다.\n\n"
            reply += f"• **목적**: {p['purpose']}\n"
            reply += f"• **신청 대상**: {p['who']}\n"
            reply += f"• **제출 서류**: {', '.join(p.get('documents', []))}\n"
            reply += f"• **진행 절차**: {' → '.join(p.get('steps', []))}\n"
            reply += f"• **신청 기간/부서**: {p.get('timing', '')} ({p.get('office', '교무처')})\n\n"
            if matched_notices:
                n = matched_notices[0]
                sources.append(f"관련 공지: {n['title']}")
                reply += f"📌 **관련 공지사항 안내**: [{n['category']}] {n['title']} ({n['date']})\n"
                reply += f"{n['content']}\n\n"
            reply += "※ 본 안내는 Step 8 프로토타입 기준이며, 실제 신청 시 학교 공식 학사공지를 반드시 확인하시기 바랍니다."
        elif matched_notices:
            n = matched_notices[0]
            sources.append(f"공지사항: {n['title']}")
            reply = f"질문하신 내용과 관련된 학교 공지사항을 찾았습니다.\n\n"
            reply += f"📢 **[{n['category']}] {n['title']}** (게시일: {n['date']}, 담당: {n['author']})\n\n"
            reply += f"{n['content']}\n\n"
            reply += "상세 내용은 공지사항 탭에서 전체 확인이 가능합니다."
        else:
            reply = f"'{message}'에 대한 정보를 찾기 어렵습니다. '휴학', '복학', '장학금', '증명서', '졸업요건', '기숙사' 또는 최신 공지사항과 관련된 키워드로 질문해 주시면 상세히 안내해 드리겠습니다."

    return jsonify({
        'reply': reply,
        'sources': sources
    })

if __name__ == '__main__':
    print("Jungwon University AI Student Assistant - Step 8 Prototype starting on http://127.0.0.1:5008")
    app.run(host='127.0.0.1', port=5008, debug=True)
