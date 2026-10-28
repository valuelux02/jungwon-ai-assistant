# -*- coding: utf-8 -*-
"""
Jungwon University AI Student Assistant - sLLM & Multilingual Translation Engine (v3.0)
Core Languages:
  1. Korean (ko) 🇰🇷
  2. English (en) 🇺🇸
  3. Vietnamese (vi) 🇻🇳
  4. Uzbek (uz) 🇺🇿
  5. Nepali (ne) 🇳🇵
  6. Khmer (km) 🇰🇭

Key Capabilities:
  1. sLLM Information Engine: Comprehensive Academic & Administrative Q&A (10 Domains)
  2. Non-truncating, chunk-based neural pivot translation
  3. Bilingual presentation support (Local language translation + Official Korean text for school office)
"""

import os
import json
import re
import html
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional

SUPPORTED_LANGUAGES = {
    'ko': {'name': '한국어', 'native': '한국어', 'flag': '🇰🇷'},
    'en': {'name': 'English', 'native': 'English', 'flag': '🇺🇸'},
    'vi': {'name': 'Tiếng Việt', 'native': 'Tiếng Việt', 'flag': '🇻🇳'},
    'uz': {'name': "O'zbekcha", 'native': "O'zbekcha", 'flag': '🇺🇿'},
    'ne': {'name': 'नेपाली', 'native': 'नेपाली', 'flag': '🇳🇵'},
    'km': {'name': 'ភាសាខ្មែរ', 'native': 'ភាសាខ្មែរ', 'flag': '🇰🇭'}
}

# Translation cache
_TRANSLATION_CACHE: Dict[str, str] = {}

# Academic domain dictionary for high precision
ACADEMIC_TERMS = {
    '휴학': {
        'en': 'Leave of Absence',
        'vi': 'Nghỉ học tạm thời',
        'uz': "Akademik ta'til",
        'ne': 'अध्ययन बिदा (Leave of Absence)',
        'km': 'ការសុំព្យួរការសិក្សា'
    },
    '복학': {
        'en': 'Return to School',
        'vi': 'Trở lại trường học',
        'uz': "O'qishga qaytish",
        'ne': 'पुनः अध्ययन सुरु (Return)',
        'km': 'ការចូលរៀនវិញ'
    },
    '장학금': {
        'en': 'Scholarship',
        'vi': 'Học bổng',
        'uz': 'Stipendiya',
        'ne': 'छात्रवृत्ति (Scholarship)',
        'km': 'អាហារូបករណ៍'
    },
    '기숙사': {
        'en': 'Dormitory / Residence Hall',
        'vi': 'Ký túc xá',
        'uz': 'Talabalar yotoqxonasi',
        'ne': 'छात्रावास (Dormitory)',
        'km': 'អន្តេវាសិកដ្ឋាន'
    },
    '증명서': {
        'en': 'Certificates / Transcripts',
        'vi': 'Giấy chứng nhận / Bảng điểm',
        'uz': "Ma'lumotnoma va diplom",
        'ne': 'प्रमाणपत्र (Certificates)',
        'km': 'លិខិតបញ្ជាក់'
    },
    '졸업요건': {
        'en': 'Graduation Requirements',
        'vi': 'Yêu cầu tốt nghiệp',
        'uz': 'Bitiruv talablari',
        'ne': 'स्नातक आवश्यकताहरू (Graduation Requirements)',
        'km': 'លក្ខខណ្ឌបញ្ចប់ការសិក្សា'
    },
    '비자': {
        'en': 'Visa & Alien Registration (D-2/D-4)',
        'vi': 'Thị thực (Visa) & Đăng ký người nước ngoài',
        'uz': "Viza va chet el fuqarosi kartasi",
        'ne': 'भिसा र विदेशी दर्ता (Visa)',
        'km': 'ទិដ្ឋាការ និងការចុះឈ្មោះជនបរទេស'
    },
    '수강신청': {
        'en': 'Course Registration & Credits',
        'vi': 'Đăng ký môn học & Tín chỉ',
        'uz': "Fanlarga ro'yxatdan o'tish va kreditlar",
        'ne': 'पाठ्यक्रम दर्ता र क्रेडिटहरू',
        'km': 'ការចុះឈ្មោះវគ្គសិក្សា'
    },
    '등록금': {
        'en': 'Tuition & Installment Payment',
        'vi': 'Học phí & Trả góp',
        'uz': "O'qish to'lovi va bo'lib to'lash",
        'ne': 'ट्यूशन शुल्क र किस्ता भुक्तानी',
        'km': 'ថ្លៃសិក្សា និងការបង់រំលស់'
    },
    '시설/식당': {
        'en': 'Campus Facilities & Cafeteria',
        'vi': 'Cơ sở vật chất & Nhà ăn sinh viên',
        'uz': 'Kampus qulayliklari va oshxona',
        'ne': 'क्याम्पस सुविधाहरू र क्याफेटेरिया',
        'km': 'សម្ភារៈបរិក្ខារ និងអាហារដ្ឋាន'
    }
}

