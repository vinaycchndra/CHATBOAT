import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8001'
const TOKEN_KEY = 'chatbot_jwt_token'
const USER_KEY = 'chatbot_user'

const initialSessions = [
  { id: 'session-101', title: 'Project kickoff', updatedAt: '2m ago' },
  { id: 'session-102', title: 'Client requirements', updatedAt: '25m ago' },
  { id: 'session-103', title: 'Product roadmap', updatedAt: '1h ago' },
  { id: 'session-104', title: 'RAG setup notes', updatedAt: 'Yesterday' },
]

const initialMessages = {
  'session-101': [
    { id: 1, sender: 'bot', text: 'Hi! I can help you with your project summary and document questions.', time: '09:10 AM' },
    { id: 2, sender: 'user', text: 'Can you summarize the goals for this sprint?', time: '09:12 AM' },
    { id: 3, sender: 'bot', text: 'This sprint focuses on onboarding, document indexing, and faster Q&A for uploaded PDFs.', time: '09:12 AM' },
  ],
  'session-102': [
    { id: 4, sender: 'user', text: 'What are the must-have features for the client?', time: '08:45 AM' },
    { id: 5, sender: 'bot', text: 'The client expects secure login, PDF upload support, and grounded answers from uploaded knowledge sources.', time: '08:46 AM' },
  ],
  'session-103': [
    { id: 6, sender: 'bot', text: 'Roadmap includes MVP launch, document parsing, and AI assistant improvements.', time: 'Yesterday' },
  ],
  'session-104': [
    { id: 7, sender: 'user', text: 'How should we structure the RAG workflow?', time: 'Mon' },
    { id: 8, sender: 'bot', text: 'Upload docs → index embeddings → query with context → generate grounded answer.', time: 'Mon' },
  ],
}

const getStoredUser = () => {
  try {
    const savedUser = localStorage.getItem(USER_KEY)
    return savedUser ? JSON.parse(savedUser) : null
  } catch {
    return null
  }
}

const getAuthToken = () => localStorage.getItem(TOKEN_KEY)

const requestWithAuth = async (endpoint, options = {}) => {
  const token = getAuthToken()
  const headers = {
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(data?.message || 'Something went wrong. Please try again.')
  }

  return data
}

const features = [
  'Upload PDFs and other knowledge files',
  'Ask grounded questions using RAG-powered search',
  'Get concise answers with source-aware context',
  'Search across documents in seconds',
]

const workflow = [
  { title: 'Upload', text: 'Add your PDFs and build a searchable document knowledge base.' },
  { title: 'Index', text: 'The system chunks and embeds your content for semantic retrieval.' },
  { title: 'Ask', text: 'Chat naturally and receive answers grounded in your uploaded material.' },
]

const stats = [
  { value: '24/7', label: 'AI assistance' },
  { value: 'PDF', label: 'document aware' },
  { value: 'RAG', label: 'retrieval flow' },
]

const MESSAGE_PAGE_SIZE = 10

const renderInlineMarkdown = (text) => {
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_)/g
  const parts = []
  let lastIndex = 0
  let match

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={`plain-${lastIndex}`}>{text.slice(lastIndex, match.index)}</span>)
    }

    const matchedText = match[0]
    const innerText = matchedText.replace(/^\*\*|\*\*$|^\*|\*$|^_|_$/g, '')

    if (matchedText.startsWith('**')) {
      parts.push(<strong key={`strong-${match.index}`}>{innerText}</strong>)
    } else {
      parts.push(<em key={`em-${match.index}`}>{innerText}</em>)
    }

    lastIndex = match.index + matchedText.length
  }

  if (lastIndex < text.length) {
    parts.push(<span key={`plain-end-${lastIndex}`}>{text.slice(lastIndex)}</span>)
  }

  return parts.length > 0 ? parts : text
}

