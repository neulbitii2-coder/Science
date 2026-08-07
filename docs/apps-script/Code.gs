/**
 * 스미싱 문자 판별기 — 공유 수집함
 *
 * 방문자가 신고한 문자를 구글 시트 한 장에 모읍니다. 서버가 따로 필요 없습니다.
 *
 * ── 설치 방법 ────────────────────────────────────────────────
 * 1. 구글 드라이브에서 새 스프레드시트를 하나 만듭니다. (이름은 아무거나)
 * 2. 메뉴 [확장 프로그램] → [Apps Script] 를 엽니다.
 * 3. 편집기의 코드를 전부 지우고 이 파일 내용을 붙여넣은 뒤 저장합니다.
 * 4. 오른쪽 위 [배포] → [새 배포] → 유형 [웹 앱] 을 고릅니다.
 *      - 실행 사용자      : 나
 *      - 액세스 권한 있는 사용자 : 모든 사용자          ← 꼭 이렇게
 * 5. [배포]를 누르고 권한을 허용하면 아래 형태의 주소가 나옵니다.
 *      https://script.google.com/macros/s/AKfycb.../exec
 * 6. 그 주소를 저장소의 data/collect_url.txt 에 한 줄로 붙여넣고
 *      python3 data/build.py
 *    를 돌린 뒤 커밋·푸시하면 웹앱이 그 시트로 신고를 보냅니다.
 *
 * ※ 코드를 고친 뒤에는 [배포] → [배포 관리] → 연필 아이콘 → 버전 [새 버전] → [배포]
 *   를 해야 반영됩니다. 주소는 그대로 유지됩니다.
 */

const SHEET_NAME = '신고문자';
const MAX_LEN = 2000;        // 문자 한 건당 저장할 최대 글자 수
const MAX_PER_MINUTE = 30;   // 같은 분 안에 받을 최대 건수 (장난 요청 완화)

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);

    if (!e || !e.postData || !e.postData.contents) return json({ ok: false, error: 'empty body' });
    if (!underRateLimit()) return json({ ok: false, error: 'rate limited' });

    const d = JSON.parse(e.postData.contents);
    const text = String(d.text == null ? '' : d.text).slice(0, MAX_LEN);
    if (!text.trim()) return json({ ok: false, error: 'no text' });

    const label = d.label === '스미싱' ? '스미싱' : d.label === '정상' ? '정상' : '미분류';
    const pct = (typeof d.pct === 'number' && isFinite(d.pct)) ? Math.round(d.pct) : '';
    const at = d.ts ? new Date(Number(d.ts)) : new Date();

    sheet().appendRow([at, text, label, pct]);
    return json({ ok: true });

  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignored) {}
  }
}

/** 브라우저에서 주소를 열어보면 지금까지 모인 건수를 알려줍니다. */
function doGet() {
  const n = Math.max(0, sheet().getLastRow() - 1);
  return json({ ok: true, rows: n });
}

function sheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(['접수시각', '문자내용', '분류', '위험도']);
    sh.setFrozenRows(1);
    sh.setColumnWidth(1, 150);
    sh.setColumnWidth(2, 620);
    sh.getRange('B:B').setWrap(true);
  }
  return sh;
}

/** 1분 단위 간이 유량 제한 */
function underRateLimit() {
  const cache = CacheService.getScriptCache();
  const key = 'rl_' + Math.floor(Date.now() / 60000);
  const n = Number(cache.get(key) || 0) + 1;
  cache.put(key, String(n), 120);
  return n <= MAX_PER_MINUTE;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
