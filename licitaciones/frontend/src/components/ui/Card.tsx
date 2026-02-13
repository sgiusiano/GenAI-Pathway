import { type ReactNode } from 'react'

/**
 * Card: Contenedor con fondo blanco, borde y sombra
 *
 * Uso:
 * <Card>
 *   <Card.Header>Titulo</Card.Header>
 *   <Card.Body>Contenido</Card.Body>
 * </Card>
 */

interface CardProps {
  children: ReactNode
  className?: string
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      {children}
    </div>
  )
}

// Sub-componentes para estructura
function CardHeader({ children, className = '' }: CardProps) {
  return (
    <div className={`px-6 py-4 border-b border-gray-200 ${className}`}>
      {children}
    </div>
  )
}

function CardBody({ children, className = '' }: CardProps) {
  return (
    <div className={`px-6 py-4 ${className}`}>
      {children}
    </div>
  )
}

function CardFooter({ children, className = '' }: CardProps) {
  return (
    <div className={`px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg ${className}`}>
      {children}
    </div>
  )
}

// Asignamos sub-componentes a Card
Card.Header = CardHeader
Card.Body = CardBody
Card.Footer = CardFooter

export default Card