# Multilingual Keyword Map for Intent Recognition
INTENT_KEYWORDS = {
    '휴학': [
        '휴학', '학업중단', '일반휴학', '군휴학', '질병휴학', '휴학신청',
        'leave of absence', 'take a semester off', 'pause study', 'leave school', 'suspension of study',
        'nghỉ học', 'tạm dừng học', 'bảo lưu', 'đơn xin nghỉ học',
        "akademik ta'til", "ta'til", "o'qishni to'xtatish", "tatil",
        'बिदा', 'अध्ययन रोक्ने', 'छुट्टी', 'अध्ययन बिदा'
    ],
    '복학': [
        '복학', '복학신청', '다시 다니다', '학업복귀',
        'return to school', 're-enrollment', 'come back', 'resume study', 'returning to university',
        'quay lại học', 'trở lại trường', 'nhập học lại',
        "o'qishga qaytish", "tiklash", "qaytish",
        'पुनः अध्ययन', 'फिर्ता', 'पुनः भर्ना'
    ],
    '장학금': [
        '장학금', '장학생', '국가장학금', '성적장학금', '면학', '장학', 'topik 장학', '토픽 장학',
        'scholarship', 'financial aid', 'grant', 'tuition waiver', 'topik scholarship',
        'học bổng', 'trợ cấp', 'miễn giảm học phí', 'học bổng topik',
        'stipendiya', 'grant', 'moliyaviy yordam', 'topik stipendiyasi',
        'छात्रवृत्ति', 'आर्थिक सहयोग', 'टोपिक छात्रवृत्ति'
    ],
    '증명서': [
        '증명서', '재학증명서', '성적증명서', '졸업증명서', '발급', '무인발급기', '인터넷 증명',
        'certificate', 'transcript', 'proof of enrollment', 'graduation certificate', 'issue certificate',
        'giấy chứng nhận', 'bảng điểm', 'xác nhận nhập học', 'chứng chỉ',
        "ma'lumotnoma", "transkript", "shahodatnoma", "diplom nusxasi",
        'प्रमाणपत्र', 'ट्रान्सक्रिप्ट', 'नतिजा', 'अध्ययन प्रमाणपत्र'
    ],
    '졸업요건': [
        '졸업', '졸업요건', '졸업시험', '졸업논문', '학점', '이수학점', '캡스톤', '조기졸업',
        'graduation', 'graduate requirements', 'thesis', 'graduation test', 'credits for graduation',
        'tốt nghiệp', 'điều kiện tốt nghiệp', 'luận văn', 'tín chỉ tốt nghiệp',
        'bitiruv', 'bitiruv talablari', 'diplom ishi', 'kreditlar',
        'स्नातक', 'दीक्षान्त', 'स्नातक आवश्यकता', 'थेसिस'
    ],
    '기숙사': [
        '기숙사', '생활관', '룸메이트', '입사', '퇴사', '기숙사비', '결핵', '결핵진단서', 'x-ray',
        'dormitory', 'dorm', 'residence hall', 'roommate', 'housing', 'tb test', 'tuberculosis',
        'ký túc xá', 'ktx', 'ở nội trú', 'phòng ở', 'khám lao', 'x-ray lao phổi',
        'yotoqxona', 'talabalar turar joyi', 'sil kasalligi', 'rentgen',
        'छात्रावास', 'होस्टेल', 'कोठा', 'क्षयरोग', 'टीबी रिपोर्ट'
    ],
    '비자': [
        '비자', '체류', '체류연장', '외국인등록증', 'd-2', 'd-4', '출입국', '알바', '아르바이트', '시간제취업', 'hikorea', '하이코리아',
        'visa', 'alien registration', 'arc', 'immigration', 'd2', 'd4', 'part time job', 'work permit',
        'thị thực', 'gia hạn visa', 'thẻ cư trú', 'cục xuất nhập cảnh', 'việc làm thêm', 'đi làm thêm',
        'viza', 'yashash ruxsati', 'chet el fuqarosi kartasi', 'immigratsiya', 'ishlash ruxsati', 'arbayt',
        'भिसा', 'विदेशी दर्ता', 'बसाइ अवधि थप', 'अध्यागमन', 'पार्ट-टाइम काम'
    ],
    '수강신청': [
        '수강신청', '정정', '강의', '시간표', '학점신청', '개설강좌', '장바구니', '학사경고', 'f학점',
        'course registration', 'class sign up', 'timetable', 'add drop', 'academic warning', 'credits',
        'đăng ký môn học', 'lịch học', 'thay đổi môn học', 'cảnh cáo học tập', 'tín chỉ',
        "fanlarga ro'yxatdan o'tish", "dars jadvali", "akademik ogohlantirish",
        'पाठ्यक्रम दर्ता', 'कक्षा दर्ता', 'समयतालिका', 'शैक्षिक चेतावनी'
    ],
    '등록금': [
        '등록금', '등록금납부', '가상계좌', '분할납부', '등록금 고지서', '납부기간',
        'tuition', 'tuition fee', 'pay tuition', 'installment', 'virtual account',
        'học phí', 'nộp học phí', 'trả góp học phí', 'tài khoản ảo',
        "o'qish to'lovi", "kontrakt to'lovi", "bo'lib to'lash",
        'ट्यूशन शुल्क', 'शुल्क भुक्तानी', 'किस्ता भुक्तानी'
    ],
    '시설/식당': [
        '도서관', '식당', '학생식당', '학식', '열람실', '보건실', '보건진료소', '국제교류원', '편의시설',
        'library', 'cafeteria', 'canteen', 'health center', 'clinic', 'facilities',
        'thư viện', 'nhà ăn', 'phòng y tế', 'cơ sở vật chất',
        'kutubxona', 'oshxona', 'tibbiyot xonasi', 'qulayliklar',
        'पुस्तकालय', 'क्याफेटेरिया', 'स्वास्थ्य केन्द्र', 'सुविधाहरू'
    ]
}


