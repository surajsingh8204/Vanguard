export function PageHeader({
  title,
  description,
  action,
  image,
}: {
  title: string
  description?: string
  action?: React.ReactNode
  image?: string
}) {
  if (image) {
    return (
      <div className="relative mb-6 overflow-hidden rounded-2xl border border-line/70 bg-surface-2">
        <img
          src={image}
          alt=""
          aria-hidden
          className="absolute inset-y-0 right-0 h-full w-[62%] object-cover object-center opacity-80 [mask-image:linear-gradient(to_right,transparent,black_45%)]"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-surface/40 via-transparent to-surface/20" />
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-accent/40 via-accent-2/30 to-transparent" />
        <div className="relative flex flex-wrap items-end justify-between gap-4 px-6 py-9 md:px-8">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-ink md:text-[1.7rem]">
              {title}
            </h1>
            {description ? (
              <p className="mt-1.5 max-w-2xl text-sm leading-6 text-ink-muted">{description}</p>
            ) : null}
          </div>
          {action}
        </div>
      </div>
    )
  }

  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">{title}</h1>
        {description ? (
          <p className="mt-1 max-w-2xl text-sm text-ink-muted">{description}</p>
        ) : null}
      </div>
      {action}
    </div>
  )
}
