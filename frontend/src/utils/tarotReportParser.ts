export interface TarotCardItem {
  position: '过去位' | '现在位' | '未来位'
  content: string
}

export interface TarotStructuredReport {
  cards: TarotCardItem[]
  actions: string[]
  risks: string[]
}

const CARD_PATTERNS: Array<{ position: TarotCardItem['position']; regex: RegExp }> = [
  { position: '过去位', regex: /过去位[:：]\s*(.+)/ },
  { position: '现在位', regex: /现在位[:：]\s*(.+)/ },
  { position: '未来位', regex: /未来位[:：]\s*(.+)/ },
]

export function parseTarotStructuredReport(text: string): TarotStructuredReport {
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)

  const cards: TarotCardItem[] = []
  for (const pattern of CARD_PATTERNS) {
    const found = lines.find((line) => pattern.regex.test(line))
    if (found) {
      const matched = found.match(pattern.regex)
      if (matched?.[1]) {
        cards.push({ position: pattern.position, content: matched[1] })
      }
    }
  }

  const actions = lines
    .filter((line) => /^[-*]\s*/.test(line) && /(建议|可做|执行)/.test(line))
    .slice(0, 4)
    .map((line) => line.replace(/^[-*]\s*/, ''))

  const risks = lines
    .filter((line) => /^[-*]\s*/.test(line) && /(风险|预警|避免)/.test(line))
    .slice(0, 3)
    .map((line) => line.replace(/^[-*]\s*/, ''))

  return { cards, actions, risks }
}
