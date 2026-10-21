export const endpoints = {
  auth: {
    register: '/auth/register',
    login: '/auth/token',
  },
  materials: {
    list: '/materials',
    byId: (id: number) => `/materials/${id}`,
  },
  orders: {
    list: '/orders',
    byId: (id: number) => `/orders/${id}`,
    status: (id: number) => `/orders/${id}/status`,
  },
  ai: {
    chat: '/ai/chat',
  },
  audit: {
    list: '/audit-logs',
  },
} as const
