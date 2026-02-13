import { createContext, useContext, useState, type ReactNode } from 'react'

/**
 * Tabs: Sistema de pestanas usando React Context
 *
 * Context permite pasar datos a traves del arbol de componentes
 * sin tener que pasarlos explicitamente como props.
 */

// Tipo del contexto
interface TabsContextValue {
  activeTab: string
  setActiveTab: (tab: string) => void
}

// Crear el contexto (undefined por defecto)
const TabsContext = createContext<TabsContextValue | undefined>(undefined)

// Hook para usar el contexto
function useTabsContext() {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs provider')
  }
  return context
}

// Props de cada componente
interface TabsProps {
  defaultTab: string
  children: ReactNode
}

interface TabsListProps {
  children: ReactNode
}

interface TabProps {
  value: string
  children: ReactNode
}

interface TabPanelProps {
  value: string
  children: ReactNode
}

// Componente principal - Provee el contexto
export function Tabs({ defaultTab, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div>{children}</div>
    </TabsContext.Provider>
  )
}

// Lista de tabs (contenedor)
export function TabsList({ children }: TabsListProps) {
  return (
    <div className="border-b border-gray-200 mb-4">
      <nav className="-mb-px flex gap-4">{children}</nav>
    </div>
  )
}

// Tab individual (boton)
export function Tab({ value, children }: TabProps) {
  const { activeTab, setActiveTab } = useTabsContext()
  const isActive = activeTab === value

  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`
        py-3 px-1 border-b-2 font-medium text-sm transition-colors
        ${
          isActive
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
        }
      `}
    >
      {children}
    </button>
  )
}

// Panel de contenido (se muestra solo si esta activo)
export function TabPanel({ value, children }: TabPanelProps) {
  const { activeTab } = useTabsContext()

  if (value !== activeTab) return null
  return <div>{children}</div>
}

// Asignar sub-componentes para uso con dot notation
Tabs.List = TabsList
Tabs.Tab = Tab
Tabs.Panel = TabPanel
