# -*- coding: utf-8 -*-
"""
Jungwon University AI Student Assistant - Smart Administrative Form Generator
Generates official, standard university application forms in printable Korean layout:
  1. 휴학원서 (Leave of Absence Application)
  2. 복학원서 (Return to School Application)
  3. 외국인 유학생 시간제취업확인서 (Part-time Work Permit for D-2/D-4)
  4. 생활관(기숙사) 입사신청서 (Dormitory Application)
"""

from datetime import datetime
from typing import Dict, Any

FORM_TYPES = {
    'leave': {
        'title': '휴 학 원 서 (Application for Leave of Absence)',
        'description': '질병, 가사, 군복무, 어학연수 등으로 학업을 일시 중단할 때 제출하는 공식 서식입니다.'
    },
    'return': {
        'title': '복 학 원 서 (Application for Return from Leave)',
        'description': '휴학 사유 종료 후 해당 정규 학기에 복학하고자 할 때 제출하는 서식입니다.'
    },
    'part_time': {
        'title': '외국인 유학생 시간제취업(알바) 확인서 (Part-time Work Permit)',
        'description': 'D-2/D-4 유학생이 출입국관리사무소에 아르바이트 체류자격외활동허가를 신청할 때 학교장의 확인을 받는 공식 서식입니다.'
    },
    'dormitory': {
        'title': '생 활 관 (기숙사) 입 사 신 청 서 (Dormitory Application)',
        'description': '중원대학교 연당마을 생활관 입사를 신청하는 공식 서식입니다.'
    }
}

