import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 创建 Axios 实例
 * baseURL: /api/v1
 */
const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

/**
 * 请求拦截器：自动添加 Authorization Token
 */
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器：处理 401 自动跳转、统一错误提示
 */
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Token 过期或无效，清除登录状态并跳转
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('权限不足，无法执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误，请稍后重试')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (error.message.includes('timeout')) {
      ElMessage.error('请求超时，请检查网络连接')
    } else {
      ElMessage.error('网络连接异常')
    }

    return Promise.reject(error)
  }
)

/**
 * 封装 GET 请求
 */
export function get<T = any>(url: string, params?: Record<string, any>, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, { params, ...config }) as Promise<T>
}

/**
 * 封装 POST 请求
 */
export function post<T = any>(url: string, data?: Record<string, any>, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config) as Promise<T>
}

/**
 * 封装 PUT 请求
 */
export function put<T = any>(url: string, data?: Record<string, any>, config?: AxiosRequestConfig): Promise<T> {
  return service.put(url, data, config) as Promise<T>
}

/**
 * 封装 DELETE 请求
 */
export function del<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, config) as Promise<T>
}

/**
 * 文件下载
 * 发起 blob 下载请求，自动解析 Content-Disposition 获取文件名并触发浏览器下载
 */
export async function downloadFile(url: string, params?: Record<string, any>) {
  const response = await axios.get(url, {
    params,
    responseType: 'blob',
    headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
  })
  const contentDisposition = response.headers['content-disposition'] as string | undefined
  let filename = 'report.xlsx'
  if (contentDisposition) {
    const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (match) filename = match[1].replace(/['"]/g, '')
  }
  const blob = new Blob([response.data])
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

export default service
