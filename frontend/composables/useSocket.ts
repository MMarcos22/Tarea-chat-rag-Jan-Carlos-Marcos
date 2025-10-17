import { io, Socket } from 'socket.io-client'

let socket: Socket | null = null

export const useSocket = () => {
  const config = useRuntimeConfig()
  if (!socket) {
    socket = io(config.public.wsBase, { transports: ['websocket'] })
  }
  const on = (event: string, cb: (...args:any[])=>void) => socket!.on(event, cb)
  const off = (event: string, cb?: (...args:any[])=>void) => socket!.off(event, cb as any)
  const emit = (event: string, payload?: any) => socket!.emit(event, payload)
  return { socket, on, off, emit }
}
