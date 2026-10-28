# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import json
import os
import sllm_engine
import form_generator

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCEDURES_FILE = os.path.join(DATA_DIR, 'procedures.json')
NOTICES_FILE = os.path.join(DATA_DIR, 'notices.json')
CALENDAR_FILE = os.path.join(DATA_DIR, 'calendar.json')
SLLM_INFO_FILE = os.path.join(DATA_DIR, 'sllm_info.json')

# 6 Supported Languages
LANGUAGES_METADATA = sllm_engine.SUPPORTED_LANGUAGES

# Multilingual UI Dictionary (KO / EN / VI / UZ / NE / KM)
TRANSLATIONS = {
    'ko': {
        'title': '중원대학교 AI 학생 어시스턴트',
        'subtitle': 'sLLM 학사행정 Q&A · 5개 국어 실시간 번역 · 스마트 서식 도우미',
        'tab_all': '통합 홈',
        'tab_chat': '🤖 AI 챗봇 (sLLM)',
        'tab_translate': '🌐 다국어 번역기',
        'tab_calendar': '📅 학사일정 & D-Day',
        'tab_forms': '📄 스마트 행정 서식',
        'tab_procedures': '📋 학생 행정 가이드',
        'tab_notices': '📢 대학 공지사항',
        'search_placeholder': '검색어를 입력하세요 (예: 휴학, 복학, 장학금, 기숙사, 비자, 등록금, 결핵검사...)',
        'chat_placeholder': '학사 행정, 비자, 장학금에 대해 자유롭게 질문하거나 마이크를 눌러 음성으로 말하세요...',
        'translate_placeholder': '번역할 내용을 입력하세요 (한국어, 베트남어, 영어, 크메르어, 네팔어, 우즈베크어 지원)...',
        'search_btn': '검색',
        'send_btn': '전송',
        'translate_btn': '번역하기',
        'swap_btn': '⇄ 언어 전환',
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
        'quick_questions': '💡 추천 질문 (Q&A)',
        'sample_q1': '휴학 신청 절차와 유의사항을 알려주세요.',
        'sample_q2': '외국인 유학생 장학금 기준과 신청 기간은 어떻게 되나요?',
        'sample_q3': '기숙사 입사 시 결핵검사서 제출 방법이 궁금해요.',
        'sample_q4': '외국인 유학생 D-2 비자 연장 및 아르바이트 허가 절차는?',
        'sample_q5': '등록금 분할납부 신청 방법과 납부 일정을 알려주세요.',
        'bot_welcome': '안녕하세요! 중원대학교 AI 학생 어시스턴트(sLLM 지식 엔진 v3.0)입니다. 학사 행정, 비자 연장, 장학금, 기숙사 등 궁금한 점을 질문하시거나 음성(🎙️) 및 다국어 번역 기능을 이용해 보세요!',
        'health_check': '시스템 상태 정상 (sLLM 가동 중)',
        'sllm_badge': 'sLLM 지식 추론 엔진 v3.0',
        'translate_source': '원본 언어',
        'translate_target': '번역 언어',
        'translate_copy': '📋 번역문 복사',
        'translate_copied': '✓ 복사 완료!'
    },
    'en': {
        'title': 'Jungwon University AI Student Assistant',
        'subtitle': 'sLLM Academic Q&A · 5-Language Real-time Translation · Smart Form Generator',
        'tab_all': 'Home',
        'tab_chat': '🤖 AI Chatbot (sLLM)',
        'tab_translate': '🌐 Multilingual Translator',
        'tab_calendar': '📅 Calendar & D-Day',
        'tab_forms': '📄 Smart Form Generator',
        'tab_procedures': '📋 Administrative Guide',
        'tab_notices': '📢 University Notices',
        'search_placeholder': 'Enter keywords (e.g. leave, scholarship, dormitory, visa, tuition, TB test...)',
        'chat_placeholder': 'Ask any question or click mic (🎙️) to speak in your language...',
        'translate_placeholder': 'Enter text to translate (Korean, Vietnamese, English, Khmer, Nepali, Uzbek)...',
        'search_btn': 'Search',
        'send_btn': 'Send',
        'translate_btn': 'Translate',
        'swap_btn': '⇄ Swap',
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
        'quick_questions': '💡 Suggested Questions (Q&A)',
        'sample_q1': 'What is the leave of absence application procedure and rules?',
        'sample_q2': 'What are the scholarship requirements and deadlines for international students?',
        'sample_q3': 'How to apply for the dormitory and submit tuberculosis (TB) test?',
        'sample_q4': 'How to extend D-2 visa and get part-time work permit (Arbeit)?',
        'sample_q5': 'How to apply for tuition installment payments and what is the schedule?',
        'bot_welcome': 'Hello! I am the Jungwon University AI Student Assistant powered by sLLM v3.0. Feel free to ask about academic administration, visas, scholarships, or use voice input and translation tools!',
        'health_check': 'System Status: Healthy (sLLM Active)',
        'sllm_badge': 'sLLM Knowledge Reasoning Engine v3.0',
        'translate_source': 'Source Language',
        'translate_target': 'Target Language',
        'translate_copy': '📋 Copy Translation',
        'translate_copied': '✓ Copied!'
    },
    'vi': {
        'title': 'Trợ lý sinh viên AI Đại học Jungwon',
        'subtitle': 'sLLM Học vụ & Hệ thống dịch thuật thời gian thực 5 ngôn ngữ & Tạo đơn hành chính',
        'tab_all': 'Trang chủ',
        'tab_chat': '🤖 AI Chatbot (sLLM)',
        'tab_translate': '🌐 Dịch thuật đa ngôn ngữ',
        'tab_calendar': '📅 Lịch học & D-Day',
        'tab_forms': '📄 Hỗ trợ tạo đơn hành chính',
        'tab_procedures': '📋 Hướng dẫn hành chính',
        'tab_notices': '📢 Thông báo đại học',
        'search_placeholder': 'Nhập từ khóa (nghỉ học, học bổng, ký túc xá, visa, học phí, khám lao...)',
        'chat_placeholder': 'Đặt câu hỏi bằng Tiếng Việt hoặc bấm micro (🎙️) để nói chuyện...',
        'translate_placeholder': 'Nhập nội dung cần dịch (Hàn, Việt, Anh, Khmer, Nepal, Uzbek)...',
        'search_btn': 'Tìm kiếm',
        'send_btn': 'Gửi',
        'translate_btn': 'Dịch ngay',
        'swap_btn': '⇄ Đổi chiều',
        'all_categories': 'Tất cả danh mục',
        'no_results': 'Không tìm thấy kết quả phù hợp.',
        'view_detail': 'Xem chi tiết →',
        'category': 'Phân loại',
        'date': 'Ngày đăng',
        'author': 'Phòng ban',
        'purpose': 'Mục đích',
        'who': 'Đối tượng',
        'timing': 'Thời gian đăng ký',
        'required_docs': 'Hồ sơ cần nộp',
        'steps': 'Quy trình thực hiện',
        'office': 'Bộ phận phụ trách / Liên hệ',
        'notes': 'Lưu ý quan trọng',
        'source': 'Nguồn',
        'back_home': '← Quay lại trang chủ',
        'quick_questions': '💡 Câu hỏi gợi ý (Q&A)',
        'sample_q1': 'Thủ tục xin nghỉ học tạm thời (휴학) và những điều cần lưu ý?',
        'sample_q2': 'Tiêu chuẩn học bổng du học sinh và thời gian nộp đơn?',
        'sample_q3': 'Cách đăng ký ký túc xá và nộp giấy khám lao phổi (X-ray)?',
        'sample_q4': 'Thủ tục gia hạn visa D-2 và xin giấy phép đi làm thêm?',
        'sample_q5': 'Cách đăng ký trả góp học phí và thời hạn đóng tiền?',
        'bot_welcome': 'Xin chào! Tôi là Trợ lý AI Sinh viên Jungwon (sLLM v3.0). Bạn có thể hỏi về thủ tục học tập, visa, ký túc xá, nộp đơn hoặc sử dụng giọng nói và công cụ dịch thuật!',
        'health_check': 'Hệ thống bình thường (sLLM)',
        'sllm_badge': 'Động cơ tri thức sLLM v3.0',
        'translate_source': 'Ngôn ngữ gốc',
        'translate_target': 'Ngôn ngữ đích',
        'translate_copy': '📋 Sao chép bản dịch',
        'translate_copied': '✓ Đã sao chép!'
    },
    'uz': {
        'title': 'Jungwon Universiteti AI Talaba Assistenti',
        'subtitle': "sLLM Ma'muriy Q&A · 5 tilda real vaqtda tarjima · Aqlli ariza yaratuvchi",
        'tab_all': 'Bosh sahifa',
        'tab_chat': '🤖 AI Chatbot (sLLM)',
        'tab_translate': '🌐 Ko\'p tilli tarjimon',
        'tab_calendar': '📅 Taqvim va D-Day',
        'tab_forms': '📄 Aqlli ariza yaratuvchi',
        'tab_procedures': "📋 Ma'muriy qo'llanma",
        'tab_notices': "📢 Universitet e'lonlari",
        'search_placeholder': "Kalit so'zni kiriting (ta'til, stipendiya, yotoqxona, viza, to'lov kontrakt...)",
        'chat_placeholder': "O'zbek tilida savol bering yoki mikrofon (🎙️) orqali gapiring...",
        'translate_placeholder': "Tarjima qilinadigan matnni kiriting (Koreys, Vetnam, Ingliz, Kxmer, Nepal, O'zbek)...",
        'search_btn': 'Qidirish',
        'send_btn': 'Yuborish',
        'translate_btn': 'Tarjima qilish',
        'swap_btn': "⇄ Tilni almashtirish",
        'all_categories': 'Barcha toifalar',
        'no_results': 'Mos natijalar topilmadi.',
        'view_detail': "Batafsil ko'rish →",
        'category': 'Toifa',
        'date': 'Sana',
        'author': "Bo'lim",
        'purpose': 'Maqsad',
        'who': 'Kimlar uchun',
        'timing': 'Ariza muddati',
        'required_docs': 'Kerakli hujjatlar',
        'steps': 'Bosqichlar',
        'office': "Mas'ul bo'lim / Aloqa",
        'notes': 'Muhim eslatma',
        'source': 'Manba',
        'back_home': '← Asosiy sahifaga qaytish',
        'quick_questions': '💡 Tavsiya etilgan savollar (Q&A)',
        'sample_q1': "Akademik ta'til (휴학) olish tartibi va qoidalari qanday?",
        'sample_q2': 'Xorijiy talabalar uchun stipendiya talablari va muddatlari?',
        'sample_q3': "Yotoqxonaga ariza berish va sil kasalligi (X-ray) tekshiruvini topshirish?",
        'sample_q4': "D-2 vizasini uzaytirish va yarim stavka ishlash (arbayt) ruxsatnomasi?",
        'sample_q5': "To'lov-shartnoma pulini bo'lib to'lash tartibi va muddati?",
        'bot_welcome': "Assalomu alaykum! Men Jungwon universiteti AI yordamchisiman (sLLM v3.0). Ta'til, stipendiya, viza yoki ariza yozish bo'yicha erkin savol bering!",
        'health_check': 'Tizim holati: Barqaror (sLLM faol)',
        'sllm_badge': 'sLLM bilim dvigateli v3.0',
        'translate_source': 'Boshlang\'ich til',
        'translate_target': 'Tarjima tili',
        'translate_copy': '📋 Tarjimani nusxalash',
        'translate_copied': '✓ Nusxalandi!'
    },
    'ne': {
        'title': 'जुङवोन विश्वविद्यालय एआई विद्यार्थी सहायक',
        'subtitle': 'sLLM प्रशासनिक प्रश्नोत्तर · ५ भाषाहरूमा प्रत्यक्ष अनुवाद · स्मार्ट फारम सहायक',
        'tab_all': 'गृहपृष्ठ',
        'tab_chat': '🤖 एआई च्याटबोट (sLLM)',
        'tab_translate': '🌐 बहुभाषिक अनुवादक',
        'tab_calendar': '📅 क्यालेन्डर र D-Day',
        'tab_forms': '📄 स्मार्ट फारम सहायक',
        'tab_procedures': '📋 प्रशासनिक मार्गदर्शन',
        'tab_notices': '📢 विश्वविद्यालय सूचनाहरू',
        'search_placeholder': 'खोज्नुहोस् (बिदा, छात्रवृत्ति, छात्रावास, भिसा, ट्यूशन, क्षयरोग...)',
        'chat_placeholder': 'नेपालीमा प्रश्न सोध्नुहोस् वा माइक (🎙️) थिचेर बोल्नुहोस्...',
        'translate_placeholder': 'अनुवाद गर्न यहाँ लेख्नुहोस् (कोरियाली, भियतनामी, अंग्रेजी, खमेर, नेपाली, उज्बेक)...',
        'search_btn': 'खोज्नुहोस्',
        'send_btn': 'पठाउनुहोस्',
        'translate_btn': 'अनुवाद गर्नुहोस्',
        'swap_btn': '⇄ भाषा बदल्नुहोस्',
        'all_categories': 'सबै वर्गहरू',
        'no_results': 'कुनै नतिजा फेला परेन।',
        'view_detail': 'विवरण हेर्नुहोस् →',
        'category': 'वर्ग',
        'date': 'मिति',
        'author': 'विभाग',
        'purpose': 'उद्देश्य',
        'who': 'योग्यता',
        'timing': 'आवेदन अवधि',
        'required_docs': 'आवश्यक कागजातहरू',
        'steps': 'प्रक्रिया चरणहरू',
        'office': 'सम्पर्क विभाग',
        'notes': 'महत्वपूर्ण सूचना',
        'source': 'स्रोत',
        'back_home': '← गृहपृष्ठमा फर्कनुहोस्',
        'quick_questions': '💡 सिफारिस गरिएका प्रश्नहरू (Q&A)',
        'sample_q1': 'अध्ययन बिदा (휴학) लिने प्रक्रिया र नियमहरू के हुन्?',
        'sample_q2': 'अन्तर्राष्ट्रिय विद्यार्थीहरूको लागि छात्रवृत्ति आवश्यकताहरू के हुन्?',
        'sample_q3': 'छात्रावास आवेदन र क्षयरोग (TB) परीक्षण रिपोर्ट कसरी बुझाउने?',
        'sample_q4': 'D-2 भिसा थप र पार्ट-टाइम काम अनुमति कसरी लिने?',
        'sample_q5': 'ट्यूशन शुल्क किस्ता भुक्तानी आवेदन प्रक्रिया के हो?',
        'bot_welcome': 'नमस्कार! म जुङवोन विश्वविद्यालय एआई विद्यार्थी सहायक (sLLM v3.0) हुँ। प्रशासनिक प्रक्रिया, छात्रवृत्ति वा भिसाबारे सोध्नुहोस्!',
        'health_check': 'प्रणाली स्थिति: सामान्य (sLLM सक्रिय)',
        'sllm_badge': 'sLLM ज्ञान इन्जिन v3.0',
        'translate_source': 'स्रोत भाषा',
        'translate_target': 'लक्ष्य भाषा',
        'translate_copy': '📋 अनुवाद प्रतिलिपि गर्नुहोस्',
        'translate_copied': '✓ प्रतिलिपि गरियो!'
    },
    'km': {
        'title': 'ជំនួយការនិស្សិត AI សាកលវិទ្យាល័យ Jungwon',
        'subtitle': 'sLLM សំណួរ-ចម្លើយរដ្ឋបាលសិក្សា · ការបកប្រែពហុភាសា · ជំនួយការទម្រង់រដ្ឋបាល',
        'tab_all': 'ទំព័រដើម',
        'tab_chat': '🤖 AI Chatbot (sLLM)',
        'tab_translate': '🌐 អ្នកបកប្រែពហុភាសា',
        'tab_calendar': '📅 ប្រតិទិនសិក្សា & D-Day',
        'tab_forms': '📄 ទម្រង់រដ្ឋបាលឆ្លាតវៃ',
        'tab_procedures': '📋 ការណែនាំរដ្ឋបាល',
        'tab_notices': '📢 សេចក្តីជូនដំណឹង',
        'search_placeholder': 'បញ្ចូលពាក្យស្វែងរក (ព្យួរការសិក្សា, អាហារូបករណ៍, ទិដ្ឋាការ, ថ្លៃសិក្សា...)',
        'chat_placeholder': 'សួរសំណួរ ឬចុចមីក្រូហ្វូន (🎙️) ដើម្បីនិយាយ...',
        'translate_placeholder': 'បញ្ចូលអត្ថបទដែលត្រូវបកប្រែ...',
        'search_btn': 'ស្វែងរក',
        'send_btn': 'ផ្ញើ',
        'translate_btn': 'បកប្រែ',
        'swap_btn': '⇄ ផ្លាស់ប្តូរភាសា',
        'all_categories': 'ប្រភេទទាំងអស់',
        'no_results': 'រកមិនឃើញលទ្ធផលដែលត្រូវគ្នាទេ។',
        'view_detail': 'មើលលម្អិត →',
        'category': 'ប្រភេទ',
        'date': 'កាលបរិច្ឆេទ',
        'author': 'ការិយាល័យ',
        'purpose': 'គោលបំណង',
        'who': 'សិទ្ធិទទួលបាន',
        'timing': 'កាលបរិច្ឆេទដាក់ពាក្យ',
        'required_docs': 'ឯកសារចាំបាច់',
        'steps': 'ជំហានអនុវត្ត',
        'office': 'ការិយាល័យ / ទំនាក់ទំនង',
        'notes': 'ចំណាំសំខាន់ៗ',
        'source': 'ប្រភព',
        'back_home': '← ត្រឡប់ទៅទំព័រដើម',
        'quick_questions': '💡 សំណួរដែលបានស្នើ (Q&A)',
        'sample_q1': 'តើខ្ញុំត្រូវដាក់ពាក្យសុំព្យួរការសិក្សា (휴학) យ៉ាងដូចម្តេច?',
        'sample_q2': 'តើលក្ខខណ្ឌអាហារូបករណ៍សម្រាប់និស្សិតអន្តរជាតិមានអ្វីខ្លះ?',
        'sample_q3': 'តើនីតិវិធីចូលស្នាក់នៅអន្តេវាសិកដ្ឋានយ៉ាងដូចម្តេច?',
        'sample_q4': 'របៀបបន្តទិដ្ឋាការ D-2 និងសុំការអនុញ្ញាតធ្វើការងារក្រៅម៉ោង?',
        'sample_q5': 'របៀបបង់ថ្លៃសិក្សាជារំលស់?',
        'bot_welcome': 'សួស្តី! ខ្ញុំជាជំនួយការនិស្សិត AI សាកលវិទ្យាល័យ Jungwon (sLLM v3.0)។',
        'health_check': 'ស្ថានភាពម៉ាស៊ីនបម្រើ៖ ប្រក្រតី',
        'sllm_badge': 'sLLM v3.0',
        'translate_source': 'ភាសាដើម',
        'translate_target': 'ភាសាគោលដៅ',
        'translate_copy': '📋 ចម្លងការបកប្រែ',
        'translate_copied': '✓ បានចម្លង!'
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

def load_calendar():
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_current_lang():
    lang = request.args.get('lang', 'ko').lower()
    return lang if lang in TRANSLATIONS else 'ko'


def load_sllm_info():
    with open(SLLM_INFO_FILE, encoding='utf-8') as info_file:
        return json.load(info_file)


@app.route('/api/sllm-info')
def api_sllm_info():
    return jsonify(load_sllm_info())

@app.route('/')
def index():
    lang = get_current_lang()
    t = TRANSLATIONS[lang]
    
    procedures = load_procedures()
    notices = load_notices()
    calendar_events = load_calendar()
    
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
        languages_meta=LANGUAGES_METADATA,
        sllm_info=load_sllm_info(),
        procedures=filtered_procedures,
        notices=filtered_notices,
        calendar_events=calendar_events,
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
        
    display_item = item.copy()
    if lang != 'ko':
        display_item['title'] = sllm_engine.translate_text(item['title'], lang, 'ko')
        display_item['purpose'] = sllm_engine.translate_text(item['purpose'], lang, 'ko')
        display_item['who'] = sllm_engine.translate_text(item['who'], lang, 'ko')
        display_item['timing'] = sllm_engine.translate_text(item['timing'], lang, 'ko')
        display_item['notes'] = sllm_engine.translate_text(item['notes'], lang, 'ko')
        display_item['documents'] = [sllm_engine.translate_text(d, lang, 'ko') for d in item.get('documents', [])]
        display_item['steps'] = [sllm_engine.translate_text(s, lang, 'ko') for s in item.get('steps', [])]

    return render_template('procedure.html', p=display_item, raw_p=item, lang=lang, t=t, languages_meta=LANGUAGES_METADATA)

@app.route('/notice/<int:nid>')
def notice_detail(nid):
    lang = get_current_lang()
    t = TRANSLATIONS[lang]
    notices = load_notices()
    item = next((n for n in notices if n.get('id') == nid), None)
    if not item:
        return 'Notice not found', 404
        
    display_item = item.copy()
    if lang != 'ko':
        display_item['title'] = sllm_engine.translate_text(item['title'], lang, 'ko')
        display_item['content'] = sllm_engine.translate_text(item['content'], lang, 'ko')
        display_item['author'] = sllm_engine.translate_text(item['author'], lang, 'ko')

    return render_template('notice.html', n=display_item, raw_n=item, lang=lang, t=t, languages_meta=LANGUAGES_METADATA)

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    response = app.send_static_file('sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/health')
def health():
    procedures = load_procedures()
    notices = load_notices()
    calendar_events = load_calendar()
    return jsonify({
        'status': 'healthy',
        'service': 'Jungwon University AI Student Assistant - sLLM & Translation Hub v3.0',
        'step': 10,
        'port': 5008,
        'sllm_engine': 'Active (Academic Q&A & Knowledge RAG)',
        'procedures_count': len(procedures),
        'notices_count': len(notices),
        'calendar_events_count': len(calendar_events),
        'supported_languages': list(LANGUAGES_METADATA.keys())
    })

@app.route('/api/procedures')
def api_procedures():
    return jsonify(load_procedures())

@app.route('/api/notices')
def api_notices():
    return jsonify(load_notices())

@app.route('/api/calendar')
def api_calendar():
    return jsonify(load_calendar())

@app.route('/api/generate_form', methods=['POST'])
def api_generate_form():
    """Smart Form Generation Endpoint: Returns official formatted university documents."""
    data = request.get_json() or {}
    res = form_generator.generate_administrative_form(data)
    return jsonify(res)

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
    """
    sLLM Chatbot Endpoint:
    Provides academic & administrative QA, RAG context synthesis, and multilingual generation.
    """
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    lang = data.get('lang', 'ko').lower()
    if lang not in TRANSLATIONS:
        lang = 'ko'
        
    if not message:
        t_fallback = {
            'ko': '질문을 입력해 주세요.',
            'en': 'Please enter your question.',
            'vi': 'Vui lòng nhập câu hỏi của bạn.',
            'uz': 'Iltimos, savolingizni kiriting.',
            'ne': 'कृपया आफ्नो प्रश्न प्रविष्ट गर्नुहोस्।',
            'km': 'សូមបញ្ចូលសំណួររបស់អ្នក។'
        }
        return jsonify({'reply': t_fallback.get(lang, 'Please enter your question.')})
        
    procedures = load_procedures()
    notices = load_notices()
    
    # Process through sLLM Engine
    result = sllm_engine.generate_sllm_response(
        query=message,
        lang=lang,
        procedures=procedures,
        notices=notices
    )
    
    return jsonify(result)

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """
    Dedicated Multilingual Translation Endpoint:
    Translates text between KO, EN, VI, UZ, NE, KM.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'JSON 객체를 보내 주세요.', 'translated': ''}), 400
    if not all(isinstance(data.get(key, default), str) for key, default in
               (('text', ''), ('source_lang', 'auto'), ('target_lang', 'en'))):
        return jsonify({'error': '텍스트와 언어 코드는 문자열이어야 합니다.', 'translated': ''}), 400
    text = data.get('text', '').strip()
    source_lang = data.get('source_lang', 'auto').strip().lower()
    target_lang = data.get('target_lang', 'en').strip().lower()
    
    if not text:
        return jsonify({'error': 'No text provided', 'translated': ''}), 400
        
    if target_lang not in LANGUAGES_METADATA or source_lang not in (*LANGUAGES_METADATA, 'auto'):
        return jsonify({'error': '지원하지 않는 언어입니다. ko, en, vi, km, ne, uz를 사용하세요.', 'translated': ''}), 400
    if len(text) > 10000:
        return jsonify({'error': '한 번에 10,000자까지 번역할 수 있습니다.', 'translated': ''}), 400
        
    try:
        translated = sllm_engine.translate_text(text, target_lang=target_lang, source_lang=source_lang, strict=True)
    except sllm_engine.TranslationUnavailable:
        return jsonify({'error': '번역 서비스에 연결할 수 없습니다. 원본 언어를 직접 선택하거나 잠시 후 다시 시도해 주세요.', 'translated': ''}), 503
    
    return jsonify({
        'original': text,
        'translated': translated,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'target_meta': LANGUAGES_METADATA[target_lang]
    })

if __name__ == '__main__':
    print("Jungwon University AI Student Assistant - Step 10 Prototype starting on http://127.0.0.1:5008")
    app.run(host='127.0.0.1', port=5008, debug=True)
