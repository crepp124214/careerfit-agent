export function formatDate(isoString: string): string {
  if (!isoString) return ''

  const date = new Date(isoString)
  if (isNaN(date.getTime())) return isoString

  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')

  return `${year}年${month}月${day}日 ${hour}:${minute}`
}

export function formatDateShort(isoString: string): string {
  if (!isoString) return ''

  const date = new Date(isoString)
  if (isNaN(date.getTime())) return isoString

  const month = date.getMonth() + 1
  const day = date.getDate()

  return `${month}/${day}`
}