# Khmer queries should work without depending on an external query translation.
for _topic, _keywords in {
    '휴학': ['ព្យួរការសិក្សា', 'ឈប់សម្រាកការសិក្សា'],
    '복학': ['ចូលរៀនវិញ', 'បន្តការសិក្សាវិញ'],
    '장학금': ['អាហារូបករណ៍'],
    '증명서': ['វិញ្ញាបនបត្រ', 'លិខិតបញ្ជាក់'],
    '졸업요건': ['បញ្ចប់ការសិក្សា'],
    '기숙사': ['អន្តេវាសិកដ្ឋាន', 'អន្តេវាសិក', 'កន្លែងស្នាក់នៅ'],
    '비자': ['ទិដ្ឋាការ', 'ការងារក្រៅម៉ោង'],
    '수강신청': ['ចុះឈ្មោះមុខវិជ្ជា', 'កាលវិភាគថ្នាក់'],
    '등록금': ['ថ្លៃសិក្សា'],
    '시설/식당': ['បណ្ណាល័យ', 'អាហារដ្ឋាន']
}.items():
    INTENT_KEYWORDS[_topic].extend(_keywords)


def _http_get_json(url: str, timeout: int = 5) -> Optional[Any]:
    """Helper to perform HTTP GET requests safely."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode('utf-8', errors='replace')
            return json.loads(content)
    except Exception:
        return None


def _query_google(text: str, sl: str, tl: str) -> Optional[str]:
    """Fast Google Translate call handling paragraphs and markdown."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and data[0]:
                return ''.join([part[0] for part in data[0] if part and part[0]])
    except Exception:
        pass
    return None


