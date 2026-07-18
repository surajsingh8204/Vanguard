import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { motion } from 'framer-motion'
import {
  Bot,
  MessagesSquare,
  Plus,
  SendHorizonal,
  Sparkles,
  Trash2,
  User as UserIcon,
} from 'lucide-react'
import { toast } from 'sonner'
import globeNetwork from '@/assets/globe-network.png'
import {
  askQuestion,
  deleteConversation,
  getConversation,
  listConversations,
} from '@/api/chat'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { cn, formatDate, truncate } from '@/lib/utils'

const SUGGESTIONS = [
  'What are the highest influence narratives right now?',
  'Summarize emerging risks across clusters.',
  'Which entities appear most connected in the knowledge graph?',
  'Explain the strongest forecast signals.',
]

export function Chat() {
  const queryClient = useQueryClient()
  const [activeId, setActiveId] = useState<number | null>(null)
  const [question, setQuestion] = useState('')
  const [pendingUser, setPendingUser] = useState<string | null>(null)
  const [lastStats, setLastStats] = useState<Record<string, unknown> | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const conversationsQuery = useQuery({
    queryKey: ['conversations'],
    queryFn: listConversations,
  })

  const conversationQuery = useQuery({
    queryKey: ['conversation', activeId],
    queryFn: () => getConversation(activeId!),
    enabled: activeId != null,
  })

  const askMutation = useMutation({
    mutationFn: ({ q, id }: { q: string; id: number | null }) => askQuestion(q, id),
    onSuccess: async (result) => {
      setActiveId(result.conversation_id)
      setPendingUser(null)
      setLastStats(result.retrieval_stats ?? null)
      await queryClient.invalidateQueries({ queryKey: ['conversations'] })
      await queryClient.invalidateQueries({
        queryKey: ['conversation', result.conversation_id],
      })
    },
    onError: (error) => {
      setPendingUser(null)
      toast.error(error instanceof Error ? error.message : 'Query failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteConversation,
    onSuccess: async (_, id) => {
      if (activeId === id) setActiveId(null)
      await queryClient.invalidateQueries({ queryKey: ['conversations'] })
      toast.success('Conversation deleted')
    },
  })

  const messages = useMemo(() => {
    const base = conversationQuery.data?.messages ?? []
    if (!pendingUser) return base
    return [
      ...base,
      {
        id: -1,
        role: 'user',
        content: pendingUser,
        created_at: new Date().toISOString(),
      },
    ]
  }, [conversationQuery.data, pendingUser])

  useEffect(() => {
    if (messages.length === 0) return
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    })
  }, [messages.length, askMutation.isPending])

  function submit(text: string) {
    const q = text.trim()
    if (!q || askMutation.isPending) return
    setQuestion('')
    setPendingUser(q)
    askMutation.mutate({ q, id: activeId })
  }

  const isEmpty = !messages.length && !askMutation.isPending

  return (
    <div className="flex h-[calc(100vh-8.5rem)] gap-5">
      {/* Conversation list */}
      <aside className="hidden w-72 shrink-0 flex-col rounded-2xl border border-line/80 bg-surface-2/50 lg:flex">
        <div className="flex items-center justify-between border-b border-line/60 px-4 py-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-ink">
            <MessagesSquare className="h-4 w-4 text-ink-muted" />
            Conversations
          </div>
          <Button
            size="sm"
            variant="secondary"
            className="gap-1.5"
            onClick={() => {
              setActiveId(null)
              setPendingUser(null)
              setLastStats(null)
            }}
          >
            <Plus className="h-3.5 w-3.5" />
            New
          </Button>
        </div>
        <div className="min-h-0 flex-1 space-y-1 overflow-auto p-3">
          {conversationsQuery.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
            </div>
          ) : conversationsQuery.data?.length ? (
            conversationsQuery.data.map((c) => (
              <div
                key={c.id}
                className={cn(
                  'group flex items-center gap-2 rounded-xl px-3 py-2.5 transition-colors',
                  activeId === c.id
                    ? 'bg-surface-3 text-ink'
                    : 'text-ink-muted hover:bg-surface-3/60 hover:text-ink',
                )}
              >
                <button
                  type="button"
                  className="min-w-0 flex-1 text-left"
                  onClick={() => setActiveId(c.id)}
                >
                  <p className="truncate text-sm font-medium">{c.title}</p>
                  <p className="mt-0.5 text-[11px] text-ink-faint">{formatDate(c.updated_at)}</p>
                </button>
                <button
                  type="button"
                  aria-label="Delete conversation"
                  className="hidden shrink-0 rounded-md p-1.5 text-ink-faint hover:bg-danger/15 hover:text-danger group-hover:block"
                  onClick={() => deleteMutation.mutate(c.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))
          ) : (
            <p className="px-3 py-6 text-center text-sm text-ink-faint">No conversations yet</p>
          )}
        </div>
      </aside>

      {/* Chat surface */}
      <section className="flex min-w-0 flex-1 flex-col rounded-2xl border border-line/80 bg-surface-2/40">
        <div className="flex items-center justify-between border-b border-line/60 px-6 py-4">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-ink">
              {conversationQuery.data?.title ?? 'New analysis session'}
            </p>
            <p className="mt-0.5 text-xs text-ink-faint">
              Grounded in the indexed narrative corpus · RAG retrieval
            </p>
          </div>
          {lastStats && Object.keys(lastStats).length ? (
            <div className="hidden flex-wrap justify-end gap-1.5 md:flex">
              {Object.entries(lastStats)
                .slice(0, 4)
                .map(([key, value]) => (
                  <Badge key={key} tone="info">
                    {key}: {typeof value === 'number' ? value.toFixed?.(2) ?? value : String(value)}
                  </Badge>
                ))}
            </div>
          ) : null}
        </div>

        <div ref={scrollRef} className="min-h-0 flex-1 overflow-auto">
          {isEmpty ? (
            <div className="flex min-h-full flex-col items-center justify-center gap-8 px-6 py-10">
              <div className="text-center">
                <div className="relative mx-auto mb-6 h-28 w-28">
                  <img
                    src={globeNetwork}
                    alt=""
                    aria-hidden
                    className="h-full w-full rounded-full object-cover shadow-[0_0_60px_rgba(91,141,239,0.35)]"
                  />
                  <span className="absolute -bottom-1 -right-1 flex h-10 w-10 items-center justify-center rounded-xl border border-accent/30 bg-surface-2 shadow-lg">
                    <Sparkles className="h-5 w-5 text-accent" />
                  </span>
                </div>
                <h2 className="text-lg font-semibold text-ink">Ask the intelligence engine</h2>
                <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-ink-muted">
                  Answers are retrieved and reranked from the vector index, then synthesized
                  with strategic context.
                </p>
              </div>
              <div className="grid w-full max-w-2xl gap-3 sm:grid-cols-2">
                {SUGGESTIONS.map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => submit(item)}
                    className="rounded-xl border border-line bg-surface/70 px-4 py-3.5 text-left text-sm leading-relaxed text-ink-muted transition-colors hover:border-accent/40 hover:bg-surface-3/40 hover:text-ink"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto max-w-3xl space-y-7 px-6 py-8">
              {messages.map((message) => {
                const isUser = message.role === 'user'
                return (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn('flex gap-4', isUser && 'flex-row-reverse')}
                  >
                    <span
                      className={cn(
                        'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border',
                        isUser
                          ? 'border-accent-2/30 bg-accent-2/10 text-accent-2'
                          : 'border-accent/30 bg-accent/10 text-accent',
                      )}
                    >
                      {isUser ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    </span>
                    <div
                      className={cn(
                        'max-w-[85%] rounded-2xl px-5 py-4 text-sm leading-7',
                        isUser
                          ? 'rounded-tr-sm bg-accent-2/12 text-ink'
                          : 'rounded-tl-sm border border-line/70 bg-surface/80 text-ink-muted',
                      )}
                    >
                      {isUser ? (
                        message.content
                      ) : (
                        <div className="prose prose-invert prose-sm max-w-none prose-p:leading-7 prose-li:leading-7">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )
              })}

              {askMutation.isPending ? (
                <div className="flex gap-4">
                  <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-accent/30 bg-accent/10 text-accent">
                    <Bot className="h-4 w-4" />
                  </span>
                  <div className="rounded-2xl rounded-tl-sm border border-line/70 bg-surface/80 px-5 py-4">
                    <span className="flex gap-1.5">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-accent/70 [animation-delay:0ms]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-accent/70 [animation-delay:150ms]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-accent/70 [animation-delay:300ms]" />
                    </span>
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>

        <div className="border-t border-line/60 px-6 py-5">
          <form
            className="mx-auto flex max-w-3xl items-end gap-3"
            onSubmit={(e) => {
              e.preventDefault()
              submit(question)
            }}
          >
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  submit(question)
                }
              }}
              rows={1}
              placeholder="Ask about narratives, risks, entities… (Enter to send, Shift+Enter for a new line)"
              className="max-h-40 min-h-[52px] flex-1 resize-none rounded-xl px-4 py-3.5 leading-6"
            />
            <Button
              size="icon"
              className="h-[52px] w-[52px] shrink-0 rounded-xl"
              disabled={askMutation.isPending || !question.trim()}
              aria-label="Send"
            >
              <SendHorizonal className="h-5 w-5" />
            </Button>
          </form>
          <p className="mx-auto mt-2.5 max-w-3xl text-[11px] text-ink-faint">
            {truncate('Responses are generated from retrieved intelligence and may require analyst verification.', 120)}
          </p>
        </div>
      </section>
    </div>
  )
}
