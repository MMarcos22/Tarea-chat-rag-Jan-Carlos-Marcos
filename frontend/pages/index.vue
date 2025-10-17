<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { definePageMeta, useRuntimeConfig } from '#imports'
import { useSocket } from '../composables/useSocket'

definePageMeta({ ssr: false })

const config = useRuntimeConfig()
const { on, emit } = useSocket()

const documentId = ref<string | null>(null)
const documentName = ref<string>('') 
const uploading = ref(false)
const question = ref('')
const messages = ref<{ role: 'user' | 'assistant', text: string }[]>([])
const dropActive = ref(false)
const scroller = ref<HTMLDivElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const openFilePicker = () => fileInputRef.value?.click()

const scrollToBottom = () => nextTick(() => {
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
})

onMounted(() => {
  on('server_ready', () => {})
  on('bot_chunk', (data: { text: string }) => {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'assistant') last.text += data.text
    else messages.value.push({ role: 'assistant', text: data.text })
    scrollToBottom()
  })
  on('bot_done', () => {})
})

/** Limpia estado de documento + chat */
const resetState = () => {
  documentId.value = null
  documentName.value = ''
  messages.value = []
  question.value = ''
  if (fileInputRef.value) fileInputRef.value.value = ''
}

/** El usuario quiere quitar el documento actual (click en ✕) */
const clearDocument = () => {
  resetState()
}

/** Subida (válida) de un archivo */
const handleFiles = async (file: File) => {
  if (!file || file.type !== 'application/pdf') {
    alert('El archivo debe ser un PDF.')
    return
  }

  // Si ya había documento cargado, reseteamos chat/estado antes de subir el nuevo
  if (documentId.value) resetState()

  uploading.value = true
  try {
    const form = new FormData()
    form.append('file', file)

    const res = await fetch(`${config.public.apiBase}/api/v1/documents`, {
      method: 'POST',
      body: form
    })

    if (!res.ok) {
      const errTxt = await res.text().catch(() => '')
      throw new Error(errTxt || `HTTP ${res.status}`)
    }

    const ct = res.headers.get('content-type') || ''
    let data: any = null
    if (ct.includes('application/json')) {
      data = await res.json()
    } else {
      const txt = await res.text()
      try { data = JSON.parse(txt) } catch { data = { document_id: txt } }
    }

    if (!data?.document_id || typeof data.document_id !== 'string') {
      throw new Error('Respuesta inválida del servidor (sin document_id)')
    }

    documentId.value = data.document_id
    documentName.value = file.name
  } catch (e) {
    console.error('Upload error:', e)
    alert(`Error subiendo el PDF: ${(e as Error)?.message || ''}`.trim())
  } finally {
    uploading.value = false
  }
}

const onFileInput = (e: Event) => {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) handleFiles(f)
}
const onDrop = (e: DragEvent) => {
  e.preventDefault()
  dropActive.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) handleFiles(f)
}
const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  dropActive.value = true
}
const onDragLeave = () => {
  dropActive.value = false
}

const ask = () => {
  const q = question.value.trim()
  if (!q || !documentId.value) return
  messages.value.push({ role: 'user', text: q })
  messages.value.push({ role: 'assistant', text: '' })
  emit('user_question', { question: q, document_id: documentId.value })
  question.value = ''
  scrollToBottom()
}

// background image url (la tuya de Pexels)
const bgUrl = "https://images.pexels.com/photos/21940153/pexels-photo-21940153.jpeg"
</script>

