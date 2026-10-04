import { createReadStream, existsSync, statSync } from 'node:fs'
import { createServer } from 'node:http'
import { extname, join, normalize, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const distDir = normalize(fileURLToPath(new URL('./dist', import.meta.url)))
const indexFile = join(distDir, 'index.html')
const port = Number(process.env.PORT) || 4173
const host = '0.0.0.0'

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

function safePath(urlPath) {
  let decoded
  try {
    decoded = decodeURIComponent(urlPath.split('?')[0])
  } catch {
    return null
  }

  const relative = decoded.replace(/^\/+/, '')
  const filePath = normalize(join(distDir, relative))
  if (filePath !== distDir && !filePath.startsWith(distDir + sep)) return null
  return filePath
}

function sendText(res, status, body) {
  res.writeHead(status, {
    'Content-Type': 'text/plain; charset=utf-8',
    'X-Content-Type-Options': 'nosniff',
  })
  res.end(body)
}

function sendFile(res, filePath) {
  const extension = extname(filePath).toLowerCase()
  res.writeHead(200, {
    'Content-Type': contentTypes[extension] || 'application/octet-stream',
    'Cache-Control': extension === '.html' ? 'no-cache' : 'public, max-age=31536000, immutable',
    'X-Content-Type-Options': 'nosniff',
  })
  createReadStream(filePath).pipe(res)
}

const server = createServer((req, res) => {
  if (!req.url) {
    sendText(res, 400, 'Bad Request')
    return
  }

  const filePath = safePath(req.url)
  if (!filePath) {
    sendText(res, 400, 'Bad Request')
    return
  }

  if (existsSync(filePath) && statSync(filePath).isFile()) {
    sendFile(res, filePath)
    return
  }

  const pathname = req.url.split('?')[0]
  if (pathname.startsWith('/assets/')) {
    sendText(res, 404, 'Not Found')
    return
  }

  if (!existsSync(indexFile)) {
    sendText(res, 500, 'Frontend build is missing. Run npm run build before npm start.')
    return
  }

  // React Router handles /, /analyze, /about, and the other client routes.
  sendFile(res, indexFile)
})

server.listen(port, host, () => {
  console.log(`Frontend listening on http://${host}:${port}`)
})
