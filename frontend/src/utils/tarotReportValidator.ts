const REQUIRED_TAROT_SECTIONS: Array<{ name: string; keywords: string[] }> = [
  { name: '问题聚焦', keywords: ['问题聚焦'] },
  { name: '抽牌结果', keywords: ['抽牌结果'] },
  { name: '逐牌专业解读', keywords: ['逐牌专业解读', '逐牌解读'] },
  { name: '行动建议', keywords: ['行动建议'] },
]

export function findMissingTarotSections(text: string): string[] {
  return REQUIRED_TAROT_SECTIONS
    .filter((section) => !section.keywords.some((keyword) => text.includes(keyword)))
    .map((section) => section.name)
}
