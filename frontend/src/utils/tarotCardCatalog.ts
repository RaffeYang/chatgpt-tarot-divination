const MAJOR_ARCANA = new Set([
  '愚者', '魔术师', '女祭司', '皇后', '皇帝', '教皇', '恋人', '战车', '力量', '隐者',
  '命运之轮', '正义', '倒吊人', '死神', '节制', '恶魔', '高塔', '星星', '月亮', '太阳',
  '审判', '世界',
  'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor',
  'The Hierophant', 'The Lovers', 'The Chariot', 'Strength', 'The Hermit',
  'Wheel of Fortune', 'Justice', 'The Hanged Man', 'Death', 'Temperance',
  'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun', 'Judgement', 'Judgment', 'The World',
])

const MINOR_CN_PATTERN = /^(权杖|圣杯|宝剑|星币)(王牌|一|二|三|四|五|六|七|八|九|十|侍从|骑士|皇后|国王)$/
const MINOR_EN_PATTERN = /^(Ace|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Page|Knight|Queen|King) of (Wands|Cups|Swords|Pentacles)$/i

export function isValidTarotCardName(cardName: string): boolean {
  const name = cardName.trim()
  if (!name) return false
  if (MAJOR_ARCANA.has(name)) return true
  if (MINOR_CN_PATTERN.test(name)) return true
  if (MINOR_EN_PATTERN.test(name)) return true
  return false
}

export function extractTarotCardName(content: string): string {
  const cleaned = content.trim().replace(/^[-*]\s*/, '')
  const match = cleaned.match(/^([^（(｜|,，\s]+)/)
  return match?.[1]?.trim() || ''
}
