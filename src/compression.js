// compression.js

export function compress(data) {
  let compressed = ''
  let count = 1
  for (let i = 0; i < data.length; i++) {
    if (data[i] === data[i + 1]) {
      count++
    } else {
      compressed += count > 1 ? count + data[i] : data[i]
      count = 1
    }
  }
  return compressed
}

export function decompress(data) {
  let decompressed = ''
  let count = ''
  for (let i = 0; i < data.length; i++) {
    if (!isNaN(data[i])) {
      count += data[i]
    } else {
      decompressed += data[i].repeat(count ? parseInt(count) : 1)
      count = ''
    }
  }
  return decompressed
}
