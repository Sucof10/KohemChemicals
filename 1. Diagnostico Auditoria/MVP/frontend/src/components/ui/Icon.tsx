import type { SVGProps } from 'react'

export type IconName =
  | 'dashboard'
  | 'materials'
  | 'orders'
  | 'ai'
  | 'audit'
  | 'user'
  | 'logout'
  | 'menu'
  | 'close'
  | 'plus'
  | 'edit'
  | 'trash'
  | 'search'
  | 'arrow-left'
  | 'send'
  | 'check'
  | 'alert'

const paths: Record<IconName, string[]> = {
  dashboard: [
    'M4 4h6v6H4z',
    'M14 4h6v6h-6z',
    'M4 14h6v6H4z',
    'M14 14h6v6h-6z',
  ],
  materials: [
    'M21 8l-9-5-9 5 9 5 9-5z',
    'M3 8v8l9 5 9-5V8',
    'M12 13v8',
  ],
  orders: [
    'M7 3h10l2 4v14H5V7l2-4z',
    'M5 8h14',
    'M9 13h6',
    'M9 17h6',
  ],
  ai: [
    'M21 14a4 4 0 0 1-4 4H9l-5 3V7a4 4 0 0 1 4-4h9a4 4 0 0 1 4 4v7z',
    'M9 9h.01',
    'M13 9h.01',
    'M17 9h.01',
  ],
  audit: ['M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z', 'M9 12l2 2 4-4'],
  user: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8z', 'M4 21a8 8 0 0 1 16 0'],
  logout: ['M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4', 'M16 17l5-5-5-5', 'M21 12H9'],
  menu: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  close: ['M6 6l12 12', 'M18 6L6 18'],
  plus: ['M12 5v14', 'M5 12h14'],
  edit: ['M4 20h4l10-10-4-4L4 16v4z', 'M14 6l4 4'],
  trash: ['M4 7h16', 'M9 7V4h6v3', 'M6 7l1 13h10l1-13', 'M10 11v6', 'M14 11v6'],
  search: ['M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14z', 'M20 20l-4-4'],
  'arrow-left': ['M19 12H5', 'M12 19l-7-7 7-7'],
  send: ['M22 2L11 13', 'M22 2l-7 20-4-9-9-4 20-7z'],
  check: ['M5 12l5 5L20 7'],
  alert: ['M12 9v4', 'M12 17h.01', 'M10.3 4.3L2.5 18a2 2 0 0 0 1.7 3h15.6a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0z'],
}

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName
}

export function Icon({ name, className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
      {...props}
    >
      {paths[name].map((path) => (
        <path key={path} d={path} />
      ))}
    </svg>
  )
}
