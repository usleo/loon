// X (Twitter) 信息流去广告 · 接口嗅探版
// 拦截规则用域名级通配覆盖 X 全域 API (x.com / api.twitter.com / twitter.com/*),
// 脚本内先快速判断再启发式过滤推广内容。X 新增/更换接口时自动覆盖,无需更新规则。
// 推广识别:entryId 含 promoted,或响应内存在 promotedMetadata 标记(递归查找,抗结构微调)。

var PROMOTED_HINT = /promot|advertis|sponsor/i;

function hasPromotedMarker(obj, depth) {
  if (obj === null || typeof obj !== 'object' || depth > 15) return false;
  if (Array.isArray(obj)) {
    for (var i = 0; i < obj.length; i++) {
      if (hasPromotedMarker(obj[i], depth + 1)) return true;
    }
    return false;
  }
  for (var k in obj) {
    if (!Object.prototype.hasOwnProperty.call(obj, k)) continue;
    if (k === 'promotedMetadata' && obj[k] !== null && obj[k] !== undefined) return true;
    if (typeof obj[k] === 'object' && hasPromotedMarker(obj[k], depth + 1)) return true;
  }
  return false;
}

function isPromotedEntry(entry) {
  if (!entry || typeof entry !== 'object') return false;
  var id = entry.entryId;
  if (typeof id === 'string' && /promoted/i.test(id)) return true;
  return hasPromotedMarker(entry, 0);
}

var removed = 0;

function walk(node) {
  var i, k;
  if (Array.isArray(node)) {
    if (node.length > 0 && node[0] !== null && typeof node[0] === 'object' &&
        typeof node[0].entryId === 'string') {
      var kept = [];
      for (i = 0; i < node.length; i++) {
        if (isPromotedEntry(node[i])) { removed++; continue; }
        kept.push(node[i]);
      }
      if (kept.length !== node.length) {
        node.length = 0;
        for (i = 0; i < kept.length; i++) node.push(kept[i]);
      }
    }
    for (i = 0; i < node.length; i++) walk(node[i]);
    return;
  }
  if (node !== null && typeof node === 'object') {
    for (k in node) {
      if (Object.prototype.hasOwnProperty.call(node, k)) walk(node[k]);
    }
  }
}

(function main() {
  var resp = (typeof $response !== 'undefined') ? $response : null;
  var body = resp && resp.body;
  // 快速放行:连推广相关字样都没有的响应直接跳过,避免每次解析大 JSON
  if (!body || !PROMOTED_HINT.test(body)) { $done({}); return; }
  var obj;
  try { obj = JSON.parse(body); } catch (e) { $done({}); return; }
  try { walk(obj); } catch (e) { $done({}); return; }
  if (removed > 0) {
    try { console.log('[X去广告] 已过滤 ' + removed + ' 条推广'); } catch (e) {}
    $done({ body: JSON.stringify(obj) });
  } else {
    $done({});
  }
})();