def generate_administrative_form(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates formatted document content and metadata."""
    form_type = data.get('form_type', 'leave')
    name = data.get('name', '홍길동 / HONG GILDONG').strip()
    student_id = data.get('student_id', '202612345').strip()
    dept = data.get('dept', '글로벌융합학부').strip()
    grade = data.get('grade', '2학년').strip()
    phone = data.get('phone', '010-1234-5678').strip()
    reason = data.get('reason', '개인 사정 및 어학 연수').strip()
    period = data.get('period', '2026학년도 1학기 ~ 2026학년도 2학기 (1년간)').strip()
    workplace = data.get('workplace', '교내 글로벌카페 / Global Cafe').strip()
    hourly_wage = data.get('hourly_wage', '10,030원 (2026 최저임금 기준)').strip()
    
    today_str = datetime.now().strftime("%Y년 %m월 %d일")

    if form_type == 'leave':
        content = f"""
================================================================================
                          휴  학  원  서
               [ Application for Leave of Absence ]
================================================================================

[ 학생 인적사항 / Student Information ]
 • 성    명 (Name): {name}
 • 학    번 (Student ID): {student_id}
 • 소속학과 (Department): {dept}
 • 학    년 (Grade): {grade}
 • 연 락 처 (Phone): {phone}

[ 휴학 신청 내용 / Application Details ]
 • 휴학 구분 (Type): 일반휴학 [ V ]  /  군휴학 [   ]  /  질병휴학 [   ]
 • 휴학 기간 (Period): {period}
 • 휴학 사유 (Reason): {reason}

[ 유의사항 확인 / Agreement ]
 1. 휴학 기간 만료 후 정해진 기한 내에 복학하지 않을 경우 학칙 제23조에 의거 '미복학 제적' 처리됨을 확인합니다.
 2. 외국인 유학생의 경우 휴학 승인 즉시 D-2 비자 효력이 상실되며 14일 이내에 출국해야 함을 확인합니다.

                              신청일자: {today_str}
                              신 청 인: {name} (인 또는 서명)

--------------------------------------------------------------------------------
[ 지도교수 및 학과장 확인 / Approval ]
 • 지도교수 의견: 면담 완료 (학업 지속 권고 및 복학 일정 확인)
   성명: ____________________ (서명)
 • 학과장 승인:
   성명: ____________________ (서명)

중원대학교 교무처장 귀하
================================================================================
"""

    elif form_type == 'return':
        content = f"""
================================================================================
                          복  학  원  서
               [ Application for Return to School ]
================================================================================

[ 학생 인적사항 / Student Information ]
 • 성    명 (Name): {name}
 • 학    번 (Student ID): {student_id}
 • 소속학과 (Department): {dept}
 • 학    년 (Grade): {grade}
 • 연 락 처 (Phone): {phone}

[ 복학 신청 내용 / Application Details ]
 • 복학 학기 (Return Semester): 2026학년도 1학기
 • 휴학 사유 (Previous Leave Reason): {reason}
 • 전역 일자 (군복무자인 경우): 해당 없음

[ 서약 사항 / Pledge ]
 본인은 위와 같이 복학을 신청하오며, 복학 승인 후 정해진 기간 내에 수강신청을 완료하고
 등록금을 성실히 납부하여 학업에 충실히 임할 것을 서약합니다.

                              신청일자: {today_str}
                              신 청 인: {name} (인 또는 서명)

중원대학교 총장 귀하
================================================================================
"""

    elif form_type == 'part_time':
        content = f"""
================================================================================
             외국인 유학생 시간제취업(알바) 확인서
             [ Part-time Work Permit Application ]
================================================================================

[ 유학생 인적사항 / Student Profile ]
 • 성    명 (Name): {name}
 • 국    적 (Nationality): 외국인 유학생
 • 학    번 (Student ID): {student_id}
 • 소속학과 (Department): {dept} ({grade})
 • 체류자격 (Visa Status): D-2 (유학)
 • 한국어능력 (TOPIK): 3급 이상 보유 확인

[ 근무 예정지 정보 / Employment Details ]
 • 근무업체명 (Company): {workplace}
 • 담당 직무 (Job Duty): 통번역 보조 및 매장 보조
 • 근무 시간 (Hours): 주당 20시간 이내 (학기 중 법정 허용 시간 준수)
 • 시    급 (Hourly Wage): {hourly_wage}

[ 학교 확인 및 의견 / University Endorsement ]
 상기 학생은 중원대학교 정규 학위과정 재학생으로서, 직전 학기 출석률(70% 이상)과
 학업 성적(평점 2.0 이상) 요건을 충족하여 출입국관리법에 따른 시간제취업 활동을 추천합니다.

                              발급일자: {today_str}
                              국제교류원 담당자: __________________ (인)
                              중원대학교 국제교류원장 [직인생략]

청주출입국·외국인사무소장 귀하
================================================================================
"""

    elif form_type == 'dormitory':
        content = f"""
================================================================================
                 생 활 관 (기숙사) 입 사 신 청 서
                 [ Dormitory Admission Application ]
================================================================================

[ 입사 신청자 정보 / Applicant ]
 • 성    명 (Name): {name}
 • 학    번 (Student ID): {student_id}
 • 소속학과 (Department): {dept} ({grade})
 • 연 락 처 (Phone): {phone}
 • 희망 호실 (Room Type): 2인 1실 [ V ]  /  4인 1실 [   ]

[ 방역 및 필수 서류 확인 / Required Documents Checklist ]
 [ V ] 흉부 X-ray 결핵 검사 진단서 (입사일 기준 1개월 이내 발급분 - 필수 지참)
 [ V ] 생활관 운영수칙(야간 통금 23:30, 전열기구 반입 금지, 무단외박 금지) 준수 서약

 본인은 중원대학교 생활관 수칙을 엄수하며, 단체생활의 질서를 준수할 것을 서약하고
 2026학년도 1학기 생활관 입사를 신청합니다.

                              신청일자: {today_str}
                              신 청 인: {name} (인 또는 서명)

중원대학교 생활관장 귀하
================================================================================
"""

    return {
        'form_type': form_type,
        'title': FORM_TYPES.get(form_type, {}).get('title', '공식 서식'),
        'content': content.strip(),
        'generated_at': today_str,
        'student_name': name,
        'student_id': student_id
    }
