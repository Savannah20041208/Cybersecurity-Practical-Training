<template>
  <div class="p-6 md:p-8">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">药品拍照识别</h1>
        <p class="text-gray-600 mt-2">上传药盒多角度照片（最多 6 张），提升识别准确率</p>
      </div>

      <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div class="text-center mb-4">
          <p class="text-gray-700">请上传药盒所有带文字的面（最多 6 张），上传越多识别越准</p>
          <p v-if="files.length > 0" class="text-blue-600 font-semibold mt-1">已上传 {{ files.length }}/6 张</p>
        </div>

        <div
          v-if="files.length === 0"
          class="border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer"
          :class="dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50/50'"
          @click="handlePick"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop.prevent="handleDrop"
        >
          <div class="text-gray-500">
            <div class="mx-auto w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-gray-500">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 7.5l-3 2.25 3 2.25m10.5-4.5l3 2.25-3 2.25M3 19.5h18M4.5 4.5h15A1.5 1.5 0 0 1 21 6v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 15V6A1.5 1.5 0 0 1 4.5 4.5Z" />
              </svg>
            </div>
            <div class="font-medium">点击上传或拖拽图片到此处</div>
            <div class="text-sm text-gray-400 mt-1">支持 JPG、PNG、GIF 格式，单张最大 16MB</div>
          </div>
        </div>

        <input
          ref="fileInput"
          type="file"
          class="hidden"
          accept="image/*"
          multiple
          @change="handleFileChange"
        />

        <div v-if="files.length > 0" class="mt-5 grid grid-cols-2 md:grid-cols-3 gap-4">
          <div
            v-for="(item, idx) in files"
            :key="item.id"
            class="relative rounded-xl overflow-hidden border border-gray-200 bg-gray-50"
          >
            <button
              type="button"
              class="absolute top-2 left-2 w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center"
            >
              {{ idx + 1 }}
            </button>

            <button
              type="button"
              class="absolute bottom-2 right-2 w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center hover:bg-red-700"
              @click.stop="removeAt(idx)"
              title="删除"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>

            <img
              :src="item.url"
              class="w-full h-40 object-cover cursor-pointer hover:scale-[1.02] transition-transform"
              :alt="`药盒照片 ${idx + 1}`"
              @click="openPreview(item.url)"
            />
          </div>
        </div>

        <div class="mt-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <label class="flex items-center gap-2 text-gray-700">
            <input type="checkbox" v-model="enhance" class="h-4 w-4 text-blue-600" />
            图像增强
          </label>

          <div class="flex items-center gap-3">
            <button
              v-if="files.length < 6"
              type="button"
              class="px-4 py-2 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50"
              @click="handlePick"
            >
              + {{ addButtonText }}
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="files.length >= 6"
              @click="openCamera"
            >
              拍照
            </button>
            <input
              ref="cameraInput"
              type="file"
              class="hidden"
              accept="image/*"
              capture="environment"
              @change="handleCameraFileChange"
            />
          </div>

          <div class="flex items-center gap-3">
            <span v-if="files.length > 0 && files.length < 6" class="text-sm text-gray-500">
              上传更多照片可提升识别准确率
            </span>
            <button
              v-if="files.length > 0"
              type="button"
              class="px-6 py-2 rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-95 disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="loading"
              @click="startIdentify"
            >
              <span v-if="loading" class="flex items-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                识别中...
              </span>
              <span v-else>开始识别</span>
            </button>
          </div>
        </div>

        <div v-if="files.length > 0 && files.length < 6" class="mt-3 text-center text-sm text-gray-500">
          {{ nextAngleHint }}
        </div>
      </div>

      <div v-if="result" class="mt-8 space-y-6">
        <div
          class="rounded-2xl shadow-lg p-6 text-white"
          :class="result.success ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-gradient-to-r from-orange-500 to-amber-600'"
        >
          <div class="flex items-center justify-between gap-6">
            <div>
              <div class="text-xl font-bold">{{ result.success ? '识别成功' : '未找到精确匹配' }}</div>
              <div class="text-sm opacity-90 mt-1">匹配类型：{{ matchTypeText(result.match_type) }}</div>
              <div v-if="result.images_processed" class="text-sm opacity-90 mt-1">处理图片：{{ result.images_processed }} 张</div>
            </div>
            <div class="text-right">
              <div class="text-3xl font-bold">{{ confidencePercent }}%</div>
              <div class="text-sm opacity-90">置信度</div>
            </div>
          </div>
          <div class="mt-4 bg-white/20 rounded-full h-2">
            <div class="bg-white rounded-full h-2" :style="{ width: confidencePercent + '%' }"></div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-1 h-6 bg-blue-600 rounded"></div>
            <h2 class="text-lg font-bold text-gray-900">药品信息</h2>
          </div>

          <div v-if="drugInfoEntries.length === 0" class="text-gray-500">暂无可展示字段</div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="item in drugInfoEntries"
              :key="item.key"
              class="pl-3 py-2 border-l-4 border-blue-500"
            >
              <div class="text-sm text-gray-500">{{ item.label }}</div>
              <div class="text-gray-900 font-medium whitespace-pre-wrap break-words">{{ item.value }}</div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <button
            type="button"
            class="w-full flex items-center justify-between"
            @click="ocrOpen = !ocrOpen"
          >
            <div class="flex items-center gap-3">
              <div class="w-1 h-6 bg-green-600 rounded"></div>
              <h2 class="text-lg font-bold text-gray-900">OCR 识别原文</h2>
            </div>
            <svg
              class="w-5 h-5 text-gray-500 transition-transform"
              :class="ocrOpen ? 'rotate-180' : ''"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="2"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="m19 9-7 7-7-7" />
            </svg>
          </button>

          <div v-if="ocrOpen" class="mt-4">
            <pre class="bg-gray-50 rounded-xl p-4 text-sm text-gray-700 whitespace-pre-wrap">{{ result.ocr_text || '无' }}</pre>
          </div>
        </div>

        <div v-if="(result.candidates || []).length > 0" class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-1 h-6 bg-yellow-500 rounded"></div>
            <h2 class="text-lg font-bold text-gray-900">候选药品</h2>
          </div>

          <div class="space-y-3">
            <div
              v-for="(c, i) in result.candidates.slice(0, 5)"
              :key="i"
              class="p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition"
            >
              <div class="flex items-center justify-between gap-4">
                <div class="font-medium text-gray-900">
                  {{ c.generic_name || c.drug_name || '未知' }}
                  <span class="text-gray-500 text-sm ml-2">{{ c.dosage_form || '' }}</span>
                </div>
                <div class="text-blue-600 font-semibold">{{ c.score || 0 }}分</div>
              </div>
              <div class="text-sm text-gray-500 mt-1">{{ c.enterprise || '' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="previewUrl" class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-6" @click="closePreview">
        <button
          type="button"
          class="absolute top-6 right-6 w-10 h-10 rounded-full bg-white/20 text-white flex items-center justify-center hover:bg-white/30"
          @click.stop="closePreview"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
        <img :src="previewUrl" class="max-w-full max-h-full object-contain rounded-xl" alt="预览" />
      </div>

      <div v-if="cameraOpen" class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-6" @click="closeCamera">
        <div class="w-full max-w-3xl bg-white rounded-2xl shadow-xl overflow-hidden" @click.stop>
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <div class="font-semibold text-gray-900">拍照</div>
            <button
              type="button"
              class="w-9 h-9 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center hover:bg-gray-200"
              @click="closeCamera"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="p-6">
            <div v-if="cameraError" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 text-sm">
              {{ cameraError }}
            </div>
            <div v-if="cameraError" class="mb-4 text-sm text-gray-600">
              {{ cameraHelpText }}
            </div>
            <div class="rounded-xl overflow-hidden bg-black relative">
              <video ref="cameraVideo" class="w-full" autoplay playsinline></video>
              <canvas ref="cameraCanvas" class="hidden"></canvas>
              <div v-if="!cameraReady && !cameraError" class="absolute inset-0 flex items-center justify-center text-white/90 text-sm">
                正在打开摄像头...
              </div>
            </div>
            <div class="mt-4 flex items-center justify-end gap-3">
              <button
                type="button"
                class="px-4 py-2 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50"
                @click="closeCamera"
              >
                取消
              </button>
              <button
                v-if="cameraError"
                type="button"
                class="px-4 py-2 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50"
                @click="retryCamera"
              >
                重试预览
              </button>
              <button
                v-if="cameraError"
                type="button"
                class="px-4 py-2 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50"
                @click="openSystemCamera"
              >
                使用系统相机拍照
              </button>
              <button
                type="button"
                class="px-6 py-2 rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-95 disabled:opacity-60 disabled:cursor-not-allowed"
                :disabled="!cameraReady"
                @click="capturePhoto"
              >
                拍照
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'

const DRUG_API_BASE_URL = import.meta.env.VITE_DRUG_API_BASE_URL || 'http://localhost:5001'

const fileInput = ref(null)
const cameraInput = ref(null)
const dragOver = ref(false)
const enhance = ref(true)
const loading = ref(false)
const ocrOpen = ref(false)

const files = ref([])
const previewUrl = ref('')
const result = ref(null)

const cameraOpen = ref(false)
const cameraError = ref('')
const cameraReady = ref(false)
const cameraVideo = ref(null)
const cameraCanvas = ref(null)

let cameraStream = null

const confidencePercent = computed(() => {
  const c = result.value?.confidence || 0
  return Math.max(0, Math.min(100, Math.round(c * 100)))
})

const addButtonText = computed(() => (files.value.length > 0 ? '继续添加照片' : '拍摄 / 上传照片'))

const nextAngleHint = computed(() => {
  const hints = ['建议先拍：正面（药名/规格/批准文号）', '建议再拍：侧面（厂家/成分）', '建议再拍：背面（用法用量/禁忌）', '建议补拍：顶面/底面（批号/有效期）']
  const idx = Math.min(hints.length - 1, Math.max(0, files.value.length - 1))
  return hints[idx]
})

const cameraHelpText = computed(() => {
  if (!cameraError.value) return ''
  if (typeof window !== 'undefined' && window.isSecureContext === false) {
    return '当前页面不是安全环境（需 https 或 localhost 才能使用网页相机预览）。请改用 http://localhost 访问，或开启 https。'
  }
  const msg = String(cameraError.value || '').toLowerCase()
  if (msg.includes('permission') || msg.includes('denied') || msg.includes('notallowed')) {
    return '请在浏览器地址栏左侧“锁/站点信息”里把相机权限改为“允许”，然后刷新页面再点“重试预览”。'
  }
  return '如果仍无法预览，可点击“使用系统相机拍照”作为替代方案。'
})

const drugInfoEntries = computed(() => {
  const info = result.value?.drug_info || result.value?.matched_drug || result.value?.parsed_info || {}
  const fields = [
    { key: 'generic_name', label: '通用名' },
    { key: 'drug_name', label: '通用名(解析)' },
    { key: 'brand_name', label: '商品名' },
    { key: 'approval_no', label: '批准文号' },
    { key: 'dosage_form', label: '剂型' },
    { key: 'spec', label: '规格' },
    { key: 'enterprise', label: '生产企业' },
    { key: 'otc_type', label: 'OTC分类' },
    { key: 'indications', label: '适应症' },
    { key: 'usage', label: '用法用量' },
    { key: 'contraindications', label: '禁忌' },
    { key: 'adverse_reactions', label: '不良反应' },
    { key: 'storage', label: '贮藏' }
  ]

  return fields
    .map(f => ({
      ...f,
      value: info?.[f.key]
    }))
    .filter(x => x.value !== undefined && x.value !== null && String(x.value).trim() !== '' && String(x.value) !== 'None' && String(x.value) !== 'null')
})

function matchTypeText(type) {
  const map = {
    approval_no: '批准文号精确匹配',
    name_enterprise: '名称+企业匹配',
    fuzzy: '模糊匹配',
    none: '未匹配'
  }
  return map[type] || (type || '未匹配')
}

function handlePick() {
  if (files.value.length >= 6) return
  fileInput.value?.click()
}

function normalizeAndAdd(selected) {
  const incoming = Array.from(selected || [])
  for (const f of incoming) {
    if (files.value.length >= 6) break
    if (!f.type?.startsWith('image/')) continue
    const url = URL.createObjectURL(f)
    files.value.push({ id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}_${Math.random()}`, file: f, url })
  }
}

function handleFileChange(e) {
  normalizeAndAdd(e.target.files)
  e.target.value = ''
}

function handleDrop(e) {
  dragOver.value = false
  normalizeAndAdd(e.dataTransfer.files)
}

function removeAt(index) {
  const item = files.value[index]
  if (item?.url) URL.revokeObjectURL(item.url)
  files.value.splice(index, 1)
}

function openPreview(url) {
  previewUrl.value = url
}

function closePreview() {
  previewUrl.value = ''
}

function handleCameraFileChange(e) {
  normalizeAndAdd(e.target.files)
  e.target.value = ''
}

async function openCamera() {
  if (files.value.length >= 6) return

  cameraError.value = ''
  cameraReady.value = false

  cameraOpen.value = true

  if (typeof window !== 'undefined' && window.isSecureContext === false) {
    cameraError.value = '无法打开摄像头预览：当前页面不是安全环境。可使用系统相机拍照。'
    return
  }

  const canGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  if (!canGetUserMedia) {
    cameraError.value = '当前浏览器不支持摄像头预览，可使用系统相机拍照。'
    return
  }

  try {
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false
      })
    } catch (e) {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      })
    }

    if (!cameraVideo.value) return
    cameraVideo.value.srcObject = cameraStream

    await new Promise(resolve => {
      if (!cameraVideo.value) return resolve()
      if (cameraVideo.value.readyState >= 2) return resolve()
      cameraVideo.value.onloadedmetadata = () => resolve()
    })

    try {
      await cameraVideo.value.play()
    } catch (e) {
    }

    cameraReady.value = true
  } catch (err) {
    cameraReady.value = false
    const msg = err && err.message ? err.message : ''
    cameraError.value = msg
      ? `无法打开摄像头预览：${msg}。可使用系统相机拍照。`
      : '无法打开摄像头预览，可使用系统相机拍照。'
  }
}

function openSystemCamera() {
  cameraInput.value?.click()
}

function retryCamera() {
  closeCamera()
  setTimeout(() => {
    openCamera()
  }, 0)
}

function closeCamera() {
  cameraOpen.value = false
  cameraReady.value = false
  cameraError.value = ''
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop())
    cameraStream = null
  }
}

function capturePhoto() {
  if (!cameraReady.value || !cameraVideo.value || !cameraCanvas.value) return
  if (files.value.length >= 6) {
    closeCamera()
    return
  }

  const video = cameraVideo.value
  const canvas = cameraCanvas.value
  const w = video.videoWidth || 1280
  const h = video.videoHeight || 720
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0, w, h)

  canvas.toBlob((blob) => {
    if (!blob) return
    const file = new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' })
    normalizeAndAdd([file])
    closeCamera()
  }, 'image/jpeg', 0.9)
}

async function startIdentify() {
  if (files.value.length === 0) return

  loading.value = true
  result.value = null
  ocrOpen.value = false

  try {
    const form = new FormData()
    for (const item of files.value) {
      form.append('images', item.file)
    }
    form.append('enhance', String(enhance.value))

    const resp = await fetch(`${DRUG_API_BASE_URL}/api/identify`, {
      method: 'POST',
      body: form
    })

    const data = await resp.json()
    if (!resp.ok) {
      throw new Error(data?.error || `HTTP ${resp.status}`)
    }

    result.value = data
  } catch (err) {
    result.value = {
      success: false,
      message: err?.message || '识别失败',
      match_type: 'none',
      confidence: 0,
      ocr_text: ''
    }
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  closeCamera()
  for (const item of files.value) {
    if (item?.url) URL.revokeObjectURL(item.url)
  }
})
</script>
