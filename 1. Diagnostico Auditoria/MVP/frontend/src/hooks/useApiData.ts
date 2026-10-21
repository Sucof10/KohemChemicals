import { useCallback, useEffect, useRef, useState } from 'react'
import { getErrorMessage } from '../api/errors'

export function useApiData<T>(
  loader: () => Promise<T>,
  deps: readonly unknown[] = [],
) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const loaderRef = useRef(loader)
  loaderRef.current = loader

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await loaderRef.current()
      setData(result)
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setIsLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    void load()
  }, [load])

  return { data, isLoading, error, reload: load, setData }
}
