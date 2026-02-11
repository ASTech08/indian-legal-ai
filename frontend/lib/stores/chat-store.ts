import { create } from 'zustand'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
    fileAnalysis?: string
}

interface ChatStore {
    messages: Message[]
    isLoading: boolean
    sendMessage: (content: string) => Promise<void>
    uploadFile: (file: File) => Promise<void>
    clearMessages: () => void
}

export const useChatStore = create<ChatStore>((set, get) => ({
    messages: [],
    isLoading: false,

    sendMessage: async (content: string) => {
          const userMessage: Message = {
                  id: Date.now().toString(),
                  role: 'user',
                  content,
                  timestamp: new Date(),
          }

      set((state) => ({
              messages: [...state.messages, userMessage],
              isLoading: true,
      }))

      try {
              const response = await axios.post(`${API_URL}/api/chat`, {
                        message: content,
              })

            const assistantMessage: Message = {
                      id: (Date.now() + 1).toString(),
                      role: 'assistant',
                      content: response.data.response,
                      timestamp: new Date(),
            }

            set((state) => ({
                      messages: [...state.messages, assistantMessage],
                      isLoading: false,
            }))
      } catch (error) {
              const errorMessage: Message = {
                        id: (Date.now() + 1).toString(),
                        role: 'assistant',
                        content: 'Sorry, I encountered an error. Please try again.',
                        timestamp: new Date(),
              }

            set((state) => ({
                      messages: [...state.messages, errorMessage],
                      isLoading: false,
            }))
      }
    },

    uploadFile: async (file: File) => {
          set({ isLoading: true })

      const formData = new FormData()
          formData.append('file', file)

      try {
              const response = await axios.post(`${API_URL}/api/analyze-document`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' },
              })

            const analysisMessage: Message = {
                      id: Date.now().toString(),
                      role: 'assistant',
                      content: response.data.analysis,
                      timestamp: new Date(),
                      fileAnalysis: file.name,
            }

            set((state) => ({
                      messages: [...state.messages, analysisMessage],
                      isLoading: false,
            }))
      } catch (error) {
              const errorMessage: Message = {
                        id: Date.now().toString(),
                        role: 'assistant',
                        content: 'Sorry, I could not analyze the document. Please try again.',
                        timestamp: new Date(),
              }

            set((state) => ({
                      messages: [...state.messages, errorMessage],
                      isLoading: false,
            }))
      }
    },

    clearMessages: () => set({ messages: [] }),
}))