class TranslationUnavailable(RuntimeError):
    """No translation provider returned a usable translation."""


def _translate_single_chunk(text: str, target_lang: str, source_lang: str = 'ko') -> str:
    """Translates a short chunk via MyMemory + Pivot as reliable fallback."""
    clean = text.strip()
    if not clean:
        return ''
        
    cache_key = f"{source_lang}->{target_lang}:{clean}"
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    # Exact term match
    for term, trans_map in ACADEMIC_TERMS.items():
        variants = {'ko': term, **trans_map}
        matches = (clean in variants.values() if source_lang == 'auto'
                   else clean == variants.get(source_lang))
        if matches and target_lang in variants:
            res = variants[target_lang]
            _TRANSLATION_CACHE[cache_key] = res
            return res

    google_result = _query_google(clean, source_lang, target_lang)
    if google_result and google_result.strip():
        _TRANSLATION_CACHE[cache_key] = google_result
        return google_result

    def _query_mymemory(q: str, sl: str, tl: str) -> Optional[str]:
        try:
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(q)}&langpair={sl}|{tl}"
            data = _http_get_json(url, timeout=3)
            if data and str(data.get('responseStatus')) == '200' and 'responseData' in data:
                res = data['responseData'].get('translatedText')
                if res and res.strip() and res.lower() != q.lower():
                    return html.unescape(res).strip()
        except Exception:
            pass
        return None

    # MyMemory requires an explicit source language; never guess Korean for auto.
    if source_lang == 'auto':
        raise TranslationUnavailable('Automatic language detection is unavailable.')
    if len(clean.encode('utf-8')) > 350:
        chunks, current = [], ''
        for char in clean:
            if len((current + char).encode('utf-8')) > 350:
                chunks.append(current)
                current = ''
            current += char
        if current:
            chunks.append(current)
        result = ' '.join(_translate_single_chunk(chunk, target_lang, source_lang) for chunk in chunks)
        _TRANSLATION_CACHE[cache_key] = result
        return result
    s_lang = source_lang
    ans = _query_mymemory(clean, s_lang, target_lang)

    # Pivot via English if needed
    if not ans and s_lang != 'en' and target_lang != 'en':
        en_mid = _query_mymemory(clean, s_lang, 'en')
        if en_mid:
            ans = _query_mymemory(en_mid, 'en', target_lang)

    if not ans:
        raise TranslationUnavailable('Translation providers are unavailable.')
    _TRANSLATION_CACHE[cache_key] = ans
    return ans


def translate_text(text: str, target_lang: str, source_lang: str = 'auto', strict: bool = False) -> str:
    """
    High-performance multilingual translator with caching, Google API primary, and MyMemory fallback.
    Preserves exact markdown structure and handles long text seamlessly.
    """
    if not text or not text.strip():
        return ''
        
    target_lang = target_lang.lower().strip()
    source_lang = source_lang.lower().strip()
    
    if target_lang not in SUPPORTED_LANGUAGES or source_lang not in (*SUPPORTED_LANGUAGES, 'auto'):
        raise ValueError('Unsupported language code')
        
    if source_lang == target_lang:
        return text

    cache_key = f"{source_lang}->{target_lang}:{text}"
    if cache_key in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cache_key]

    try:
        # Try the whole text first; short valid translations are also accepted.
        if len(text.encode('utf-8')) < 1800:
            result = _translate_single_chunk(text, target_lang, source_lang)
        else:
            # Bound by UTF-8 bytes for providers with byte-based request limits.
            # Every character is retained, including text without punctuation.
            translated_lines = []
            for line in text.split('\n'):
                chunks, current, size = [], '', 0
                for char in line:
                    char_size = len(char.encode('utf-8'))
                    if size + char_size > 350:
                        chunks.append(current)
                        current, size = '', 0
                    current += char
                    size += char_size
                if current:
                    chunks.append(current)
                translated_lines.append(' '.join(
                    _translate_single_chunk(chunk, target_lang, source_lang)
                    for chunk in chunks
                ))
            result = '\n'.join(translated_lines)
    except TranslationUnavailable:
        if strict:
            raise
        # Existing detail pages can still display their Korean original.
        # Do not cache failures, so a later request can retry.
        return text

    final_result = result
    _TRANSLATION_CACHE[cache_key] = final_result
    return final_result


