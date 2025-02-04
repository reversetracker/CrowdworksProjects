from re2g import datasets
from re2g.datasets.v1 import DprDataset, SquadDataset


def test_squad_kor_v1_dataset():
    assert datasets.v1.DprDataset.example() == {
        "id": "6521755-3-1",
        "title": "알렉산더_헤이그",
        "context": '그의 편에 헤이그는 지구촌의 논점들의 국내적 정치 노력들에 관해서만 근심한 레이건의 가까운 조언자들을 "외교 정책의 아마추어"로 묘사하였다. 1982년 6월 25일 결국적으로 온 그의 국무장관으로서 사임은 불가능한 상황이 된 것을 끝냈다. 헤이그는 개인적 생활로 돌아갔다가 1988년 대통령 선거를 위한 공화당 후보직을 안정시키는 시도를 하는 데 충분하게 정계로 돌아갔으나 후보직을 이기는 데 성원을 가지지 않았다. 그는 외교 정책 논쟁들에 연설자로서 활동적으로 남아있었으나 그의 전념은 정치에서 개인적 생활로 옮겨졌다. 그는 Worldwide Associates Inc.의 국제적 상담 회사에 의하여 기용되었고, 그 기구의 의장과 회장이 되었다.',
        "question": "헤이그가 사적생활을 하다가 정계로 돌아갔던 해는 언제인가?",
        "answers": {"text": ["1988년"], "answer_start": [153]},
        "bm25_contexts": [
            "사법연수원을 16기로 수료한 후 변호사 생활을 하다가 16대 총선에서 서울 강남을에 출마하여 정계에 입문했다. 제16대 국회의원 시절 4년 연속 시민단체 주관 국정감사 우수위원으로 선정되었고, 정치개혁특위 간사를 맡아 깨끗하고 투명한 선거를 목적으로 한 소위 ‘오세훈 선거법’으로 불리는 3개 정치관계법 개정을 주도했다. 2006년 서울시장에 당선되어 2011년까지 서울특별시장을 연임하며 창의시정과 디자인 서울을 주요 정책으로 하면서, 청렴도 향상, 강남북 균형발전, 복지 정책 희망드림 프로젝트, 대기환경 개선 등에 주력하였고, 다산 콜 센터와 장기전세주택 시프트를 도입하였다. 2011년 저소득층을 대상으로 선별적 복지를 주장하며 서울시 무상 급식 정책에서 주민 투표를 제안하고, 투표율이 미달되자 시장직을 사퇴하였다. 바른정당 상임고문을 지내다가 국민의당과의 합당에 반대하며 2018년 2월 5일 바른정당을 탈당했다.",
            "지원 이동통신의 경우, LTE Cat.12·13, LTE Cat.9 그리고 LTE Cat.6 모델이 있다. 우선, 업로드 속도는 Cat.13이 150 Mbps, Cat.9와 Cat.6이 50 Mbps로 최대 속도가 잡혀있고, 다운로드 속도는 Cat.12가 600 Mbps, Cat.9가 450 Mbps 그리고 Cat.6이 300 Mbps로 최대 속도가 잡혀져있다. 3 Band 캐리어 어그리게이션의 경우 상황에 따라 추가적으로 지원하며, VoLTE를 지원한다. 또한, 갤럭시 S7과 같이 모든 기기의 통신 모뎀 솔루션이 모바일 AP에 내장된 최초의 갤럭시 S 시리즈 중 하나이다. 이는 퀄컴 스냅드래곤 시리즈를 탑재한 기존 갤럭시 S 시리즈 스마트폰은 극소수를 제외하면 통신 모뎀 솔루션이 기본적으로 내장되어 있었으나, 삼성 엑시노스 시리즈는 플래그십 AP로는 삼성 엑시노스 8890이 통신 모뎀 솔루션을 내장한 최초의 모바일 AP이기 때문이다.",
            "대학로에서 소문난 연기파 배우로서 2004년 아카펠라 연극 '겨울공주 평강이야기'를 시작으로 연극과 뮤지컬 무대에서 입지를 다졌다. 2015년 드라마 《육룡이 나르샤》에서 정도전의 혁명동지 역으로 시청자들에게 눈도장을 찍었으며, 2017년 영화 《범죄도시》에서는 흑룡파 조직의 보스 장첸(윤계상)의 오른팔로서 삭발한 머리와 날카로운 눈빛으로 등장하여 첫 악역 연기에 선보였다. 진선규는 600만 관객을 동원한 영화 《범죄도시》를 \"연기 인생의 터닝 포인트이자 인생작\"이라고 말했다. 진선규는 이 영화로 2017년 청룡영화제 남우조연상을 수상하였고, 시상식에서 수상자로 호명돼 무대에 오르자마자 눈물을 쏟는 수상 소감으로 감동을 안겼다.",
        ],
        "bm25_labels": [0, 0, 0],
    }


def test_dpr_dataset():
    squad_dataset = SquadDataset(split="validation")
    dpr_dataset = datasets.v1.DprDataset(dataset=squad_dataset, bm25_k=4)

    assert isinstance(dpr_dataset, DprDataset)

    assert any(dpr_dataset[0]["bm25_labels"]) is False
    assert any(dpr_dataset[1]["bm25_labels"]) is False
    assert any(dpr_dataset[2]["bm25_labels"]) is False
    assert any(dpr_dataset[3]["bm25_labels"]) is False

    assert dpr_dataset[0]["context"] not in dpr_dataset[0]["bm25_contexts"]
    assert dpr_dataset[1]["context"] not in dpr_dataset[1]["bm25_contexts"]
    assert dpr_dataset[2]["context"] not in dpr_dataset[2]["bm25_contexts"]
    assert dpr_dataset[3]["context"] not in dpr_dataset[3]["bm25_contexts"]

    assert len(dpr_dataset[0]["bm25_contexts"]) == 4
    assert len(dpr_dataset[1]["bm25_contexts"]) == 4
    assert len(dpr_dataset[2]["bm25_contexts"]) == 4
    assert len(dpr_dataset[3]["bm25_contexts"]) == 4
