# -*- coding: utf-8 -*-
"""
한국어 스미싱/정상 문자 데이터셋 생성기 (1,000건)

원본 CSV(메시지_데이터_최종본_1000.csv)와 동일한 규격으로 만듭니다.
  - 열: 문자내용, 분류
  - 분류 값: 스미싱 / 정상
  - 스미싱 500건, 정상 500건

어휘/빈도는 Orange Word Cloud 결과(ㅁㅁ링크, [Web발신], 안내, 확인, 알림,
신청, 무료, 고객님, 즉시, 이벤트 …)를 참고해 구성했습니다.

사용법:
    python3 data/generate_dataset.py            # data/messages_1000.csv 생성
    python3 data/build.py                       # index.html 안에 데이터 주입
"""

import csv
import os
import random
import itertools

SEED = 20260807
random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "messages_1000.csv")

# --------------------------------------------------------------------------
# 공통 슬롯
# --------------------------------------------------------------------------
LINKS = (
    ["ㅁㅁ링크"] * 6
    + [
        "http://vo.la/{r4}",
        "http://me2.kr/{r4}",
        "hxxp://bit.ly/{r5}",
        "http://han.gl/{r4}",
        "http://xn--{r5}.xyz",
        "http://kr-{r4}.top",
        "http://{r4}.duckdns.org",
    ]
)

COURIER = ["CJ대한통운", "우체국택배", "롯데택배", "한진택배", "로젠택배", "쿠팡", "CU편의점택배"]
BANK = ["국민은행", "신한은행", "우리은행", "하나은행", "농협은행", "기업은행", "카카오뱅크", "새마을금고"]
CARD = ["삼성카드", "현대카드", "국민카드", "신한카드", "롯데카드", "하나카드", "BC카드"]
GOV = ["국세청", "국민연금공단", "건강보험공단", "행정안전부", "질병관리청", "서울시청", "관세청", "경찰청"]
SHOP = ["백화점", "이마트", "롯데마트", "신세계몰", "쿠팡", "11번가", "G마켓"]
MONEY = ["12,900", "35,000", "48,700", "128,000", "356,000", "1,250,000", "2,480,000", "89,000", "770,000"]
NAMES = ["김민수", "이영희", "박정호", "최수진", "정대현", "강미경", "윤성호", "임지은", "한상철", "조은주"]
FAMILY = ["엄마", "아빠", "형", "누나", "언니", "동생", "이모", "삼촌", "할머니"]
TIME = ["09:12", "10:45", "13:20", "15:07", "17:33", "19:48", "21:15", "22:40"]
DATE = ["1/12", "2/03", "3/21", "4/09", "5/17", "6/28", "7/05", "8/14", "9/23", "10/11", "11/02", "12/19"]
HOSP = ["서울내과의원", "행복치과", "우리정형외과", "미소안과", "한마음병원", "연세이비인후과"]
TELCO = ["SKT", "KT", "LG U+", "알뜰폰"]


def rnd(n):
    return "".join(random.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(n))


def phone():
    return random.choice(
        [
            "010-{0}{1}{2}{3}-{4}{5}{6}{7}",
            "070-{0}{1}{2}{3}-{4}{5}{6}{7}",
            "02-{0}{1}{2}{3}-{4}{5}{6}{7}",
            "1588-{0}{1}{2}{3}",
            "1666-{0}{1}{2}{3}",
        ]
    ).format(*[random.randint(0, 9) for _ in range(8)])


def link():
    t = random.choice(LINKS)
    return t.format(r4=rnd(4), r5=rnd(5))


def masked_name():
    n = random.choice(NAMES)
    return n[0] + "*" + n[2]


def card_no():
    return "{0}{1}{2}{3}*".format(*[random.randint(0, 9) for _ in range(4)])