const formatMessageText = (text) => {
  if (!text) {
    return []
  }

  const normalizedText = String(text)
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/?p>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\r/g, '')

  return normalizedText.split(/\n/).map((line, index) => {
    const trimmed = line.trim()

    if (!trimmed) {
      return <div key={`empty-${index}`} className="message-line empty" />
    }

    if (/^###\s+/.test(trimmed)) {
      return (
        <div key={`line-${index}`} className="message-line heading heading-3">
          {renderInlineMarkdown(trimmed.replace(/^###\s+/, ''))}
        </div>
      )
    }

    if (/^[-*]\s+/.test(trimmed)) {
      const bulletContent = trimmed.replace(/^[-*]\s+/, '')
      return (
        <div key={`line-${index}`} className="message-line bullet">
          {renderInlineMarkdown(bulletContent)}
        </div>
      )
    }

    return <div key={`line-${index}`} className="message-line">{renderInlineMarkdown(line)}</div>
  })
}

function App() {
  const [sessionUser, setSessionUser] = useState(getStoredUser)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState('register')
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [sessions, setSessions] = useState([])
  const [messagesBySession, setMessagesBySession] = useState({})
  const [activeSessionId, setActiveSessionId] = useState('')
  const [draft, setDraft] = useState('')
  const [isLoadingSessions, setIsLoadingSessions] = useState(false)
  const [isAiThinking, setIsAiThinking] = useState(false)
  const [sessionMessageOffsets, setSessionMessageOffsets] = useState({})
  const [isLoadingMessages, setIsLoadingMessages] = useState({})
  const [uploadedDocs, setUploadedDocs] = useState([
    { id: 1, name: 'Project-Overview.pdf', size: '2.3 MB', uploadedAt: 'Today' },
    { id: 2, name: 'Customer-FAQs.pdf', size: '1.1 MB', uploadedAt: 'Yesterday' },
  ])
  const [isDocsModalOpen, setIsDocsModalOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState([])
  const [uploadToast, setUploadToast] = useState({ visible: false, type: 'success', title: '', message: '', files: [] })
  const [isFetchingDocs, setIsFetchingDocs] = useState(false)
  const messagesListRef = useRef(null)
  const textareaRef = useRef(null)
  const uploadInputRef = useRef(null)

  const activeSession = sessions.find((session) => session.session_id === activeSessionId) || sessions[0] || null
  const activeMessages = activeSession ? messagesBySession[activeSessionId] || [] : []

  const scrollToBottom = (behavior = 'auto') => {
    const container = messagesListRef.current
    if (!container) {
      return
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior,
    })
  }

  const loadSessions = async () => {
    if (!sessionUser) {
      return
    }

    setIsLoadingSessions(true)

    try {
      const response = await requestWithAuth('/v1/chat-session/query-session/', {
        method: 'POST',
        body: {},
      })

      const sessionList = Array.isArray(response?.data) ? response.data : []
      setSessions(sessionList)

      if (sessionList.length > 0) {
        setActiveSessionId(sessionList[0].session_id)
      } else {
        setActiveSessionId('')
      }
    } catch (fetchError) {
      console.error('Failed to load chat sessions:', fetchError)
      setSessions([])
      setActiveSessionId('')
    } finally {
      setIsLoadingSessions(false)
    }
  }

  useEffect(() => {
    if (sessionUser) {
      loadSessions()
    } else {
      setSessions([])
      setActiveSessionId('')
    }
  }, [sessionUser])

  const fetchSessionMessages = async (sessionId, append = false) => {
    if (!sessionId) {
      return
    }

    const currentOffset = append ? (sessionMessageOffsets[sessionId] ?? 0) : 0

    setIsLoadingMessages((prev) => ({ ...prev, [sessionId]: true }))

    try {
      const response = await requestWithAuth(
        `/v1/chat-message/${sessionId}/messages?limit=${MESSAGE_PAGE_SIZE}&offset=${currentOffset}`,
        { method: 'GET' },
      )

      const nextMessages = Array.isArray(response) ? response : []

      if (!nextMessages.length) {
        return
      }

      const normalizedMessages = nextMessages
        .map((message) => ({
          id: message.id,
          sender: message.role === 'human' ? 'user' : 'bot',
          text: message.message,
          time: message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : 'Just now',
          createdAt: message.created_at,
        }))
        .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))

      setMessagesBySession((prev) => {
        const existingMessages = prev[sessionId] || []
        const mergedMessages = append
          ? [...normalizedMessages, ...existingMessages].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
          : normalizedMessages

        return {
          ...prev,
          [sessionId]: mergedMessages,
        }
      })

      setSessionMessageOffsets((prev) => ({
        ...prev,
        [sessionId]: (prev[sessionId] ?? 0) + nextMessages.length,
      }))
    } catch (fetchError) {
      console.error('Failed to load session messages:', fetchError)
    } finally {
      setIsLoadingMessages((prev) => ({ ...prev, [sessionId]: false }))
    }
  }

  useEffect(() => {
    if (!activeSessionId) {
      return
    }

    const existingMessages = messagesBySession[activeSessionId]
    if (!existingMessages || existingMessages.length === 0) {
      fetchSessionMessages(activeSessionId, false)
    }
  }, [activeSessionId, messagesBySession])

  const handleMessagesScroll = async () => {
    const container = messagesListRef.current
    if (!container || !activeSessionId) {
      return
    }

    const isNearTop = container.scrollTop <= 80
    const offset = sessionMessageOffsets[activeSessionId] ?? 0
    const isBusy = isLoadingMessages[activeSessionId]

    if (isNearTop && offset > 0 && !isBusy) {
      const previousScrollHeight = container.scrollHeight
      const previousScrollTop = container.scrollTop

      await fetchSessionMessages(activeSessionId, true)

      requestAnimationFrame(() => {
        const nextContainer = messagesListRef.current
        if (!nextContainer) {
          return
        }

        nextContainer.scrollTop = nextContainer.scrollHeight - previousScrollHeight + previousScrollTop
      })
    }
  }

  useEffect(() => {
    if (!activeSessionId) {
      return
    }

    const container = messagesListRef.current
    if (!container) {
      return
    }

    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 120

    if (isNearBottom) {
      requestAnimationFrame(() => scrollToBottom('auto'))
    }
  }, [activeMessages, activeSessionId, isAiThinking])

  useEffect(() => {
    if (!activeSessionId) {
      return
    }

    requestAnimationFrame(() => scrollToBottom('auto'))
  }, [activeSessionId])

  useEffect(() => {
    if (!textareaRef.current) {
      return
    }

    if (!isAiThinking) {
      textareaRef.current.focus()
    }
  }, [activeSessionId, isAiThinking, activeMessages.length])

  const openAuthModal = (mode) => {
    setAuthMode(mode)
    setError('')
    setSuccess('')
    setForm({ name: '', email: '', password: '' })
    setIsAuthModalOpen(true)
  }

  const closeAuthModal = () => {
    setIsAuthModalOpen(false)
    setError('')
    setSuccess('')
    setForm({ name: '', email: '', password: '' })
  }

  const handleInputChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }))
  }

  const handleAuthSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')

    const email = form.email.trim()
    const password = form.password
    const name = form.name.trim()

    if (!email || !password || (authMode === 'register' && !name)) {
      setError('Please fill in all required fields.')
      return
    }

    try {
      const endpoint = authMode === 'register' ? '/v1/users/register/' : '/v1/users/login/'
      const payload = authMode === 'register' ? { email, password, name } : { email, password }

      const result = await requestWithAuth(endpoint, {
        method: 'POST',
        body: payload,
      })

      if (authMode === 'register') {
        setSuccess('Registration successful. Please log in to continue.')
        setAuthMode('login')
        setForm({ name: '', email, password: '' })
        return
      }

      const token = result.token
      const user = {
        user_id: result.user_id,
        email: result.email || email,
      }

      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      setSessionUser(user)
      setIsAuthModalOpen(false)
      setForm({ name: '', email: '', password: '' })
    } catch (submitError) {
      setError(submitError.message)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setSessionUser(null)
  }

  const handleUploadPdf = async (event) => {
    setUploadError('')
    const files = Array.from(event.target.files || [])
    if (!files.length) return

    const pdfFiles = files.filter((file) => file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf'))
    if (!pdfFiles.length) return

    setIsUploading(true)
    try {
      const uploadResults = []

      for (const file of pdfFiles) {
        const form = new FormData()
        form.append('file', file)

        const headers = {}
        const token = getAuthToken()
        if (token) headers.Authorization = `Bearer ${token}`

        const resp = await fetch(`${API_BASE}/v1/file`, {
          method: 'POST',
          headers,
          body: form,
        })

        const data = await resp.json().catch(() => null)
        if (!resp.ok) {
          const msg = data?.message || `Upload failed for ${file.name}`
          throw new Error(msg)
        }

        uploadResults.push(data)
      }

      // Merge uploaded files into UI list using backend response when available
      const nextDocs = uploadResults
        .map((res, index) => {
          const d = res?.data
          if (!d) return null
          return {
            id: d.id || `uploaded-${Date.now()}-${index}`,
            name: d.file_name || pdfFiles[index].name,
            size: d.file_size ? `${(d.file_size / (1024 * 1024)).toFixed(2)} MB` : `${(pdfFiles[index].size / (1024 * 1024)).toFixed(2)} MB`,
            uploadedAt: d.created_at || 'Just now',
          }
        })
        .filter(Boolean)

      setUploadedDocs((prev) => [...nextDocs, ...prev])
      setUploadSuccess(nextDocs)
      setUploadError('')
      // Show toast instead of opening the My Docs modal immediately
      setUploadToast({
        visible: true,
        type: 'success',
        title: 'Upload successful',
        message: `${nextDocs.length} file(s) uploaded successfully.`,
        files: nextDocs,
      })
      // Auto-dismiss after a few seconds
      setTimeout(() => setUploadToast((t) => ({ ...t, visible: false })), 6000)
    } catch (err) {
      console.error('Upload error:', err)
      // Improve duplicate-file message clarity for users
      const msg = err.message || 'Upload failed'
      const userMessage = msg.toLowerCase().includes('already uploaded')
        ? 'This file appears to be already uploaded. If you meant to upload a new file, rename it and try again.'
        : msg
      setUploadError(userMessage)
      setUploadSuccess([])
      setUploadToast({ visible: true, type: 'error', title: 'Upload failed', message: userMessage, files: [] })
      setTimeout(() => setUploadToast((t) => ({ ...t, visible: false })), 8000)
    } finally {
      setIsUploading(false)
      event.target.value = ''
    }
  }

  const loadDocsFromBackend = async () => {
    setIsFetchingDocs(true)
    setUploadError('')
    try {
      const response = await requestWithAuth('/v1/file?is_uploaded=true', { method: 'GET' })
      const list = Array.isArray(response?.data) ? response.data : []
      const mapped = list.map((d) => ({
        id: d.id,
        name: d.file_name,
        size: d.file_size ? `${(d.file_size / (1024 * 1024)).toFixed(2)} MB` : '—',
        uploadedAt: d.created_at || '',
        processed: !!d.processed,
      }))
      setUploadedDocs(mapped)
    } catch (err) {
      console.error('Failed to load docs:', err)
      setUploadError('Could not load documents. Please try again later.')
    } finally {
      setIsFetchingDocs(false)
    }
  }

  const handleCreateSession = async () => {
    try {
      const response = await requestWithAuth('/v1/chat-session/create', {
        method: 'POST',
      })

      const newSession = {
        session_id: response.session_id,
        user_id: response.user_id,
        session_summary: response.session_summary || '',
        created_at: response.created_at,
        updated_at: response.updated_at,
        archived: false,
      }

      setSessions((prev) => [newSession, ...prev])
      setActiveSessionId(newSession.session_id)
      setSessionMessageOffsets((prev) => ({ ...prev, [newSession.session_id]: 0 }))
      setMessagesBySession((prev) => ({
        ...prev,
        [newSession.session_id]: [],
      }))
      fetchSessionMessages(newSession.session_id, false)
    } catch (createError) {
      console.error('Failed to create a new session:', createError)
    }
  }

  const sendMessageToBackend = async (sessionId, text) => {
    const response = await requestWithAuth(`/v1/chat-message/${sessionId}/send`, {
      method: 'POST',
      body: { message_text: text },
    })

    return {
      id: Date.now() + 10,
      sender: response?.role === 'human' ? 'user' : 'bot',
      text: response?.message || 'No response received.',
      time: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
    }
  }

  const handleSendMessage = async (event) => {
    event.preventDefault()
    const trimmedMessage = draft.trim()

    if (!trimmedMessage || !activeSessionId || isAiThinking) {
      return
    }

    const newUserMessage = {
      id: Date.now(),
      sender: 'user',
      text: trimmedMessage,
      time: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
    }

    setMessagesBySession((prev) => ({
      ...prev,
      [activeSessionId]: [...(prev[activeSessionId] || []), newUserMessage],
    }))

    setDraft('')
    setIsAiThinking(true)
    requestAnimationFrame(() => {
      scrollToBottom('smooth')
      textareaRef.current?.focus()
    })

    try {
      const botReply = await sendMessageToBackend(activeSessionId, trimmedMessage)

      setMessagesBySession((prev) => ({
        ...prev,
        [activeSessionId]: [...(prev[activeSessionId] || []), botReply],
      }))

      requestAnimationFrame(() => {
        scrollToBottom('smooth')
        textareaRef.current?.focus()
      })
    } catch (error) {
      console.error('Send message failed:', error)
      setMessagesBySession((prev) => ({
        ...prev,
        [activeSessionId]: [...(prev[activeSessionId] || []), {
          id: Date.now() + 11,
          sender: 'bot',
          text: 'The message could not be sent. Please try again.',
          time: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
        }],
      }))
    } finally {
      setIsAiThinking(false)
    }
  }

  if (sessionUser) {
    return (
      <div className="chat-app">
        {isDocsModalOpen && (
          <div className="auth-modal-backdrop" onClick={() => setIsDocsModalOpen(false)}>
            <div className="docs-modal" onClick={(event) => event.stopPropagation()}>
              <div className="auth-header">
                <h3>My Documents</h3>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={loadDocsFromBackend}
                    disabled={isFetchingDocs}
                    style={{ padding: '6px 10px' }}
                  >
                    {isFetchingDocs ? 'Refreshing...' : 'Refresh'}
                  </button>
                  <button type="button" className="close-btn" onClick={() => setIsDocsModalOpen(false)}>
                    ×
                  </button>
                </div>
              </div>

              <div className="docs-list">
                {isFetchingDocs ? (
                  <p className="empty-state">Loading documents…</p>
                ) : uploadedDocs.length === 0 ? (
                  <p className="empty-state">No PDFs uploaded yet.</p>
                ) : (
                  uploadedDocs.map((doc) => (
                    <div key={doc.id} className="doc-item" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div className="doc-icon">PDF</div>
                      <div className="doc-meta" style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
                          <strong style={{ wordBreak: 'break-all' }}>{doc.name}</strong>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span style={{ fontSize: 13, color: 'var(--muted)' }}>{doc.size}</span>
                            {doc.processed ? (
                              <span style={{ background: '#e6fffa', color: '#055d46', padding: '4px 8px', borderRadius: 999, fontSize: 12, border: '1px solid #c7f3e6' }}>AI ready</span>
                            ) : (
                              <span style={{ background: '#fff7ed', color: '#7a4d00', padding: '4px 8px', borderRadius: 999, fontSize: 12, border: '1px solid #ffe8c2' }}>Processing</span>
                            )}
                          </div>
                        </div>
                        <div style={{ marginTop: 6, fontSize: 13, color: 'var(--muted)' }}>{doc.uploadedAt}</div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        <header className="dashboard-header">
          <div className="brand">
            <div className="brand-mark">AI</div>
            <span>ChatBot</span>
          </div>

          <div className="dashboard-actions">
            <button
              type="button"
              className="nav-button secondary-nav"
              onClick={() => uploadInputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : 'Upload PDF'}
            </button>
            <button
              type="button"
              className="nav-button secondary-nav"
              onClick={async () => {
                await loadDocsFromBackend()
                setIsDocsModalOpen(true)
              }}
            >
              My Docs
            </button>
            <span className="user-pill">{sessionUser.email}</span>
            <button className="nav-button" onClick={handleLogout}>Log out</button>
          </div>
        </header>

        {uploadToast.visible && (
          <>
            <div
              className="upload-toast-backdrop"
              onClick={() => setUploadToast((t) => ({ ...t, visible: false }))}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0,0,0,0.32)',
                zIndex: 1190,
                backdropFilter: 'blur(2px)'
              }}
            />

            <div
              className="upload-toast-centered"
              role="dialog"
              aria-live="polite"
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 1200,
                width: 'min(520px, 92%)',
                padding: 20,
                borderRadius: 12,
                boxShadow: '0 20px 40px rgba(2,6,23,0.35)',
                background: uploadToast.type === 'error' ? '#FFF5F5' : '#F6FFFA',
                border: `1px solid ${uploadToast.type === 'error' ? '#FFD6D6' : '#D1FADF'}`,
                color: 'var(--text, #0b1220)'
              }}
            >
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ fontSize: 26 }}>
                  {uploadToast.type === 'error' ? '❌' : '✅'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: 16 }}>{uploadToast.title}</strong>
                    <button
                      type="button"
                      onClick={() => setUploadToast((t) => ({ ...t, visible: false }))}
                      aria-label="Close upload message"
                      style={{ background: 'transparent', border: 'none', fontSize: 18, lineHeight: 1 }}
                    >
                      ×
                    </button>
                  </div>

                  <div style={{ marginTop: 8, color: uploadToast.type === 'error' ? '#6b0b0b' : '#0f5132' }}>
                    {uploadToast.message}
                  </div>

                  {uploadToast.files && uploadToast.files.length > 0 && (
                    <ul style={{ marginTop: 10, paddingLeft: 18 }}>
                      {uploadToast.files.map((f) => (
                        <li key={f.id} style={{ fontSize: 13, marginBottom: 4 }}>
                          {f.name} • {f.size}
                        </li>
                      ))}
                    </ul>
                  )}

                  <div style={{ marginTop: 14, display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                    <button
                      type="button"
                      className="secondary-btn"
                      onClick={() => {
                        setIsDocsModalOpen(true)
                        setUploadToast((t) => ({ ...t, visible: false }))
                      }}
                    >
                      View docs
                    </button>
                    <button
                      type="button"
                      className="primary-btn"
                      onClick={() => setUploadToast((t) => ({ ...t, visible: false }))}
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        <input
          ref={uploadInputRef}
          type="file"
          accept=".pdf,application/pdf"
          multiple
          hidden
          onChange={handleUploadPdf}
        />

        {/* Fetch docs from backend */}
        

        <div className="dashboard-shell">
          <aside className="sidebar">
            <div className="sidebar-header">
              <h3>Chat sessions</h3>
              <button type="button" className="new-session-btn" onClick={handleCreateSession}>
                New
              </button>
            </div>

            {isLoadingSessions ? (
              <div className="empty-state">Loading sessions...</div>
            ) : sessions.length === 0 ? (
              <div className="empty-state">No chat sessions yet.</div>
            ) : (
              sessions.map((session) => (
                <button
                  key={session.session_id}
                  type="button"
                  className={`session-item ${session.session_id === activeSessionId ? 'active' : ''}`}
                  onClick={() => setActiveSessionId(session.session_id)}
                >
                  <div className="session-title-block">
                    <span className="session-name">
                      {session.session_id || 'Session'}
                    </span>
                    <span className="session-time">
                      {session.created_at ? new Date(session.created_at).toLocaleString() : 'Recently'}
                    </span>
                  </div>
                </button>
              ))
            )}
          </aside>

          <main className="chat-panel">
            <div className="chat-header">
              <div>
                <p className="chat-label">Current session</p>
                <h2>{activeSession ? (activeSession.session_id || 'No session selected') : 'No session selected'}</h2>
              </div>
            </div>

            <div className="messages-list" ref={messagesListRef} onScroll={handleMessagesScroll}>
              {!activeSession ? (
                <div className="empty-state">Select a session to view conversations.</div>
              ) : activeMessages.length === 0 ? (
                <div className="empty-state">{isLoadingMessages[activeSessionId] ? 'Loading messages...' : 'No messages in this chat yet.'}</div>
              ) : (
                activeMessages.map((message) => (
                  <div key={message.id} className={`message-row ${message.sender}`}>
                    <div className="message-bubble">
                      <span className="role">{message.sender === 'user' ? 'You' : 'AI'}</span>
                      <div className="message-content">
                        {formatMessageText(message.text)}
                      </div>
                      <small>{message.time}</small>
                    </div>
                  </div>
                ))
              )}

              {isAiThinking && (
                <div className="message-row bot">
                  <div className="message-bubble thinking-bubble">
                    <span className="role">AI</span>
                    <div className="thinking-text">
                      <span>AI is thinking</span>
                      <span className="thinking-dots" aria-label="AI is processing">
                        <i />
                        <i />
                        <i />
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <form className="composer" onSubmit={handleSendMessage}>
              <textarea
                ref={textareaRef}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Type your message here..."
                rows={1}
                disabled={isAiThinking}
              />
              <button type="submit" className="primary-btn send-btn" disabled={isAiThinking}>
                {isAiThinking ? 'Thinking...' : 'Send'}
              </button>
            </form>
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="landing-page">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <span>ChatBot</span>
        </div>

        <nav className="nav">
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
        </nav>

        <div className="auth-actions">
          <button className="nav-button secondary-nav" onClick={() => openAuthModal('register')}>
            Register now
          </button>
          <button className="nav-button" onClick={() => openAuthModal('login')}>
            Log in
          </button>
        </div>
      </header>

      <main className="hero-section">
        <div className="hero-copy">
          <span className="eyebrow">AI-powered knowledge assistant</span>
          <h1>Chat with your documents using a smart PDF-based AI chatbot.</h1>
          <p>
            Our AI ChatBot uses retrieval-augmented generation to answer questions from your
            uploaded PDFs, giving you fast, grounded responses based on the content you trust.
          </p>

          <div className="cta-row">
            <button className="primary-btn" onClick={() => openAuthModal('register')}>
              Register now
            </button>
            <button className="secondary-btn" onClick={() => openAuthModal('login')}>
              Log in
            </button>
          </div>

          <ul className="feature-list">
            {features.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
        </div>

        <div className="hero-panel" aria-label="AI chatbot preview">
          <div className="panel-header">
            <span className="dot red" />
            <span className="dot yellow" />
            <span className="dot green" />
          </div>

          <div className="chat-box">
            <div className="message bot">
              <span className="role">AI</span>
              <p>Ask me about your uploaded PDFs, contracts, reports, or training materials.</p>
            </div>
            <div className="message user">
              <span className="role">You</span>
              <p>What are the key risks in this report?</p>
            </div>
            <div className="message bot">
              <span className="role">AI</span>
              <p>
                Based on the uploaded document, the main risks are compliance gaps, delayed
                delivery timelines, and unresolved vendor dependencies.
              </p>
            </div>
          </div>

          <div className="upload-card">
            <div className="upload-icon">📄</div>
            <div>
              <strong>3 PDF files uploaded</strong>
              <p>Ready for semantic search and Q&amp;A</p>
            </div>
          </div>
        </div>
      </main>

      <section id="features" className="info-section">
        <div className="section-heading">
          <span className="eyebrow">Why teams use it</span>
          <h2>Turn documents into answers.</h2>
        </div>

        <div className="stats-grid">
          {stats.map((stat) => (
            <div key={stat.label} className="stat-card">
              <strong>{stat.value}</strong>
              <span>{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="workflow-section">
        <div className="section-heading center">
          <span className="eyebrow">How it works</span>
          <h2>From upload to instant insight.</h2>
        </div>

        <div className="workflow-grid">
          {workflow.map((step, index) => (
            <div key={step.title} className="workflow-card">
              <span className="step-number">0{index + 1}</span>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      {isAuthModalOpen && (
        <div className="auth-modal-backdrop" onClick={closeAuthModal}>
          <div className="auth-modal" onClick={(event) => event.stopPropagation()}>
            <div className="auth-header">
              <h3>{authMode === 'register' ? 'Create account' : 'Welcome back'}</h3>
              <button type="button" className="close-btn" onClick={closeAuthModal}>
                ×
              </button>
            </div>

            <form className="auth-form" onSubmit={handleAuthSubmit}>
              {authMode === 'register' && (
                <label>
                  Full name
                  <input
                    type="text"
                    value={form.name}
                    onChange={handleInputChange('name')}
                    placeholder="Ajith Akash"
                  />
                </label>
              )}

              <label>
                Email
                <input
                  type="email"
                  value={form.email}
                  onChange={handleInputChange('email')}
                  placeholder="you@example.com"
                />
              </label>

              <label>
                Password
                <input
                  type="password"
                  value={form.password}
                  onChange={handleInputChange('password')}
                  placeholder="••••••••"
                />
              </label>

              {error && <p className="auth-message error">{error}</p>}
              {success && <p className="auth-message success">{success}</p>}

              <button type="submit" className="primary-btn auth-submit">
                {authMode === 'register' ? 'Register now' : 'Log in'}
              </button>
            </form>

            <p className="switch-text">
              {authMode === 'register' ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button
                type="button"
                className="text-link"
                onClick={() => {
                  setAuthMode((prev) => (prev === 'register' ? 'login' : 'register'))
                  setError('')
                  setSuccess('')
                }}
              >
                {authMode === 'register' ? 'Log in' : 'Register now'}
              </button>
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
