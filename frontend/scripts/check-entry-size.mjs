import { readFile, stat } from 'node:fs/promises'
import { resolve } from 'node:path'

const dist = resolve('dist')
const html = await readFile(resolve(dist, 'index.html'), 'utf8')
const match = html.match(/<script[^>]+src="\/next\/(assets\/[^"]+\.js)"/)
if (!match) throw new Error('Unable to find the entry JavaScript asset in dist/index.html')
const bytes = (await stat(resolve(dist, match[1]))).size
const limit = 500 * 1024
console.log(`Entry bundle ${match[1]}: ${(bytes / 1024).toFixed(1)} KiB (limit 500 KiB)`)
if (bytes >= limit) process.exitCode = 1