# --------------------------------------------------------------------------
# 스미싱 템플릿
# --------------------------------------------------------------------------
SPAM = [
    # 택배 사칭
    "[Web발신]\n[{courier}] 주소불일치로 물품 배송이 보류되었습니다. 주소 확인 {link}",
    "[Web발신]\n[{courier}] 미수령 택배 1건 보관중. 오늘까지 미확인시 반송됩니다 {link}",
    "[Web발신]\n[{courier}] 송장번호 오류로 배송 지연. 정보 수정 바랍니다 {link}",
    "[Web발신]\n고객님 앞으로 도착한 종물물품 1건이 있습니다. 조회 {link}",
    "[Web발신]\n[{courier}] 배송지 미확인 상품 반송 예정입니다. 확인 {link}",
    "[국제우편] 통관보류 물품 안내드립니다. 미확인시 폐기 처리 {link}",
    # 공공기관 사칭
    "[Web발신]\n[{gov}] 종합소득세 환급금 {money}원이 미수령 상태입니다. 신청 {link}",
    "[Web발신]\n[{gov}] 미납 과태료 {money}원 최종 안내. 미납시 재산압류 {link}",
    "[Web발신]\n[{gov}] 국민연금 미환급금 조회 대상자입니다. 확인 {link}",
    "[Web발신]\n[{gov}] 건강검진 미수검자 안내. 대상자 조회 {link}",
    "[Web발신]\n[법원] 전자소송 출석요구서가 송달되었습니다. 열람 {link}",
    "[Web발신]\n[검찰청] 귀하의 명의로 계좌가 개설되어 수사중입니다. 확인 {link}",
    "[Web발신]\n[{gov}] 정부지원금 신청 대상자로 선정되셨습니다. 신청기한 오늘까지 {link}",
    "[Web발신]\n[{gov}] 소상공인 재난지원금 지급 대상 안내 {link}",
    "[Web발신]\n[{gov}] 재택 근무자 지원금 신청 접수중입니다 {link}",
    # 금융/대출
    "[Web발신]\n[{bank}] 저금리 대환대출 최대 {money}원 한도확인 가능합니다 {link}",
    "[Web발신]\n[{bank}] 고객님 신용등급 상승으로 추가한도 승인되었습니다 {link}",
    "[Web발신]\n[{card}] 카드 발급이 완료되었습니다. 본인 신청이 아니면 {link}",
    "[Web발신]\n[{card}] 해외결제 {money}원 승인. 본인 아닐시 즉시 문의 {link}",
    "[Web발신]\n[{bank}] 비정상 로그인 감지. 계정 정지 예정입니다 {link}",
    "[Web발신]\n[{bank}] 고객님 계좌에서 {money}원 이체 시도가 감지되었습니다 {link}",
    "[Web발신]\n[{card}] 결제 오류로 승인 실패. 카드정보 재등록 필요합니다 {link}",
    "[Web발신]\n마이너스통장 신규 대상자입니다. 서류없이 당일 입금 {link}",
    "[Web발신]\n[{bank}] 대출 심사 결과 안내드립니다. 결과 확인 {link}",
    # 결제/구매 미끼
    "[Web발신]\n[{shop}] {money}원 결제가 완료되었습니다. 본인 아니면 {phone}",
    "[Web발신]\n해외 직구 {money}원 결제 승인 안내. 취소 문의 {phone}",
    "[Web발신]\n[{shop}] 주문하신 상품이 결제 처리되었습니다. 취소 {link}",
    "[Web발신]\n앱 정기결제 {money}원 자동 갱신 예정입니다. 해지 {link}",
    # 경품/이벤트
    "[Web발신]\n축하합니다! {shop} 경품 이벤트에 당첨되셨습니다 {link}",
    "[Web발신]\n[이벤트] 무료 상품권 {money}원 선착순 지급중. 지금 신청 {link}",
    "[Web발신]\n고객님 포인트 소멸 예정입니다. 무료 전환 신청 {link}",
    "[Web발신]\n{shop} 상품권 무료 증정 이벤트 당첨자로 선정되셨습니다 {link}",
    "[Web발신]\n[긴급] 미사용 포인트 {money}점 오늘 소멸됩니다 {link}",
    # 부업/투자
    "[Web발신]\n재택 부업 모집. 하루 2시간 고수익 보장 {link}",
    "[Web발신]\n단기 알바 급하게 구합니다. 일당 20만원 지급 {phone}",
    "[Web발신]\n[투자] 종목 무료 추천방 오픈. 수익률 182% 실화입니다 {link}",
    "[Web발신]\n소액으로 시작하는 재테크. 원금보장 고수익 {link}",
    "[Web발신]\n온라인 쇼핑몰 리뷰 알바 모집합니다. 건당 1만원 {link}",
    # 계정/보안
    "[Web발신]\n[보안경고] 개인정보 유출이 확인되었습니다. 즉시 조치 {link}",
    "[Web발신]\n타지역에서 로그인 시도가 감지되었습니다. 본인확인 {link}",
    "[Web발신]\n계정 도용 의심으로 이용이 제한되었습니다. 해제 {link}",
    "[Web발신]\n귀하의 명의로 휴대폰이 개통되었습니다. 신고 {link}",
    "[Web발신]\n앱 업데이트공개 필요. 미업데이트시 서비스 중단됩니다 {link}",
    # 지인 사칭 / 초대장
    "엄마 나 폰 고장나서 컴퓨터로 문자해. 급하게 필요한거 있어서 {link}",
    "아빠 지금 통화 안돼서 문자로 보내. 이거 좀 확인해줘 {link}",
    "[모바일 청첩장] {name} 결혼합니다. 초대장 확인 {link}",
    "[부고] 삼가 고인의 명복을 빕니다. 부고장 {link}",
    "[모바일 초대장] 우리 아이 돌잔치에 초대합니다 {link}",
    # 기타
    "[Web발신]\n무료 운세 이벤트 참여하고 상품 받아가세요 {link}",
    "[Web발신]\n[알림] 미납 통신요금 {money}원 정지 예정 안내 {link}",
    "[Web발신]\n백신 접종 예약 변경 안내드립니다. 확인 {link}",
    "[Web발신]\n고객님 계좌가 보이스피싱 피해 계좌로 신고되었습니다 {phone}",
]

