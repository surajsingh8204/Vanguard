import ReactECharts from 'echarts-for-react'

export const CHART_PALETTE = [
  '#3ddc97',
  '#5b8def',
  '#9d7bef',
  '#4dd0e1',
  '#f0b429',
  '#f78fb3',
  '#ef6b6b',
  '#7bd88f',
  '#6fa8ff',
  '#c39bff',
  '#59d4c2',
  '#ffb26b',
]

export function DonutChart({
  data,
  height = 300,
  centerLabel,
  centerValue,
  backdrop,
}: {
  data: Array<{ name: string; value: number }>
  height?: number
  centerLabel?: string
  centerValue?: string
  backdrop?: string
}) {
  const option = {
    backgroundColor: 'transparent',
    color: CHART_PALETTE,
    tooltip: {
      trigger: 'item',
      backgroundColor: '#111a2c',
      borderColor: '#243149',
      textStyle: { color: '#e8eef7', fontSize: 12 },
      formatter: '{b}<br/>{c} ({d}%)',
    },
    graphic: centerValue
      ? [
          {
            type: 'text',
            left: 'center',
            top: '42%',
            style: {
              text: centerValue,
              fill: '#e8eef7',
              fontSize: 26,
              fontWeight: 600,
              fontFamily: 'IBM Plex Mono, monospace',
            },
          },
          {
            type: 'text',
            left: 'center',
            top: '54%',
            style: {
              text: centerLabel ?? '',
              fill: '#5a6a84',
              fontSize: 11,
            },
          },
        ]
      : undefined,
    series: [
      {
        type: 'pie',
        radius: ['58%', '82%'],
        avoidLabelOverlap: true,
        padAngle: 2,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#0b1220',
          borderWidth: 2,
        },
        label: { show: false },
        emphasis: {
          scale: true,
          scaleSize: 4,
          label: { show: false },
        },
        data,
      },
    ],
  }

  if (backdrop) {
    return (
      <div className="relative">
        <img
          src={backdrop}
          alt=""
          aria-hidden
          className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-20 [mask-image:radial-gradient(circle_at_center,black_25%,transparent_72%)]"
        />
        <ReactECharts
          option={option}
          style={{ height, position: 'relative', zIndex: 1 }}
          notMerge
          lazyUpdate
        />
      </div>
    )
  }

  return <ReactECharts option={option} style={{ height }} notMerge lazyUpdate />
}

export function GaugeChart({
  value,
  max = 1,
  title,
  height = 220,
  color = '#3ddc97',
  formatter,
}: {
  value: number | null
  max?: number
  title: string
  height?: number
  color?: string
  formatter?: (value: number) => string
}) {
  const safe = value != null && Number.isFinite(value) ? value : null
  const option = {
    backgroundColor: 'transparent',
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max,
        radius: '95%',
        pointer: { show: false },
        progress: {
          show: true,
          overlap: false,
          roundCap: true,
          clip: false,
          itemStyle: { color },
        },
        axisLine: {
          lineStyle: { width: 14, color: [[1, '#182338']] },
        },
        splitLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        title: {
          fontSize: 11,
          color: '#5a6a84',
          offsetCenter: [0, '32%'],
        },
        detail: {
          valueAnimation: true,
          fontSize: 24,
          fontWeight: 600,
          fontFamily: 'IBM Plex Mono, monospace',
          color: safe == null ? '#5a6a84' : '#e8eef7',
          offsetCenter: [0, '0%'],
          formatter: (v: number) =>
            safe == null ? 'n/a' : formatter ? formatter(v) : v.toFixed(2),
        },
        data: [{ value: safe ?? 0, name: title }],
      },
    ],
  }

  return <ReactECharts option={option} style={{ height }} notMerge lazyUpdate />
}
