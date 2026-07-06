#!/usr/bin/env node

import http from 'node:http'
import https from 'node:https'
import fs from 'node:fs'
import { promises as fsp } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')
const distDir = path.join(projectRoot, 'dist')
const indexFile = path.join(distDir, 'index.html')

const backendBaseUrl = new URL(process.env.STUDYPOINT_BACKEND_URL || 'http://127.0.0.1:8001')
const contentTypes = {
  '.css': 'text/css; charset=utf-8',
  '.gif': 'image/gif',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.jpeg': 'image/jpeg',
  '.jpg': 'image/jpeg',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.txt': 'text/plain; charset=utf-8',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
}

function parseArgs(argv) {
  const options = {
    host: '127.0.0.1',
    port: '4173',
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]

    if (arg === '--host' && argv[i + 1]) {
      options.host = argv[i + 1]
      i += 1
      continue
    }

    if (arg.startsWith('--host=')) {
      options.host = arg.slice('--host='.length)
      continue
    }

    if (arg === '--port' && argv[i + 1]) {
      options.port = argv[i + 1]
      i += 1
      continue
    }

    if (arg.startsWith('--port=')) {
      options.port = arg.slice('--port='.length)
    }
  }

  return options
}

function shouldProxy(pathname) {
  return (
    pathname === '/api' ||
    pathname.startsWith('/api/') ||
    pathname === '/docs' ||
    pathname.startsWith('/docs/') ||
    pathname === '/redoc' ||
    pathname.startsWith('/redoc/') ||
    pathname === '/static/plugins' ||
    pathname.startsWith('/static/plugins/') ||
    pathname === '/static/modules' ||
    pathname.startsWith('/static/modules/')
  )
}

function defaultPort(protocol) {
  return protocol === 'https:' ? 443 : 80
}

function sendText(res, statusCode, message) {
  res.writeHead(statusCode, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Length': Buffer.byteLength(message),
  })
  res.end(message)
}

async function statIfExists(filePath) {
  try {
    return await fsp.stat(filePath)
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null
    }
    throw error
  }
}

async function serveFile(req, res, filePath, stat) {
  const ext = path.extname(filePath).toLowerCase()
  const headers = {
    'Content-Length': stat.size,
    'Content-Type': contentTypes[ext] || 'application/octet-stream',
    'Cache-Control': filePath.includes(`${path.sep}assets${path.sep}`)
      ? 'public, max-age=31536000, immutable'
      : 'no-cache',
  }

  res.writeHead(200, headers)

  if (req.method === 'HEAD') {
    res.end()
    return
  }

  const stream = fs.createReadStream(filePath)
  stream.on('error', (error) => {
    console.error('Static file stream error:', error)
    if (!res.headersSent) {
      sendText(res, 500, 'Static file read failed')
      return
    }
    res.destroy(error)
  })
  stream.pipe(res)
}

async function serveStatic(req, res, pathname) {
  if (!['GET', 'HEAD'].includes(req.method || 'GET')) {
    res.setHeader('Allow', 'GET, HEAD')
    sendText(res, 405, 'Method not allowed')
    return
  }

  let decodedPathname
  try {
    decodedPathname = decodeURIComponent(pathname)
  } catch {
    sendText(res, 400, 'Bad request')
    return
  }

  const requestedPath = path.resolve(distDir, `.${decodedPathname}`)
  const distRootPrefix = `${distDir}${path.sep}`
  if (requestedPath !== distDir && !requestedPath.startsWith(distRootPrefix)) {
    sendText(res, 403, 'Forbidden')
    return
  }

  let filePath = requestedPath
  let stat = await statIfExists(filePath)

  if (stat?.isDirectory()) {
    filePath = path.join(filePath, 'index.html')
    stat = await statIfExists(filePath)
  }

  if (stat?.isFile()) {
    await serveFile(req, res, filePath, stat)
    return
  }

  if (path.extname(decodedPathname)) {
    sendText(res, 404, 'Not found')
    return
  }

  const indexStat = await statIfExists(indexFile)
  if (!indexStat?.isFile()) {
    sendText(res, 503, 'Frontend build output is missing')
    return
  }

  await serveFile(req, res, indexFile, indexStat)
}

function proxyRequest(req, res, pathnameAndSearch) {
  const upstreamUrl = new URL(pathnameAndSearch, backendBaseUrl)
  const transport = upstreamUrl.protocol === 'https:' ? https : http
  const forwardedFor = [req.headers['x-forwarded-for'], req.socket.remoteAddress]
    .filter(Boolean)
    .join(', ')

  const headers = {
    ...req.headers,
    host: upstreamUrl.host,
    'x-forwarded-for': forwardedFor,
    'x-forwarded-host': req.headers.host || '',
    'x-forwarded-proto': req.socket.encrypted ? 'https' : 'http',
  }

  const upstreamReq = transport.request(
    {
      protocol: upstreamUrl.protocol,
      hostname: upstreamUrl.hostname,
      port: upstreamUrl.port || defaultPort(upstreamUrl.protocol),
      method: req.method || 'GET',
      path: `${upstreamUrl.pathname}${upstreamUrl.search}`,
      headers,
    },
    (upstreamRes) => {
      res.writeHead(upstreamRes.statusCode || 502, upstreamRes.headers)
      if (req.method === 'HEAD') {
        upstreamRes.resume()
        res.end()
        return
      }
      upstreamRes.pipe(res)
    },
  )

  upstreamReq.on('error', (error) => {
    console.error('Backend proxy error:', error)
    if (!res.headersSent) {
      sendText(res, 502, 'Backend is unavailable')
      return
    }
    res.destroy(error)
  })

  if (['GET', 'HEAD'].includes(req.method || 'GET')) {
    upstreamReq.end()
    return
  }

  req.pipe(upstreamReq)
}

async function main() {
  await fsp.access(distDir)
  const { host, port: rawPort } = parseArgs(process.argv.slice(2))
  const port = Number.parseInt(rawPort, 10)

  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    console.error(`Invalid port: ${rawPort}`)
    process.exit(1)
  }

  const server = http.createServer(async (req, res) => {
    try {
      const originHost = req.headers.host || `${host}:${port}`
      const requestUrl = new URL(req.url || '/', `http://${originHost}`)
      const pathnameAndSearch = `${requestUrl.pathname}${requestUrl.search}`

      if (shouldProxy(requestUrl.pathname)) {
        proxyRequest(req, res, pathnameAndSearch)
        return
      }

      await serveStatic(req, res, requestUrl.pathname)
    } catch (error) {
      console.error('Frontend server error:', error)
      if (!res.headersSent) {
        sendText(res, 500, 'Internal server error')
        return
      }
      res.destroy(error)
    }
  })

  server.on('clientError', (error, socket) => {
    console.error('Client connection error:', error)
    socket.end('HTTP/1.1 400 Bad Request\r\n\r\n')
  })

  server.on('error', (error) => {
    console.error('Failed to bind frontend server:', error)
    process.exit(1)
  })

  server.listen(port, host, () => {
    console.log(`StudyPoint frontend server listening on http://${host}:${port}`)
    console.log(`Proxying backend requests to ${backendBaseUrl.origin}`)
  })
}

main().catch((error) => {
  console.error('Failed to start frontend server:', error)
  process.exit(1)
})