# --------------------------------------------------------------------------
# 정상 템플릿
# --------------------------------------------------------------------------
HAM = [
    # 실제 카드/은행 알림
    "[Web발신]\n{card} 승인 {maskname}\n{money}원 일시불\n{date} {time}\n{shop}",
    "[Web발신]\n{bank} 입금 {money}원\n잔액 {money2}원\n{date} {time}",
    "[Web발신]\n{bank} 출금 {money}원\n{date} {time} 자동이체",
    "[Web발신]\n{card} {date} 청구금액 {money}원 안내드립니다. 문의 {phone}",
    "[Web발신]\n{bank} 예금 만기 안내. 자세한 내용은 영업점 또는 {phone}",
    "{card} 카드 이용대금 {money}원이 정상 출금되었습니다.",
    "[Web발신]\n{bank} 체크카드 승인 {money}원 {shop} {time}",
    # 택배 정상
    "[{courier}] 고객님의 상품이 오늘 도착 예정입니다. 기사 {name} {phone}",
    "[{courier}] 상품을 문 앞에 두고 갔습니다. 확인 부탁드립니다.",
    "안녕하세요 {courier} {name}입니다. 부재중이라 경비실에 맡겨두었습니다.",
    "[{courier}] 배송이 완료되었습니다. 이용해 주셔서 감사합니다.",
    "{shop} 주문하신 상품이 발송되었습니다. 송장번호는 앱에서 확인하세요.",
    # 병원/예약
    "{hosp}입니다. 내일 {time} 예약 확인 전화드렸는데 부재중이셨습니다. {phone}",
    "{hosp} 예약 안내: {date} {time}. 변경은 {phone}로 연락 주세요.",
    "{hosp}입니다. 처방하신 약 준비되었습니다. 방문해 주세요.",
    "{hosp} 검진 결과가 나왔습니다. 내원하셔서 상담 받으시기 바랍니다.",
    # 관공서 정상 안내
    "[{gov}] 예방접종 안내입니다. 가까운 보건소에서 접종 가능합니다. 문의 {phone}",
    "[{gov}] 민방위 교육 일정 안내입니다. 대상자는 사이버교육 이수 바랍니다.",
    "[{gov}] 주민세 납부 기한은 {date}까지입니다. 문의는 {phone}",
    "[주민센터] 신청하신 서류 발급이 완료되었습니다. 방문 수령 바랍니다.",
    # 학교/기관
    "[{school}] 내일은 단축수업입니다. 하교 시간 확인 부탁드립니다.",
    "[{school}] 학부모 상담 주간 안내드립니다. 신청서를 보내드렸습니다.",
    "[{school}] 급식 식단표를 가정통신문으로 배부하였습니다.",
    "[{school}] 현장학습 관련 동의서 제출 부탁드립니다.",
    "[학원] {name} 학생 오늘 결석했습니다. 확인 부탁드립니다.",
    # 회사/업무
    "{name}님 내일 회의 {time}으로 변경되었습니다. 확인 부탁드립니다.",
    "오늘 회식 {time}에 시작합니다. 장소는 사무실 앞에서 모입니다.",
    "{name} 대리님 요청하신 자료 메일로 보냈습니다. 확인 부탁드려요.",
    "월요일 출근 전에 보고서 초안 공유 부탁드립니다. 감사합니다.",
    "휴가 결재 승인되었습니다. 인수인계 진행해 주세요.",
    # 개인 대화
    "{fam} 오늘 저녁에 집에 몇 시쯤 와? 밥 차려놓을게",
    "{fam} 약 잘 챙겨 드시고 계세요. 주말에 갈게요",
    "나 지금 출발했어. {time}쯤 도착할 것 같아",
    "어제 고마웠어. 다음에 밥 한번 사줄게",
    "{name}아 생일 축하해! 좋은 하루 보내",
    "비 온대. 우산 챙겨서 나가",
    "이번 주말에 시간 괜찮아? 얼굴 한번 보자",
    "장 보러 가는데 뭐 필요한 거 있어?",
    "{fam} 사진 잘 받았어요. 건강 조심하세요",
    # 통신/생활
    "[{telco}] 이번 달 요금은 {money}원입니다. 자세한 내역은 고객센터 {phone}",
    "[{telco}] 데이터 사용량이 80%를 초과했습니다. 남은 기간 확인하세요.",
    "[{telco}] 요금이 정상 납부되었습니다. 이용해 주셔서 감사합니다.",
    "[아파트관리사무소] 정기 소방점검이 {date}에 있습니다. 협조 부탁드립니다.",
    "[아파트관리사무소] 단수 안내: {date} {time}부터 2시간 단수 예정입니다.",
    "[{shop}] 주문번호 확인 결과 정상 배송 중입니다. 문의 {phone}",
    "[도서관] 대출하신 도서 반납일이 {date}입니다.",
    "[헬스장] 회원권이 {date}에 만료됩니다. 데스크로 문의 주세요.",
    "[미용실] 예약 {date} {time} 확인되었습니다. 늦지 않게 방문 부탁드려요.",
    "[세탁소] 맡기신 옷 세탁 완료되었습니다. 편하실 때 찾아가세요.",
]

