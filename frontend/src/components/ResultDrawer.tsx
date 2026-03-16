import { Button } from '@/components/ui/button'
import { Sparkles, X } from 'lucide-react'
import { useRef, useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { parseTarotStructuredReport, type TarotCardItem } from '@/utils/tarotReportParser'

interface ResultDrawerProps {
  show: boolean
  onClose: () => void
  result: string
  rawResult?: string
  loading: boolean
  streaming: boolean
  divinationType?: string
}

export function ResultDrawer({
  show,
  onClose,
  result,
  rawResult = '',
  loading,
  streaming,
  divinationType,
}: ResultDrawerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isAnimating, setIsAnimating] = useState(false)

  // 控制入场动画
  useEffect(() => {
    if (show) {
      // 延迟一帧，让浏览器先渲染初始状态
      requestAnimationFrame(() => {
        setIsAnimating(true)
      })
    } else {
      setIsAnimating(false)
    }
  }, [show])

  // 自动滚动到底部 - 在内容更新时自动滚动
  useEffect(() => {
    if (result && containerRef.current) {
      const timeoutId = setTimeout(() => {
        if (containerRef.current) {
          containerRef.current.scrollTop = containerRef.current.scrollHeight
        }
      }, 100)
      return () => clearTimeout(timeoutId)
    }
  }, [result])

  if (!show) return null

  const tarotStructured = divinationType === 'tarot' ? parseTarotStructuredReport(rawResult) : null
  const invalidTarotCards = tarotStructured
    ? tarotStructured.cards.filter((card) => !card.isValidName)
    : []
  const tarotCardByPosition: Record<TarotCardItem['position'], TarotCardItem | undefined> = {
    过去位: tarotStructured?.cards.find((card) => card.position === '过去位'),
    现在位: tarotStructured?.cards.find((card) => card.position === '现在位'),
    未来位: tarotStructured?.cards.find((card) => card.position === '未来位'),
  }

  const drawerContent = (
    <div className="fixed inset-0 z-50 animate-in fade-in duration-200">
      {/* 背景遮罩 */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      ></div>
      {/* 抽屉容器 - 固定在底部 */}
      <div
        className="fixed inset-x-0 bottom-0 z-50 h-[80vh] rounded-t-2xl md:rounded-t-3xl border-t bg-background shadow-2xl transition-transform duration-300 ease-out"
        style={{
          transform: isAnimating ? 'translateY(0)' : 'translateY(100%)',
        }}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between border-b p-4 md:p-6 bg-card">
          <div className="flex items-center gap-2 md:gap-3">
            <Sparkles className="h-4 w-4 md:h-5 md:w-5 text-primary" />
            <h3 className="text-lg md:text-xl font-semibold">占卜结果</h3>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="rounded-full hover:bg-muted h-8 w-8 md:h-10 md:w-10"
          >
            <X className="h-4 w-4 md:h-5 md:w-5" />
          </Button>
        </div>
        {/* 内容区域 */}
        <div
          ref={containerRef}
          className="overflow-y-auto p-4 md:p-6 h-[calc(80vh-5rem)]"
        >
          {loading ? (
            <div className="flex flex-col items-center justify-center h-full space-y-4 md:space-y-6">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 md:h-20 md:w-20 border-4 border-primary/20 border-t-primary"></div>
                <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-6 w-6 md:h-8 md:w-8 text-primary animate-pulse" />
              </div>
              <div className="text-center space-y-2">
                <p className="text-base md:text-lg font-medium">正在占卜中...</p>
                <p className="text-xs md:text-sm text-muted-foreground">
                  请稍候，AI 正在为您解读
                </p>
              </div>
            </div>
          ) : result ? (
            <div className={streaming ? 'streaming-content' : 'animate-in fade-in duration-300'}>
              {divinationType === 'tarot' && tarotStructured && tarotStructured.cards.length > 0 && (
                <div className="mb-5 space-y-3 rounded-xl border border-primary/20 bg-card/60 p-3 md:p-4">
                  <div className="text-sm font-semibold text-primary">塔罗结构化摘要</div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    {(['过去位', '现在位', '未来位'] as const).map((position) => {
                      const card = tarotCardByPosition[position]
                      return (
                        <div key={position} className="rounded-lg border border-border bg-background/60 p-2">
                          <div className="text-xs text-muted-foreground flex items-center justify-between">
                            <span>{position}</span>
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] ${
                                !card
                                  ? 'bg-slate-500/15 text-slate-600'
                                  : card.isValidName
                                    ? 'bg-emerald-500/15 text-emerald-600'
                                    : 'bg-amber-500/15 text-amber-600'
                              }`}
                            >
                              {!card ? '缺失' : card.isValidName ? 'RWS' : '待核验'}
                            </span>
                          </div>
                          <div className="text-sm mt-1">
                            {card?.content || '未提取到该位置牌面，请查看下方全文。'}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  {(tarotStructured.tendency || tarotStructured.confidence !== undefined) && (
                    <div className="rounded-lg border border-primary/20 bg-primary/5 p-2">
                      <div className="text-xs text-muted-foreground mb-1">决策信号</div>
                      {tarotStructured.tendency && (
                        <div className="text-sm">{tarotStructured.tendency}</div>
                      )}
                      {tarotStructured.confidence !== undefined && (
                        <div className="text-sm mt-1">置信度：{tarotStructured.confidence}%</div>
                      )}
                    </div>
                  )}
                  {invalidTarotCards.length > 0 && (
                    <div className="rounded-lg border border-amber-400/30 bg-amber-500/10 p-2">
                      <div className="text-xs text-amber-700 font-medium">牌名校验提醒</div>
                      <div className="text-xs mt-1 text-amber-700/90">
                        以下牌名不在标准 RWS 命名内，请人工复核：
                        {invalidTarotCards.map((card) => card.cardName || card.position).join('、')}
                      </div>
                    </div>
                  )}
                  {tarotStructured.actions.length > 0 && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">行动建议</div>
                      <ul className="list-disc pl-5 space-y-1">
                        {tarotStructured.actions.map((item, idx) => (
                          <li key={`${item}-${idx}`} className="text-sm">{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {tarotStructured.risks.length > 0 && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">风险提示</div>
                      <ul className="list-disc pl-5 space-y-1">
                        {tarotStructured.risks.map((item, idx) => (
                          <li key={`${item}-${idx}`} className="text-sm">{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              <div
                className="prose prose-xs md:prose-sm max-w-none dark:prose-invert prose-headings:text-foreground prose-p:text-foreground/90 prose-strong:text-foreground prose-ul:text-foreground/90 prose-ol:text-foreground/90"
                dangerouslySetInnerHTML={{ __html: result }}
              />
              {streaming && (
                <span className="inline-flex w-1.5 h-5 ml-1 bg-primary cursor-blink align-middle rounded-sm shadow-lg"></span>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )

  // 使用 Portal 将抽屉渲染到 body,避免父容器样式干扰
  return createPortal(drawerContent, document.body)
}