<template>
  <!-- Fondo con imagen + overlay oscuro -->
  <div class="fixed inset-0 -z-10">
    <div
      class="absolute inset-0 bg-center bg-cover"
      :style="{ backgroundImage: `url('${bgUrl}')` }"
      aria-hidden="true"
    />
    <div class="absolute inset-0 bg-black/60" aria-hidden="true" />
  </div>

  <div class="min-h-screen flex flex-col text-neutral-100">
    <!-- Topbar -->
    <header class="sticky top-0 z-10 border-b border-white/10 bg-black/40 backdrop-blur">
      <div class="mx-auto w-full max-w-6xl px-5 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="size-9 rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 grid place-items-center font-extrabold text-neutral-950">R</div>
          <div>
            <h1 class="m-0 text-base font-semibold">Lector de PDF</h1>
            <p class="m-0 text-xs text-neutral-300">Sube tu documento PDF, haz preguntas y con nuestro chatbot resolveremos tu duda.</p>
          </div>
        </div>
        <a
          class="text-sm text-cyan-200 border border-white/10 rounded-lg px-3 py-1 hover:bg-white/10 transition"
          href="http://localhost:8000/docs"
          target="_blank"
        >
          API
        </a>
      </div>
    </header>

    <!-- Main -->
    <main class="mx-auto w-full max-w-6xl px-5 py-6 grid grid-cols-1 lg:grid-cols-3 gap-5 flex-1">
      <!-- Left: PDF panel -->
      <section class="lg:col-span-1 rounded-2xl p-4 bg-black/40 border border-white/10">
        <h2 class="text-sm font-semibold mb-3">Documento</h2>

        <div
          class="relative rounded-xl border border-dashed p-6 text-center transition
                 bg-black/30 border-white/10 hover:border-white/20"
          :class="dropActive ? 'ring-2 ring-cyan-400/40 border-cyan-400/40' : ''"
          @dragover="onDragOver" @dragleave="onDragLeave" @drop="onDrop"
        >
          <!-- Input oculto -->
          <input
            id="fileInput"
            ref="fileInputRef"
            type="file"
            accept="application/pdf"
            @change="onFileInput"
            class="hidden"
          />

          <!-- Botón funcional -->
          <div class="flex items-center justify-center gap-3">
            <div class="text-3xl">📄</div>
            <div>
              <p class="font-medium">Arrastra tu PDF aquí</p>
              <p class="text-sm text-neutral-300">o</p>
              <button
                type="button"
                @click="openFilePicker"
                class="inline-flex items-center gap-2 text-sm font-medium mt-1
                       rounded-lg px-3 py-1.5 border border-white/10 bg-white/5 hover:bg-white/10 transition"
              >
                Seleccionar archivo
              </button>
            </div>
          </div>

          <!-- Overlay de carga -->
          <div v-if="uploading"
               class="absolute inset-0 grid place-items-center rounded-xl bg-black/60 pointer-events-none">
            <div class="flex items-center gap-2 text-sm">
              <span class="h-4 w-4 border-2 border-neutral-300/70 border-t-transparent rounded-full animate-spin"></span>
              Procesando PDF…
            </div>
          </div>
        </div>

        <!-- Tarjeta del documento + botón quitar -->
        <div v-if="documentId" class="mt-4 rounded-xl border border-white/10 p-3 bg-black/30">
          <div class="flex items-center justify-between gap-3 mb-1">
            <span class="px-2 py-0.5 text-xs rounded-full bg-emerald-600/30 text-emerald-200 border border-emerald-500/40">Cargado</span>
            <small class="text-xs text-neutral-300 truncate max-w-[220px]">ID: {{ documentId }}</small>
          </div>

          <div class="flex items-start justify-between gap-2">
            <div class="font-medium truncate" :title="documentName">{{ documentName }}</div>
            <button
              type="button"
              @click="clearDocument"
              class="shrink-0 inline-flex items-center justify-center size-7 rounded-md border border-white/10 hover:bg-white/10 text-neutral-300"
              title="Quitar documento"
              aria-label="Quitar documento"
            >
              ✕
            </button>
          </div>

          <p class="text-sm text-neutral-300 mt-1">Ya puedes hacer preguntas en el chat.</p>
        </div>

        <p v-else class="text-sm text-neutral-300 mt-4">Aún no hay documento PDF. Sube un documento PDF para empezar y activar el chat.</p>
      </section>

      <!-- Right: Chat -->
      <section class="lg:col-span-2 rounded-2xl border border-white/10 bg-black/40 flex flex-col overflow-hidden">
        <div class="px-4 py-3 border-b border-white/10 flex items-center gap-3">
          <div class="size-8 rounded-full grid place-items-center font-bold border border-white/10 bg-white/5">AI</div>
          <div>
            <h3 class="text-sm font-semibold m-0">Asistente</h3>
            <p class="text-xs text-neutral-300 m-0">
              {{ documentId ? 'Usando tu documento PDF como contexto' : 'Esperando documento…' }}
            </p>
          </div>
        </div>

        <div ref="scroller" class="flex-1 overflow-auto p-4 space-y-3">
          <div v-if="messages.length === 0" class="h-full grid place-items-center">
            <p class="text-neutral-300 text-sm">Sube un PDF y escribe tu primera pregunta para ayudarte.</p>
          </div>

          <div
            v-for="(m, i) in messages"
            :key="i"
            class="flex items-end gap-3"
            :class="m.role === 'user' ? 'flex-row-reverse' : ''"
          >
            <div
              class="size-8 rounded-full grid place-items-center font-bold border border-white/10"
              :class="m.role === 'user' ? 'bg-cyan-600/30 text-cyan-100' : 'bg-violet-600/30 text-violet-100'"
            >
              {{ m.role === 'user' ? 'Tú' : 'AI' }}
            </div>

            <div
              class="max-w-[70%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap border border-white/10"
              :class="m.role === 'user' ? 'bg-cyan-900/40' : 'bg-white/5'"
            >
              {{ m.text }}
            </div>
          </div>
        </div>

        <div class="p-3 border-t border-white/10 flex gap-2">
          <input
            v-model="question"
            :disabled="uploading || !documentId"
            :placeholder="documentId ? 'Escribe tu pregunta…' : 'Sube un PDF para comenzar'"
            class="flex-1 bg-black/40 border border-white/10 rounded-xl px-3 py-2 outline-none
                   focus:border-cyan-400/60 disabled:opacity-60"
            @keyup.enter="ask"
          />
          <button
            class="px-4 py-2 rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 text-neutral-950 font-semibold
                   disabled:opacity-60"
            :disabled="!question.trim() || uploading || !documentId"
            @click="ask"
          >
            Enviar
          </button>
        </div>
      </section>
    </main>

    <footer class="border-t border-white/10 px-5 py-4 text-center text-neutral-300 text-sm">
      Hecho por Marcos
    </footer>
  </div>
</template>