def detect_intent(query: str) -> str:
    """Identifies the academic/administrative topic from the query across 5 languages."""
    q_lower = query.lower()
    for topic, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in q_lower:
                return topic
    return 'general'


def generate_sllm_response(
    query: str,
    lang: str = 'ko',
    procedures: Optional[List[Dict[str, Any]]] = None,
    notices: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    sLLM (Small Language Model) Academic Q&A Engine (v3.0)
    Generates structured, comprehensive answers and supports bilingual presentation.
    """
    if not procedures:
        procedures = []
    if not notices:
        notices = []

    lang = lang.lower() if lang in SUPPORTED_LANGUAGES else 'ko'
    q_clean = query.strip()
    q_lower = q_clean.lower()

    # 1. Direct translation request detection
    trans_prefix_match = re.match(r'^(번역|translate|dịch|tarjima|अनुवाद|បកប្រែ)\s*[:：]?\s*(.*)$', q_clean, re.IGNORECASE)
    if trans_prefix_match:
        text_to_translate = trans_prefix_match.group(2).strip()
        if text_to_translate:
            target = 'en' if lang == 'ko' else lang
            try:
                translated = translate_text(text_to_translate, target_lang=target, source_lang='auto', strict=True)
            except TranslationUnavailable:
                return {
                    'reply': '번역 서비스에 연결할 수 없습니다. 번역기에서 원본 언어를 직접 선택하거나 잠시 후 다시 시도해 주세요.',
                    'korean_text': '', 'sources': [], 'intent': 'translation_error', 'lang': 'ko'
                }
            meta = SUPPORTED_LANGUAGES[target]
            return {
                'reply': f"🌐 **[sLLM 실시간 번역 ({meta['flag']} {meta['name']})]**\n\n{translated}",
                'korean_text': text_to_translate,
                'sources': ['sLLM 다국어 번역 엔진 (Neural Pivot)'],
                'intent': 'translation',
                'lang': target,
                'model': 'Jungwon-sLLM-Translator-v3'
            }

    # 2. Intent Identification
    intent = detect_intent(q_clean)

    # 3. RAG Retrieval across procedures.json
    matched_proc = None
    if intent != 'general':
        for p in procedures:
            if intent in p.get('category', '') or intent in p.get('title', ''):
                matched_proc = p
                break

    if not matched_proc:
        for p in procedures:
            blob = json.dumps(p, ensure_ascii=False).lower()
            if any(w in blob for w in q_lower.split() if len(w) > 1):
                matched_proc = p
                break

    # Notice retrieval
    matched_notice = None
    for n in notices:
        n_blob = json.dumps(n, ensure_ascii=False).lower()
        if intent != 'general' and intent in n_blob:
            matched_notice = n
            break
        elif any(w in n_blob for w in q_lower.split() if len(w) > 1):
            matched_notice = n
            break

    sources = []
    response_lines = []

    # 4. Construct Comprehensive Q&A Response
    if matched_proc:
        sources.append(f"학사행정가이드: {matched_proc['title']}")
        
        response_lines.append(f"🎓 **[{matched_proc['category']}] {matched_proc['title']}**\n")
        response_lines.append(f"📌 **개요 및 목적**: {matched_proc['purpose']}")
        response_lines.append(f"👤 **신청 대상 및 자격**: {matched_proc['who']}")
        
        if matched_proc.get('timing'):
            response_lines.append(f"⏰ **신청 기간 및 일정**: {matched_proc['timing']}")
            
        if matched_proc.get('documents'):
            docs_formatted = '\n   - ' + '\n   - '.join(matched_proc['documents'])
            response_lines.append(f"📄 **필요 제출 서류**:{docs_formatted}")
            
        if matched_proc.get('steps'):
            steps_formatted = '\n   ' + '\n   ➔ '.join([f"{idx+1}. {step}" for idx, step in enumerate(matched_proc['steps'])])
            response_lines.append(f"🚶 **단계별 진행 절차**:{steps_formatted}")
            
        if matched_proc.get('office'):
            response_lines.append(f"🏛️ **담당 부서 및 문의**: {matched_proc['office']}")
            
        if matched_proc.get('notes'):
            response_lines.append(f"\n⚠️ **중요 유의사항 및 비자 규정**: {matched_proc['notes']}")

        if matched_notice:
            sources.append(f"대학공지: {matched_notice['title']}")
            response_lines.append(f"\n📢 **관련 최신 대학 공지사항**:")
            response_lines.append(f"• **[{matched_notice['category']}] {matched_notice['title']}** (게시: {matched_notice['author']}, {matched_notice['date']})")
            response_lines.append(f"  {matched_notice['content']}")

    elif matched_notice:
        sources.append(f"대학공지: {matched_notice['title']}")
        response_lines.append(f"📢 **[{matched_notice['category']}] 관련 공지사항 안내**\n")
        response_lines.append(f"📌 **공지 제목**: {matched_notice['title']}")
        response_lines.append(f"📅 **게시일자**: {matched_notice['date']} (담당: {matched_notice['author']})")
        response_lines.append(f"📝 **주요 내용**:\n{matched_notice['content']}")
        if matched_notice.get('attachments'):
            response_lines.append(f"📎 **첨부서식**: {', '.join(matched_notice['attachments'])}")
        response_lines.append("\n상세 서식 및 원문은 종합정보시스템 및 대학 공지사항 탭에서 열람 가능합니다.")

    else:
        sources.append("중원대 학사 헬프데스크")
        response_lines.append(f"입력하신 **'{q_clean}'**에 대한 맞춤형 규정을 찾기 어렵습니다.\n")
        response_lines.append("💡 **sLLM 추천 행정·학사 분야**:")
        response_lines.append("1. **휴학 / 복학**: 신청 시기, 휴학원서 서식, 유학생 비자 출국 규정")
        response_lines.append("2. **장학금**: 성적우수장학, 국가장학금, 외국인 TOPIK 3~6급 감면 장학금")
        response_lines.append("3. **증명서**: 재학증명서, 성적증명서 국문/영문 즉시 발급 방법")
        response_lines.append("4. **생활관/기숙사**: 입사 신청, 흉부 X-ray 결핵진단서 필수 제출, 통금 규정")
        response_lines.append("5. **비자/체류관리**: D-2 비자 연장, 외국인등록증(ARC), 시간제취업허가(알바)")
        response_lines.append("6. **수강신청/학점**: 수강신청 일정, 장바구니, 수강정정, 학사경고(GPA 1.5 미만)")
        response_lines.append("7. **등록금**: 가상계좌 납부, 분할납부(최대 4회) 신청 절차")
        response_lines.append("8. **캠퍼스 시설**: 도서관 열람실, 학생식당, 보건진료소, 국제교류원")
        response_lines.append("\n한국어, 영어, 베트남어, 크메르어(캄보디아), 네팔어, 우즈베크어로 자유롭게 질문해 주세요!")

    korean_reply = "\n".join(response_lines)

    # 5. Multilingual Translation & Bilingual Output
    final_reply = korean_reply
    reply_lang = lang
    if lang != 'ko':
        try:
            final_reply = translate_text(korean_reply, target_lang=lang, source_lang='ko', strict=True)
            lang_meta = SUPPORTED_LANGUAGES[lang]
            sources.append(f"{lang_meta['flag']} {lang_meta['name']} 번역 제공")
        except TranslationUnavailable:
            reply_lang = 'ko'
            sources.append('번역 서비스 연결 실패: 한국어 원문을 표시합니다.')

    return {
        'reply': final_reply,
        'korean_text': korean_reply,
        'sources': sources,
        'intent': intent,
        'model': 'Jungwon-sLLM-Academic-v3.0',
        'lang': reply_lang
    }