SCHOOL = ["햇살초등학교", "중앙중학교", "한빛고등학교", "새싹유치원", "푸른어린이집"]


def fill_spam(t):
    return (
        t.replace("{link}", link())
        .replace("{phone}", phone())
        .replace("{courier}", random.choice(COURIER))
        .replace("{gov}", random.choice(GOV))
        .replace("{bank}", random.choice(BANK))
        .replace("{card}", random.choice(CARD))
        .replace("{shop}", random.choice(SHOP))
        .replace("{money}", random.choice(MONEY))
        .replace("{name}", random.choice(NAMES))
    )


def fill_ham(t):
    return (
        t.replace("{phone}", phone())
        .replace("{courier}", random.choice(COURIER))
        .replace("{gov}", random.choice(GOV))
        .replace("{bank}", random.choice(BANK))
        .replace("{card}", random.choice(CARD))
        .replace("{shop}", random.choice(SHOP))
        .replace("{money2}", random.choice(MONEY))
        .replace("{money}", random.choice(MONEY))
        .replace("{name}", random.choice(NAMES))
        .replace("{maskname}", masked_name())
        .replace("{date}", random.choice(DATE))
        .replace("{time}", random.choice(TIME))
        .replace("{hosp}", random.choice(HOSP))
        .replace("{fam}", random.choice(FAMILY))
        .replace("{telco}", random.choice(TELCO))
        .replace("{school}", random.choice(SCHOOL))
    )


# 정상 문자에도 일부 링크가 들어가야 "링크=스미싱"으로만 학습되지 않는다.
HAM_LINK_SUFFIX = [
    "",
    "",
    "",
    "",
    "",
    " 자세히 보기: {link}",
    " 앱에서 확인: {link}",
]


def build(n_each=500):
    rows = []

    seen = set()
    tries = 0
    while sum(1 for r in rows if r[1] == "스미싱") < n_each and tries < 200000:
        tries += 1
        s = fill_spam(random.choice(SPAM))
        if s in seen:
            continue
        seen.add(s)
        rows.append((s, "스미싱"))

    tries = 0
    while sum(1 for r in rows if r[1] == "정상") < n_each and tries < 200000:
        tries += 1
        h = fill_ham(random.choice(HAM))
        suf = random.choice(HAM_LINK_SUFFIX)
        if suf:
            h += suf.replace("{link}", "https://www.naver.com/" + rnd(4))
        if h in seen:
            continue
        seen.add(h)
        rows.append((h, "정상"))

    random.shuffle(rows)
    return rows


def main():
    rows = build()
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["문자내용", "분류"])
        w.writerows(rows)
    n_spam = sum(1 for r in rows if r[1] == "스미싱")
    print(f"생성 완료: {OUT}")
    print(f"  총 {len(rows)}건 (스미싱 {n_spam} / 정상 {len(rows) - n_spam})")


if __name__ == "__main__":
    main()
