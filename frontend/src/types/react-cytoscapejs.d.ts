declare module 'react-cytoscapejs' {
  import type { ComponentType, CSSProperties } from 'react'
  import type { Core, ElementDefinition, LayoutOptions, StylesheetStyle } from 'cytoscape'

  type Props = {
    elements: ElementDefinition[]
    style?: CSSProperties
    stylesheet?: StylesheetStyle[]
    layout?: LayoutOptions
    cy?: (cy: Core) => void
    className?: string
  }

  const CytoscapeComponent: ComponentType<Props>
  export default CytoscapeComponent
}
